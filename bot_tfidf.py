"""
bot_tfidf.py  —  Chatbot that uses TF-IDF word-weights for matching
Requires:  numpy, scikit-learn
Works with the helper file token_tfidf.py
"""

import numpy as np
import token_tfidf as tf                    # ← helper that loads docs & builds TF-IDF

# ----------------------------------------------------------------------
# 1) Build the corpus and a TF-IDF vectorizer **once** when the program starts
# ----------------------------------------------------------------------
DOCS          = tf.load_docs()               # list of paragraph strings
VECTORIZER    = tf.build_vectorizer(DOCS)    # sklearn TfidfVectorizer
DOC_VECTORS   = VECTORIZER.transform(DOCS)   # sparse matrix [n_docs, vocab]

# ----------------------------------------------------------------------
# 2) Answer function — returns the best-matching paragraph for a question
# ----------------------------------------------------------------------
def answer(question: str) -> str:
    q_vec  = VECTORIZER.transform([question])       # shape [1, vocab]
    sims   = (q_vec @ DOC_VECTORS.T).toarray()[0]   # cosine similarity because TF-IDF vectors are L2-normed
    best_i = int(np.argmax(sims))                   # index of highest score
    return DOCS[best_i]

# ----------------------------------------------------------------------
# 3) Simple command-line chat loop
# ----------------------------------------------------------------------
if __name__ == "__main__":
    print(f"Loaded {len(DOCS)} paragraphs.  Type a question (exit to quit):\n")
    while True:
        q = input("You> ").strip()
        if q.lower() in {"exit", "quit"}:
            break
        print("\nBot>", answer(q), "\n")