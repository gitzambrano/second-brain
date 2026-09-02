#!/usr/bin/env python3
"""Fail if the public site exposes an unpublished essay identity or a private path.

Two independent checks:

1. no private essay slug or title appears in any generated ``.html``/``.json``;
2. no private repository path vocabulary appears in any generated file.

No-argument default: audit SITE_ROOT and report PASS/FAIL.
"""
from __future__ import annotations

import argparse
import json
import re

from repo_paths import ESSAYS_DIR, SITE_ROOT
from site_common import collect_public, parse

SCANNED_SUFFIXES = {".html", ".json"}
MACHINE_FILES = ("search-index.json", "graph.json", "site-manifest.json")

# Generated links and metadata must never name the private repository layout.
FORBIDDEN_PATHS = [
    r"\bdata/wiki/",
    r"\bwiki/sources/",
    r"\bdata/raw/",
    r"\bdata/plan/",
    r"\bwiki/status\.md",
    r"\bwiki/log\.md",
]


def private_identities() -> tuple[set[str], list[tuple[str, str]]]:
    """Return (public slugs, [(private slug, private title), ...])."""
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


def audit() -> list[str]:
    errors: list[str] = []
    _allowed, private = private_identities()

    for name in MACHINE_FILES:
        if not (SITE_ROOT / name).exists():
            errors.append(f"missing {name}")

    if not SITE_ROOT.exists():
        return errors

    for path in sorted(SITE_ROOT.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SCANNED_SUFFIXES:
            continue
        rel = path.relative_to(SITE_ROOT)
        text = path.read_text(encoding="utf-8", errors="replace")

        # Private identities must be absent from every generated file, not only
        # the machine indexes: rendered prose is where a body would leak.
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
