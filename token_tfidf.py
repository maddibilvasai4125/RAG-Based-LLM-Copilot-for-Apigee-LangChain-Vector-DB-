# token_tfidf.py
import re, pathlib
from sklearn.feature_extraction.text import TfidfVectorizer

def load_docs(folder="data"):
    txts = []
    for p in pathlib.Path(folder).glob("*.txt"):
        text = p.read_text(encoding="utf8").lower()
        txts += [t for t in text.split("\n\n") if t.strip()]
    return txts

def build_vectorizer(docs):
    return TfidfVectorizer(token_pattern=r"[a-z']+").fit(docs)

# quick test
if __name__ == "__main__":
    docs = load_docs()
    vec = build_vectorizer(docs)
    q = "where was i born"
    sims = (vec.transform([q]) @ vec.transform(docs).T).toarray()[0]
    best = docs[sims.argmax()]
    print("BEST:", best)