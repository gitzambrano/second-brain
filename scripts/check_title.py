#!/usr/bin/env python3
"""
check_title.py - Checagem exata/fuzzy de título antes de criar página nova.

Chamado por /insight add, /chapter, /essay, /digest, /absorb antes de criar
uma página nova (essay, concept, entity ou insight) — evita títulos
quase-duplicados nascerem (ex: "Autopoiese" vs "Auto-poiese") sem precisar
ler wiki/index.md e varrer concepts/entities manualmente pra saber se um
wikilink já tem destino. Cobre os 4 tipos de página de uma vez.

Usa o cache de wiki/index.json quando existir (gerado por
build_index.py); --force-scan ignora o cache e lê os arquivos direto —
útil se o índice estiver desatualizado no meio de uma sessão.

Exit codes (uso programático):
    0 - nenhum match: título livre, seguro criar
    1 - match exato: já existe página com esse título
    2 - match(es) fuzzy: possível quase-duplicata, revisar antes de criar

Usage:
    python scripts/check_title.py "Autopoiese e Sistemas Vivos"
    python scripts/check_title.py "Auto-poiese" --threshold 0.8
    python scripts/check_title.py "Novo Título" --force-scan
"""

import argparse
import difflib
import json
import re
import sys
import unicodedata
from pathlib import Path

import yaml

import console_encoding  # noqa: F401  (UTF-8 no console; ver o módulo)

ROOT_DIR = Path(__file__).resolve().parent.parent
WIKI_ROOT = ROOT_DIR / "wiki"
ESSAYS_DIR = WIKI_ROOT / "essays"
CONCEPTS_DIR = WIKI_ROOT / "concepts"
ENTITIES_DIR = WIKI_ROOT / "entities"
INSIGHTS_DIR = WIKI_ROOT / "insights"
INDEX_CACHE = WIKI_ROOT / "index.json"

DIRS_BY_TYPE = {
    "essay": ESSAYS_DIR,
    "concept": CONCEPTS_DIR,
    "entity": ENTITIES_DIR,
    "insight": INSIGHTS_DIR,
}

DEFAULT_THRESHOLD = 0.82


def load(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return f.read()


def get_h1(content):
    m = re.search(r"(?m)^# (.+)", content)
    return m.group(1).strip() if m else None


def normalize(title):
    """Normaliza acento, hífen, case e espaçamento pra comparação robusta."""
    t = unicodedata.normalize("NFKD", title)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = t.lower().replace("-", " ")
    t = re.sub(r"\s+", " ", t).strip()
    return t


def scan_live():
    """Título -> (tipo, path), lendo os 4 diretórios de página direto do disco."""
    pages = {}
    for node_type, d in DIRS_BY_TYPE.items():
        if not d.exists():
            continue
        for f in sorted(d.glob("*.md")):
            if f.name == ".gitkeep":
                continue
            title = get_h1(load(f))
            if title:
                pages[title] = (node_type, str(f.relative_to(ROOT_DIR)))
    return pages


def load_from_cache():
    if not INDEX_CACHE.exists():
        return None
    try:
        data = json.loads(INDEX_CACHE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    pages = {}
    for node_type in ("essay", "concept", "entity", "insight"):
        key = node_type + "s" if node_type != "entity" else "entities"
        for entry in data.get(key, []):
            pages[entry["title"]] = (node_type, entry["path"])
    return pages


def collect_pages(force_scan):
    if not force_scan:
        cached = load_from_cache()
        if cached is not None:
            return cached, True
    return scan_live(), False


def resolve(candidate, pages, threshold):
    norm_candidate = normalize(candidate)

    # Exato: match direto de título, ou match só depois de normalizar
    for title, (node_type, path) in pages.items():
        if title == candidate:
            return "exact", [(title, node_type, path, 1.0)]
    normalized_map = {normalize(t): (t, nt, p) for t, (nt, p) in pages.items()}
    if norm_candidate in normalized_map:
        title, node_type, path = normalized_map[norm_candidate]
        return "exact", [(title, node_type, path, 1.0)]

    # Fuzzy: difflib sobre título normalizado
    fuzzy_matches = []
    for title, (node_type, path) in pages.items():
        ratio = difflib.SequenceMatcher(None, norm_candidate, normalize(title)).ratio()
        if ratio >= threshold:
            fuzzy_matches.append((title, node_type, path, round(ratio, 3)))
    if fuzzy_matches:
        fuzzy_matches.sort(key=lambda x: x[3], reverse=True)
        return "fuzzy", fuzzy_matches

    return "none", []


def main():
    parser = argparse.ArgumentParser(description="Checa duplicata exata/fuzzy de título antes de criar página")
    parser.add_argument("title", help="Título candidato para a página nova")
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD,
                         help=f"Similaridade mínima 0-1 para considerar fuzzy match (default: {DEFAULT_THRESHOLD})")
    parser.add_argument("--force-scan", action="store_true",
                         help="Ignora wiki/index.json e lê os arquivos direto do disco")
    args = parser.parse_args()

    pages, used_cache = collect_pages(args.force_scan)

    if not pages:
        print(f'"{args.title}" — nenhuma página existente encontrada (wiki vazia ou diretórios ausentes).')
        return 0

    kind, matches = resolve(args.title, pages, args.threshold)
    source = "cache (wiki/index.json)" if used_cache else "leitura direta do disco"

    if kind == "none":
        print(f'"{args.title}" — livre, nenhum match (fonte: {source}).')
        return 0

    if kind == "exact":
        title, node_type, path, _ = matches[0]
        print(f'MATCH EXATO: "{args.title}" já existe como {node_type} em {path} (fonte: {source}).')
        return 1

    print(f'POSSÍVEL QUASE-DUPLICATA para "{args.title}" (fonte: {source}):')
    for title, node_type, path, ratio in matches:
        print(f'  - "{title}" ({node_type}, {path}) — similaridade {ratio}')
    return 2


if __name__ == "__main__":
    sys.exit(main())
