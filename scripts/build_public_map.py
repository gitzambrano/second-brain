#!/usr/bin/env python3
"""Generate the public map — graph and sphere — with the wiki's own renderers.

`build_graph.py` and `build_sphere.py` already produce the interactive map the
wiki uses — index panel, expandable summaries, draft badges, search, styling.
This script does not reimplement any of that. It takes the same node set, strips
what must not be public, and hands it to the same renderers.

What crosses into the public map:
    title, type, tags, summary (essays), draft status, degree, size, layout,
    every connection, and the external URL of a bibliography entry.

What never crosses:
    the body of any page, the `file` path into the private repository, and a
    read link for anything that is not an authorized essay. An unpublished node
    is on the map and cannot be opened.

A static site cannot hide what it serves: a title or summary here is public.
That is the deliberate trade — the catalogue is public, the text is not.

No-argument default: write the public map into SITE_ROOT.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import build_graph
import build_sphere
from repo_paths import SITE_ROOT
from site_common import collect_public

# Node fields that would leak content or point back at the private repository.
FORBIDDEN_NODE_FIELDS = ("file", "body", "text", "path")

# Summaries are published for essays only; the renderer shows no others.
SUMMARY_TYPES = {"essay"}

MD_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
MD_EMPHASIS = re.compile(r"[*_]{1,3}")


def clean_citation(text: str) -> str:
    """Render an AIAA citation as plain text for a map label."""
    text = MD_LINK.sub(
        lambda m: "" if m.group(1).strip().lower() == "link" else m.group(1), text
    )
    text = MD_EMPHASIS.sub("", text)
    return re.sub(r"\s+", " ", text).strip(" .,;")


def essay_slug(node_id: str) -> str:
    kind, _, slug = str(node_id).partition(":")
    return slug if kind == "essay" else ""


def sanitize(nodes, published: set[str]):
    """Return public copies of the wiki nodes, in place of the private ones."""
    public_nodes = []
    for node in nodes:
        slug = essay_slug(node["id"])
        is_public = bool(slug) and slug in published

        clean = dict(node)
        for field in FORBIDDEN_NODE_FIELDS:
            clean.pop(field, None)

        # A read link exists only for an authorized essay.
        clean["htmlFile"] = f"essays/{slug}.html" if is_public else None
        clean["public"] = is_public

        if node["type"] not in SUMMARY_TYPES:
            clean.pop("summary", None)
        if node["type"] == "reference":
            clean["title"] = clean_citation(node["title"])
        else:
            # Only a bibliography entry keeps an outbound URL.
            clean["url"] = None

        public_nodes.append(clean)
    return public_nodes


def build(width: int = 1900, height: int = 1200):
    nodes, edges, isolated = build_graph.build_graph()
    tag_gaps = build_graph.compute_tag_gaps(nodes, edges)
    build_graph.compute_layout(nodes, edges, width=width, height=height)

    published = {e.slug for e in collect_public()}
    public_nodes = sanitize(nodes, published)
    return public_nodes, edges, tag_gaps, isolated


def data_payload(nodes, edges, isolated) -> dict:
    counts: dict[str, int] = {}
    for node in nodes:
        counts[node["type"]] = counts.get(node["type"], 0) + 1
    return {
        "nodes": nodes,
        "edges": edges,
        "counts": counts,
        "published": sum(1 for n in nodes if n.get("public")),
        "isolated": len(isolated),
    }


def write(root: Path, nodes, edges, tag_gaps, isolated) -> list[tuple[str, float]]:
    root.mkdir(parents=True, exist_ok=True)
    empty_reader = {"essays": {}, "mathjax": "", "css": ""}
    written = []

    (root / "graph.json").write_text(
        json.dumps(data_payload(nodes, edges, isolated),
                   ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    written.append(("graph.json", (root / "graph.json").stat().st_size / 1024 / 1024))

    for name, renderer in (("graph.html", build_graph.render_html),
                           ("sphere.html", build_sphere.render_sphere_html)):
        path = root / name
        path.write_text(renderer(nodes, edges, tag_gaps, empty_reader), encoding="utf-8")
        written.append((name, path.stat().st_size / 1024 / 1024))

    return written


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, default=SITE_ROOT,
                    help="directory to write into (default: SITE_ROOT)")
    ap.add_argument("--json", action="store_true",
                    help="print the sanitized data instead of writing")
    args = ap.parse_args()

    nodes, edges, tag_gaps, isolated = build()

    if args.json:
        print(json.dumps(data_payload(nodes, edges, isolated),
                         ensure_ascii=False, indent=2))
        return 0

    written = write(args.output, nodes, edges, tag_gaps, isolated)
    readable = sum(1 for n in nodes if n.get("public"))
    print(f"public map: {len(nodes)} nodes, {len(edges)} edges, {readable} readable")
    for name, size in written:
        print(f"  {name:12s} {size:.1f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
