# bot.py – retrieval engine (standard library only)
import os, math, re
import tokenizer

DATA_DIR = "data"            # folder with .txt files

# ---------- 1. load paragraphs ----------
def load_corpus(folder):
    docs = []
    for fname in os.listdir(folder):
        if fname.endswith(".txt"):
            with open(os.path.join(folder, fname), encoding="utf8") as f:
                text = f.read()
            docs += [p.strip().lower()
                    for p in text.split("\n\n") if p.strip()]
    return docs

# ---------- 2. vectorise ----------
def vectorize(doc, vocab):
    vec = [0] * len(vocab)
    for tok in tokenizer.tokenize(doc):
        if tok in vocab:                   # skip unknown words
            vec[vocab[tok]] += 1
    return vec

def build_index(docs, vocab):
    return [vectorize(p, vocab) for p in docs]

# ---------- 3. cosine similarity ----------
def cosine(a, b):
    dot   = sum(x*y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x*x for x in a))
    mag_b = math.sqrt(sum(y*y for y in b))
    return dot / (mag_a * mag_b + 1e-9)

def retrieve(query, vocab, index, docs, k=1):
    q_vec  = vectorize(query, vocab)
    scored = [(cosine(q_vec, v), i) for i, v in enumerate(index)]
    scored.sort(reverse=True)
    return [docs[i] for _, i in scored[:k]]

# ---------- 4. build corpus once (for server & CLI) ----------
DOCS  = load_corpus(DATA_DIR)
VOCAB = tokenizer.build_vocab(DOCS)
INDEX = build_index(DOCS, VOCAB)

def answer(question: str) -> str:
    """Return the best-matching paragraph for a query."""
    best = retrieve(question, VOCAB, INDEX, DOCS)[0]

    # optional tidy-up for “my name” questions
    if re.search(r"\bname\b", question.lower()):
        m = re.search(r"my name is ([a-z\s]+?)[\.,]", best)
        if m:
            best = m.group(1).strip()
    return best

# ---------- 5. optional command-line chat ----------
def main():
    print(f"Loaded {len(DOCS)} paragraphs. Ask away!  (type 'exit' to quit)\n")
    while True:
        q = input("You> ").strip()
        if q.lower() in {"exit", "quit"}:
            break
        print("\nBot>", answer(q), "\n")

if __name__ == "__main__":
    main()