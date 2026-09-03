#!/usr/bin/env python3
"""
find_backlinks.py - Lookup reverso de [[wikilinks]]: quem já linka uma
página (mesma resolução [[Target]]/[[Target|Display]] do build_graph.py).

Lê:
    wiki/{essays,concepts,entities,insights}/*.md  (corpo sem frontmatter)

Gera:
    stdout: páginas que apontam para o título dado; com --orphans, as que
    não recebem nenhum backlink no escopo

Uso:
    python scripts/find_backlinks.py "Autopoiese"
    python scripts/find_backlinks.py --orphans
    python scripts/find_backlinks.py --orphans --scope concepts entities

Flags:
    title        título alvo (posicional; obrigatório sem --orphans)
    --orphans    lista páginas sem nenhum backlink
    --scope ...  pastas do escopo (default de --orphans: concepts entities)
"""

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

import console_encoding  # noqa: F401  (UTF-8 no console; ver o módulo)

from repo_paths import CODE_ROOT, DATA_ROOT, WIKI_ROOT

ROOT_DIR = CODE_ROOT
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
                pages[title] = (scope, str(f.relative_to(DATA_ROOT)))
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
                    index[target].append((source_title, scope, str(f.relative_to(DATA_ROOT))))
    return index, pages


def lookup(title, scopes=ALL_SCOPES):
    """Devolve quem linka um título, no formato do índice reverso."""
    index, _ = build_backlink_index(scopes)
    return index.get(title, [])


def orphans(scopes=None):
    """Dois graus de orfandade, nos escopos dados.

    Devolve (totais, sem_essay):
      totais    — ninguém cita, em lugar nenhum. Órfão de verdade.
      sem_essay — citada só por concept/entity/insight, nunca por essay.
                  Legítimo (insight que ainda não virou essay, concept que se
                  apoia noutro); informativo, não defeito.
    """
    target_scopes = scopes or DEFAULT_ORPHAN_SCOPE
    index, all_pages = build_backlink_index(ALL_SCOPES)
    totais, sem_essay = [], []
    for title, (node_type, path) in all_pages.items():
        if node_type not in target_scopes:
            continue
        # Um wikilink pode apontar pelo slug do arquivo (`[[andy-clark|...]]`,
        # forma canônica que o Obsidian resolve) ou pelo H1 antigo. A página só
        # é órfã quando NENHUMA das duas grafias aparece em lugar nenhum.
        slug = Path(path).stem
        fontes = index.get(title, []) + index.get(slug, [])
        if not fontes:
            totais.append((title, node_type, path))
        elif not any(src_type == "essays" for _, src_type, _ in fontes):
            sem_essay.append((title, node_type, path))
    ordena = lambda r: sorted(r, key=lambda x: (x[1], x[0]))
    return ordena(totais), ordena(sem_essay)


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
        totais, sem_essay = orphans(args.scope)
        if not totais and not sem_essay:
            scopes_label = ", ".join(args.scope or DEFAULT_ORPHAN_SCOPE)
            print(f"Nenhum órfão encontrado (escopo: {scopes_label}).")
            return 0
        if totais:
            print(f"{len(totais)} órfão(s) TOTAL (nenhuma página cita):")
            for title, node_type, path in totais:
                print(f"  - [{node_type}] {title} ({path})")
        if sem_essay:
            if totais:
                print()
            print(f"{len(sem_essay)} sem essay (citada só por concept/entity/insight — informativo):")
            for title, node_type, path in sem_essay:
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
