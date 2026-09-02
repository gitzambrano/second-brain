#!/usr/bin/env python3
"""Enforce what the public site may and may not expose.

The site publishes two different things, under two different rules.

The **map** (``graph.json``) deliberately carries the whole base: every essay,
concept, entity, insight and reference, by title, plus every connection. That is
an explicit decision — a static site cannot hide what it serves, so a node title
here is public. What the map must never carry is readable content or a way in:
no summary for an unpublished page, no link into ``essays/`` for one, and no
field that points back at the private repository.

Everything else — the rendered pages, the reading index and the manifest — stays
restricted to essays authorized with ``publish: true``. An unpublished essay's
slug or title appearing there is a leak.

No-argument default: audit SITE_ROOT and report PASS/FAIL.
"""
from __future__ import annotations

import argparse
import json
import re

from repo_paths import ESSAYS_DIR, SITE_ROOT
from site_common import collect_public, parse

# graph.json is the map and is checked structurally, not for identities.
MAP_FILE = "graph.json"
SCANNED_SUFFIXES = {".html", ".json"}
MACHINE_FILES = ("search-index.json", MAP_FILE, "site-manifest.json")

# Fields that would turn a map node into readable content or a private pointer.
FORBIDDEN_NODE_FIELDS = ("file", "htmlFile", "body", "text", "path")

# Generated links and metadata must never name the private repository layout.
FORBIDDEN_PATHS = [
    r"\bdata/wiki/",
    r"\bwiki/sources/",
    r"\bdata/raw/",
    r"\bdata/plan/",
    r"\bwiki/status\.md",
    r"\bwiki/log\.md",
]


def private_essays() -> tuple[set[str], list[tuple[str, str]]]:
    """Return (authorized slugs, [(slug, title), ...] for every other essay)."""
    allowed = {e.slug for e in collect_public()}
    private: list[tuple[str, str]] = []
    if ESSAYS_DIR.exists():
        for path in sorted(ESSAYS_DIR.glob("*.md")):
            if path.name == ".gitkeep" or path.stem in allowed:
                continue
            _meta, body = parse(path)
            heading = re.search(r"(?m)^#\s+(.+)$", body)
            private.append((path.stem, heading.group(1).strip() if heading else path.stem))
    return allowed, private


def audit_map(allowed: set[str]) -> list[str]:
    """The map may name everything; it may not expose or open anything."""
    errors: list[str] = []
    path = SITE_ROOT / MAP_FILE
    if not path.exists():
        return [f"missing {MAP_FILE}"]

    payload = json.loads(path.read_text(encoding="utf-8"))
    for node in payload.get("nodes", []):
        node_id = node.get("id", "?")
        slug = str(node_id).partition(":")[2]
        readable = bool(node.get("published"))

        if readable and slug not in allowed:
            errors.append(f"node marked published but not authorized: {node_id}")
        if not readable and node.get("summary"):
            errors.append(f"summary exposed for unpublished node: {node_id}")

        url = str(node.get("url") or "")
        if url.startswith("essays/") and (not readable or url != f"essays/{slug}.html"):
            errors.append(f"unauthorized essay link in map: {node_id} -> {url}")
        if url and not url.startswith(("essays/", "http://", "https://")):
            errors.append(f"suspicious url in map: {node_id} -> {url}")

        for field in FORBIDDEN_NODE_FIELDS:
            if field in node:
                errors.append(f"private field '{field}' in map node {node_id}")
    return errors


def audit() -> list[str]:
    errors: list[str] = []
    allowed, private = private_essays()

    for name in MACHINE_FILES:
        if not (SITE_ROOT / name).exists():
            errors.append(f"missing {name}")

    if not SITE_ROOT.exists():
        return errors

    errors.extend(audit_map(allowed))

    for path in sorted(SITE_ROOT.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SCANNED_SUFFIXES:
            continue
        rel = path.relative_to(SITE_ROOT)
        text = path.read_text(encoding="utf-8", errors="replace")

        # Outside the map, an unpublished essay must not exist at all.
        if path.name != MAP_FILE:
            for slug, title in private:
                if slug and slug in text:
                    errors.append(f"private essay slug leaked in {rel}: {slug}")
                if title and title in text:
                    errors.append(f"private essay title leaked in {rel}: {title}")

        for pattern in FORBIDDEN_PATHS:
            if re.search(pattern, text, re.I):
                errors.append(f"private path leaked in {rel}: {pattern}")

    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    errors = audit()
    if args.json:
        print(json.dumps(
            {"status": "fail" if errors else "pass", "errors": errors},
            ensure_ascii=False, indent=2,
        ))
    else:
        print("site-privacy: PASS" if not errors else "site-privacy: FAIL")
        for error in errors:
            print(f"  ERROR {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
