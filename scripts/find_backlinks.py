#!/usr/bin/env python3
"""
find_backlinks.py - Lookup reverso de [[wikilinks]]: quem já linka essa página.

Sem isso, saber quem referencia uma página exige reler wiki/essays/*.md
inteiro toda vez (o que /organize passo 2 e stats.py já fazem do zero a
cada chamada). Este script isola esse cálculo pra reuso por qualquer
skill: /organize (órfãos), /chapter e /essay (sugerir "## Conexões" com
contexto real — "esses 3 essays já citam esse concept"), /gaps.

Escaneia o corpo inteiro de essays/concepts/entities/insights (depois de
tirar o frontmatter) por [[Target]] ou [[Target|Display]], igual
build_graph.py — wikilinks só aparecem em ## Conexões e em páginas de
concept/entity, nunca inline no corpo do essay (ver conventions/SKILL.md),
então isso não pega falso positivo de link externo.

Usage:
    python scripts/find_backlinks.py "Autopoiese"
    python scripts/find_backlinks.py --orphans
    python scripts/find_backlinks.py --orphans --scope concepts entities
"""

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

import console_encoding  # noqa: F401  (UTF-8 no console; ver o módulo)

ROOT_DIR = Path(__file__).resolve().parent.parent
WIKI_ROOT = ROOT_DIR / "wiki"
ESSAYS_DIR = WIKI_ROOT / "essays"
CONCEPTS_DIR = WIKI_ROOT / "concepts"
ENTITIES_DIR = WIKI_ROOT / "entities"
INSIGHTS_DIR = WIKI_ROOT / "insights"

DIRS = {
    "essays": ESSAYS_DIR,
    "concepts": CONCEPTS_DIR,
    "entities": ENTITIES_DIR,
    "insights": INSIGHTS_DIR,
}
ALL_SCOPES = list(DIRS.keys())
# órfão de verdade (concept/entity sem essay que o referencie) é sobre
# concepts/entities, que é o que /organize e stats.py já auditam — mas o
# --scope permite ampliar pra insights também quando fizer sentido.
DEFAULT_ORPHAN_SCOPE = ["concepts", "entities"]


def load(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return f.read()


def get_h1(content):
    m = re.search(r"(?m)^# (.+)", content)
    return m.group(1).strip() if m else None


def strip_frontmatter(content):
    return re.sub(r"^---\s*\n.*?\n---\s*\n?", "", content, count=1, flags=re.DOTALL)


def strip_fences(body):
    return re.sub(r"```.*?```", "", body, flags=re.DOTALL)


def collect_pages(scopes):
    """title -> (node_type, relpath) para todas as páginas nos escopos dados."""
    pages = {}
    for scope in scopes:
        d = DIRS.get(scope)
        if not d or not d.exists():
            continue
        for f in sorted(d.glob("*.md")):
            if f.name == ".gitkeep":
                continue
            title = get_h1(load(f))
            if title:
                pages[title] = (scope, str(f.relative_to(ROOT_DIR)))
    return pages


def build_backlink_index(scopes=ALL_SCOPES):
    """target_title -> [(source_title, source_type, source_path), ...]"""
    pages = collect_pages(scopes)
    index = defaultdict(list)
    for scope in scopes:
        d = DIRS.get(scope)
        if not d or not d.exists():
            continue
        for f in sorted(d.glob("*.md")):
            if f.name == ".gitkeep":
                continue
            content = load(f)
            source_title = get_h1(content)
            if not source_title:
                continue
            body = strip_fences(strip_frontmatter(content))
            for m in re.finditer(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", body):
                target = m.group(1).strip()
                if target != source_title:
                    index[target].append((source_title, scope, str(f.relative_to(ROOT_DIR))))
    return index, pages


def lookup(title, scopes=ALL_SCOPES):
    index, _ = build_backlink_index(scopes)
    return index.get(title, [])


def orphans(scopes=None):
    """Páginas nos escopos dados sem nenhum backlink de scope algum (busca em ALL_SCOPES)."""
    target_scopes = scopes or DEFAULT_ORPHAN_SCOPE
    index, all_pages = build_backlink_index(ALL_SCOPES)
    result = []
    for title, (node_type, path) in all_pages.items():
        if node_type in target_scopes and title not in index:
            result.append((title, node_type, path))
    return sorted(result, key=lambda x: (x[1], x[0]))


def main():
    parser = argparse.ArgumentParser(description="Lookup reverso de [[wikilinks]] e órfãos")
    parser.add_argument("title", nargs="?", help="Título exato da página a consultar")
    parser.add_argument("--orphans", action="store_true",
                         help="Lista páginas sem nenhum backlink (default: concepts + entities)")
    parser.add_argument("--scope", nargs="+", choices=ALL_SCOPES, default=None,
                         help="Restringe o escopo (para --orphans: quais tipos auditar)")
    args = parser.parse_args()

    # Sem argumento, cai no relatório de órfãos: é a única pergunta que este
    # script responde sobre o corpus inteiro, e sair com erro deixava o caso
    # `python find_backlinks.py` sem utilidade nenhuma.
    if not args.title and not args.orphans:
        args.orphans = True

    if args.orphans:
        found = orphans(args.scope)
        if not found:
            scopes_label = ", ".join(args.scope or DEFAULT_ORPHAN_SCOPE)
            print(f"Nenhum órfão encontrado (escopo: {scopes_label}).")
            return 0
        print(f"{len(found)} órfão(s) (sem nenhum backlink):")
        for title, node_type, path in found:
            print(f"  - [{node_type}] {title} ({path})")
        return 0

    scopes = args.scope or ALL_SCOPES
    backlinks = lookup(args.title, scopes)
    if not backlinks:
        print(f'"{args.title}" — nenhum backlink encontrado (escopo: {", ".join(scopes)}).')
        return 0
    print(f'"{args.title}" — {len(backlinks)} backlink(s):')
    for source_title, node_type, path in backlinks:
        print(f"  - [{node_type}] {source_title} ({path})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
