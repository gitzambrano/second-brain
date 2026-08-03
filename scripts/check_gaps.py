#!/usr/bin/env python3
"""
check_gaps.py — camada léxica de /gaps: candidatos a página nova e a
wikilink ausente entre páginas já existentes, tratando essays, concepts,
entities e insights como peers (os mesmos quatro tipos que /connect trata
como peers em ## Conexões).

Cobre a direção que check_wiki.py e /organize (passo 2) NÃO cobrem:
  - check_wiki.py: wikilinks que já existem e apontam pra nada -> "link morto"
  - /organize passo 2: concept/entity que já existe sem essay que o linke -> "órfão reverso"
  - este script: termo citado repetidamente na prosa de QUALQUER tipo de
    página (via link externo, negrito, ou nome próprio capitalizado) que
    NUNCA foi promovido a wikilink e não corresponde a nenhuma página
    existente -> "órfão de cobertura" (PARTE 1); e o caso em que a página
    já existe mas outra página a cita sem linkar -> "menção sem link"
    (PARTE 2), agora nas duas direções entre os quatro tipos, não só
    essay -> concept/entity.

É heurístico por natureza (não há NLP real aqui) — produz listas de
CANDIDATOS ranqueadas para quem chamou decidir, nunca escreve em disco
sozinho. Falso positivo é esperado e ok; falso negativo silencioso é o
que queremos evitar.

Usado por:
  - /gaps (.agents/skills/gaps/SKILL.md) — camada léxica da identificação;
    roda com --skip-tags, já que balanço de tag agora é auditado por
    /organize, não por /gaps.
  - /organize (.agents/skills/organize/SKILL.md) — só a Parte 3
    (--tags-only), balanço de cobertura por tag.
  - /connect (.agents/skills/connect/SKILL.md) não chama este script
    diretamente: invoca /gaps como passo 1 e reusa a lista que /gaps já
    produziu (ver "## O que este skill reusa" em connect/SKILL.md).

Usage:
    python scripts/check_gaps.py                # as três partes
    python scripts/check_gaps.py --skip-tags     # só Partes 1 e 2 (usado por /gaps)
    python scripts/check_gaps.py --tags-only     # só Parte 3 (usado por /organize)
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

import console_encoding  # noqa: F401  (UTF-8 no console; ver o módulo)

ROOT_DIR = Path(__file__).resolve().parent.parent
WIKI_ROOT = ROOT_DIR / "wiki"
ESSAYS_DIR = WIKI_ROOT / "essays"
CONCEPTS_DIR = WIKI_ROOT / "concepts"
ENTITIES_DIR = WIKI_ROOT / "entities"
INSIGHTS_DIR = WIKI_ROOT / "insights"
INDEX_JSON_PATH = WIKI_ROOT / "index.json"

# Os quatro tipos como peers — mesma lista que /connect trata em ## Conexões.
SOURCE_DIRS = {
    "essays": ESSAYS_DIR,
    "concepts": CONCEPTS_DIR,
    "entities": ENTITIES_DIR,
    "insights": INSIGHTS_DIR,
}

# Só concept/entity recebem página nova a partir da Parte 1 — nunca essay
# nem insight. Mesma regra que /connect já seguia pra Parte C ("não crie
# essay nem insight, só concepts/ e entities/, e só como stub mínimo").
CREATABLE_TYPES = {"concepts", "entities"}

MIN_PAGE_HITS = 2       # termo precisa aparecer em pelo menos N páginas distintas
MIN_TOTAL_HITS = 3      # ou N vezes no total (mesma página repetindo)
TOP_N = 40               # não afoga quem chamou — corta a cauda longa


def load_content(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return f.read()


def strip_frontmatter(content):
    return re.sub(r"^---.*?---\s*", "", content, count=1, flags=re.DOTALL)


def get_h1(content):
    m = re.search(r"(?m)^# (.+)", content)
    return m.group(1).strip() if m else None


def get_frontmatter(content):
    m = re.match(r"^---\s*(.*?)---", content, flags=re.DOTALL)
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}


def strip_code_and_urls(body):
    body = re.sub(r"```.*?```", "", body, flags=re.DOTALL)
    body = re.sub(r"`[^`]*`", "", body)
    # byline (\"> Tipo\") e qualquer blockquote — estrutural, não prosa
    body = re.sub(r"(?m)^>.*$", "", body)
    # links internos de âncora ([Texto](#secao)) — Sumário aponta pra dentro do
    # próprio documento, não é um termo citado; mata o par inteiro pra não
    # sobrar o texto-âncora capitalizado como falso positivo de nome próprio.
    body = re.sub(r"\[([^\]]+)\]\(#[^\)]*\)", "", body)
    return body


def extract_wikilinks(body):
    """Retorna set de alvos (lowercase, sem display text) linkados via [[...]]."""
    targets = set()
    for m in re.finditer(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", body):
        targets.add(m.group(1).strip().lower())
    return targets


def extract_external_link_anchors(body):
    """Texto-âncora de links externos [texto](url) — não wikilinks."""
    anchors = []
    for m in re.finditer(r"(?<!!)\[([^\]]+)\]\((https?://[^\)]+)\)", body):
        anchors.append(m.group(1).strip())
    return anchors


def extract_bold_terms(body):
    return [m.group(1).strip() for m in re.finditer(r"\*\*([^\*\n]{3,60})\*\*", body)]


def extract_capitalized_phrases(body):
    """Sequências de 1-4 palavras capitalizadas seguidas — proxy pra nome próprio/termo técnico."""
    body = re.sub(r"(?m)^#{1,6} .+$", "", body)  # tira headings
    phrases = []
    for m in re.finditer(
        r"(?<![.!?]\s)(?<!^)\b([A-ZÀ-Ý][a-zà-ÿ]+(?:\s+[A-ZÀ-Ý][a-zà-ÿ]+){0,3})\b",
        body,
    ):
        phrase = m.group(1).strip()
        if len(phrase.split()) == 1 and len(phrase) < 5:
            continue
        phrases.append(phrase)
    return phrases


NOISE_TERMS = {
    "portanto", "assim", "logo", "porém", "contudo", "entretanto",
    "referências", "conexões", "sumário", "índice",
}


def normalize(term):
    return term.strip().lower().rstrip(".,;:")


def collect_sources():
    """Mapa Path -> (conteúdo, node_type), pros quatro tipos como peers."""
    sources = {}
    for node_type, d in SOURCE_DIRS.items():
        if not d.exists():
            continue
        for p in d.glob("*.md"):
            if p.name == ".gitkeep":
                continue
            sources[p] = (load_content(p), node_type)
    return sources


def collect_existing_pages():
    """Mapa normalized_title -> (caminho relativo, node_type), pros quatro tipos.

    Primeira ocorrência vence em caso de colisão de nome normalizado —
    duas páginas convergindo pro mesmo nome é sinal pra check_dedupe.py
    (via /connect ou /organize), não algo a resolver aqui.
    """
    pages = {}
    for node_type, d in SOURCE_DIRS.items():
        if not d.exists():
            continue
        for p in d.glob("*.md"):
            if p.name == ".gitkeep":
                continue
            content = load_content(p)
            h1 = get_h1(content)
            names = {normalize(p.stem.replace("-", " "))}
            if h1:
                names.add(normalize(h1))
            rel = str(p.relative_to(ROOT_DIR))
            for n in names:
                if n not in pages:
                    pages[n] = (rel, node_type)
    return pages


def analyze_gap_candidates(sources, existing_pages):
    # term -> {"pages": set((node_type, filename)), "total": int, "kinds": set()}
    stats = defaultdict(lambda: {"pages": set(), "total": 0, "kinds": set()})

    for path, (content, node_type) in sources.items():
        body = strip_frontmatter(content)
        wikilink_targets = extract_wikilinks(body)
        body_no_code = strip_code_and_urls(body)

        candidates_this_page = []
        for a in extract_external_link_anchors(body_no_code):
            candidates_this_page.append((a, "link-externo"))
        for b in extract_bold_terms(body_no_code):
            candidates_this_page.append((b, "negrito"))
        for c in extract_capitalized_phrases(body_no_code):
            candidates_this_page.append((c, "nome-proprio"))

        for term, kind in candidates_this_page:
            norm = normalize(term)
            if not norm or norm in NOISE_TERMS or len(norm) < 4:
                continue
            if norm in wikilink_targets:
                continue  # já promovido a wikilink nesta página
            if norm in existing_pages:
                continue  # já tem página — não é gap, é possível wikilink faltando (ver Parte 2)
            stats[term]["pages"].add((node_type, path.name))
            stats[term]["total"] += 1
            stats[term]["kinds"].add(kind)

    ranked = [
        (term, d)
        for term, d in stats.items()
        if len(d["pages"]) >= MIN_PAGE_HITS or d["total"] >= MIN_TOTAL_HITS
    ]
    ranked.sort(key=lambda x: (len(x[1]["pages"]), x[1]["total"]), reverse=True)
    return ranked[:TOP_N]


def analyze_unlinked_existing_pages(sources, existing_pages):
    """Termo que JÁ tem página em qualquer um dos quatro tipos, aparece na
    prosa de outra página, mas essa página não linka a existente nem em
    ## Conexões nem em wikilink nenhum."""
    findings = []
    for path, (content, node_type) in sources.items():
        body = strip_frontmatter(content)
        own_path = str(path.relative_to(ROOT_DIR))

        # Compara PÁGINA-ALVO, não texto do link — mesmo alvo pode ser citado
        # pelo slug ou pelo H1 (\"[[andy-clark|Andy Clark]]\" vs. \"Andy Clark\"
        # na prosa), então cada wikilink é testado nas duas grafias.
        linked_paths = set()
        for t in extract_wikilinks(body):
            for cand in (t, t.replace("-", " ")):
                if cand in existing_pages:
                    linked_paths.add(existing_pages[cand][0])
                    break

        # ## Referências só existe em essays (concepts/entities/insights não
        # ganham bibliografia própria — ver conventions/SKILL.md). Autor
        # citado na bibliografia não é o conceito sendo discutido na prosa;
        # exigir wikilink por causa dele seria ruído.
        if node_type == "essays":
            body = re.split(r"(?m)^## Referências\s*$", body)[0]

        # Wikilinks fora do corpo antes de extrair termos: um conceito que só
        # aparece DENTRO do título de outra página já linkada é menção à
        # página linkada, não ao conceito em si.
        body = re.sub(r"\[\[[^\]]+\]\]", "", body)

        body_no_code = strip_code_and_urls(body)
        mentioned = set()
        for a in extract_external_link_anchors(body_no_code):
            mentioned.add(normalize(a))
        for b in extract_bold_terms(body_no_code):
            mentioned.add(normalize(b))
        for c in extract_capitalized_phrases(body_no_code):
            mentioned.add(normalize(c))

        for term in mentioned:
            if term not in existing_pages:
                continue
            target_path, target_type = existing_pages[term]
            if target_path == own_path:
                continue  # página se auto-mencionando, não é gap
            if target_path not in linked_paths:
                findings.append((node_type, path.name, term, target_type, target_path))
    return findings


def analyze_tag_balance():
    """Balanço de cobertura por tag, lido direto de wiki/index.json
    (essays[].tags) — ver conventions/SKILL.md, ## Tags — Vocabulário
    Controlado. Escopo é só essay: tese própria é a unidade de cobertura
    temática (concepts/entities são apoio, não o que se mede aqui).
    """
    if not INDEX_JSON_PATH.exists():
        return {}
    try:
        index = json.loads(load_content(INDEX_JSON_PATH))
    except (json.JSONDecodeError, OSError):
        return {}
    counts = defaultdict(int)
    for essay in index.get("essays", []):
        for tag in essay.get("tags") or []:
            counts[tag] += 1
    return dict(counts)


def print_part1(gap_candidates):
    print("=" * 70)
    print("PARTE 1 — candidatos a concept/entity que NÃO existem ainda")
    print("=" * 70)
    if not gap_candidates:
        print("Nenhum candidato acima do threshold "
              f"(>= {MIN_PAGE_HITS} páginas ou >= {MIN_TOTAL_HITS} ocorrências).")
    for term, d in gap_candidates:
        pages_list = ", ".join(sorted(f"{t}/{n}" for t, n in d["pages"]))
        kinds = ", ".join(sorted(d["kinds"]))
        print(f"- \"{term}\" — {len(d['pages'])} página(s) [{pages_list}], "
              f"{d['total']} ocorrência(s), sinal: {kinds}")


def print_part2(unlinked):
    print()
    print("=" * 70)
    print("PARTE 2 — página já existe, mas outra página cita sem linkar")
    print("=" * 70)
    if not unlinked:
        print("Nenhum caso encontrado.")
    for source_type, source_name, term, target_type, target_path in sorted(unlinked):
        print(f"- {source_type}/{source_name} cita \"{term}\" — "
              f"página existe em {target_path} ({target_type}), sem wikilink")


def print_part3(balance):
    print()
    print("=" * 70)
    print("PARTE 3 — balanço de cobertura por tag (wiki/index.json, essays)")
    print("=" * 70)
    if not balance:
        print("wiki/index.json não encontrado, desatualizado, ou sem tags "
              "(rode 'python scripts/build_index.py').")
    else:
        for tag, n in sorted(balance.items(), key=lambda x: x[1]):
            print(f"- {tag}: {n} essay(s)")


def main():
    parser = argparse.ArgumentParser(
        description="Candidatos a página nova e a wikilink ausente, léxico, 4 tipos como peers."
    )
    parser.add_argument("--skip-tags", action="store_true",
                         help="omite Parte 3 (balanço de tag) — usado por /gaps")
    parser.add_argument("--tags-only", action="store_true",
                         help="só Parte 3 (balanço de tag) — usado por /organize")
    args = parser.parse_args()

    if args.tags_only:
        print_part3(analyze_tag_balance())
        return 0

    sources = collect_sources()
    if not sources:
        print("Nenhuma página encontrada em wiki/{essays,concepts,entities,insights}/ "
              "— nada para analisar.")
        return 0

    existing_pages = collect_existing_pages()

    print_part1(analyze_gap_candidates(sources, existing_pages))
    print_part2(analyze_unlinked_existing_pages(sources, existing_pages))
    if not args.skip_tags:
        print_part3(analyze_tag_balance())
    return 0


if __name__ == "__main__":
    sys.exit(main())
