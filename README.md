


# 🤖 RAG-Based LLM Copilot for Apigee

> An intelligent, retrieval-augmented generation chatbot for Apigee API Management — powered by LangChain, ChromaDB vector storage, and `all-MiniLM-L6-v2` sentence embeddings. Built entirely from scratch with no external LLM APIs. Runs locally on any machine.

---

## 📌 Overview

This project is a **production-style Retrieval-Augmented Generation (RAG) system** purpose-built for Apigee API management knowledge. It combines semantic vector search, a persistent ChromaDB vector store, a LangChain retrieval chain, and a custom-trained PyTorch neural classifier to answer technical questions about Apigee policies, proxies, security, and architecture with precision.

Built as a full-stack AI application — from raw tokenization to a polished browser-based chat interface — entirely in Python.

---

https://github.com/user-attachments/assets/1d5aee05-d96a-40e0-b21d-7e690327c685

## 🧠 How It Works

```
User Question
      │
      ▼
┌──────────────────────────┐
│  Sentence Transformer    │  → Encodes question into a 384-dim semantic vector
│  (all-MiniLM-L6-v2)      │    using all-MiniLM-L6-v2
└──────────────────────────┘
      │
      ▼
┌──────────────────────────┐
│  ChromaDB Vector Store   │  → Performs approximate nearest-neighbour search
│                          │    across all embedded knowledge paragraphs
└──────────────────────────┘
      │
      ▼
┌──────────────────────────┐
│  LangChain Retrieval     │  → Retrieval chain selects the top-k most
│  Chain                   │    semantically relevant documents
└──────────────────────────┘
      │
      ▼
┌──────────────────────────┐
│  PyTorch Classifier      │  → Trained on labeled Q&A pairs to validate
│  (nn.Linear)             │    intent and confirm answer relevance
└──────────────────────────┘
      │
      ▼
  Best Answer
  Returned to UI
```

The system uses a **three-stage pipeline**: semantic embedding via a transformer model, vector similarity search through ChromaDB, and intent validation via a trained neural classifier — ensuring answers are both semantically relevant and intent-accurate.

---

## 🏗️ Project Structure

```
Scratch_bot/
│
├── data/
│   ├── story.txt           # Knowledge base — rich Apigee documentation paragraphs
│   └── train.csv           # Labeled Q&A pairs for classifier training
│
├── static/
│   └── index.html          # Professional chat UI (HTML/CSS/JS)
│
├── tokenizer.py            # Custom tokenizer — vocabulary builder
├── token_tfidf.py          # TF-IDF vectorizer for feature extraction
├── token_embed.py          # Embedding pipeline — all-MiniLM-L6-v2 via sentence-transformers
├── bot.py                  # Core RAG retrieval engine
├── bot_embed.py            # Semantic embedding-based retrieval with ChromaDB
├── bot_classifier.py       # Classifier-enhanced answer selection
├── train_classifier.py     # Neural network training script (PyTorch)
├── classifier.pt           # Saved trained model weights
└── server.py               # HTTP server exposing /ask endpoint
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| Embeddings | `sentence-transformers` — `all-MiniLM-L6-v2` (384-dim vectors) |
| Vector Store | ChromaDB — persistent local vector database |
| Retrieval Chain | LangChain `RetrievalQA` |
| Classification | PyTorch `nn.Linear` — trained on labeled Q&A pairs |
| Feature Extraction | TF-IDF (custom implementation) |
| Server | Python `http.server` (zero-dependency HTTP) |
| Frontend | Vanilla HTML / CSS / JavaScript |
| Data | Custom `story.txt` knowledge base + `train.csv` intent labels |

---

## 🚀 Getting Started

### Prerequisites

```bash
Python 3.11+
pip
```

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/Scratch_bot.git
cd Scratch_bot

# Install dependencies
pip install sentence-transformers torch langchain chromadb scikit-learn pandas numpy
```

### Run the Application

Execute these steps **in order**:

```bash
# Step 1 — Build vocabulary from knowledge base
python tokenizer.py

# Step 2 — Generate and store embeddings in ChromaDB
python token_embed.py

# Step 3 — Train the intent classifier
python train_classifier.py

# Step 4 — Start the server
python server.py
```

Then open your browser at:

```
http://localhost:8000
```

---

## 💬 Sample Questions

These questions are optimized for the current knowledge base:

| # | Question | Topic |
|---|---|---|
| 1 | What is Apigee? | Platform overview |
| 2 | What is an API proxy? | Core concept |
| 3 | What is a ProxyEndpoint? | Proxy architecture |
| 4 | What is a TargetEndpoint? | Backend connectivity |
| 5 | How does OAuth work in Apigee? | Security |
| 6 | What is a Quota policy? | Traffic management |
| 7 | What is SpikeArrest? | Rate limiting |
| 8 | What is Apigee X? | Latest platform |
| 9 | What is a KVM in Apigee? | Secret management |
| 10 | What is a shared flow? | Reusability |

---

## 🧩 Core Components Explained

### `tokenizer.py`
Builds a vocabulary index from the knowledge base. Lowercases text, strips punctuation, and maps each unique token to an integer index. This vocabulary is shared across the vectorizer and classifier.

### `token_tfidf.py`
Implements TF-IDF (Term Frequency–Inverse Document Frequency) vectorization for feature extraction. Converts raw text into numeric vectors that capture word importance relative to the entire corpus.

### `token_embed.py`
Encodes every paragraph in `story.txt` into a 384-dimensional semantic vector using `all-MiniLM-L6-v2` from the `sentence-transformers` library. Vectors are persisted in a local ChromaDB collection so embeddings only need to be generated once.

### `bot.py` + `bot_embed.py`
The core RAG retrieval engine. For any incoming question it encodes the question using the same transformer model, queries ChromaDB for the top-k most similar paragraphs, and passes the results through a LangChain `RetrievalQA` chain to select the best answer.

### `train_classifier.py`
Trains a single-layer `nn.Linear` PyTorch model on the labeled `train.csv` dataset. The classifier maps TF-IDF vectors to intent labels, providing a secondary validation layer that ensures answers match the expected intent category even when semantic similarity is ambiguous.

### `server.py`
A lightweight HTTP server that exposes a single `/ask?q=` GET endpoint. Calls the retrieval pipeline and returns a JSON response `{ "answer": "..." }` consumed by the frontend chat UI.

---

## 🔑 Key Design Decisions

**Why `all-MiniLM-L6-v2` for embeddings?**
It is the top-ranked model for semantic search and Q&A retrieval on the SBERT benchmarks. At only 80MB it runs on any laptop with no GPU required, making it ideal for local demo environments. Its 384-dimensional vectors strike the optimal balance between retrieval accuracy and inference speed.

**Why ChromaDB as the vector store?**
ChromaDB is the most developer-friendly persistent vector database available today. It requires zero infrastructure setup, stores embeddings on disk, and supports cosine similarity search out of the box. For a project of this scope it eliminates the operational overhead of Pinecone or Weaviate while delivering equivalent retrieval quality.

**Why LangChain for the retrieval chain?**
LangChain standardizes the retrieval pipeline into a composable interface. Using `RetrievalQA` means the retrieval logic, document ranking, and response formatting are decoupled from the server layer — making it trivial to swap the underlying retriever or upgrade to a generative LLM response layer in the future.

**Why a neural classifier on top of semantic retrieval?**
Semantic similarity alone retrieves the most contextually similar paragraph. The classifier adds intent awareness — distinguishing between questions that share vocabulary but have different intents. This two-stage design mirrors production RAG architectures used at scale.

---

## 📈 Future Enhancements

- [ ] Add a generative LLM layer (Mistral or LLaMA via Ollama) on top of retrieval for synthesized answers
- [ ] Expand ChromaDB collection to cover 100+ Apigee documentation pages
- [ ] Add streaming response support to the frontend
- [ ] Implement multi-hop reasoning for complex multi-part questions
- [ ] Deploy to Google Cloud Run with Apigee X as the API gateway (dogfooding)
- [ ] Add conversation memory using LangChain `ConversationBufferMemory`

---

## 👤 Author

**Bilva Sai Eswar Maddi**

- 🐙 GitHub: [@maddibilvasai4125](https://github.com/maddibilvasai4125)
- 💼 LinkedIn: [Bilva Sai Eswar Maddi](https://www.linkedin.com/in/bilva-sai-eswar-maddi/)
- 📧 Email: catchbilvasaieswar@gmail.com
- 🌐 Portfolio: [My Portfolio](https://bilvasaieswarmaddi.com/)

## 📄 License

This project is licensed under the MIT License. See `LICENSE` for details.

---

> *"The best way to understand a technology is to build something with it that actually works."*
