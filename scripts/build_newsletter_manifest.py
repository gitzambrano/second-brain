#!/usr/bin/env python3
"""Build the public newsletter manifest from essay front matter.

Only essays already authorized for public publication can enter this manifest.
An essay is eligible when its front matter contains ``newsletter: true``.
The output contains only public metadata needed by the site-side sender.
"""
from __future__ import annotations

import json
from pathlib import Path

from repo_paths import SITE_ROOT
from site_common import collect_public, parse

OUTPUT_NAME = "newsletter-manifest.json"


def collect_newsletter_entries() -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for essay in collect_public():
        meta, _body = parse(essay.path)
        if meta.get("newsletter") is not True:
            continue
        entries.append(
            {
                "slug": essay.slug,
                "title": essay.title,
                "summary": essay.summary,
                "updated": essay.updated,
                "path": f"essays/{essay.slug}.html",
            }
        )
    return entries


def build(output: Path | None = None) -> Path:
    output = output or (SITE_ROOT / OUTPUT_NAME)
    payload = {"version": 1, "entries": collect_newsletter_entries()}
    output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return output


def main() -> int:
    path = build()
    print(f"newsletter manifest: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
