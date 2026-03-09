"""
Chunks → embeddings → vector store (Chroma or FAISS)
New Chroma API (langchain-chroma): persist via chromadb.PersistentClient; no vs.persist().
"""
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

import json
import shutil
from typing import List, Dict

import chromadb
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.vectorstores import FAISS

from settings import DATA_CHUNKS, INDEX_DIR, EMBED_MODEL, VECTOR_STORE, ensure_dirs

RESET = True          # set True to rebuild from scratch
COLLECTION = "apigee_docs"

def load_chunks() -> (List[str], List[Dict], List[str]):
    meta_path = DATA_CHUNKS / "chunks_meta.json"
    if not meta_path.exists():
        raise SystemExit("Missing data/chunks/chunks_meta.json — run tools/chunk.py first.")
    metas = json.loads(meta_path.read_text(encoding="utf-8"))
    texts, metadatas, ids = [], [], []
    for m in metas:
        cid = m["id"]
        t = (DATA_CHUNKS / f"{cid}.md").read_text(encoding="utf-8")
        texts.append(t)
        metadatas.append(m)
        ids.append(cid)
    return texts, metadatas, ids

def main():
    ensure_dirs()

    if VECTOR_STORE == "chroma":
        # Optional clean rebuild
        if RESET and INDEX_DIR.exists():
            shutil.rmtree(INDEX_DIR)

    texts, metadatas, ids = load_chunks()

    embed = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        encode_kwargs={"normalize_embeddings": True},
    )

    if VECTOR_STORE == "chroma":
        # ✅ New persistence pattern
        client = chromadb.PersistentClient(path=str(INDEX_DIR))
        vs = Chroma(
            client=client,
            collection_name=COLLECTION,
            embedding_function=embed,
        )
        # Add documents (auto-persisted by PersistentClient)
        vs.add_texts(texts=texts, metadatas=metadatas, ids=ids)
        print(f"✓ Built Chroma index at {INDEX_DIR}")
    else:
        vs = FAISS.from_texts(texts=texts, embedding=embed, metadatas=metadatas)
        FAISS.save_local(vs, str(INDEX_DIR / "faiss_index"))
        print("✓ Built FAISS index (saved under ./index/faiss_index)")

if __name__ == "__main__":
    main()