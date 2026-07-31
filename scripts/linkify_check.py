#!/usr/bin/env python3
"""
linkify_check.py — Verificador da seção `## Referências` de essays.

Complementa `format_check.py`, que só checa se a seção existe (`NO_REFERENCIAS`);
aqui o conteúdo dela é validado contra o padrão AIAA definido em
`conventions/SKILL.md`, seção `## Formato de "## Referências" — padrão AIAA`.
Chamado por `/linkify`, e pela varredura mecânica de `/format` e `/organize`.

Códigos emitidos:

    REFERENCIA_FORMATO_INVALIDO  ERROR    entrada fora do padrão `[N] ...` com
                                          título em itálico, ou numeração fora
                                          de ordem
    DUPLICATE_REFERENCIA         ERROR    duas entradas com a mesma URL
                                          normalizada no MESMO essay
    LINK_NOT_IN_REFERENCIAS      ERROR    URL usada no corpo sem entrada
                                          correspondente em `## Referências`
    REFERENCIA_SEM_LINK          WARNING  entrada sem link; legítima só para
                                          fonte sem edição digital confiável
    REFERENCIA_NAO_USADA         WARNING  entrada `[N]` nunca citada no corpo

`NO_REFERENCIAS` continua sendo emitido por `format_check.py` e não é duplicado
aqui: este script assume que a seção existe e apenas pula o essay se não achar.

O modo `--fix-format` faz só a parte **mecânica** da migração do formato antigo
(bullet `- Autor. *Título.* ...`) para o AIAA:

    1. bullet vira `[N]`, numerado na ordem em que já estava;
    2. dentro de cada itálico da citação, remove aspas envolventes e o ponto
       final (`*"Título."*` -> `*Título*`);
    3. uma linha em branco entre entradas.

O que **não** faz, por não ser decidível mecanicamente: escolher a URL da fonte.
No formato antigo os links que aparecem numa entrada costumam ser links de
glossário dentro da nota (por exemplo um verbete da Wikipédia para um termo
citado), e não o endereço da própria obra; promovê-los a link da citação
inventaria bibliografia. Essas entradas saem do `--fix-format` sinalizadas com
`REFERENCIA_SEM_LINK`, para tratamento editorial via `/linkify`.

Uso:
    python linkify_check.py                    # todos os essays
    python linkify_check.py --file meu-essay   # essay único (slug ou .md)
    python linkify_check.py --json             # saída JSON para a skill parsear
    python linkify_check.py --fix-format       # aplica a migração mecânica
"""

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import console_encoding  # noqa: F401  (UTF-8 no console; ver o módulo)
from references_index import (
    LINKED_RE,
    extract_referencias_section,
    normalize_url,
    parse_reference_line,
)

ROOT_DIR = Path(__file__).resolve().parent.parent
WIKI_ROOT = ROOT_DIR / "wiki"
ESSAYS_DIR = WIKI_ROOT / "essays"

# `LINK_NOT_IN_REFERENCIAS` só vale para link que é de fato uma fonte. A regra 3
# de `## Estrutura obrigatória do essay` obriga link externo para todo termo
# técnico na primeira ocorrência, então a maioria esmagadora dos links do corpo é
# glossário (verbete de enciclopédia para um termo citado), não bibliografia —
# exigir entrada em `## Referências` para todos eles marcaria ~2000 falsos erros
# no corpus atual. Estes são os domínios/formatos que caracterizam uma obra
# citável. Para voltar ao comportamento estrito, esvazie esta tupla.
CITATION_LIKE = (
    "doi.org",
    "arxiv.org",
    "biorxiv.org",
    "ntrs.nasa.gov",
    "aiaa.org",
    "sciencedirect.com",
    "springer.com",
    "link.springer.com",
    "jstor.org",
    "nature.com",
    "science.org",
    "ieee.org",
    "ieeexplore.ieee.org",
    "acm.org",
    "dl.acm.org",
    "pubmed.ncbi.nlm.nih.gov",
    "journals.aps.org",
    "royalsocietypublishing.org",
)

# Padrão do link da obra: a palavra "link", clicável, logo depois do título em
# itálico. Mantém a citação inteira como texto limpo — só a palavra "link" fica
# azul — e preserva o itálico do título, que sublinhado de hyperlink estragaria.
LINK_ANCHOR = "link"
CANONICAL_LINK_RE = re.compile(r"\[link\]\((?P<url>https?://[^\)\s]+)\)")
TITLE_THEN_LINK_RE = re.compile(r"(?<!\*)\*[^*\n]+\*\s*\[link\]\(https?://[^\)\s]+\)")
LINKED_TITLE_RE = re.compile(r"\[(?P<title>\*[^*\n]+\*)\]\((?P<url>https?://[^\)\s]+)\)")

NUMBERED_RE = re.compile(r"^\[(\d+)\]\s+(.+)$")
BULLET_RE = re.compile(r"^[-*]\s+(.+)$")
MD_LINK_RE = re.compile(r"\[(?P<text>[^\]]*)\]\((?P<url>https?://[^\)\s]+)\)")
# Itálico de verdade: um asterisco de cada lado, nunca dois. Sem os lookarounds
# esta regex entra dentro de `**negrito**` — casa o segundo `*` da abertura com
# o primeiro `*` do fechamento — e aí qualquer reescrita corrompe o texto.
ITALIC_RE = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")
INLINE_CITATION_RE = re.compile(r"\[(\d+)\]")
QUOTE_CHARS = "\"'“”‘’"


def load(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return f.read()


def split_body(content):
    """Corpo argumentativo: sem frontmatter e sem `## Referências` em diante."""
    body = re.sub(r"(?s)\A---\r?\n.*?\r?\n---\r?\n", "", content, count=1)
    m = re.search(r"(?m)^## Referências\s*$", body)
    return body[: m.start()] if m else body


def citation_and_note(rest_of_line):
    """Separa a citação da nota opcional que vem depois de ' — '.

    Nem todo travessão separa nota: no arranjo `Autor — *Título*. Editora, Ano.`
    ele separa o autor do resto da própria citação, e cortar ali reduziria a
    citação ao nome do autor. O título em itálico desempata — se o pedaço antes
    do travessão não tem itálico, ele não é uma citação completa.
    """
    head, sep, tail = rest_of_line.partition(" — ")
    if sep and ITALIC_RE.search(head):
        return head.strip(), tail.strip()
    return rest_of_line.strip(), None


def normalize_italics(text):
    """`*"Título."*` -> `*Título*`. Só mexe no que já está em itálico.

    Nunca toca em `**negrito**` (ver `ITALIC_RE`) e nunca consome espaço fora
    dos delimitadores: o texto entre um itálico e o próximo é copiado intacto.
    """
    out = []
    pos = 0
    for m in ITALIC_RE.finditer(text):
        inner = m.group(1).strip().strip(QUOTE_CHARS).strip()
        if not inner:
            continue
        had_terminal_period = inner.endswith(".")
        out.append(text[pos : m.start()])
        out.append(f"*{inner.rstrip('.').strip()}*")
        pos = m.end()
        # No formato antigo o ponto que separava título e container morava
        # dentro do itálico. Tirá-lo sem repor nada deixaria
        # "*Título* Oxford University Press" sem separador algum, então a
        # vírgula do padrão AIAA entra no lugar — mas só quando o que vem a
        # seguir é mesmo um container, e não pontuação que já separa.
        if had_terminal_period and re.match(r"\s+[^\s,.;:—)\]]", text[pos:]):
            out.append(",")
    out.append(text[pos:])
    return "".join(out)


def is_citation_like(url):
    """A URL aponta para uma obra citável, e não para um verbete de glossário?"""
    netloc = urlparse(url).netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    if urlparse(url).path.lower().endswith(".pdf"):
        return True
    return any(netloc == d or netloc.endswith("." + d) for d in CITATION_LIKE)


def has_italic_title(citation):
    """Todo título vai em itálico, sem exceção por tipo de fonte."""
    return any(m.group(1).strip() for m in ITALIC_RE.finditer(citation))


BOLD_NUMBERED_RE = re.compile(r"^\*\*\[(\d+)\]\*\*\s+(.+)$")
BLOCKQUOTE_RE = re.compile(r"^>\s+(.+)$")


def canonicalize_entry_lines(section):
    """Normaliza variantes de escrita para o formato `[N] ...`, uma por linha.

    O corpus acumulou quatro estilos de bibliografia. Dois deles são
    deterministicamente conversíveis e entram aqui:

    - `**[1]** Citação.` seguida da nota num parágrafo próprio: o negrito sai e
      a nota volta para a mesma linha, depois de ` — `.
    - `> Citação` em blockquote, uma por linha e sem numeração: vira `[N]` na
      ordem em que já estava.

    O que sobra (link envolvendo só o título, ou entrada sem título em itálico)
    depende de saber qual pedaço do texto é o título da obra, e isso não é
    decidível sem ler a fonte — fica para `/linkify`.
    """
    out = []
    pending_bold = None      # entrada `**[N]**` esperando a nota do parágrafo seguinte
    blockquote_number = 0

    for raw in section.splitlines():
        line = raw.strip()

        if not line or line == "---":
            continue

        m = BOLD_NUMBERED_RE.match(line)
        if m:
            if pending_bold:
                out.append(pending_bold)
            pending_bold = f"[{m.group(1)}] {m.group(2)}"
            continue

        m = BLOCKQUOTE_RE.match(line)
        if m:
            blockquote_number += 1
            out.append(f"[{blockquote_number}] {m.group(1)}")
            continue

        if pending_bold:
            # Parágrafo solto logo após uma entrada `**[N]**` é a nota dela.
            out.append(f"{pending_bold} — {line}")
            pending_bold = None
            continue

        out.append(line)

    if pending_bold:
        out.append(pending_bold)

    return "\n".join(out)


def parse_entries(section):
    """Cada linha não vazia da seção, classificada por formato."""
    entries = []
    for lineno, raw in enumerate(section.splitlines()):
        line = raw.strip()
        if not line:
            continue
        m = NUMBERED_RE.match(line)
        if m:
            entries.append(
                {"kind": "numbered", "number": int(m.group(1)), "rest": m.group(2), "raw": line}
            )
            continue
        m = BULLET_RE.match(line)
        if m:
            entries.append({"kind": "bullet", "number": None, "rest": m.group(1), "raw": line})
            continue
        entries.append({"kind": "unknown", "number": None, "rest": line, "raw": line})
    return entries


def check_essay(path):
    content = load(path)
    issues = []
    section = extract_referencias_section(content)

    if section is None:
        # NO_REFERENCIAS é responsabilidade de format_check.py.
        return {"name": path.name, "slug": path.stem, "issues": issues, "skipped": True}

    entries = parse_entries(section)
    body = split_body(content)
    cited_numbers = {int(n) for n in INLINE_CITATION_RE.findall(body)}

    seen_urls = {}
    for position, entry in enumerate(entries, start=1):
        label = entry["raw"][:70]

        if entry["kind"] != "numbered":
            issues.append(
                {
                    "code": "REFERENCIA_FORMATO_INVALIDO",
                    "severity": "ERROR",
                    "fixable": entry["kind"] == "bullet",
                    "message": (
                        f"entrada {position} não está no padrão `[N] ...`: {label}"
                        + ("  (corrigível com --fix-format)" if entry["kind"] == "bullet" else "")
                    ),
                }
            )
            continue

        if entry["number"] != position:
            issues.append(
                {
                    "code": "REFERENCIA_FORMATO_INVALIDO",
                    "severity": "ERROR",
                    "fixable": True,
                    "message": (
                        f"numeração fora de ordem: entrada {position} está como "
                        f"[{entry['number']}]  (corrigível com --fix-format)"
                    ),
                }
            )

        # A URL da obra é a do âncora `[link](...)`. Qualquer outro link na
        # entrada é de glossário, dentro da nota, e não identifica a fonte.
        canonical = CANONICAL_LINK_RE.search(entry["rest"])
        url = canonical.group("url") if canonical else None
        has_link = bool(url)
        outros_links = [
            m.group("url")
            for m in MD_LINK_RE.finditer(entry["rest"])
            if m.group("text").strip().lower() != LINK_ANCHOR
        ]

        if not has_italic_title(entry["rest"]):
            issues.append(
                {
                    "code": "REFERENCIA_FORMATO_INVALIDO",
                    "severity": "ERROR",
                    "fixable": False,
                    "message": f"entrada [{entry['number']}] sem título em itálico: {label}",
                }
            )
        elif has_link and not TITLE_THEN_LINK_RE.search(entry["rest"]):
            issues.append(
                {
                    "code": "REFERENCIA_FORMATO_INVALIDO",
                    "severity": "ERROR",
                    "fixable": True,
                    "message": (
                        f"entrada [{entry['number']}]: o `[link]` não vem logo depois do "
                        f"título em itálico  (corrigível com --fix-format): {label}"
                    ),
                }
            )
        elif not has_link and outros_links:
            issues.append(
                {
                    "code": "REFERENCIA_FORMATO_INVALIDO",
                    "severity": "ERROR",
                    "fixable": True,
                    "message": (
                        f"entrada [{entry['number']}] tem URL, mas fora do âncora `[link]` "
                        f"(corrigível com --fix-format): {label}"
                    ),
                }
            )

        if not has_link and not outros_links:
            issues.append(
                {
                    "code": "REFERENCIA_SEM_LINK",
                    "severity": "WARNING",
                    "fixable": False,
                    "message": (
                        f"entrada [{entry['number']}] sem link; só é legítimo para fonte "
                        f"sem edição digital confiável: {label}"
                    ),
                }
            )
        # Dedup só é possível com a URL da obra. Entrada cuja única URL está
        # solta na nota já foi sinalizada como formato inválido acima; sem
        # âncora `[link]` não dá para dizer qual das URLs identifica a fonte.
        if url:
            key = normalize_url(url)
            if key in seen_urls:
                issues.append(
                    {
                        "code": "DUPLICATE_REFERENCIA",
                        "severity": "ERROR",
                        "fixable": False,
                        "message": (
                            f"entradas [{seen_urls[key]}] e [{entry['number']}] apontam "
                            f"para a mesma URL normalizada: {key}"
                        ),
                    }
                )
            else:
                seen_urls[key] = entry["number"]

        # `REFERENCIA_NAO_USADA` só faz sentido num essay que de fato usa
        # citação numérica inline. Nenhuma regra de conventions/SKILL.md obriga
        # isso — a bibliografia pode ser lista de leitura, não aparato de
        # citação. Num essay sem nenhuma citação `[N]` no corpo, marcar todas as
        # entradas como "não usadas" seria ruído, não achado; o que interessa é
        # o caso misto, em que o autor citou algumas e esqueceu outras.
        if cited_numbers and entry["number"] not in cited_numbers:
            issues.append(
                {
                    "code": "REFERENCIA_NAO_USADA",
                    "severity": "WARNING",
                    "fixable": False,
                    "message": (
                        f"entrada [{entry['number']}] nunca citada no corpo, num essay "
                        f"que cita outras entradas inline"
                    ),
                }
            )

    for m in MD_LINK_RE.finditer(body):
        url = m.group("url")
        if not is_citation_like(url):
            continue
        key = normalize_url(url)
        if key not in seen_urls:
            issues.append(
                {
                    "code": "LINK_NOT_IN_REFERENCIAS",
                    "severity": "ERROR",
                    "fixable": False,
                    "message": (
                        f"link do corpo sem entrada em `## Referências`: "
                        f"{m.group('url')}"
                    ),
                }
            )

    return {"name": path.name, "slug": path.stem, "issues": issues, "skipped": False}


def promote_link(citation):
    """Move a URL da obra para o âncora `[link]` logo depois do título.

    Cobre os três arranjos que o corpus acumulou:

    - `[Autor, *Título*, Editora, Ano.](url)` — link envolvendo a citação inteira
    - `Autor — [*Título*](url). Editora, Ano.` — link envolvendo só o título
    - `Autor, *Título*, Editora, Ano.` sem link — fica como está

    A URL nunca é inventada: se a entrada não tem link, sai sem link, e o aviso
    `REFERENCIA_SEM_LINK` é o lugar certo para isso aparecer.
    """
    if CANONICAL_LINK_RE.search(citation):
        return citation  # já está no padrão

    url = None

    # Link envolvendo a citação inteira: desembrulha e guarda a URL.
    m = LINKED_RE.match(citation)
    if m:
        url = m.group("url").strip()
        citation = m.group("text").strip() + m.group("trailing")

    # Link envolvendo só o título: `[*Título*](url)` -> `*Título*`.
    if url is None:
        m = LINKED_TITLE_RE.search(citation)
        if m:
            url = m.group("url")
            citation = citation[: m.start()] + m.group("title") + citation[m.end() :]

    if url is None:
        return citation

    # O âncora entra logo depois do primeiro título em itálico.
    m = ITALIC_RE.search(citation)
    if m:
        return f"{citation[: m.end()]} [{LINK_ANCHOR}]({url}){citation[m.end() :]}"
    return f"{citation} [{LINK_ANCHOR}]({url})"


def rebuild_section(section):
    """Reescreve a seção no padrão AIAA. Retorna (novo_texto, n_entradas)."""
    section = canonicalize_entry_lines(section)
    entries = [e for e in parse_entries(section) if e["kind"] in ("numbered", "bullet")]
    if not entries:
        return None, 0

    lines = []
    for number, entry in enumerate(entries, start=1):
        citation, note = citation_and_note(entry["rest"])
        citation = promote_link(normalize_italics(citation))
        line = f"[{number}] {citation}"
        if note:
            line += f" — {note}"
        lines.append(line)

    return "\n\n" + "\n\n".join(lines) + "\n\n", len(entries)


def fix_essay(path):
    """Aplica a migração mecânica. Retorna n_entradas reescritas, 0 se nada mudou."""
    content = load(path)
    m = re.search(r"(?m)^## Referências[ \t]*$", content)
    if not m:
        return 0

    rest = content[m.end():]
    next_h2 = re.search(r"(?m)^## ", rest)
    end = m.end() + (next_h2.start() if next_h2 else len(rest))
    section = content[m.end():end]

    new_section, count = rebuild_section(section)
    if new_section is None or new_section == section:
        return 0

    path.write_text(content[: m.end()] + new_section + content[end:], encoding="utf-8")
    return count


def resolve_essay(slug):
    p = Path(slug)
    if p.exists():
        return p.resolve()
    for ext in ("", ".md"):
        candidate = ESSAYS_DIR / (slug + ext)
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        f"Essay '{slug}' não encontrado em {ESSAYS_DIR} nem como caminho direto"
    )


def build_parser():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--file", help="essay único (slug ou nome .md)")
    p.add_argument("--json", action="store_true", help="saída JSON para a skill parsear")
    p.add_argument(
        "--fix-format",
        action="store_true",
        help="aplica a migração mecânica do formato antigo para o AIAA",
    )
    return p


def main():
    args = build_parser().parse_args()

    if args.file:
        try:
            essay_paths = [resolve_essay(args.file)]
        except FileNotFoundError as e:
            print(f"ERRO: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        essay_paths = sorted(ESSAYS_DIR.glob("*.md"))
        if not essay_paths:
            print(f"Nenhum essay encontrado em {ESSAYS_DIR}", file=sys.stderr)
            sys.exit(0)

    if args.fix_format:
        touched = 0
        for path in essay_paths:
            count = fix_essay(path)
            if count:
                touched += 1
                print(f"reescrito: {path.name} ({count} entrada(s))")
        print(f"\n{touched}/{len(essay_paths)} essay(s) tiveram `## Referências` reescrita.")
        print("Rode `python scripts/references_index.py` para regenerar o índice de referências.")
        if touched:
            print(
                "A migração é só mecânica: entradas que continuarem sem link da própria "
                "obra saem sinalizadas como REFERENCIA_SEM_LINK e precisam de /linkify."
            )
        return

    results = [check_essay(p) for p in essay_paths]

    if args.json:
        print(json.dumps({"essays": results}, ensure_ascii=False, indent=2))
        return

    severity_order = {"ERROR": 0, "WARNING": 1}
    icons = {"ERROR": "❌", "WARNING": "⚠️ "}
    by_code = {}
    total_issues = 0
    clean = 0

    for result in results:
        if result["skipped"]:
            continue
        issues = result["issues"]
        if not issues:
            print(f"✅ {result['name']}")
            clean += 1
            continue
        print(f"\n{'─' * 60}")
        print(f"📄 {result['name']}")
        for issue in sorted(issues, key=lambda x: severity_order.get(x["severity"], 9)):
            print(f"   {icons.get(issue['severity'], '•')} [{issue['code']}] {issue['message']}")
            by_code[issue["code"]] = by_code.get(issue["code"], 0) + 1
        total_issues += len(issues)

    checked = sum(1 for r in results if not r["skipped"])
    print(f"\n{'=' * 60}")
    print(f"Resultado: {clean}/{checked} essay(s) limpo(s), {total_issues} issue(s) no total")
    for code, count in sorted(by_code.items(), key=lambda kv: -kv[1]):
        print(f"  {code}: {count}")
    if by_code.get("REFERENCIA_FORMATO_INVALIDO"):
        print("\nParte disso é mecânica: `python scripts/linkify_check.py --fix-format`.")


if __name__ == "__main__":
    main()
