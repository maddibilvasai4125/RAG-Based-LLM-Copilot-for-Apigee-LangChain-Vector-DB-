"""
bot_classifier.py  —  chat with the tiny neural-net classifier you trained
Requires:  torch, numpy, scikit-learn
Depends on:  token_tfidf.py   and   classifier.pt  (created by train_classifier.py)
"""

import token_tfidf as tf
import torch, torch.nn as nn
import numpy as np

# ----------------------------------------------------------------------
# 1)  Load paragraphs + TF-IDF feature space
# ----------------------------------------------------------------------
DOCS       = tf.load_docs()
VECT       = tf.build_vectorizer(DOCS)          # same vocab as during training

# ----------------------------------------------------------------------
# 2)  Re-create the exact linear model shape and load learned weights
# ----------------------------------------------------------------------
model = nn.Linear(len(VECT.vocabulary_), len(DOCS))
model.load_state_dict(torch.load("classifier.pt"))
model.eval()                                    # inference mode

# ----------------------------------------------------------------------
# 3)  Helper to pick answer or say "I don't know"
# ----------------------------------------------------------------------
def answer(question: str, threshold: float = 0.15) -> str:
    x = torch.tensor(VECT.transform([question]).toarray(),
                     dtype=torch.float32)       # shape [1, vocab]
    with torch.no_grad():
        probs = torch.softmax(model(x), dim=1).numpy()[0]   # convert to numpy
    best_idx = int(np.argmax(probs))
    best_prob = probs[best_idx]

    # If the model isn't confident, apologise.
    if best_prob < threshold:
        return "Hmm, I'm not sure."
    return DOCS[best_idx]

# ----------------------------------------------------------------------
# 4)  Command-line chat loop
# ----------------------------------------------------------------------
if __name__ == "__main__":
    print(f"Loaded {len(DOCS)} paragraphs. Ask away! (type 'exit' to quit)\n")
    while True:
        q = input("You> ").strip()
        if q.lower() in {"exit", "quit"}:
            break
        print("\nBot>", answer(q), "\n")