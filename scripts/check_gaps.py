#!/usr/bin/env python3
"""
check_gaps.py — candidatos a página (concept/entity) e a link ausentes.

Cobre a direção que check_wiki.py e /organize (passo 2) NÃO cobrem:
  - check_wiki.py: wikilinks que já existem e apontam pra nada -> "link morto"
  - /organize passo 2: concept/entity que já existe sem essay que o linke -> "órfão reverso"
  - este script: termo citado repetidamente na prosa (via link externo, negrito,
    ou nome próprio capitalizado) que NUNCA foi promovido a wikilink nem tem
    página em concepts/ ou entities/ -> "órfão de cobertura"

É heurístico por natureza (não há NLP real aqui) — produz uma lista de
CANDIDATOS ranqueada por frequência para o usuário decidir, nunca cria página
sozinho. Falsos positivos são esperados e ok; falso negativo silencioso é o
que queremos evitar.
"""

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
INDEX_JSON_PATH = WIKI_ROOT / "index.json"

MIN_ESSAY_HITS = 2      # termo precisa aparecer em pelo menos N essays distintos
MIN_TOTAL_HITS = 3      # ou N vezes no total (mesmo essay repetindo)
TOP_N = 40               # não afoga o usuário — corta a cauda longa


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
    # byline ("> Tipo") e qualquer blockquote — estrutural, não prosa
    body = re.sub(r"(?m)^>.*$", "", body)
    # links internos de âncora ([Texto](#secao)) — Sumário aponta pra dentro do
    # próprio essay, não é um termo citado; mata o par inteiro pra não sobrar
    # o texto-âncora capitalizado como falso positivo de nome próprio.
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
    # remove começo de frase (depois de . ! ? ou heading) pra reduzir falso positivo
    # de palavra só capitalizada por estar no início de sentença.
    body = re.sub(r"(?m)^#{1,6} .+$", "", body)  # tira headings
    phrases = []
    for m in re.finditer(
        r"(?<![.!?]\s)(?<!^)\b([A-ZÀ-Ý][a-zà-ÿ]+(?:\s+[A-ZÀ-Ý][a-zà-ÿ]+){0,3})\b",
        body,
    ):
        phrase = m.group(1).strip()
        # descarta frases de 1 palavra muito curtas (ruído alto) e stopword-capitalizadas comuns
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


def collect_existing_pages():
    """Mapa normalized_title -> caminho relativo, para concepts/ e entities/."""
    pages = {}
    for d in (CONCEPTS_DIR, ENTITIES_DIR):
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
            for n in names:
                pages[n] = str(p.relative_to(ROOT_DIR))
    return pages


def collect_essays():
    essays = {}
    if not ESSAYS_DIR.exists():
        return essays
    for p in ESSAYS_DIR.glob("*.md"):
        if p.name == ".gitkeep":
            continue
        content = load_content(p)
        essays[p] = content
    return essays


def analyze_gap_candidates(essays, existing_pages):
    # term -> {"essays": set(paths), "total": int, "kind": set()}
    stats = defaultdict(lambda: {"essays": set(), "total": 0, "kinds": set()})

    for path, content in essays.items():
        body = strip_frontmatter(content)
        wikilink_targets = extract_wikilinks(body)
        body_no_code = strip_code_and_urls(body)

        candidates_this_essay = []
        for a in extract_external_link_anchors(body_no_code):
            candidates_this_essay.append((a, "link-externo"))
        for b in extract_bold_terms(body_no_code):
            candidates_this_essay.append((b, "negrito"))
        for c in extract_capitalized_phrases(body_no_code):
            candidates_this_essay.append((c, "nome-proprio"))

        for term, kind in candidates_this_essay:
            norm = normalize(term)
            if not norm or norm in NOISE_TERMS or len(norm) < 4:
                continue
            if norm in wikilink_targets:
                continue  # já promovido a wikilink neste essay
            if norm in existing_pages:
                continue  # já tem página — não é gap, é possível wikilink faltando (ver parte 2)
            stats[term]["essays"].add(path.name)
            stats[term]["total"] += 1
            stats[term]["kinds"].add(kind)

    # filtra por threshold e ordena por (nº essays distintos, total) desc
    ranked = [
        (term, d)
        for term, d in stats.items()
        if len(d["essays"]) >= MIN_ESSAY_HITS or d["total"] >= MIN_TOTAL_HITS
    ]
    ranked.sort(key=lambda x: (len(x[1]["essays"]), x[1]["total"]), reverse=True)
    return ranked[:TOP_N]


def analyze_unlinked_existing_pages(essays, existing_pages):
    """Termo que JÁ tem página em concepts/entities, aparece na prosa de um essay,
    mas esse essay não linka a página em ## Conexões nem em wikilink nenhum."""
    findings = []
    for path, content in essays.items():
        body = strip_frontmatter(content)
        wikilink_targets = extract_wikilinks(body)
        body_no_code = strip_code_and_urls(body)
        mentioned = set()
        for a in extract_external_link_anchors(body_no_code):
            mentioned.add(normalize(a))
        for b in extract_bold_terms(body_no_code):
            mentioned.add(normalize(b))
        for c in extract_capitalized_phrases(body_no_code):
            mentioned.add(normalize(c))
        for term in mentioned:
            if term in existing_pages and term not in wikilink_targets:
                findings.append((path.name, term, existing_pages[term]))
    return findings


def analyze_tag_balance():
    """Balanço de cobertura por tag, lido direto de wiki/index.json
    (essays[].tags) — substitui o antigo parse de `## Categoria` em
    wiki/index.md, que deixou de existir como agrupamento (ver
    conventions/SKILL.md, ## Tags — Vocabulário Controlado).
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


def main():
    essays = collect_essays()
    if not essays:
        print("Nenhum essay encontrado em wiki/essays/ — nada para analisar.")
        return

    existing_pages = collect_existing_pages()

    print("=" * 70)
    print("PARTE 1 — candidatos a concept/entity que NÃO existem ainda")
    print("=" * 70)
    gap_candidates = analyze_gap_candidates(essays, existing_pages)
    if not gap_candidates:
        print("Nenhum candidato acima do threshold "
              f"(>= {MIN_ESSAY_HITS} essays ou >= {MIN_TOTAL_HITS} ocorrências).")
    for term, d in gap_candidates:
        essays_list = ", ".join(sorted(d["essays"]))
        kinds = ", ".join(sorted(d["kinds"]))
        print(f"- \"{term}\" — {len(d['essays'])} essay(s) [{essays_list}], "
              f"{d['total']} ocorrência(s), sinal: {kinds}")

    print()
    print("=" * 70)
    print("PARTE 2 — página já existe, mas essay cita sem linkar")
    print("=" * 70)
    unlinked = analyze_unlinked_existing_pages(essays, existing_pages)
    if not unlinked:
        print("Nenhum caso encontrado.")
    for essay_name, term, page_path in sorted(unlinked):
        print(f"- {essay_name} cita \"{term}\" — página existe em {page_path}, sem wikilink")

    print()
    print("=" * 70)
    print("PARTE 3 — balanço de cobertura por tag (wiki/index.json)")
    print("=" * 70)
    balance = analyze_tag_balance()
    if not balance:
        print("wiki/index.json não encontrado, desatualizado, ou sem tags "
              "(rode 'python scripts/build_index.py').")
    else:
        for tag, n in sorted(balance.items(), key=lambda x: x[1]):
            print(f"- {tag}: {n} essay(s)")


if __name__ == "__main__":
    sys.exit(main())
