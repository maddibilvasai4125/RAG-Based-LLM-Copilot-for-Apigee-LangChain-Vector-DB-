# token_embed.py
from sentence_transformers import SentenceTransformer
import numpy as np, pathlib, re

MODEL = SentenceTransformer("thenlper/gte-small")   # auto-downloads

def load_docs(folder="data"):
    txts = []
    for p in pathlib.Path(folder).glob("*.txt"):
        text = p.read_text(encoding="utf8").lower()
        txts += [t for t in text.split("\n\n") if t.strip()]
    return txts

def embed(texts):
    return MODEL.encode(texts, normalize_embeddings=True)