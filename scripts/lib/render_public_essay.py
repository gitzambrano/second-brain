#!/usr/bin/env python3
"""Render public essays with the very same pipeline as the HTML export.

The export already solves essay typography: `html_preprocess.transform_markdown`
turns the corpus blockquote conventions into typed boxes, verdicts, pull-quotes
and cards, and `essay_template.html` lays out the cover, byline, chapter rules,
ornaments, justified measure and footnotes. Reimplementing any of that for the
site would mean maintaining two renderers that drift.

So this module calls the export's own `prepare_for_pandoc` and its template, and
then layers the site on top:

    * a theme override — the site palette, background and font;
    * site chrome — nav back to the Atlas, a floating summary, related essays;
    * shared images instead of data URIs, so a page stays tens of kilobytes.

Only essays authorized with `visibility: public` can be rendered.

No-argument default: render every public essay into SITE_ROOT/essays.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from export_essay_html import PANDOC_FROM, TEMPLATE_PATH, prepare_for_pandoc
from repo_paths import ASSETS_DIR, SITE_ROOT, SITE_SRC_DIR
from site_common import collect_public, public_connections, sanitize_private_wikilinks

IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
REMOTE_RE = re.compile(r"^(https?://|data:)", re.I)
ALLOWED_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}


def rewrite_images(markdown: str, source: Path) -> str:
    """Copy referenced local images into the site and rewrite their links.

    An image is published only if it resolves inside DATA_ROOT/wiki/assets and
    has a web-safe extension. Anything else degrades to its alt text rather than
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


def pandoc(markdown: str, title: str, subtitle: str, author: str,
           summary: str, status: str) -> str:
    """Run the export's own Pandoc invocation, minus the offline embedding."""
    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "essay.md"
        source.write_text(markdown, encoding="utf-8")
        cmd = [
            "pandoc", str(source),
            "--standalone",
            f"--template={TEMPLATE_PATH}",
            "--highlight-style=pygments",
            "--mathjax",
            "-V", f"title={title}",
            "-V", f"subtitle={subtitle}",
            "-V", f"author={author}",
            "-V", f"summary={summary}",
            *(["-V", f"status={status}"] if status else []),
            "-f", PANDOC_FROM,
            "-t", "html5",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              encoding="utf-8", errors="replace")
        if proc.returncode:
            raise SystemExit("Pandoc failed:\n" + proc.stderr)
        return proc.stdout


def asset_version(name: str) -> str:
    """Content fingerprint, so a redeploy can never serve a stale script."""
    source = SITE_SRC_DIR / name
    if not source.exists():
        return "0"
    return hashlib.sha256(source.read_bytes()).hexdigest()[:8]


def site_chrome(essay, related) -> str:
    """Nav back to the Atlas, a floating summary, and public connections."""
    related_html = "".join(
        f'<a class="sb-related-card" href="{html.escape(r.slug)}.html">'
        f"<strong>{html.escape(r.title)}</strong>"
        f"<span>{html.escape(r.summary)}</span></a>"
        for r in related
    )
    related_block = (
        f'<section class="sb-related"><h2>Continue explorando</h2>'
        f'<div class="sb-related-grid">{related_html}</div></section>'
        if related else ""
    )
    tags = "".join(f'<span class="sb-tag">{html.escape(t)}</span>' for t in essay.tags)
    theme_v = asset_version("theme.js")
    essay_v = asset_version("essay.js")

    return f"""
<header class="sb-bar">
  <a class="sb-brand" href="../index.html"><span class="sb-mark">SB</span>Second Brain Atlas</a>
  <nav class="sb-nav">
    <a href="../index.html">Essays</a>
    <a href="../graph.html">Grafo</a>
    <a href="../sphere.html">Globo</a>
    <button type="button" id="sbTheme" aria-label="Alternar tema" aria-pressed="false">◐</button>
  </nav>
</header>
<div class="sb-progress"><span id="sbProgressFill"></span></div>
<div class="sb-tags">{tags}</div>
{related_block}
<button class="sb-toc-fab" type="button" id="sbTocFab" aria-expanded="false" aria-controls="sbToc" title="Sumário do essay">
  <span class="sb-toc-icon" aria-hidden="true">☰</span>
  <span class="sb-toc-text">Sumário</span>
</button>
<aside class="sb-toc" id="sbToc" hidden aria-label="Sumário do essay">
  <header><strong>Sumário</strong>
    <button type="button" id="sbTocClose" aria-label="Fechar">×</button></header>
  <nav id="sbTocList"></nav>
</aside>
<script src="../assets/theme.js?v={theme_v}"></script>
<script src="../assets/essay.js?v={essay_v}"></script>
"""


def render(slug: str, output: Path) -> None:
    essays = collect_public()
    by_slug = {e.slug: e for e in essays}
    if slug not in by_slug:
        raise SystemExit(f"not public or not found: {slug}")

    essay = by_slug[slug]
    allowed = set(by_slug)

    # The export reads the file; give it one with public-safe wikilinks and
    # site-relative images, leaving its own preprocessing untouched.
    prepared = sanitize_private_wikilinks(essay.path.read_text(encoding="utf-8-sig"), allowed)
    prepared = rewrite_images(prepared, essay.path)

    with tempfile.TemporaryDirectory() as tmp:
        staged = Path(tmp) / essay.path.name
        staged.write_text(prepared, encoding="utf-8")
        body, title, subtitle, author_date, summary, status = prepare_for_pandoc(staged)

    page = pandoc(body, title, subtitle, author_date, summary, status)

    theme = (SITE_SRC_DIR / "essay-theme.css").read_text(encoding="utf-8")
    related = [by_slug[s] for s in public_connections(essay, allowed) if s in by_slug]
    chrome = site_chrome(essay, related)

    page = page.replace("</head>", f"<style>{theme}</style>\n</head>", 1)
    page = page.replace("</body>", chrome + "</body>", 1)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(page, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("slug", nargs="?",
                    help="essay slug; omit to render every public essay")
    ap.add_argument("--output", type=Path,
                    help="explicit output file (requires an explicit slug)")
    args = ap.parse_args()

    if args.slug is None:
        if args.output:
            raise SystemExit("--output requires an explicit slug")
        slugs = [e.slug for e in collect_public()]
        if not slugs:
            print("no public essays")
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
