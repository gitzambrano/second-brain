#!/usr/bin/env python3
"""Block corpus scripts that hard-code engine-local wiki/plan/raw/output paths.

Corpus and generated private artifacts must be resolved through ``repo_paths``
so they land in DATA_ROOT, never in the public engine checkout.

No-argument default: audit every script and report PASS/FAIL.
"""
from __future__ import annotations

import argparse
import json
import re

from repo_paths import SCRIPTS_DIR

FORBIDDEN = [
    re.compile(r"\b(?:ROOT_DIR|CODE_ROOT)\s*/\s*[\"']" + name + r"[\"']")
    for name in ("wiki", "plan", "raw", "output")
]

# repo_paths defines the roots; the migration tool and this checker must name the
# legacy locations literally in order to do their job.
EXEMPT = {"repo_paths.py", "migrate_private_data.py", "check_path_discipline.py"}


def audit() -> list[dict[str, str]]:
    issues = []
    for path in sorted(SCRIPTS_DIR.glob("*.py")):
        if path.name in EXEMPT:
            continue
        source = path.read_text(encoding="utf-8-sig")
        if any(pattern.search(source) for pattern in FORBIDDEN):
            issues.append({
                "path": str(path.relative_to(SCRIPTS_DIR.parent)),
                "message": "hard-coded engine-local data path; import repo_paths",
            })
    return issues


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    issues = audit()
    if args.json:
        print(json.dumps({
            "status": "fail" if issues else "pass",
            "issues": issues,
            "errors": [f"{i['path']}: {i['message']}" for i in issues],
        }, ensure_ascii=False, indent=2))
    else:
        print(f"path-discipline: {'FAIL' if issues else 'PASS'}")
        for issue in issues:
            print(f"  ERROR {issue['path']}: {issue['message']}")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
