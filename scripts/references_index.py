#!/usr/bin/env python3
"""
references_index.py - Gera wiki/references.json e wiki/references.md a
partir da seção `## Referências` de todos os essays.

Mesmo padrão de build_index.py (wiki/index.json + wiki/index.md):
artefatos na raiz de wiki/, nunca editados à mão, sempre regenerados.
Chamado ao final de /essay, /expand, /absorb, /digest, /import, /linkify,
/review, /organize — qualquer skill que crie ou edite `## Referências`
(ver conventions/SKILL.md, ## `wiki/references.md` e `wiki/references.json`).

Formato esperado de cada entrada (padrão AIAA, ver conventions/SKILL.md,
## Formato de "## Referências" — padrão AIAA):

    [1] [Sobrenome, I., *Título*, Fonte, Ano.](https://exemplo.org/x) — nota opcional.
    [2] Sobrenome, I., *Título*, Editora, Cidade, Ano. — sem link, caso genuíno.

Este script só agrega o que já está escrito nos essays — não valida
formato (isso é `linkify_check.py`) e não decide quase-duplicatas entre
essays diferentes (isso é `dedupe_check.py`).

Usage:
    python scripts/references_index.py
"""

import datetime
import json
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import urlparse

import console_encoding  # noqa: F401  (UTF-8 no console; ver o módulo)

ROOT_DIR = Path(__file__).resolve().parent.parent
WIKI_ROOT = ROOT_DIR / "wiki"
ESSAYS_DIR = WIKI_ROOT / "essays"
OUTPUT_JSON_PATH = WIKI_ROOT / "references.json"
OUTPUT_MD_PATH = WIKI_ROOT / "references.md"

DOMAIN_GROUPS = (
    ("doi.org", "doi"),
    ("nasa.gov", "nasa"),
    ("ntrs.nasa.gov", "nasa"),
    ("aiaa.org", "aiaa"),
    ("plato.stanford.edu", "sep"),
    ("wikipedia.org", "wikipedia"),
    ("github.com", "github"),
)

DOMAIN_GROUP_LABELS = {
    "doi": "DOI",
    "nasa": "NASA",
    "aiaa": "AIAA",
    "sep": "Stanford Encyclopedia of Philosophy",
    "wikipedia": "Wikipedia",
    "github": "GitHub",
    "institucional": "Institucional",
    "sem-link": "Sem link",
}

REFERENCE_LINE_RE = re.compile(r"^\[(\d+)\]\s+(.+)$")
LINKED_RE = re.compile(r"^\[(?P<text>.+?)\]\((?P<url>[^\)]+)\)(?P<trailing>.*)$")
CANONICAL_LINK_RE = re.compile(r"\[link\]\((?P<url>https?://[^\)\s]+)\)")
LINKED_TITLE_RE = re.compile(r"\[(?P<title>\*[^*\n]+\*)\]\((?P<url>https?://[^\)\s]+)\)")

# Nome do autor para ordenação: o que vem antes da primeira vírgula, sem
# artigo inicial e sem marcação, para "Barrow, J. D." cair em B.
SORT_KEY_STRIP_RE = re.compile(r"^[\*_\[\s]+|^(?:o|a|os|as|the|an|el|la)\s+", re.IGNORECASE)


def load(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return f.read()


def get_h1(content):
    m = re.search(r"(?m)^# (.+)", content)
    return m.group(1).strip() if m else None


def normalize_citation(text):
    """Normaliza citação para dedup exato (acento/case/espaço) quando não há URL."""
    t = unicodedata.normalize("NFKD", text)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = t.lower()
    t = re.sub(r"\s+", " ", t).strip()
    return t


def normalize_url(url):
    """Normaliza URL pra dedup: sem query/fragment, sem barra final, sem www."""
    p = urlparse(url.strip())
    netloc = p.netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    path = p.path.rstrip("/")
    return f"{p.scheme}://{netloc}{path}"


def domain_group_for(url):
    netloc = urlparse(url).netloc.lower()
    for suffix, group in DOMAIN_GROUPS:
        if netloc == suffix or netloc.endswith("." + suffix):
            return group
    return "institucional"


def extract_referencias_section(content):
    """Corpo de `## Referências`: da heading até a próxima `## ` ou fim do arquivo."""
    m = re.search(r"(?m)^## Referências\s*$", content)
    if not m:
        return None
    rest = content[m.end():]
    next_h2 = re.search(r"(?m)^## ", rest)
    return rest[: next_h2.start()] if next_h2 else rest


def parse_reference_line(rest_of_line):
    """Extrai (citation_aiaa, url, has_link) de uma entrada `[N] ...`."""
    # Padrão atual: a URL da obra mora no âncora `[link]`, logo depois do
    # título em itálico. Qualquer outro link da entrada é de glossário, dentro
    # da nota, e não identifica a fonte.
    m = CANONICAL_LINK_RE.search(rest_of_line)
    if m:
        return rest_of_line.strip(), m.group("url").strip(), True

    # Formatos anteriores, ainda presentes no corpus até `/linkify --fix-format`
    # passar: link envolvendo a citação inteira, ou envolvendo só o título.
    m = LINKED_RE.match(rest_of_line)
    if m:
        citation = m.group("text").strip()
        url = m.group("url").strip()
        return citation, url, True

    m = LINKED_TITLE_RE.search(rest_of_line)
    if m:
        return rest_of_line.strip(), m.group("url").strip(), True
    # Sem link envolvendo a citação inteira: o texto até " — " *pode* ser a
    # citação, com uma nota depois. Mas nem todo travessão separa nota — no
    # arranjo `[N] Autor — [*Título*](url). Container, Ano.` ele separa o autor
    # do resto da própria citação, e cortar ali reduziria a citação ao nome do
    # autor. O título em itálico é o desempate: se o pedaço antes do travessão
    # não tem itálico, ele não é uma citação completa, e a linha inteira é.
    head, sep, _tail = rest_of_line.partition(" — ")
    citation = head.strip() if sep and re.search(r"\*[^*]+\*", head) else rest_of_line.strip()
    return citation, None, False


def collect_essay_references(path):
    content = load(path)
    title = get_h1(content) or path.stem
    slug = path.stem
    section = extract_referencias_section(content)
    refs = []
    if not section:
        return slug, title, refs
    for line in section.splitlines():
        line = line.strip()
        if not line:
            continue
        m = REFERENCE_LINE_RE.match(line)
        if not m:
            continue
        citation, url, has_link = parse_reference_line(m.group(2))
        refs.append({"citation_aiaa": citation, "url": url, "has_link": has_link})
    return slug, title, refs


def sort_key(citation):
    """Chave alfabética estável: acento e marcação não deslocam a entrada."""
    t = re.sub(r"\[link\]\([^\)]*\)", "", citation)
    t = SORT_KEY_STRIP_RE.sub("", t).strip()
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]", "", t.lower()).strip()


def build():
    entries = {}  # dedup key -> entry dict
    essays_seen = 0

    if ESSAYS_DIR.exists():
        for f in sorted(ESSAYS_DIR.glob("*.md")):
            if f.name == ".gitkeep":
                continue
            essays_seen += 1
            slug, title, refs = collect_essay_references(f)
            for ref in refs:
                if ref["url"]:
                    key = ("url", normalize_url(ref["url"]))
                    domain_group = domain_group_for(ref["url"])
                else:
                    key = ("text", normalize_citation(ref["citation_aiaa"]))
                    # Ausência de link não é um tipo de fonte: uma obra sem
                    # edição digital continua sendo livro, paper ou verbete.
                    # `domain_group` fica nulo, e a entrada aparece na lista
                    # junto com todas as outras, apenas sem a palavra "link".
                    domain_group = None

                if key not in entries:
                    entries[key] = {
                        "url": ref["url"],
                        "citation_aiaa": ref["citation_aiaa"],
                        "domain_group": domain_group,
                        "cited_by": [],
                        "has_link": ref["has_link"],
                    }
                entry = entries[key]
                if slug not in entry["cited_by"]:
                    entry["cited_by"].append(slug)

    references = sorted(entries.values(), key=lambda e: sort_key(e["citation_aiaa"]))
    return {
        "generated": datetime.date.today().isoformat(),
        "essays_scanned": essays_seen,
        "references": references,
    }


def render_references_md(data):
    lines = [
        "# Referências",
        "",
        f"_Artefato gerado — nunca edite à mão, rode `python scripts/references_index.py`. "
        f"{len(data['references'])} referência(s) única(s) em {data['essays_scanned']} essay(s), "
        f"gerado em {data['generated']}._",
        "",
    ]

    # Lista única em ordem alfabética. Sem agrupar por domínio: agrupar por onde
    # a obra está hospedada separaria o livro do paper do mesmo autor, e criava
    # um balde "Sem link" que dizia respeito à disponibilidade digital, não ao
    # tipo de fonte. Bibliografia se lê por autor.
    for ref in data["references"]:
        citation = ref["citation_aiaa"]
        if ref["url"] and not CANONICAL_LINK_RE.search(citation):
            # Entrada ainda num formato antigo: o âncora entra no fim, para o
            # arquivo gerado não ficar sem o link que a entrada de fato tem.
            citation = f"{citation.rstrip()} [link]({ref['url']})"
        lines.append(f"- {citation}")
        lines.append(f"  <br>_citada em: {', '.join(ref['cited_by'])}_")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main():
    data = build()
    WIKI_ROOT.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    with open(OUTPUT_MD_PATH, "w", encoding="utf-8") as f:
        f.write(render_references_md(data))

    no_link = sum(1 for r in data["references"] if not r["has_link"])
    print(f"Referências indexadas: {len(data['references'])} única(s) em {data['essays_scanned']} essay(s) "
          f"({no_link} sem link).")
    print(f"  {OUTPUT_JSON_PATH.relative_to(ROOT_DIR)}")
    print(f"  {OUTPUT_MD_PATH.relative_to(ROOT_DIR)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
