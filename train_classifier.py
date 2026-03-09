import csv, torch, torch.nn as nn
import token_tfidf as tf

DOCS = tf.load_docs()
vec  = tf.build_vectorizer(DOCS)     # use same TF-IDF as features
N    = len(DOCS)

X, y = [], []
with open("train.csv") as f:
    for q, idx in csv.reader(f):
        X.append(vec.transform([q]).toarray()[0])
        y.append(int(idx))
X = torch.tensor(X, dtype=torch.float32)
y = torch.tensor(y, dtype=torch.long)

model = nn.Linear(X.shape[1], N)
opt   = torch.optim.Adam(model.parameters(), lr=1e-2)
for epoch in range(200):
    opt.zero_grad()
    loss = nn.CrossEntropyLoss()(model(X), y)
    loss.backward(); opt.step()
torch.save(model.state_dict(), "classifier.pt")
print("trained, final loss", loss.item())