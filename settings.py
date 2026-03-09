"""
Project settings for paths & defaults.
Why now: all other scripts import these constants so we don’t hardcode paths everywhere.
"""
from pathlib import Path

# Root folders (project directory)
PROJECT_ROOT = Path(__file__).resolve().parent

# Data layout
DATA_DIR = PROJECT_ROOT / "data"
DATA_RAW = DATA_DIR / "raw"      # save raw HTML for audit/repro
DATA_CLEAN = DATA_DIR / "clean"  # normalized Markdown with front-matter
DATA_CHUNKS = DATA_DIR / "chunks" # (used next chunk)

# Index folder (used next chunk)
INDEX_DIR = PROJECT_ROOT / "index"

# Prompts folder (used later)
PROMPTS_DIR = PROJECT_ROOT / "prompts"

# Eval folder (optional, later)
EVAL_DIR = PROJECT_ROOT / "eval"

# Reasonable default chunk settings (used next chunk)
CHUNK_SIZE_TOKENS = 800
CHUNK_OVERLAP_TOKENS = 100

# Models (used next chunk / answering)
EMBED_MODEL = "BAAI/bge-small-en-v1.5"
RERANK_MODEL = "BAAI/bge-reranker-base"
VECTOR_STORE = "chroma"  # or "faiss"
LLM_MODEL = "llama3:8b-instruct"  # local via Ollama later


def ensure_dirs():
    """Create all project folders if missing (idempotent)."""
    for p in [DATA_RAW, DATA_CLEAN, DATA_CHUNKS, INDEX_DIR, PROMPTS_DIR, EVAL_DIR]:
        p.mkdir(parents=True, exist_ok=True)