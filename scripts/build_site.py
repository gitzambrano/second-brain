#!/usr/bin/env python3
"""Build the public Digital Garden into SITE_ROOT from the publication allowlist.

The site is a one-way projection: only essays whose frontmatter carries the YAML
boolean ``publish: true`` are rendered, indexed or linked. Nothing else from the
private data repository is ever copied.

No-argument default: rebuild the whole site.
    --manifest   print what would be published, write nothing
    --check      verify an existing site against the current allowlist
    --no-render  skip Pandoc rendering (structure/index only)
"""
from __future__ import annotations

import argparse
import html
import json
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

import build_public_map
from repo_paths import CODE_ROOT, SITE_ROOT, SITE_SRC_DIR
from site_common import (
    collect_all,
    collect_public,
    plain_text,
    public_body_for_index,
)

GENERATED_ROOT_FILES = {
    "index.html", "graph.html", "sphere.html", "404.html",
    "graph.json", "search-index.json", "site-manifest.json",
}
GENERATED_DIRS = {"essays", "assets"}
FRONTEND_ASSETS = ("site.css", "theme.js", "site.js", "essay.js")

# Fields that would turn a map node into readable body content or into a pointer
# at the private repository. `htmlFile` is the read link and is checked on its own.
GRAPH_PRIVATE_FIELDS = ("file", "body", "text", "path")


def require_site_root(root: Path) -> None:
    """Refuse to write anywhere that is not a marked site checkout."""
    if not root.is_dir():
        raise SystemExit(f"SITE_ROOT does not exist: {root}")
    if not (root / ".second-brain-site").exists():
        raise SystemExit(f"refusing to write without .second-brain-site marker: {root}")


def clean(root: Path) -> None:
    require_site_root(root)
    for name in GENERATED_ROOT_FILES:
        path = root / name
        if path.exists():
            path.unlink()
    for name in GENERATED_DIRS:
        path = root / name
        if path.exists():
            shutil.rmtree(path)


def copy_frontend(root: Path) -> None:
    assets = root / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    for name in FRONTEND_ASSETS:
        shutil.copy2(SITE_SRC_DIR / name, assets / name)


WORDS_PER_MINUTE = 220


def reading_minutes(text: str) -> int:
    """Rounded reading time, never below one minute."""
    words = len(text.split())
    return max(1, round(words / WORDS_PER_MINUTE))


def write_data(root: Path, catalogue) -> dict[str, int]:
    """Write the machine files.

    The catalogue lists every essay, because the index does. Only an authorized
    essay contributes its body: `text` powers full-text search and exists solely
    for pages a reader can actually open.
    """
    allowed = {e.slug for e in catalogue if e.published}
    body_text = {
        e.slug: plain_text(public_body_for_index(e, allowed))
        for e in catalogue if e.published
    }

    search = []
    for essay in catalogue:
        entry = {
            "slug": essay.slug,
            "title": essay.title,
            "summary": essay.summary,
            "tags": list(essay.tags),
            "updated": essay.updated,
            "created": essay.created,
            "status": essay.status,
            "published": essay.published,
        }
        if essay.published:
            entry["minutes"] = reading_minutes(body_text[essay.slug])
            entry["url"] = f"essays/{essay.slug}.html"
            entry["text"] = body_text[essay.slug]
        search.append(entry)

    def dump(name: str, data) -> None:
        (root / name).write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    dump("search-index.json", search)
    dump("site-manifest.json", {
        "generated": date.today().isoformat(),
        "published": sorted(allowed),
        "count": len(allowed),
        "catalogue": len(catalogue),
    })
    return {slug: reading_minutes(text) for slug, text in body_text.items()}


def render_index(root: Path, catalogue, minutes: dict[str, int] | None = None) -> None:
    """Render the catalogue: every essay, with only the authorized ones linked."""
    minutes = minutes or {}
    template = (SITE_SRC_DIR / "index.html").read_text(encoding="utf-8")
    tags = sorted({t for e in catalogue for t in e.tags}, key=str.casefold)
    tag_counts = {t: sum(1 for e in catalogue if t in e.tags) for t in tags}
    latest = sorted(catalogue, key=lambda e: e.updated or e.created, reverse=True)
    published = [e for e in catalogue if e.published]

    cards = []
    for essay in latest:
        tag_html = "".join(
            f'<span class="tag">{html.escape(t)}</span>' for t in essay.tags
        )
        # The search haystack is pre-folded so the client only lowercases input.
        searchable = html.escape(
            " ".join([essay.title, essay.summary, *essay.tags]).casefold(), quote=True
        )

        meta = [f'<span>{html.escape(essay.updated)}</span>']
        reading = minutes.get(essay.slug, 0)
        if reading:
            meta.append('<span class="dot" aria-hidden="true">·</span>'
                        f'<span>{reading} min de leitura</span>')

        badges = []
        if not essay.published:
            badges.append('<span class="badge badge-private">Privado</span>')
        if essay.status == "draft":
            badges.append('<span class="badge badge-draft">Rascunho</span>')
        badge_html = f'<div class="badges">{"".join(badges)}</div>' if badges else ""

        inner = (
            f'<div class="card-meta">{"".join(meta)}</div>'
            f'{badge_html}'
            f'<h3>{html.escape(essay.title)}</h3>'
            f'<p>{html.escape(essay.summary)}</p>'
            f'<div class="tags">{tag_html}</div>'
        )
        if essay.published:
            inner += ('<span class="read-link">Ler essay '
                      '<span aria-hidden="true">&rarr;</span></span>')
            body = f'<a href="essays/{html.escape(essay.slug)}.html">{inner}</a>'
        else:
            # No link: the text is not published, and the card must not pretend.
            inner += '<span class="read-link muted">Não publicado</span>'
            body = f'<div class="card-body">{inner}</div>'

        cards.append(
            f'<article class="essay-card{"" if essay.published else " is-private"}"'
            f' data-search="{searchable}"'
            f' data-tags="{html.escape("|".join(essay.tags), quote=True)}"'
            f' data-updated="{html.escape(essay.updated, quote=True)}"'
            f' data-minutes="{reading}"'
            f' data-published="{"1" if essay.published else "0"}"'
            f' data-title="{html.escape(essay.title, quote=True)}">'
            f'{body}</article>'
        )

    chips = "".join(
        f'<button class="filter-chip" type="button" data-tag="{html.escape(t, quote=True)}">'
        f'{html.escape(t)} <span class="count">{tag_counts[t]}</span></button>'
        for t in tags
    )
    updated = max((e.updated for e in catalogue if e.updated), default="—")

    page = (template
            .replace("{{COUNT}}", str(len(catalogue)))
            .replace("{{PUBLISHED}}", str(len(published)))
            .replace("{{TAG_COUNT}}", str(len(tags)))
            .replace("{{UPDATED}}", html.escape(updated))
            .replace("{{CARDS}}", "\n".join(cards))
            .replace("{{TAG_FILTERS}}", chips))
    (root / "index.html").write_text(page, encoding="utf-8")


def render_essays(root: Path, essays, no_render: bool = False) -> None:
    out = root / "essays"
    out.mkdir(parents=True, exist_ok=True)
    if no_render:
        return
    renderer = CODE_ROOT / "scripts" / "render_public_essay.py"
    for essay in essays:
        proc = subprocess.run(
            [sys.executable, str(renderer), essay.slug,
             "--output", str(out / f"{essay.slug}.html")],
            cwd=CODE_ROOT, capture_output=True, text=True,
            encoding="utf-8", errors="replace",
        )
        if proc.returncode:
            raise SystemExit(proc.stdout + "\n" + proc.stderr)


def build(root: Path, no_render: bool = False):
    catalogue = collect_all()
    essays = [e for e in catalogue if e.published]
    clean(root)
    copy_frontend(root)
    minutes = write_data(root, catalogue)
    render_index(root, catalogue, minutes)

    # The map is produced by the wiki's own renderers, on sanitized nodes.
    nodes, edges, tag_gaps, isolated = build_public_map.build()
    build_public_map.write(root, nodes, edges, tag_gaps, isolated)

    source = SITE_SRC_DIR / "404.html"
    if source.exists():
        shutil.copy2(source, root / "404.html")
    render_essays(root, essays, no_render)
    return essays


def check(root: Path) -> list[str]:
    """Verify a built site still matches the current allowlist exactly."""
    require_site_root(root)
    allowed = {e.slug for e in collect_public()}
    errors: list[str] = []

    manifest = root / "site-manifest.json"
    if not manifest.exists():
        errors.append("missing site-manifest.json")
    else:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        if set(payload.get("published", [])) != allowed:
            errors.append("manifest differs from current publish:true allowlist")

    # The catalogue lists every essay. Body text and a page link belong only to
    # the authorized ones.
    search = root / "search-index.json"
    if search.exists():
        for entry in json.loads(search.read_text(encoding="utf-8")):
            slug = entry.get("slug")
            if entry.get("published") and slug not in allowed:
                errors.append(f"entry marked published but not authorized: {slug}")
            if not entry.get("published"):
                if entry.get("text"):
                    errors.append(f"body text exposed for unpublished essay: {slug}")
                if entry.get("url"):
                    errors.append(f"unauthorized link in search index: {slug}")

    # The map deliberately contains every node. What it must never contain is
    # body text, a private path, or a way into anything outside the allowlist.
    graph = root / "graph.json"
    if graph.exists():
        payload = json.loads(graph.read_text(encoding="utf-8"))
        for node in payload.get("nodes", []):
            node_id = node.get("id")
            slug = str(node_id or "").partition(":")[2]
            readable = bool(node.get("public"))
            if readable and slug not in allowed:
                errors.append(f"node marked public but not authorized: {node_id}")
            link = str(node.get("htmlFile") or "")
            if link and (not readable or link != f"essays/{slug}.html"):
                errors.append(f"unauthorized read link in map: {node_id} -> {link}")
            url = str(node.get("url") or "")
            if url and not url.startswith(("http://", "https://")):
                errors.append(f"non-external url in map: {node_id} -> {url}")
            for field in GRAPH_PRIVATE_FIELDS:
                if node.get(field):
                    errors.append(f"private field '{field}' in map node {node_id}")

    essays_dir = root / "essays"
    if essays_dir.exists():
        extra = {p.stem for p in essays_dir.glob("*.html")} - allowed
        if extra:
            errors.append(f"stale/private HTML: {sorted(extra)}")

    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="validate an existing site")
    ap.add_argument("--manifest", action="store_true", help="list what would be published")
    ap.add_argument("--no-render", action="store_true", help="skip Pandoc rendering")
    args = ap.parse_args()

    if args.manifest:
        print(json.dumps(
            [{"slug": e.slug, "title": e.title} for e in collect_public()],
            ensure_ascii=False, indent=2,
        ))
        return 0

    if args.check:
        errors = check(SITE_ROOT)
        print("site: PASS" if not errors else "site: FAIL")
        for error in errors:
            print(f"  ERROR {error}")
        return 1 if errors else 0

    essays = build(SITE_ROOT, args.no_render)
    print(f"site generated: {SITE_ROOT}")
    print(f"published essays: {len(essays)}")
    for essay in essays:
        print(f"  {essay.slug} — {essay.title}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
