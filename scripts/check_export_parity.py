#!/usr/bin/env python3
"""Compare semantic invariants across Markdown, HTML and PDF exports.

This is intentionally not byte/pixel regression. It checks whether exportable
information survived the pipeline. ``## Conexões`` is the known exception: it
must remain in Markdown and disappear from both external formats.

No-argument default: audit every essay for which both HTML and PDF exist.
"""
from __future__ import annotations

import argparse
import html as html_lib
import re
from pathlib import Path

from repo_paths import ESSAYS_DIR, HTML_DIR, PDF_DIR
from sanity_common import CheckResult


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def html_text(path: Path) -> tuple[str, int]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    try:
        from bs4 import BeautifulSoup, FeatureNotFound
        try:
            soup = BeautifulSoup(raw, "html5lib")
        except FeatureNotFound:
            soup = BeautifulSoup(raw, "html.parser")
        return soup.get_text(" ", strip=True), len(soup.find_all("img"))
    except ImportError:
        plain = re.sub(r"<script.*?</script>|<style.*?</style>", " ", raw, flags=re.S | re.I)
        plain = re.sub(r"<[^>]+>", " ", plain)
        return html_lib.unescape(plain), len(re.findall(r"<img\b", raw, re.I))


def pdf_text(path: Path) -> tuple[str, int]:
    import pymupdf as fitz
    doc = fitz.open(path)
    try:
        text = "\n".join(page.get_text("text") for page in doc)
        images = sum(len(page.get_images(full=True)) for page in doc)
        return text, images
    finally:
        doc.close()


def source_fingerprint(path: Path) -> dict:
    md = path.read_text(encoding="utf-8-sig")
    title = (re.search(r"(?m)^#\s+(.+)$", md) or [None, ""])[1].strip()
    h2 = [h.strip() for h in re.findall(r"(?m)^##\s+(.+)$", md)]
    export_h2 = [h for h in h2 if h != "Conexões"]
    refs = re.findall(r"(?m)^\[\d+\]\s+(.+)$", md)
    ref_titles = []
    for ref in refs:
        m = re.search(r"\*([^*]+)\*", ref)
        if m:
            ref_titles.append(m.group(1).strip())
    return {
        "title": title,
        "h2": export_h2,
        "connections": "Conexões" in h2,
        "reference_titles": ref_titles,
        "images": len(re.findall(r"!\[[^\]]*\]\([^\)]+\)", md)),
    }


def audit(slug: str | None = None) -> CheckResult:
    result = CheckResult("export-parity")
    sources = [ESSAYS_DIR / f"{slug}.md"] if slug else sorted(ESSAYS_DIR.glob("*.md")) if ESSAYS_DIR.exists() else []
    checked = 0
    for source in sources:
        if not source.exists() or source.name == ".gitkeep":
            continue
        hp = HTML_DIR / f"{source.stem}.html"
        pp = PDF_DIR / f"{source.stem}.pdf"
        if not hp.exists() or not pp.exists():
            result.skip(
                "EXPORT_PAIR_INCOMPLETE",
                f"{source.stem}: HTML and PDF are both required for parity",
                source.name,
            )
            continue
        try:
            ptext, pimages = pdf_text(pp)
        except ImportError:
            result.error("PYMUPDF_MISSING", "PyMuPDF required for parity")
            break
        htext, himages = html_text(hp)
        fp = source_fingerprint(source)
        nh, npdf = norm(htext), norm(ptext)
        for label in [fp["title"], *fp["h2"]]:
            if label and norm(label) not in nh:
                result.error("HTML_TEXT_MISSING", f"missing heading/title: {label}", source.name)
            if label and norm(label) not in npdf:
                result.error("PDF_TEXT_MISSING", f"missing heading/title: {label}", source.name)
        for title in fp["reference_titles"]:
            if norm(title) not in nh:
                result.error("HTML_REFERENCE_MISSING", title, source.name)
            if norm(title) not in npdf:
                result.error("PDF_REFERENCE_MISSING", title, source.name)
        if fp["connections"]:
            if "conexões" in nh:
                result.error("HTML_CONNECTIONS_EXPORTED", "Conexões should not be exported", source.name)
            if "conexões" in npdf:
                result.error("PDF_CONNECTIONS_EXPORTED", "Conexões should not be exported", source.name)
        if himages < fp["images"]:
            result.error("HTML_IMAGE_COUNT", f"source {fp['images']}, HTML {himages}", source.name)
        if pimages < fp["images"]:
            result.error("PDF_IMAGE_COUNT", f"source {fp['images']}, PDF {pimages}", source.name)
        checked += 1
    if not checked and not result.issues:
        result.skip("NO_EXPORT_PAIRS", "no complete Markdown+HTML+PDF export pairs found")
    result.meta["pairs_checked"] = checked
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("slug", nargs="?", help="optional essay stem; default audits all complete export pairs")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    result = audit(args.slug)
    result.print(args.json)
    return result.exit_code()


if __name__ == "__main__":
    raise SystemExit(main())
