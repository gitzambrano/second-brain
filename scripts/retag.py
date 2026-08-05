#!/usr/bin/env python3
"""
retag.py — Renomeia ou consolida uma tag em toda a wiki.

Troca uma tag pela outra no campo `tags:` (frontmatter YAML de essays,
concepts, entities, insights) e no campo `Tags:` de wiki/sources/manifest.md
— a mesma fonte única de vocabulário descrita em conventions/SKILL.md.

Usado por /organize passo 6 (tags quase-duplicadas) para aplicar a
consolidação já decidida com o Usuário — este script não decide nada,
só executa a troca em massa.

Uso:
    python scripts/retag.py "tag-velha" "tag-nova"
    python scripts/retag.py "tag-velha" "tag-nova" --dry-run

Se a página já tiver `tag-nova`, `tag-velha` é apenas removida (evita
duplicata na mesma lista). Depois de rodar, regenere o índice:

    python scripts/build_index.py
"""

import argparse
import re
import sys
from pathlib import Path

import yaml

import console_encoding  # noqa: F401  (UTF-8 no console; ver o módulo)

ROOT_DIR = Path(__file__).resolve().parent.parent
WIKI_ROOT = ROOT_DIR / "wiki"
PAGE_DIRS = [WIKI_ROOT / d for d in ("essays", "concepts", "entities", "insights")]
MANIFEST_PATH = WIKI_ROOT / "sources" / "manifest.md"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def load(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return f.read()


def retag_page(path, old_tag, new_tag, dry_run):
    content = load(path)
    m = FRONTMATTER_RE.match(content)
    if not m:
        return False
    fm = yaml.safe_load(m.group(1)) or {}
    tags = fm.get("tags") or []
    if old_tag not in tags:
        return False

    new_tags = [t for t in tags if t != old_tag]
    if new_tag not in new_tags:
        new_tags.append(new_tag)
    fm["tags"] = new_tags

    new_frontmatter = "---\n" + yaml.safe_dump(
        fm, allow_unicode=True, sort_keys=False, default_flow_style=None
    ) + "---\n"
    new_content = FRONTMATTER_RE.sub(lambda _: new_frontmatter, content, count=1)

    if not dry_run:
        path.write_text(new_content, encoding="utf-8")
    return True


def retag_manifest(old_tag, new_tag, dry_run):
    if not MANIFEST_PATH.exists():
        return 0
    content = load(MANIFEST_PATH)
    count = 0

    def replace_line(match):
        nonlocal count
        raw = match.group(1).strip()
        bracketed = raw.startswith("[") and raw.endswith("]")
        inner = raw[1:-1] if bracketed else raw
        tags = [t.strip().strip('"').strip("'") for t in inner.split(",") if t.strip()]
        if old_tag not in tags:
            return match.group(0)
        tags = [t for t in tags if t != old_tag]
        if new_tag not in tags:
            tags.append(new_tag)
        count += 1
        rebuilt = ", ".join(tags)
        return f"Tags: [{rebuilt}]" if bracketed else f"Tags: {rebuilt}"

    new_content = re.sub(r"(?m)^Tags:\s*(.+?)\.?$", replace_line, content)
    if count and not dry_run:
        MANIFEST_PATH.write_text(new_content, encoding="utf-8")
    return count


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("old_tag", help="Tag a ser substituída")
    p.add_argument("new_tag", help="Tag que substitui a antiga")
    p.add_argument("--dry-run", action="store_true", help="Só lista o que mudaria, sem escrever")
    args = p.parse_args()

    if args.old_tag == args.new_tag:
        print("ERRO: tag antiga e nova são iguais.", file=sys.stderr)
        sys.exit(1)

    changed_pages = []
    for d in PAGE_DIRS:
        if not d.exists():
            continue
        for f in sorted(d.glob("*.md")):
            if retag_page(f, args.old_tag, args.new_tag, args.dry_run):
                changed_pages.append(f)

    manifest_count = retag_manifest(args.old_tag, args.new_tag, args.dry_run)

    verb = "seriam alteradas" if args.dry_run else "alteradas"
    for f in changed_pages:
        print(f"{'Would retag' if args.dry_run else 'Retagged'}: {f.relative_to(ROOT_DIR)}")
    print(f"\n{len(changed_pages)} página(s) {verb}; "
          f"{manifest_count} entrada(s) de manifest.md {verb}.")
    if changed_pages or manifest_count:
        if args.dry_run:
            print("Dry-run — nada foi escrito.")
        else:
            print("Rode `python scripts/build_index.py` para regenerar tags_in_use.")


if __name__ == "__main__":
    main()
