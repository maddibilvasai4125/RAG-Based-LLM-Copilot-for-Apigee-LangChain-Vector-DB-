# bot_embed.py  – chat with sentence-embeddings
import token_embed as te           # helper we made earlier
import numpy as np

DOCS  = te.load_docs()
EMBDS = te.embed(DOCS)             # matrix  [n_paragraphs, 384]

def answer(q: str) -> str:
    qv   = te.embed([q])[0]        # 384-dim vector for the question
    sims = EMBDS @ qv              # cosine because embed() returns unit vectors
    return DOCS[int(np.argmax(sims))]

# tiny CLI loop
if __name__ == "__main__":
    print(f"Loaded {len(DOCS)} paragraphs. Ask me anything (exit to quit)!\n")
    while True:
        q = input("You> ").strip()
        if q.lower() in {"exit", "quit"}:
            break
        print("\nBot>", answer(q), "\n")