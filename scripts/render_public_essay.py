#!/usr/bin/env python3
"""Render public essays into the site shell using Pandoc.

Only essays authorized with ``publish: true`` can be rendered. Wikilinks pointing
at private pages are neutralised before rendering, and an image is copied only
when it lives inside DATA_ROOT/wiki/assets.

No-argument default: render every publish:true essay into SITE_ROOT/essays.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import subprocess
from pathlib import Path

from repo_paths import ASSETS_DIR, SITE_ROOT, SITE_SRC_DIR
from site_common import (
    collect_public,
    public_connections,
    sanitize_private_wikilinks,
    strip_public_body,
)

IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
REMOTE_RE = re.compile(r"^(https?://|data:)", re.I)
ALLOWED_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}


def rewrite_images(markdown: str, source: Path) -> str:
    """Copy referenced local images into the site and rewrite their links.

    An image is published only if it resolves inside DATA_ROOT/wiki/assets and has
    a web-safe extension. Anything else degrades to its alt text rather than
    leaking a private path.
    """
    destdir = SITE_ROOT / "assets" / "media"
    destdir.mkdir(parents=True, exist_ok=True)

    def replace(match: re.Match[str]) -> str:
        alt, raw = match.group(1), match.group(2).strip()
        if REMOTE_RE.match(raw):
            return match.group(0)

        clean = raw.split(" ", 1)[0].strip("<>")
        candidate = (source.parent / clean).resolve()
        if not candidate.exists():
            candidate = (ASSETS_DIR / Path(clean).name).resolve()

        placeholder = alt or "[imagem omitida]"
        if not candidate.is_file():
            return placeholder
        try:
            candidate.relative_to(ASSETS_DIR.resolve())
        except ValueError:
            return placeholder
        if candidate.suffix.lower() not in ALLOWED_IMAGE_SUFFIXES:
            return placeholder

        dest = destdir / candidate.name
        payload = candidate.read_bytes()
        if dest.exists() and dest.read_bytes() != payload:
            digest = hashlib.sha256(payload).hexdigest()[:12]
            dest = destdir / f"{candidate.stem}-{digest}{candidate.suffix}"
        shutil.copy2(candidate, dest)
        return f"![{alt}](../assets/media/{dest.name})"

    return IMAGE_RE.sub(replace, markdown)


def pandoc(markdown: str) -> str:
    proc = subprocess.run(
        ["pandoc", "--from", "markdown+tex_math_dollars", "--to", "html5", "--mathjax"],
        input=markdown, text=True, capture_output=True,
        encoding="utf-8", errors="replace",
    )
    if proc.returncode:
        raise SystemExit("Pandoc failed:\n" + proc.stderr)
    return proc.stdout


def render(slug: str, output: Path) -> None:
    essays = collect_public()
    by_slug = {e.slug: e for e in essays}
    if slug not in by_slug:
        raise SystemExit(f"not publish:true or not found: {slug}")

    essay = by_slug[slug]
    allowed = set(by_slug)

    body = sanitize_private_wikilinks(strip_public_body(essay.body), allowed)
    body = rewrite_images(body, essay.path)
    fragment = pandoc(body)

    related = [by_slug[s] for s in public_connections(essay, allowed) if s in by_slug]
    related_html = "".join(
        f'<a class="related-card" href="{html.escape(r.slug)}.html">'
        f'<strong>{html.escape(r.title)}</strong>'
        f'<span>{html.escape(r.summary)}</span></a>'
        for r in related
    ) or '<p class="muted">Nenhuma conexão pública direta.</p>'

    tags_html = "".join(
        f'<span class="tag">{html.escape(t)}</span>' for t in essay.tags
    )

    template = (SITE_SRC_DIR / "essay.html").read_text(encoding="utf-8")
    page = (template
            .replace("{{TITLE}}", html.escape(essay.title))
            .replace("{{SUMMARY}}", html.escape(essay.summary))
            .replace("{{UPDATED}}", html.escape(essay.updated))
            .replace("{{TAGS}}", tags_html)
            .replace("{{BODY}}", fragment)
            .replace("{{RELATED}}", related_html)
            .replace("{{META_JSON}}", html.escape(json.dumps(
                {"slug": essay.slug, "title": essay.title}, ensure_ascii=False))))

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(page, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("slug", nargs="?",
                    help="essay slug; omit to render every publish:true essay")
    ap.add_argument("--output", type=Path,
                    help="explicit output file (requires an explicit slug)")
    args = ap.parse_args()

    if args.slug is None:
        if args.output:
            raise SystemExit("--output requires an explicit slug")
        slugs = [e.slug for e in collect_public()]
        if not slugs:
            print("no publish:true essays")
            return 0
        for slug in slugs:
            out = SITE_ROOT / "essays" / f"{slug}.html"
            render(slug, out)
            print(out)
        return 0

    out = args.output or SITE_ROOT / "essays" / f"{args.slug}.html"
    render(args.slug, out)
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
