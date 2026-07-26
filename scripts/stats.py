#!/usr/bin/env python3
"""
stats.py - Read-only health dashboard for the Second Brain wiki.

Reports counts and integrity signals. Never modifies anything —
that is the job of lint_all.py / auto_fix_lint.py. This script only
reads and reports, inspired by the PROJECT_MAP.md pattern (a generated,
always-current snapshot of the workspace) but scoped to counts and
gaps rather than a full file tree.

Usage:
    python stats.py              # print report to stdout
    python stats.py --save       # also write to output/stats/stats-YYYY-MM-DD.md
"""

import re
import sys
import argparse
import datetime
from pathlib import Path
from collections import Counter, defaultdict

WIKI_ROOT = Path(__file__).resolve().parent.parent
ESSAYS_DIR = WIKI_ROOT / "essays"
CONCEPTS_DIR = WIKI_ROOT / "concepts"
ENTITIES_DIR = WIKI_ROOT / "entities"
SOURCES_DIR = WIKI_ROOT / "sources"
HANDOUTS_DIR = WIKI_ROOT / "handouts"
SYNTHESIS_DIR = WIKI_ROOT / "synthesis"
OUTPUT_DIR = WIKI_ROOT.parent / "output" / "stats"

SOURCE_TYPES = [
    "Ensaio Completo Importado",
    "Web Clipping",
    "Artigo Acadêmico",
    "Livro",
    "Documentação Técnica",
    "Transcrição",
    "Ideias",
    "Outro",
]

SOURCE_TYPE_TO_FOLDER = {
    "Ensaio Completo Importado": "ensaio-importado",
    "Web Clipping": "web-clipping",
    "Artigo Acadêmico": "artigo-academico",
    "Livro": "livro",
    "Documentação Técnica": "documentacao-tecnica",
    "Transcrição": "transcricao",
    "Ideias": "ideias",
    "Outro": "outro",
}


def load(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return f.read()


def get_frontmatter_field(content, field):
    """Very small YAML-ish extractor, good enough for tags/sources lists and dates."""
    m = re.search(rf"(?m)^{field}:\s*(.*)$", content)
    if not m:
        return None
    return m.group(1).strip()


def parse_list_field(raw):
    if raw is None:
        return []
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
        raw = raw[1:-1]
    return [x.strip().strip('"').strip("'") for x in raw.split(",") if x.strip()]


def get_h1(content):
    m = re.search(r"(?m)^# (.+)", content)
    return m.group(1).strip() if m else None


def count_travessoes(content):
    """Count em-dashes in argumentative prose, excluding fixed formatting spots."""
    # Drop the byline lines (use · not travessão, but be safe), the index-style
    # wikilink display separators, and code blocks before counting.
    lines = content.split("\n")
    total = 0
    in_code = False
    for line in lines:
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if line.strip().startswith(">"):
            continue  # byline / blockquotes
        total += line.count("—")
    return total


def essay_stats():
    essays = sorted(ESSAYS_DIR.glob("*.md")) if ESSAYS_DIR.exists() else []
    tag_counts = Counter()
    type_counts = Counter()
    category_counts = Counter()
    travessao_offenders = []
    missing_referencias = []
    missing_conexoes = []
    missing_sumario = []
    has_resumo_executivo = []
    all_essay_titles = set()

    for e in essays:
        content = load(e)
        title = get_h1(content)
        if title:
            all_essay_titles.add(title)

        tags = parse_list_field(get_frontmatter_field(content, "tags"))
        for t in tags:
            tag_counts[t] += 1

        m = re.search(r"(?m)^> (Ensaio|White Paper|Brainstorm|Estudo|Análise)\s*·\s*(.+)$", content)
        if m:
            type_counts[m.group(1)] += 1
            category_counts[m.group(2).strip()] += 1

        n_dash = count_travessoes(content)
        if n_dash > 2:
            travessao_offenders.append((e.stem, n_dash))

        if "## Referências" not in content:
            missing_referencias.append(e.stem)
        if "## Conexões" not in content:
            missing_conexoes.append(e.stem)
        if "## Sumário" not in content:
            missing_sumario.append(e.stem)
        if "## Resumo Executivo" in content:
            has_resumo_executivo.append(e.stem)

    return {
        "count": len(essays),
        "tag_counts": tag_counts,
        "type_counts": type_counts,
        "category_counts": category_counts,
        "travessao_offenders": travessao_offenders,
        "missing_referencias": missing_referencias,
        "missing_conexoes": missing_conexoes,
        "missing_sumario": missing_sumario,
        "has_resumo_executivo": has_resumo_executivo,
        "titles": all_essay_titles,
    }


def collect_wikilinks(content):
    """[[Target]] or [[Target|Display]] -> Target, only from ## Conexões section."""
    m = re.search(r"(?ms)^## Conex[õo]es\s*\n(.*)$", content)
    if not m:
        return []
    section = m.group(1)
    links = re.findall(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", section)
    return [l.strip() for l in links]


def orphan_stats(essay_titles):
    """Concepts/entities not referenced by any essay's ## Conexões."""
    referenced = set()
    if ESSAYS_DIR.exists():
        for e in ESSAYS_DIR.glob("*.md"):
            referenced.update(collect_wikilinks(load(e)))

    orphans = defaultdict(list)
    for label, d in [("concepts", CONCEPTS_DIR), ("entities", ENTITIES_DIR)]:
        if not d.exists():
            continue
        for f in d.glob("*.md"):
            title = get_h1(load(f))
            if title and title not in referenced:
                orphans[label].append(title)
    return orphans


def source_stats():
    if not SOURCES_DIR.exists():
        return {"total": 0, "by_type_folder": {}, "unmanifested": [], "misfiled": [], "manifest_entries": 0}

    manifest_path = SOURCES_DIR / "manifest.md"
    manifest_content = load(manifest_path) if manifest_path.exists() else ""
    manifest_files = set(re.findall(r"(?m)^## \[\d{4}-\d{2}-\d{2}\]\s+(.+)$", manifest_content))
    manifest_entries = len(manifest_files)

    by_type_folder = Counter()
    unmanifested = []
    misfiled = []
    total = 0

    valid_folders = set(SOURCE_TYPE_TO_FOLDER.values())

    for sub in SOURCES_DIR.iterdir():
        if not sub.is_dir():
            continue
        folder_name = sub.name
        for f in sub.iterdir():
            if f.name == ".gitkeep" or f.is_dir():
                continue
            total += 1
            by_type_folder[folder_name] += 1
            if f.name not in manifest_files:
                unmanifested.append(f"{folder_name}/{f.name}")
            if folder_name not in valid_folders:
                misfiled.append(f"{folder_name}/{f.name}")

    return {
        "total": total,
        "by_type_folder": dict(by_type_folder),
        "unmanifested": unmanifested,
        "misfiled": misfiled,
        "manifest_entries": manifest_entries,
    }


def handout_stats():
    if not HANDOUTS_DIR.exists():
        return {"count": 0, "essays_without_handout_but_flagged": []}
    handouts = list(HANDOUTS_DIR.glob("*.md"))
    return {"count": len(handouts)}


def format_report(essay, orphans, sources, handouts):
    lines = []
    lines.append(f"# Second Brain Stats — {datetime.date.today().isoformat()}")
    lines.append("")
    lines.append("Relatório read-only. Não corrige nada — use /organize ou /sweep para isso.")
    lines.append("")

    lines.append("## Essays")
    lines.append(f"- Total: {essay['count']}")
    if essay["type_counts"]:
        lines.append("- Por tipo: " + ", ".join(f"{k} ({v})" for k, v in essay["type_counts"].most_common()))
    if essay["category_counts"]:
        lines.append("- Por categoria temática:")
        for cat, n in essay["category_counts"].most_common():
            lines.append(f"  - {cat}: {n}")
    lines.append("")

    lines.append("## Tags (vocabulário controlado)")
    if essay["tag_counts"]:
        for tag, n in essay["tag_counts"].most_common():
            lines.append(f"- {tag}: {n}")
    else:
        lines.append("- (nenhuma)")
    lines.append("")

    lines.append("## Sinais de lint (contagem rápida, não substitui /organize ou /sweep)")
    lines.append(f"- Essays com `## Resumo Executivo` (não deveria existir mais): {len(essay['has_resumo_executivo'])}")
    for s in essay["has_resumo_executivo"]:
        lines.append(f"  - {s}")
    lines.append(f"- Essays com mais de 2 travessões: {len(essay['travessao_offenders'])}")
    for s, n in essay["travessao_offenders"]:
        lines.append(f"  - {s} ({n} travessões)")
    lines.append(f"- Essays sem `## Sumário`: {len(essay['missing_sumario'])}")
    lines.append(f"- Essays sem `## Referências`: {len(essay['missing_referencias'])}")
    lines.append(f"- Essays sem `## Conexões`: {len(essay['missing_conexoes'])}")
    lines.append("")

    lines.append("## Órfãos (concepts/entities sem essay que os referencie)")
    total_orphans = sum(len(v) for v in orphans.values())
    lines.append(f"- Total: {total_orphans}")
    for label, items in orphans.items():
        if items:
            lines.append(f"- {label}:")
            for i in items:
                lines.append(f"  - {i}")
    lines.append("")

    lines.append("## Sources")
    lines.append(f"- Total de arquivos em wiki/sources/**: {sources['total']}")
    lines.append(f"- Entradas no manifest.md: {sources['manifest_entries']}")
    if sources["by_type_folder"]:
        lines.append("- Por subpasta:")
        for folder, n in sorted(sources["by_type_folder"].items()):
            lines.append(f"  - {folder}/: {n}")
    lines.append(f"- Sem entrada no manifesto: {len(sources['unmanifested'])}")
    for u in sources["unmanifested"]:
        lines.append(f"  - {u}")
    lines.append(f"- Em subpasta fora do vocabulário controlado: {len(sources['misfiled'])}")
    for m in sources["misfiled"]:
        lines.append(f"  - {m}")
    lines.append("")

    lines.append("## Handouts")
    lines.append(f"- Total: {handouts['count']}")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Second Brain read-only stats dashboard")
    parser.add_argument("--save", action="store_true", help="Also write report to output/stats/")
    args = parser.parse_args()

    essay = essay_stats()
    orphans = orphan_stats(essay["titles"])
    sources = source_stats()
    handouts = handout_stats()

    report = format_report(essay, orphans, sources, handouts)
    print(report)

    if args.save:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        out_path = OUTPUT_DIR / f"stats-{datetime.date.today().isoformat()}.md"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\nSaved to {out_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
