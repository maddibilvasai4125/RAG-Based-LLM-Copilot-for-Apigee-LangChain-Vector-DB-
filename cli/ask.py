"""
Ask the bot: retrieve → rerank → prompt → local LLM → print with citations.

WHY (kid + interview):
- Vector search (k=20) = cast a wide net (recall).
- Reranker (top-5) = a careful reader picks the best (precision).
- Strict prompt = answer ONLY from those passages (grounding) + citations.
- Local LLM via Ollama = free, private, fast to iterate.
"""
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))  # allow 'from settings import ...'

import argparse
import textwrap
from typing import List, Dict

import chromadb
from FlagEmbedding import FlagReranker
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.llms import Ollama

from settings import INDEX_DIR, EMBED_MODEL, RERANK_MODEL, LLM_MODEL, PROMPTS_DIR

PROMPT_PATH = PROMPTS_DIR / "base.txt"


def load_vectorstore():
    """Open the persisted Chroma collection using PersistentClient (new API)."""
    embed = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        encode_kwargs={"normalize_embeddings": True},  # BGE authors recommend cosine-normalized embeddings
    )
    client = chromadb.PersistentClient(path=str(INDEX_DIR))
    return Chroma(client=client, collection_name="apigee_docs", embedding_function=embed)


def topk_with_rerank(vs, question: str, k_search=20, k_final=5) -> List[Dict]:
    """
    1) vector search for recall
    2) rerank for precision (cross-encoder reads Q+passage together)
    Returns top k_final passages with their metadata.
    """
    docs = vs.similarity_search(question, k=k_search)
    candidates = [{"text": d.page_content, "meta": d.metadata} for d in docs]
    if not candidates:
        return []

    pairs = [(question, c["text"]) for c in candidates]
    reranker = FlagReranker(RERANK_MODEL, use_fp16=False)  # CPU-friendly
    scores = reranker.compute_score(pairs)                 # list[float]
    ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
    return [c for (c, _) in ranked[:k_final]]


def build_prompt(passages: List[Dict], question: str) -> str:
    """Fill the 5 slots; if fewer passages, leave blanks so the format stays fixed."""
    tpl = PROMPT_PATH.read_text(encoding="utf-8")
    slots = {f"passage_{i+1}": (passages[i]["text"] if i < len(passages) else "") for i in range(5)}
    return tpl.format(question=question, **slots)


def main():
    ap = argparse.ArgumentParser(description="Ask Apigee-LLM a question.")
    ap.add_argument("question", nargs="*", help="Your question")
    args = ap.parse_args()
    q = " ".join(args.question).strip()
    if not q:
        print('Usage: python cli/ask.py "Your question here"')
        raise SystemExit(1)

    vs = load_vectorstore()
    top5 = topk_with_rerank(vs, q, k_search=20, k_final=5)
    if not top5:
        print("I don’t have that in the docs yet.")
        return

    prompt = build_prompt(top5, q)

    try:
        llm = Ollama(model=LLM_MODEL, temperature=0.3, num_ctx=4096)
        answer = llm.invoke(prompt).strip()
    except Exception as e:
        print("LLM backend (Ollama) error:", e)
        print("Fix:")
        print("  1) brew install --cask ollama    # macOS")
        print("  2) ollama pull llama3:8b-instruct")
        print("  3) ollama serve   (or open the Ollama app)")
        return

    # Deduplicate sources in the order we used them
    seen = set()
    sources = []
    for p in top5:
        t = p["meta"].get("title", "")
        u = p["meta"].get("url", "")
        key = (t, u)
        if (t or u) and key not in seen:
            seen.add(key)
            sources.append((t, u))

    print("\n=== Answer ===\n")
    print(textwrap.fill(answer, width=100))

    print("\n=== Sources ===")
    for i, (t, u) in enumerate(sources, 1):
        label = t if t else u
        print(f"[S{i}] {label} -> {u}")

    print("\n--- Retrieved passages (debug) ---")
    for i, p in enumerate(top5, 1):
        title = p['meta'].get('title', '')
        snippet = p['text'].replace("\n", " ")
        print(f"[{i}] {title}")
        print(textwrap.shorten(snippet, width=300))
        print()


if __name__ == "__main__":
    main()