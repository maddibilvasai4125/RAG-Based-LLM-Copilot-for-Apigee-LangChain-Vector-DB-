"""
HTML → clean Markdown with front-matter metadata (resilient)
- Follows canonical links when the first fetch is a shell/placeholder.
- Tries version fallbacks for Google Cloud docs ('latest' → concrete v1.x).
"""
# allow running from subfolder
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

import time
import re
import yaml
import requests
from bs4 import BeautifulSoup
import trafilatura
from slugify import slugify
from pydantic import BaseModel
from settings import DATA_RAW, DATA_CLEAN, ensure_dirs

UA = {"User-Agent": "ApigeeDocsRAG/1.0 (local-edu)"}

class Source(BaseModel):
    url: str
    product: str
    topic: str

FRONT_MATTER = (
    "---\n"
    "title: \"{title}\"\n"
    "product: {product}\n"
    "topic: {topic}\n"
    "url: {url}\n"            # final URL actually used (after any fallbacks)
    "fetched_at: {ts}\n"
    "---\n\n"
)

LOW_QUALITY_PATTERNS = [
    "The equivalent page does not exist in the selected hybrid version",
    "Click the browser\nback button",
    "Except as otherwise noted, the content of this page is licensed",
]

FALLBACK_VERSIONS = ["v1.12", "v1.11", "v1.10", "v1.9"]


def fetch_html(url: str) -> str:
    r = requests.get(url, headers=UA, timeout=30)
    r.raise_for_status()
    return r.text


def extract_main_text(html: str) -> str | None:
    # Prefer trafilatura; fallback to plaintext
    extracted = trafilatura.extract(
        html, include_comments=False, include_tables=True, favor_precision=True
    )
    if extracted:
        return extracted.strip()
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text("\n").strip()


def is_low_quality(text: str) -> bool:
    if not text or len(text.split()) < 80:
        return True
    lower = text.lower()
    for p in LOW_QUALITY_PATTERNS:
        if p.lower() in lower:
            return True
    return False


def find_canonical(html: str, base_url: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    link = soup.find("link", rel="canonical")
    if link and link.get("href") and link["href"] != base_url:
        return link["href"]
    return None


def try_version_fallbacks(url: str) -> str | None:
    """If url contains '/latest/', try concrete versions."""
    if "/latest/" not in url:
        return None
    for v in FALLBACK_VERSIONS:
        candidate = url.replace("/latest/", f"/{v}/")
        try:
            html = fetch_html(candidate)
            text = extract_main_text(html)
            if not is_low_quality(text):
                return candidate
        except Exception:
            pass
    return None


def smart_fetch(url: str) -> tuple[str, str, str]:
    """
    Returns (final_url, title, text)
    Strategy:
      1) fetch url
      2) if low-quality → follow canonical if present
      3) if still low-quality and url had /latest/ → try version fallbacks
    """
    # Add ?hl=en to stabilize content language
    base_url = url if "cloud.google.com" not in url else (url + ("?hl=en" if "?" not in url else "&hl=en"))

    html = fetch_html(base_url)
    text = extract_main_text(html)
    soup = BeautifulSoup(html, "html.parser")
    title = (soup.title.string.strip() if soup.title and soup.title.string else base_url)

    if not is_low_quality(text):
        return base_url, title, text

    # 2) canonical
    canon = find_canonical(html, base_url)
    if canon:
        try:
            html2 = fetch_html(canon)
            text2 = extract_main_text(html2)
            soup2 = BeautifulSoup(html2, "html.parser")
            title2 = (soup2.title.string.strip() if soup2.title and soup2.title.string else canon)
            if not is_low_quality(text2):
                return canon, title2, text2
        except Exception:
            pass

    # 3) version fallbacks for /latest/
    vf = try_version_fallbacks(base_url)
    if vf:
        html3 = fetch_html(vf)
        text3 = extract_main_text(html3)
        soup3 = BeautifulSoup(html3, "html.parser")
        title3 = (soup3.title.string.strip() if soup3.title and soup3.title.string else vf)
        return vf, title3, text3

    # Give back whatever we have (will likely be filtered at chunk/index time)
    return base_url, title, text


def main():
    ensure_dirs()
    src_path = Path("data/sources.yml")
    if not src_path.exists():
        raise SystemExit("Missing data/sources.yml — add your doc URLs.")

    sources = [Source(**row) for row in yaml.safe_load(src_path.read_text())]

    for s in sources:
        try:
            final_url, title, text = smart_fetch(s.url)

            # Save raw snapshot from the final_url too (for audit)
            raw_name = f"{slugify(final_url)[:120]}.html"
            (DATA_RAW / raw_name).write_text(fetch_html(final_url), encoding="utf-8")

            md = FRONT_MATTER.format(
                title=title.replace('"', '\\"'),
                product=s.product,
                topic=s.topic,
                url=final_url,
                ts=int(time.time()),
            ) + text + "\n"

            out_name = f"{slugify(s.product)}__{slugify(s.topic)}__{slugify(title)[:80]}.md"
            (DATA_CLEAN / out_name).write_text(md, encoding="utf-8")
            print(f"✓ Saved clean markdown: {out_name}  ← {final_url}")
        except Exception as e:
            print(f"! Failed {s.url}: {e}")


if __name__ == "__main__":
    main()