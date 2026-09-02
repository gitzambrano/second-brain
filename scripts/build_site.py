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

from repo_paths import CODE_ROOT, SITE_ROOT, SITE_SRC_DIR
from site_common import (
    collect_public,
    plain_text,
    public_body_for_index,
    public_connections,
)

GENERATED_ROOT_FILES = {
    "index.html", "graph.html", "404.html",
    "graph.json", "search-index.json", "site-manifest.json",
}
GENERATED_DIRS = {"essays", "assets"}
FRONTEND_ASSETS = ("site.css", "theme.js", "site.js", "essay.js", "graph.js")


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


def write_data(root: Path, essays) -> None:
    """Write the machine files. They carry public identities only."""
    allowed = {e.slug for e in essays}

    search = [{
        "slug": e.slug,
        "title": e.title,
        "summary": e.summary,
        "tags": list(e.tags),
        "updated": e.updated,
        "created": e.created,
        "url": f"essays/{e.slug}.html",
        "text": plain_text(public_body_for_index(e, allowed)),
    } for e in essays]

    nodes = [{
        "id": e.slug,
        "title": e.title,
        "summary": e.summary,
        "tags": list(e.tags),
        "updated": e.updated,
        "url": f"essays/{e.slug}.html",
    } for e in essays]

    edges = []
    seen = set()
    for essay in essays:
        for target in public_connections(essay, allowed):
            key = tuple(sorted((essay.slug, target)))
            if key not in seen:
                seen.add(key)
                edges.append({"source": essay.slug, "target": target})

    def dump(name: str, payload) -> None:
        (root / name).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    dump("search-index.json", search)
    dump("graph.json", {"nodes": nodes, "edges": edges})
    dump("site-manifest.json", {
        "generated": date.today().isoformat(),
        "published": [e.slug for e in essays],
        "count": len(essays),
    })


def render_index(root: Path, essays) -> None:
    template = (SITE_SRC_DIR / "index.html").read_text(encoding="utf-8")
    tags = sorted({t for e in essays for t in e.tags}, key=str.casefold)
    latest = sorted(essays, key=lambda e: e.updated or e.created, reverse=True)

    cards = []
    for essay in latest:
        tag_html = "".join(
            f'<span class="tag">{html.escape(t)}</span>' for t in essay.tags
        )
        searchable = html.escape(
            " ".join([essay.title, essay.summary, *essay.tags]).casefold(), quote=True
        )
        cards.append(
            '<article class="essay-card"'
            f' data-search="{searchable}"'
            f' data-tags="{html.escape("|".join(essay.tags), quote=True)}"'
            f' data-updated="{html.escape(essay.updated, quote=True)}"'
            f' data-title="{html.escape(essay.title, quote=True)}">'
            f'<a href="essays/{html.escape(essay.slug)}.html">'
            f'<div class="card-meta"><span>{html.escape(essay.updated)}</span></div>'
            f'<h3>{html.escape(essay.title)}</h3>'
            f'<p>{html.escape(essay.summary)}</p>'
            f'<div class="tags">{tag_html}</div>'
            '<span class="read-link">Ler essay <span aria-hidden="true">&rarr;</span></span>'
            '</a></article>'
        )

    chips = "".join(
        f'<button class="filter-chip" type="button" data-tag="{html.escape(t, quote=True)}">'
        f'{html.escape(t)}</button>'
        for t in tags
    )
    updated = max((e.updated for e in essays if e.updated), default="—")

    page = (template
            .replace("{{COUNT}}", str(len(essays)))
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
    essays = collect_public()
    clean(root)
    copy_frontend(root)
    write_data(root, essays)
    render_index(root, essays)
    for name in ("graph.html", "404.html"):
        source = SITE_SRC_DIR / name
        if source.exists():
            shutil.copy2(source, root / name)
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

    search = root / "search-index.json"
    if search.exists():
        indexed = {x.get("slug") for x in json.loads(search.read_text(encoding="utf-8"))}
        leaked = indexed - allowed
        if leaked:
            errors.append(f"private slugs in search index: {sorted(leaked)}")

    graph = root / "graph.json"
    if graph.exists():
        payload = json.loads(graph.read_text(encoding="utf-8"))
        leaked = {x.get("id") for x in payload.get("nodes", [])} - allowed
        if leaked:
            errors.append(f"private graph nodes: {sorted(leaked)}")
        for edge in payload.get("edges", []):
            if edge.get("source") not in allowed or edge.get("target") not in allowed:
                errors.append(f"private graph edge: {edge}")

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
