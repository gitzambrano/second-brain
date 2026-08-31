#!/usr/bin/env python3
"""Semantic/integrity checker for exported PDFs using PyMuPDF.

No-argument default: audit every ``output/pdf/*.pdf``. A skeleton repository
with no PDFs is a valid SKIP, not a failure.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from repo_paths import ESSAYS_DIR, PDF_DIR
from sanity_common import CheckResult

A4 = (595.28, 841.89)
SIZE_TOLERANCE_PT = 4.0


def _source_for(pdf: Path) -> Path | None:
    candidate = ESSAYS_DIR / f"{pdf.stem}.md"
    return candidate if candidate.exists() else None


def audit_file(path: Path, result: CheckResult) -> None:
    try:
        import fitz
    except ImportError:
        result.error("PYMUPDF_MISSING", "PyMuPDF is required for PDF checks", path.name)
        return
    try:
        doc = fitz.open(path)
    except Exception as exc:
        result.error("PDF_OPEN_FAILED", str(exc), path.name)
        return
    try:
        if doc.page_count == 0:
            result.error("EMPTY_DOCUMENT", "PDF has zero pages", path.name)
            return
        all_text: list[str] = []
        image_total = 0
        for index, page in enumerate(doc):
            rect = page.rect
            if abs(rect.width - A4[0]) > SIZE_TOLERANCE_PT or abs(rect.height - A4[1]) > SIZE_TOLERANCE_PT:
                result.error(
                    "PAGE_SIZE_INVALID",
                    f"page {index + 1}: {rect.width:.1f}x{rect.height:.1f}pt, expected A4",
                    path.name,
                )
            text = page.get_text("text")
            images = page.get_images(full=True)
            image_total += len(images)
            if not text.strip() and not images and not page.get_drawings():
                result.error("EMPTY_PAGE", f"page {index + 1} has no text, images or drawings", path.name)
            if "\ufffd" in text:
                result.error("REPLACEMENT_CHARACTER", f"page {index + 1} contains U+FFFD", path.name)
            for link in page.get_links():
                kind = link.get("kind")
                if kind == fitz.LINK_URI and not str(link.get("uri", "")).startswith(
                    ("http://", "https://", "mailto:")
                ):
                    result.error("BROKEN_EXTERNAL_LINK", f"page {index + 1}: {link.get('uri')!r}", path.name)
                if kind == fitz.LINK_GOTO:
                    target = link.get("page", -1)
                    if not isinstance(target, int) or target < 0 or target >= doc.page_count:
                        result.error("BROKEN_INTERNAL_LINK", f"page {index + 1}: invalid target {target}", path.name)
            all_text.append(text)
        joined = "\n".join(all_text)
        if re.search(r"(?mi)^\s*(?:##\s*)?Conexões\s*$", joined):
            result.error("CONEXOES_EXPORTED", "internal Conexões section is visible in PDF", path.name)

        source = _source_for(path)
        if source:
            md = source.read_text(encoding="utf-8-sig")
            h1 = re.search(r"(?m)^#\s+(.+)$", md)
            if h1 and h1.group(1).strip() not in joined:
                result.error("TITLE_MISSING", f"source title not found in PDF: {h1.group(1).strip()}", path.name)
            if "Gustavo Zambrano" in md and "Gustavo Zambrano" not in joined:
                result.error("AUTHOR_MISSING", "author missing from rendered PDF", path.name)
            if "## Sumário" in md and "Sumário" not in joined:
                result.error("SUMARIO_MISSING", "source has Sumário but PDF text does not", path.name)
            if "## Referências" in md and "Referências" not in joined:
                result.error("REFERENCES_MISSING", "source has Referências but PDF text does not", path.name)
            source_images = len(re.findall(r"!\[[^\]]*\]\([^\)]+\)", md))
            if source_images and image_total < source_images:
                result.error(
                    "IMAGE_MISSING",
                    f"source has {source_images} image(s), PDF exposes {image_total}",
                    path.name,
                )
    finally:
        doc.close()


def audit(slug: str | None = None) -> CheckResult:
    result = CheckResult("pdf-content")
    files = sorted(PDF_DIR.glob(f"{slug or '*'}.pdf")) if PDF_DIR.exists() else []
    if not files:
        result.skip("NO_PDF", f"no PDFs in {PDF_DIR}")
        return result
    for path in files:
        audit_file(path, result)
    result.meta["files"] = len(files)
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("slug", nargs="?", help="optional PDF stem; default audits all PDFs")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--fail-on-warning", action="store_true")
    args = ap.parse_args()
    result = audit(args.slug)
    result.print(args.json)
    return result.exit_code(args.fail_on_warning)


if __name__ == "__main__":
    raise SystemExit(main())
