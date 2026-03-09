# tokenizer.py – zero-dependency word helper
import re
from typing import List, Dict, Sequence

def tokenize(text: str) -> List[str]:
    """Split text into lowercase word tokens (a-z and ')."""
    return re.findall(r"[a-z']+", text.lower())

def build_vocab(docs: Sequence[str]) -> Dict[str, int]:
    """Return word→id dictionary gathered from every doc."""
    vocab: Dict[str, int] = {}
    for doc in docs:
        for tok in tokenize(doc):
            if tok not in vocab:
                vocab[tok] = len(vocab)
    return vocab

def encode(text_or_tokens, vocab: Dict[str, int]) -> List[int]:
    """Convert words to ids, skipping unknowns."""
    if isinstance(text_or_tokens, str):
        text_or_tokens = tokenize(text_or_tokens)
    return [vocab[t] for t in text_or_tokens if t in vocab]

def decode(ids: Sequence[int], inv_vocab: Dict[int, str]) -> str:
    """Convert ids back to a space-separated string."""
    return " ".join(inv_vocab[i] for i in ids)