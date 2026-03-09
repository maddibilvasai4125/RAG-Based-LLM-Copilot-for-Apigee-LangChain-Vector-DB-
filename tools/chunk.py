"""
Markdown → overlapping chunks for RAG.
Kid analogy: cut your neat notes into labeled index cards with a little overlap.
Why: small pieces = precise retrieval; overlap keeps context across cuts.
"""
# Allow running from subfolder (python tools/chunk.py)
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

import re
import json
from typing import Dict, List
from pydantic import BaseModel
from langchain_text_splitters import RecursiveCharacterTextSplitter
from settings import (
    DATA_CLEAN, DATA_CHUNKS,
    CHUNK_SIZE_TOKENS, CHUNK_OVERLAP_TOKENS,
    ensure_dirs,
)

# Simple boilerplate/placeholder detector (skip ultra-short or obvious boilerplate)
LOW_SIGNAL_MIN_CHARS = 200
LOW_SIGNAL_PATTERNS = [
    "The equivalent page does not exist in the selected hybrid version",
    "Click the browser\nback button",
    "Except as otherwise noted, the content of this page is licensed",
]

class ChunkMeta(BaseModel):
    id: str
    file: str
    title: str
    product: str
    topic: str
    url: str
    start_char: int
    end_char: int

def read_front_matter(text: str) -> Dict[str, str]:
    m = re.match(r"^---\n(.+?)\n---\n", text, re.S)
    meta = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip().strip('"')
    return meta

def strip_front_matter(text: str) -> str:
    return re.sub(r"^---\n(.+?)\n---\n", "", text, flags=re.S)

def is_low_signal(s: str) -> bool:
    if not s or len(s) < LOW_SIGNAL_MIN_CHARS:
        return True
    low = s.lower()
    for p in LOW_SIGNAL_PATTERNS:
        if p.lower() in low:
            return True
    return False

def main():
    ensure_dirs()
    DATA_CHUNKS.mkdir(parents=True, exist_ok=True)

    splitter = RecursiveCharacterTextSplitter(
        # ~4 chars ≈ 1 token heuristic; adjust if you later add a tokenizer
        chunk_size=CHUNK_SIZE_TOKENS * 4,
        chunk_overlap=CHUNK_OVERLAP_TOKENS * 4,
        length_function=len,
        separators=["\n## ", "\n### ", "\n- ", "\n", " "],
    )

    all_meta: List[Dict] = []
    for md_path in DATA_CLEAN.glob("*.md"):
        text = md_path.read_text(encoding="utf-8")
        meta = read_front_matter(text)
        body = strip_front_matter(text)

        if is_low_signal(body):
            print(f"! Skipped low-signal file: {md_path.name}")
            continue

        pieces = splitter.split_text(body)

        # Filter very short chunks (noise)
        pieces = [c for c in pieces if not is_low_signal(c)]
        if not pieces:
            print(f"! No usable chunks after filtering: {md_path.name}")
            continue

        for i, chunk in enumerate(pieces):
            cid = f"{md_path.stem}__{i:03d}"
            (DATA_CHUNKS / f"{cid}.md").write_text(chunk, encoding="utf-8")
            all_meta.append(ChunkMeta(
                id=cid,
                file=md_path.name,
                title=meta.get("title", md_path.stem),
                product=meta.get("product", "unknown"),
                topic=meta.get("topic", "unknown"),
                url=meta.get("url", ""),
                start_char=0,
                end_char=len(chunk),
            ).model_dump())
        print(f"✓ {md_path.name}: {len(pieces)} chunks")

    (DATA_CHUNKS / "chunks_meta.json").write_text(
        json.dumps(all_meta, indent=2), encoding="utf-8"
    )
    print("✓ Saved: data/chunks/chunks_meta.json")

if __name__ == "__main__":
    main()