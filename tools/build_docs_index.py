#!/usr/bin/env python3
"""Auto-generate the grounded documentation index from source specs.

Scans docs/contract-additions/*.md (+ the surfaces README) and emits a grounded
corpus: {path, title, summary, headings, keywords} per doc. The NLQA/support surface
answers ONLY from this index and cites back to it — a doc is a witness of source, and
an answer is a witness of the docs. Regenerate whenever the specs change; the surface's
LIVE/SAMPLE badge reflects whether it is reading a freshly generated index.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STOP = set("the a an and or of to in for is are on with by as it be this that from at into your you our we".split())


def _keywords(text, k=12):
    words = re.findall(r"[A-Za-z][A-Za-z0-9-]{2,}", text.lower())
    freq = {}
    for w in words:
        if w not in STOP:
            freq[w] = freq.get(w, 0) + 1
    return [w for w, _ in sorted(freq.items(), key=lambda x: -x[1])[:k]]


def index_doc(p: Path) -> dict:
    text = p.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    title = next((l.lstrip("# ").strip() for l in lines if l.startswith("# ")), p.stem)
    headings = [l.lstrip("# ").strip() for l in lines if re.match(r"^#{2,3} ", l)]
    # first non-heading, non-blank paragraph as summary
    summary = ""
    for l in lines:
        s = l.strip()
        if s and not s.startswith("#") and not s.startswith("|") and not s.startswith(">"):
            summary = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)  # strip md links
            break
    return {
        "path": str(p.relative_to(ROOT)),
        "title": title,
        "summary": summary[:280],
        "headings": headings[:12],
        "keywords": _keywords(title + " " + " ".join(headings) + " " + summary + " " + text),
    }


def main() -> int:
    docs = sorted((ROOT / "docs" / "contract-additions").glob("*.md"))
    readme = ROOT / "docs" / "surfaces" / "README.md"
    if readme.exists():
        docs.append(readme)
    index = [index_doc(p) for p in docs if p.name != "README.md" or p == readme]
    out = ROOT / "docs" / "surfaces" / "data" / "docs-index.json"
    out.write_text(json.dumps({
        "provenance": "live",
        "generated_by": "tools/build_docs_index.py",
        "doc_count": len(index),
        "docs": index,
    }, ensure_ascii=False, indent=2) + "\n")
    print(f"docs-index: {len(index)} docs → {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
