#!/usr/bin/env python3
"""Generate the privacy-safe public graph from publish:true essays only.

This is a separate, sanitized generator. The rich private graph stays in
``build_graph.py``/``build_sphere.py`` and writes to DATA_ROOT/output/graph.

No-argument default: write SITE_ROOT/graph.json.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from repo_paths import SITE_ROOT
from site_common import collect_public, public_connections


def payload() -> dict:
    essays = collect_public()
    allowed = {e.slug for e in essays}

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

    return {"nodes": nodes, "edges": edges}


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
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"public graph: {len(data['nodes'])} nodes, {len(data['edges'])} edges")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
