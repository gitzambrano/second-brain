#!/usr/bin/env python3
"""Generate the public knowledge graph.

The graph shows the *shape* of the whole base — every essay, concept, entity,
insight and reference, and every connection between them. Only essays with the
YAML boolean ``publish: true`` are readable: those get a summary and a link to
their page. Every other node ships as identity only.

What crosses into the public graph:
    id, title, type, tags, degree, layout position

What never crosses:
    body text, the `summary:` of an unpublished page, its file path inside the
    private repository, its draft status, and any link that would open it.

A static site cannot hide what it serves: a node title in this file is public.
That is the deliberate trade — the map is public, the territory is not.

No-argument default: write SITE_ROOT/graph.json.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from build_graph import build_graph, compute_layout
from repo_paths import SITE_ROOT
from site_common import collect_public

# Node fields produced by build_graph that must never reach the public site.
# `status` is not here on purpose: the map labels drafts, and that label is part
# of what the map is for.
PRIVATE_FIELDS = ("file", "htmlFile", "sizeBytes", "sizeLines",
                  "maturidade", "subtype")

MD_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
MD_EMPHASIS = re.compile(r"[*_]{1,3}")


def clean_citation(text: str) -> str:
    """Render an AIAA citation as plain text for a graph label."""
    text = MD_LINK.sub(lambda m: "" if m.group(1).strip().lower() == "link" else m.group(1), text)
    text = MD_EMPHASIS.sub("", text)
    return re.sub(r"\s+", " ", text).strip(" .,;")


def essay_slug(node_id: str) -> str | None:
    """`essay:dutch-roll` -> `dutch-roll`; anything else -> None."""
    kind, _, slug = node_id.partition(":")
    return slug if kind == "essay" and slug else None


def payload(width: int = 1900, height: int = 1200) -> dict:
    raw_nodes, raw_edges, isolated = build_graph()
    compute_layout(raw_nodes, raw_edges, width=width, height=height)

    published = {e.slug: e for e in collect_public()}
    nodes = []

    for node in raw_nodes:
        slug = essay_slug(node["id"])
        essay = published.get(slug) if slug else None

        title = node["title"]
        if node["type"] == "reference":
            title = clean_citation(title)

        public = {
            "id": node["id"],
            "title": title,
            "type": node["type"],
            "tags": list(node.get("tags") or []),
            "degree": node.get("degree", 0),
            "published": essay is not None,
            "x": round(node.get("x0", 0.0), 1),
            "y": round(node.get("y0", 0.0), 1),
        }

        # Draft state is shown as a badge on the map, for essays only.
        if node["type"] == "essay" and node.get("status"):
            public["status"] = node["status"]

        if essay is not None:
            public["summary"] = essay.summary
            public["url"] = f"essays/{essay.slug}.html"
        elif node["type"] == "reference":
            # A bibliography entry is a citation plus an external link. Neither
            # points at the private repository, so both stay.
            if node.get("url"):
                public["url"] = node["url"]

        assert not any(field in public for field in PRIVATE_FIELDS)
        nodes.append(public)

    edges = [{"source": e["source"], "target": e["target"], "kind": e.get("kind", "wikilink")}
             for e in raw_edges]

    counts: dict[str, int] = {}
    for node in nodes:
        counts[node["type"]] = counts.get(node["type"], 0) + 1

    return {
        "nodes": nodes,
        "edges": edges,
        "counts": counts,
        "published": sum(1 for n in nodes if n["published"]),
        "isolated": len(isolated),
        "extent": {"width": width, "height": height},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, default=SITE_ROOT / "graph.json")
    ap.add_argument("--json", action="store_true", help="print instead of writing")
    args = ap.parse_args()

    data = payload()
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )
    print(f"public graph: {len(data['nodes'])} nodes, {len(data['edges'])} edges, "
          f"{data['published']} readable")
    for kind, total in sorted(data["counts"].items()):
        print(f"  {kind:10s} {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
