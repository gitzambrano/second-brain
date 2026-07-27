#!/usr/bin/env python3
"""
search.py - Busca com trecho (não arquivo inteiro) na wiki.

Devolve só os trechos relevantes de cada arquivo (algumas linhas antes/
depois do match, mescladas em blocos quando se sobrepõem), em vez de forçar
Read no arquivo inteiro para descobrir se ele é relevante. Não tem
dependência externa (nem qmd) — é grep -n com contexto, restrito ao
vocabulário de pastas da wiki.

Escopo default: essays, concepts, entities, insights (as páginas de
conteúdo). sources e handouts ficam de fora por padrão — sources porque
inclui originais grandes e às vezes binários, handouts porque é derivado
sob demanda — inclua explicitamente via --scope quando precisar.

Usage:
    python scripts/search.py "termo da busca"
    python scripts/search.py "termo" --scope essays concepts
    python scripts/search.py "auto.?poiese" --regex
    python scripts/search.py "termo" --list-only
    python scripts/search.py "termo" --context 4 --ignore-case
"""

import argparse
import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
WIKI_ROOT = ROOT_DIR / "wiki"

SCOPE_DIRS = {
    "essays": WIKI_ROOT / "essays",
    "concepts": WIKI_ROOT / "concepts",
    "entities": WIKI_ROOT / "entities",
    "insights": WIKI_ROOT / "insights",
    "handouts": WIKI_ROOT / "handouts",
    "sources": WIKI_ROOT / "sources",
}
DEFAULT_SCOPE = ["essays", "concepts", "entities", "insights"]


def load(path):
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            return f.read()
    except (UnicodeDecodeError, OSError):
        return None  # binário ou ilegível — pulado silenciosamente (relevante p/ sources)


def collect_files(scopes):
    files = []
    for scope in scopes:
        d = SCOPE_DIRS.get(scope)
        if not d or not d.exists():
            continue
        if scope == "sources":
            # recursivo: inclui subpastas de tipo, resumos/, manifest.md, map.md
            for f in sorted(d.rglob("*")):
                if f.is_file() and f.name != ".gitkeep":
                    files.append(f)
        else:
            for f in sorted(d.glob("*.md")):
                if f.name != ".gitkeep":
                    files.append(f)
    return files


def build_pattern(query, use_regex, ignore_case):
    flags = re.IGNORECASE if ignore_case else 0
    pattern = query if use_regex else re.escape(query)
    try:
        return re.compile(pattern, flags)
    except re.error as e:
        print(f"Regex inválida: {e}", file=sys.stderr)
        sys.exit(1)


def merge_ranges(ranges):
    """[(start,end), ...] ordenados/sobrepostos -> blocos mesclados."""
    if not ranges:
        return []
    ranges = sorted(ranges)
    merged = [ranges[0]]
    for start, end in ranges[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end + 1:
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))
    return merged


def search_file(path, pattern, context):
    content = load(path)
    if content is None:
        return None, 0
    lines = content.split("\n")
    match_lines = [i for i, line in enumerate(lines) if pattern.search(line)]
    if not match_lines:
        return [], 0
    ranges = [(max(0, i - context), min(len(lines) - 1, i + context)) for i in match_lines]
    blocks = []
    for start, end in merge_ranges(ranges):
        block_lines = lines[start:end + 1]
        blocks.append((start + 1, end + 1, block_lines, {m + 1 for m in match_lines if start <= m <= end}))
    return blocks, len(match_lines)


def main():
    parser = argparse.ArgumentParser(description="Busca com trecho na wiki (grep -n com contexto)")
    parser.add_argument("query", help="Termo ou padrão a buscar")
    parser.add_argument(
        "--scope", nargs="+", choices=list(SCOPE_DIRS.keys()), default=DEFAULT_SCOPE,
        help=f"Pastas a buscar (default: {' '.join(DEFAULT_SCOPE)})",
    )
    parser.add_argument("--regex", action="store_true", help="Trata query como regex (default: literal)")
    parser.add_argument("--context", type=int, default=2, help="Linhas de contexto antes/depois (default: 2)")
    parser.add_argument("--ignore-case", action="store_true", help="Busca case-insensitive")
    parser.add_argument("--list-only", action="store_true", help="Só lista arquivo + contagem de ocorrências")
    args = parser.parse_args()

    pattern = build_pattern(args.query, args.regex, args.ignore_case)
    files = collect_files(args.scope)

    if not files:
        print(f"Nenhum arquivo encontrado no escopo: {', '.join(args.scope)}")
        return 1

    total_matches = 0
    files_with_hits = 0

    for path in files:
        blocks, n_matches = search_file(path, pattern, args.context)
        if blocks is None or n_matches == 0:
            continue
        files_with_hits += 1
        total_matches += n_matches
        rel = path.relative_to(ROOT_DIR)

        if args.list_only:
            print(f"{rel}: {n_matches} ocorrência(s)")
            continue

        print(f"\n=== {rel} ({n_matches} ocorrência(s)) ===")
        for start, end, block_lines, match_line_nums in blocks:
            for offset, line in enumerate(block_lines):
                lineno = start + offset
                marker = ">" if lineno in match_line_nums else " "
                print(f"{marker} {lineno:>5} | {line}")
            if len(blocks) > 1:
                print("  ...")

    print(f"\n{total_matches} ocorrência(s) em {files_with_hits} arquivo(s) "
          f"(escopo: {', '.join(args.scope)}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
