#!/usr/bin/env python3
"""
Validação read-only da allowlist de publicação no frontmatter dos essays.

Só o booleano YAML ``true`` autoriza publicação. A string ``"true"`` — ou
qualquer outro valor de aparência verdadeira — é reportada como inválida e
tratada como privada.

Default sem argumentos: listar a allowlist atual e validá-la.
    --expect-only "<busca>"  exige exatamente um essay público casando com a busca
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata

import visibility
from repo_paths import ESSAYS_DIR
from site_common import parse


def norm(value) -> str:
    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", text.casefold()).strip()


def audit() -> tuple[list[dict], list[dict], list[str]]:
    public: list[dict] = []
    invalid: list[dict] = []
    errors: list[str] = []

    if ESSAYS_DIR.exists():
        for path in sorted(ESSAYS_DIR.glob("*.md")):
            if path.name == ".gitkeep":
                continue
            meta, body = parse(path)
            level = visibility.of(meta)
            if level == visibility.PUBLIC:
                heading = re.search(r"(?m)^#\s+(.+)$", body)
                public.append({
                    "slug": path.stem,
                    "title": heading.group(1).strip() if heading else path.stem,
                })
            bad = visibility.invalid_value(meta)
            if bad:
                invalid.append({"slug": path.stem, "value": bad})

    if invalid:
        errors.append(
            "visibility must be public/private/hidden (or the legacy boolean "
            f"publish: true): {invalid}"
        )
    return public, invalid, errors


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--expect-only", help="require exactly this one public essay")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    public, invalid, errors = audit()

    if args.expect_only:
        expected = norm(args.expect_only)
        if len(public) != 1:
            errors.append(f"expected exactly one public essay, found {len(public)}")
        elif (expected not in norm(public[0]["title"])
                and expected not in norm(public[0]["slug"])):
            errors.append(f"only public essay is not expected target: {public[0]}")

    payload = {
        "status": "fail" if errors else "pass",
        "public": public,
        "invalid": invalid,
        "errors": errors,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"publication: {payload['status'].upper()} — {len(public)} public essay(s)")
        for entry in public:
            print(f"  {entry['slug']} — {entry['title']}")
        for error in errors:
            print(f"  ERROR {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
