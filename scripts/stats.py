#!/usr/bin/env python3
"""
stats.py - Dashboard read-only da saúde da wiki: contagens e sinais de
integridade (essays por tag/tipo, órfãos, sources sem manifest, handouts,
itens do plano, travessões). Nunca modifica nada - corrigir é trabalho de
check_wiki.py/fix_lint.py.

Lê:
    wiki/{essays,concepts,entities,sources,handouts,insights}/** e plan/plano.md

Gera:
    stdout (relatório); com --save também output/stats/stats-YYYY-MM-DD.md

Uso:
    python scripts/stats.py            # imprime o relatório
    python scripts/stats.py --save     # grava snapshot datado além do stdout

Flags:
    --save   grava o relatório em output/stats/stats-YYYY-MM-DD.md
"""

import re
import sys
import argparse
import datetime
from pathlib import Path
from collections import Counter, defaultdict

import console_encoding  # noqa: F401  (UTF-8 no console; ver o módulo)

ROOT_DIR = Path(__file__).resolve().parent.parent
WIKI_ROOT = ROOT_DIR / "wiki"
PLAN_DIR = ROOT_DIR / "plan"
ESSAYS_DIR = WIKI_ROOT / "essays"
CONCEPTS_DIR = WIKI_ROOT / "concepts"
ENTITIES_DIR = WIKI_ROOT / "entities"
SOURCES_DIR = WIKI_ROOT / "sources"
HANDOUTS_DIR = WIKI_ROOT / "handouts"
INSIGHTS_DIR = WIKI_ROOT / "insights"
PLANO_FILE = PLAN_DIR / "plano.md"
OUTPUT_DIR = ROOT_DIR / "output" / "stats"

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

        m = re.search(r"(?m)^> (Ensaio|White Paper|Brainstorm|Estudo|Análise)\s*$", content)
        if m:
            type_counts[m.group(1)] += 1

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
    """Dois graus de orfandade (mesma regra de check_wiki.py/find_backlinks.py).

    orphans      — nenhuma página cita. Órfão de verdade.
    sem_essay    — citada só por concept/entity/insight, nunca por essay.
    """
    def referenced_by(dirs):
        ref = set()
        for d in dirs:
            if d.exists():
                for f in d.glob("*.md"):
                    ref.update(collect_wikilinks(load(f)))
        return ref

    por_essay = referenced_by([ESSAYS_DIR])
    por_outros = referenced_by([CONCEPTS_DIR, ENTITIES_DIR, INSIGHTS_DIR])

    orphans = defaultdict(list)
    sem_essay = defaultdict(list)
    for label, d in [("concepts", CONCEPTS_DIR), ("entities", ENTITIES_DIR)]:
        if not d.exists():
            continue
        for f in d.glob("*.md"):
            title = get_h1(load(f))
            if not title:
                continue
            # A forma canônica é `[[slug|Título]]`: casa pelo slug do arquivo E
            # pelo H1, senão todo link canônico conta como órfão.
            grafias = {title, f.stem}
            if grafias & por_essay:
                continue
            if grafias & por_outros:
                sem_essay[label].append(title)
            else:
                orphans[label].append(title)
    return orphans, sem_essay


def source_stats():
    if not SOURCES_DIR.exists():
        return {"total": 0, "by_type_folder": {}, "unmanifested": [], "misfiled": [], "manifest_entries": 0,
                "tag_counts": Counter(), "missing_tags": []}

    manifest_path = SOURCES_DIR / "manifest.md"
    manifest_content = load(manifest_path) if manifest_path.exists() else ""
    entry_blocks = re.split(r"(?m)^## \[\d{4}-\d{2}-\d{2}\]\s+(.+)$", manifest_content)
    manifest_files = set()
    tag_counts = Counter()
    missing_tags = []
    # entry_blocks alterna [preambulo, filename, body, filename, body, ...]
    for i in range(1, len(entry_blocks), 2):
        filename, body = entry_blocks[i].strip(), entry_blocks[i + 1]
        manifest_files.add(filename)
        tags_m = re.search(r"(?m)^Tags:\s*(.+?)\.?$", body)
        if not tags_m:
            missing_tags.append(filename)
        else:
            tags = parse_list_field(tags_m.group(1))
            for t in tags:
                tag_counts[t] += 1
    manifest_entries = len(manifest_files)

    by_type_folder = Counter()
    unmanifested = []
    misfiled = []
    total = 0

    valid_folders = set(SOURCE_TYPE_TO_FOLDER.values())
    # "resumos" is a utility folder for /digest summaries, not a source-type
    # folder — it doesn't hold raw sources and isn't part of the Tipo:
    # vocabulary, so it's exempt from the manifest/misfiled audit below.
    utility_folders = {"resumos"}

    for sub in SOURCES_DIR.iterdir():
        if not sub.is_dir() or sub.name in utility_folders:
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
        "tag_counts": tag_counts,
        "missing_tags": missing_tags,
    }


def handout_stats():
    if not HANDOUTS_DIR.exists():
        return {"count": 0, "essays_without_handout_but_flagged": []}
    handouts = list(HANDOUTS_DIR.glob("*.md"))
    return {"count": len(handouts)}


PLAN_SECOES = ["Tarefas", "Fontes para Ingerir", "Revisões", "Estudos", "Essays Futuros"]


def plan_stats():
    """Parse plan/plano.md: 5 fixed '## Seção' headings, each with '### Título'
    items carrying '- Status:' fields."""
    if not PLANO_FILE.exists():
        return {"total": 0, "by_secao": Counter(), "by_status": Counter(), "missing_secoes": PLAN_SECOES}

    content = load(PLANO_FILE)
    secoes_found = {}
    # Split on "## " (level-2 headings) to isolate each section's block.
    parts = re.split(r"(?m)^## ", content)[1:]
    for part in parts:
        heading, _, rest = part.partition("\n")
        heading = heading.strip()
        if heading in PLAN_SECOES:
            secoes_found[heading] = rest

    by_secao = Counter()
    by_status = Counter()
    total = 0
    for secao, body in secoes_found.items():
        items = re.split(r"(?m)^### ", body)[1:]
        for item in items:
            status_m = re.search(r"(?m)^- Status:\s*(.+)$", item)
            total += 1
            by_secao[secao] += 1
            by_status[status_m.group(1).strip() if status_m else "(sem status)"] += 1

    missing_secoes = [s for s in PLAN_SECOES if s not in secoes_found]
    return {"total": total, "by_secao": by_secao, "by_status": by_status, "missing_secoes": missing_secoes}


def insights_stats():
    """Count wiki/insights/ pages by maturidade (solta/germinando/madura)."""
    if not INSIGHTS_DIR.exists():
        return {"total": 0, "by_maturidade": Counter(), "madura_ready": []}

    by_maturidade = Counter()
    madura_ready = []
    total = 0
    for f in sorted(INSIGHTS_DIR.glob("*.md")):
        content = load(f)
        total += 1
        maturidade = get_frontmatter_field(content, "maturidade") or "(sem maturidade)"
        by_maturidade[maturidade] += 1
        if maturidade == "madura":
            madura_ready.append(get_h1(content) or f.stem)
    return {
        "total": total,
        "by_maturidade": by_maturidade,
        "madura_ready": madura_ready,
    }


def format_report(essay, orphans, sem_essay, sources, handouts, insights, plan):
    lines = []
    lines.append(f"# Second Brain Stats — {datetime.date.today().isoformat()}")
    lines.append("")
    lines.append("Relatório read-only. Não corrige nada — use /organize ou /sweep para isso.")
    lines.append("")

    lines.append("## Essays")
    lines.append(f"- Total: {essay['count']}")
    if essay["type_counts"]:
        lines.append("- Por tipo: " + ", ".join(f"{k} ({v})" for k, v in essay["type_counts"].most_common()))
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

    lines.append("## Órfãos (nenhuma página os referencia)")
    total_orphans = sum(len(v) for v in orphans.values())
    lines.append(f"- Total: {total_orphans}")
    for label, items in orphans.items():
        if items:
            lines.append(f"- {label}:")
            for i in items:
                lines.append(f"  - {i}")
    lines.append("")

    lines.append("## Sem essay (citados só por concept/entity/insight — informativo)")
    total_sem_essay = sum(len(v) for v in sem_essay.values())
    lines.append(f"- Total: {total_sem_essay}")
    for label, items in sem_essay.items():
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
    lines.append(f"- Entradas do manifesto sem `Tags:`: {len(sources['missing_tags'])}")
    for m in sources["missing_tags"]:
        lines.append(f"  - {m}")
    if sources["tag_counts"]:
        lines.append("- Tags em uso no manifesto (mesmo vocabulário controlado dos essays):")
        for tag, n in sources["tag_counts"].most_common():
            lines.append(f"  - {tag}: {n}")
    lines.append("")

    lines.append("## Handouts")
    lines.append(f"- Total: {handouts['count']}")
    lines.append("")

    lines.append("## Insights (wiki/insights/)")
    lines.append(f"- Total: {insights['total']}")
    if insights["by_maturidade"]:
        lines.append("- Por maturidade: " + ", ".join(
            f"{k} ({v})" for k, v in insights["by_maturidade"].most_common()
        ))
    if insights["madura_ready"]:
        lines.append(f"- Maduras, prontas para promover (/insight promote): {len(insights['madura_ready'])}")
        for m in insights["madura_ready"]:
            lines.append(f"  - {m}")
    lines.append("")

    lines.append("## Plano (plan/plano.md)")
    lines.append(f"- Total de itens: {plan['total']}")
    if plan["by_secao"]:
        lines.append("- Por seção: " + ", ".join(
            f"{s} ({plan['by_secao'].get(s, 0)})" for s in PLAN_SECOES
        ))
    if plan["by_status"]:
        lines.append("- Por status: " + ", ".join(f"{k} ({v})" for k, v in plan["by_status"].most_common()))
    if plan["missing_secoes"]:
        lines.append(f"- ⚠ Seções ausentes do arquivo: {', '.join(plan['missing_secoes'])}")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Second Brain read-only stats dashboard")
    parser.add_argument("--save", action="store_true", help="Also write report to output/stats/")
    args = parser.parse_args()

    essay = essay_stats()
    orphans, sem_essay = orphan_stats(essay["titles"])
    sources = source_stats()
    handouts = handout_stats()
    insights = insights_stats()
    plan = plan_stats()

    report = format_report(essay, orphans, sem_essay, sources, handouts, insights, plan)
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
