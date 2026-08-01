#!/usr/bin/env python3
"""
check_format.py — Verificador unificado de formatação de essays.

Substitui deep_format_check.py. Cobre todas as regras de formatação de
essay definidas em conventions/SKILL.md:

    1.  Frontmatter YAML: campos obrigatórios e status válido
    2.  H1 + byline: formato exato, separador ·, autor, tipo
    3.  Byline: sem [[wikilinks]], sem dois-pontos, sem LaTeX chars perigosos
    4.  Espaço em branco após H1 e após cada heading
    5.  ## Sumário: presente, links internos batem com headings reais
    6.  ## Referências: heading exato (H2, nome exato)
    7.  ## Conexões: presente e é a última seção H2
    8.  Wikilinks fora de Conexões
    9.  Links externos (mínimo 10 no corpo)
   10.  Aspas ASCII " e ' suspeitas dentro da prosa (indica tipográficas ausentes
        ou LaTeX-unsafe quando há LaTeX no pipeline)
   11.  Caracteres LaTeX perigosos (&, %, #, _não-escapado) no YAML/byline
   12.  Espaços duplos no meio de parágrafos
   13.  Linhas em branco excessivas (≥3 consecutivas)
   14.  Travessões (—) — conta por essay; >2 é WARNING
   15.  Bullets (- / *) no corpo argumentativo fora de Sumário/Referências
   16.  HTML residual
   17.  Símbolos residuais (◆, replacement char, NBSP, &amp;, etc.)
   18.  Idioma: parágrafos possivelmente em inglês (não traduzidos)
   19.  Obsidian: wikilink display text sem dois-pontos

Uso:
    python check_format.py                   # todos os essays
    python check_format.py --file meu-essay  # essay único (slug ou nome .md)
    python check_format.py --json            # saída JSON para parsear no skill
    python check_format.py --file X --json   # combinado
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

import console_encoding  # noqa: F401  (UTF-8 no console; ver o módulo)

# ---------------------------------------------------------------------------
# Configuração de caminhos
# ---------------------------------------------------------------------------

ROOT_DIR   = Path(__file__).resolve().parent.parent
WIKI_ROOT  = ROOT_DIR / "wiki"
ESSAYS_DIR = WIKI_ROOT / "essays"

# ---------------------------------------------------------------------------
# Vocabulário controlado
# ---------------------------------------------------------------------------

VALID_TYPES  = {"Ensaio", "White Paper", "Brainstorm", "Estudo", "Análise"}
VALID_STATUS = {"draft", "maduro", "finalizado"}

# `summary:` é resumo de uma linha; acima disto vira parágrafo e quebra o
# layout de wiki/index.md (ver `## Frontmatter` em conventions/SKILL.md).
SUMMARY_MAX_CHARS = 120

ENGLISH_ONLY_WORDS = {
    "the", "and", "with", "this", "that", "these", "those", "from", "have",
    "has", "been", "were", "was", "which", "their", "there", "where", "when",
    "because", "however", "therefore", "although", "between", "through",
    "into", "onto", "about", "should", "would", "could", "cannot",
    "doesn't", "isn't", "aren't", "wasn't", "weren't", "don't", "does",
    "did", "than",
}
PORTUGUESE_ONLY_WORDS = {
    "não", "com", "para", "uma", "isso", "está", "então", "porque", "entre",
    "sobre", "quando", "onde", "porém", "contudo", "embora", "através",
    "seus", "suas", "já", "também", "mais", "menos", "muito",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FENCE_RE = re.compile(r"^```")


def load(path: Path) -> str:
    with open(path, encoding="utf-8-sig") as f:
        return f.read()


def split_frontmatter(content: str):
    """Returns (fm_text, body_text). fm_text is '' if no frontmatter."""
    if content.startswith("---\n"):
        end = content.find("\n---", 4)
        if end != -1:
            eob = content.find("\n", end + 1)
            eob = eob + 1 if eob != -1 else len(content)
            return content[:eob], content[eob:]
    return "", content


def strip_fences(text: str) -> str:
    """Remove fenced code block contents (keep the delimiters as markers)."""
    lines, out, in_fence = text.splitlines(), [], False
    for line in lines:
        if FENCE_RE.match(line.strip()):
            in_fence = not in_fence
            out.append("")
        else:
            out.append("" if in_fence else line)
    return "\n".join(out)


def heading_anchor(heading_text: str) -> str:
    """Convert heading text to Obsidian/GitHub markdown anchor."""
    s = heading_text.lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"\s+", "-", s.strip())
    return s


# ---------------------------------------------------------------------------
# Checker principal
# ---------------------------------------------------------------------------

def check_essay(filepath: Path) -> dict:
    """
    Retorna dict com:
        name: str
        issues: list[dict]  — cada issue: {severity, code, message}
    severity: CRITICAL | ERROR | WARNING | INFO
    """
    issues = []

    def add(severity, code, msg):
        issues.append({"severity": severity, "code": code, "message": msg})

    content = load(filepath)
    fm_text, body = split_frontmatter(content)
    body_clean = strip_fences(body)  # sem blocos de código
    lines = content.splitlines()
    # Mesmo alinhamento de linhas que `lines`, mas com o interior das fences em
    # branco. Regra de prosa não se aplica a código: um comentário Python `# x`
    # não é heading, `q[0]` não é citação, e aspas ASCII são obrigatórias lá.
    lines_clean = strip_fences(content).splitlines()
    name = filepath.name

    # -----------------------------------------------------------------------
    # 1. Frontmatter
    # -----------------------------------------------------------------------
    if not fm_text:
        add("CRITICAL", "NO_FRONTMATTER", "Sem YAML frontmatter")
        return {"name": name, "issues": issues}

    import yaml  # importado aqui para não crashar se ausente em contextos sem yaml
    try:
        fm_data = yaml.safe_load(fm_text.strip("---\n")) or {}
    except Exception as e:
        add("CRITICAL", "BAD_FRONTMATTER", f"YAML inválido: {e}")
        return {"name": name, "issues": issues}

    for field in ("tags", "sources", "created", "updated"):
        if field not in fm_data:
            add("ERROR", "FM_MISSING_FIELD", f"Frontmatter sem campo '{field}'")
        elif field in ("tags", "sources") and not isinstance(fm_data[field], list):
            add("ERROR", "FM_BAD_TYPE", f"Campo '{field}' deve ser lista")

    # `summary:` alimenta cada entrada de wiki/index.md (ver `## Formato do
    # índice` em conventions/SKILL.md). Sem ele o índice sai sem resumo, e não
    # há outro lugar de onde um script possa tirar essa linha.
    summary = fm_data.get("summary")
    if summary is None:
        add("ERROR", "FM_NO_SUMMARY",
            "Frontmatter sem campo 'summary' — wiki/index.md sai sem resumo desta entrada")
    elif not isinstance(summary, str) or not summary.strip():
        add("ERROR", "FM_BAD_SUMMARY", "Campo 'summary' vazio ou não é texto")
    elif len(summary.strip()) > SUMMARY_MAX_CHARS:
        add("WARNING", "FM_LONG_SUMMARY",
            f"'summary' com {len(summary.strip())} caracteres "
            f"(máximo {SUMMARY_MAX_CHARS}) — é um resumo de uma linha, não um parágrafo")

    status = fm_data.get("status")
    if status is None:
        add("ERROR", "FM_NO_STATUS",
            f"Frontmatter sem campo 'status' (esperado: {sorted(VALID_STATUS)})")
    elif status not in VALID_STATUS:
        add("ERROR", "FM_BAD_STATUS",
            f"'status: {status}' inválido (esperado: {sorted(VALID_STATUS)})")

    # -----------------------------------------------------------------------
    # 2. H1 + byline
    # -----------------------------------------------------------------------
    h1_match = re.search(r"^# (.+)$", content, re.MULTILINE)
    if not h1_match:
        add("CRITICAL", "NO_H1", "Sem título H1 (# Título)")
        return {"name": name, "issues": issues}

    title = h1_match.group(1).strip()

    # encontra índice de linha do H1
    h1_idx = next(
        (i for i, l in enumerate(lines) if l.strip() == f"# {title}"), None
    )

    if h1_idx is not None:
        # espaço em branco após H1
        if h1_idx + 1 < len(lines) and lines[h1_idx + 1].strip() != "":
            add("ERROR", "NO_BLANK_AFTER_H1",
                f"Linha {h1_idx+2}: falta linha em branco entre H1 e byline")

        # byline: duas linhas de blockquote após H1 (com linha em branco no meio)
        byline_lines = []
        idx = h1_idx + 2
        while idx < len(lines) and lines[idx].strip().startswith(">"):
            byline_lines.append(lines[idx].strip())
            idx += 1

        if len(byline_lines) < 2:
            add("ERROR", "BYLINE_MISSING",
                f"Byline ausente ou incompleta ({len(byline_lines)} linha(s) de blockquote encontrada(s))")
        else:
            bl1, bl2 = byline_lines[0], byline_lines[1]

            m1 = re.match(
                r"^>\s*(Ensaio|White Paper|Brainstorm|Estudo|Análise)\s*$",
                bl1,
            )
            m2 = re.match(
                r"^>\s*Gustavo Zambrano\s*·\s*([A-Za-zÀ-ÿ]+ de \d{4})$",
                bl2,
            )

            if not m1:
                add("ERROR", "BYLINE_LINE1",
                    f"Byline linha 1 formato inválido: '{bl1}' "
                    f"(esperado: '> [Tipo]', Tipo ∈ {sorted(VALID_TYPES)})")
            if not m2:
                add("ERROR", "BYLINE_LINE2",
                    f"Byline linha 2 formato inválido: '{bl2}' "
                    "(esperado: '> Gustavo Zambrano · Mês de Ano', ex: 'Junho de 2026')")
            if "[[" in bl1 or "[[" in bl2:
                add("ERROR", "BYLINE_WIKILINK",
                    "Byline contém [[wikilinks]] — deve ser texto puro")
            if ":" in bl1 or ":" in bl2:
                add("ERROR", "BYLINE_COLON",
                    "Byline contém ':' — Obsidian interpreta como separador de bloco")

            # LaTeX chars perigosos na byline/título
            for bad_char, desc in [("&", "&"), ("%", "%"), ("#", "#")]:
                if bad_char in bl1 or bad_char in bl2:
                    add("WARNING", "BYLINE_LATEX_CHAR",
                        f"Byline contém '{bad_char}' ({desc}) — pode quebrar exportação LaTeX; use 'e'/'e'/'\\{bad_char}'")

    # LaTeX chars perigosos no title (frontmatter já é escapado pelo export, mas alertar)
    for bad_char in ("&", "%"):
        if bad_char in title:
            add("WARNING", "TITLE_LATEX_CHAR",
                f"Título H1 contém '{bad_char}' — verifique o escape no export_essay_pdf.py")

    # -----------------------------------------------------------------------
    # 3. Espaçamento de headings
    # -----------------------------------------------------------------------
    heading_spacing_errors = []
    for i, line in enumerate(lines_clean):
        if re.match(r"^#{1,6} ", line):
            # pula H1 — a regra do H1 é: linha em branco, depois byline
            if i == h1_idx:
                continue
            next_i = i + 1
            if next_i < len(lines):
                nxt = lines[next_i].strip()
                if nxt and not nxt.startswith("#"):
                    heading_spacing_errors.append(i + 1)
    if heading_spacing_errors:
        add("ERROR", "HEADING_SPACING",
            f"{len(heading_spacing_errors)} heading(s) sem linha em branco após: "
            f"linhas {heading_spacing_errors[:5]}"
            + ("..." if len(heading_spacing_errors) > 5 else ""))

    # -----------------------------------------------------------------------
    # 4. ## Sumário — presença e âncoras
    # -----------------------------------------------------------------------
    if "## Sumário" not in content:
        add("ERROR", "NO_SUMARIO", "Seção '## Sumário' ausente")
    else:
        # deve terminar com ---
        if not re.search(r"## Sumário\s*\n.*?\n---", content, re.DOTALL):
            add("ERROR", "SUMARIO_NO_HR",
                "'## Sumário' deve terminar com '---' (separador horizontal)")

        # verifica âncoras: extrai links [Texto](#ancora) do Sumário
        sum_block = re.search(
            r"## Sumário\s*\n(.*?)\n---", content, re.DOTALL
        )
        if sum_block:
            # headings reais no corpo (exceto H1, Sumário, Referências, Conexões)
            real_headings = [
                m.group(1).strip()
                for m in re.finditer(r"^#{2,6} (.+)$", content, re.MULTILINE)
                if m.group(1).strip()
                not in ("Sumário", "Referências", "Conexões")
            ]
            real_anchors = {heading_anchor(h) for h in real_headings}

            sumario_links = re.findall(r"\[([^\]]+)\]\(#([^\)]+)\)", sum_block.group(1))
            for display, anchor in sumario_links:
                if anchor not in real_anchors:
                    add("WARNING", "SUMARIO_BROKEN_ANCHOR",
                        f"Sumário link '#{anchor}' não bate com nenhum heading real "
                        f"(esperados: {sorted(real_anchors)[:4]}...)")

    # -----------------------------------------------------------------------
    # 5. ## Referências
    # -----------------------------------------------------------------------
    if not re.search(r"^## Referências$", content, re.MULTILINE):
        variants = [
            (r"^## Referências Bibliográficas", "usa '## Referências Bibliográficas'"),
            (r"^### Referências",               "usa ### em vez de ##"),
            (r"^# Referências",                 "usa # (H1) em vez de ##"),
        ]
        msg = "Seção '## Referências' ausente"
        for pat, desc in variants:
            if re.search(pat, content, re.MULTILINE):
                msg = f"Referências mal formatada: {desc} — use exatamente '## Referências'"
                break
        add("ERROR", "NO_REFERENCIAS", msg)
    else:
        ref_match = re.search(
            r"^## Referências$\n(.*?)(?=^## |\Z)", content, re.MULTILINE | re.DOTALL
        )
        ref_block = ref_match.group(1) if ref_match else ""
        ref_entries = re.findall(r"^\[\d+\].*$", ref_block, re.MULTILINE)

        # 5a. Referências vazia mas corpo tem links externos substanciais —
        # sintoma real: essay inteiro sem bibliografia apesar de citar fontes.
        body_before_ref = content.split("## Referências")[0]
        body_ext_links = re.findall(r"\[([^\]]+)\]\((https?://[^\)]+)\)", body_before_ref)
        if not ref_entries and len(body_ext_links) >= 5:
            add("ERROR", "EMPTY_REFERENCIAS",
                f"'## Referências' está vazia, mas o corpo tem {len(body_ext_links)} "
                f"link(s) externo(s) — bibliografia provavelmente nunca foi construída")

        # 5b. Nome de autor em **negrito** — convenção usa só itálico no título,
        # autor em texto normal (ex.: bug visto em metodos-matematicos-*.md).
        bold_entries = [e for e in ref_entries if "**" in e]
        if bold_entries:
            add("WARNING", "REF_BOLD_AUTHOR",
                f"{len(bold_entries)} entrada(s) em '## Referências' com **negrito** "
                f"— convenção não usa negrito, só itálico no título: "
                f"{[e[:40] for e in bold_entries[:3]]}")

        # 5c. Itálico envolvendo "Autor (Ano)" inteiro em vez do título real —
        # sintoma de título nunca preenchido (bug visto em psicometria-*.md,
        # entradas [11] e [18]: "*Haworth, C. M. A. et al. (2010)*.").
        author_as_title = re.compile(
            r"\*[A-ZÀ-Ú][a-zà-úãõçêé]+(?:,|\s&|\set al\.)[^*]{0,60}\(\d{4}\)[^*]*\*"
        )
        title_bug_entries = [e for e in ref_entries if author_as_title.search(e)]
        if title_bug_entries:
            add("ERROR", "REF_TITLE_IS_AUTHOR",
                f"{len(title_bug_entries)} entrada(s) com 'Autor (Ano)' dentro do "
                f"itálico — ou o título real nunca foi preenchido (itálico = só "
                f"autor+ano), ou autor/ano foram incorretamente colados dentro do "
                f"itálico do título. Confira manualmente (WebFetch/DOI) antes de "
                f"aceitar: {[e[:50] for e in title_bug_entries[:3]]}")

        # 5d-bis. Título com " — Autor (Ano)" colado dentro do próprio itálico —
        # variante do mesmo bug: o título real está lá, mas autor/ano foram
        # grudados no fim do span itálico em vez de ficarem fora (bug visto em
        # etica-moralidade-*.md e mente-aumentada.md, ex.: "*Being No One —
        # Thomas Metzinger (2003)*", "*W.D. Hamilton — Inclusive Fitness*").
        embedded_author = re.compile(
            r"\*[^*]+ — [A-ZÀ-Ú][\wÀ-ú.]*(?: [A-ZÀ-Ú][\wÀ-ú.]*){0,3}(?: \(\d{4}\))?\*"
        )
        embedded_entries = [e for e in ref_entries if embedded_author.search(e)]
        if embedded_entries:
            add("WARNING", "REF_EMBEDDED_AUTHOR_IN_TITLE",
                f"{len(embedded_entries)} entrada(s) parecem ter autor/ano ou "
                f"subtítulo inventado colado dentro do itálico do título (padrão "
                f"'*Título — Nome (Ano)*') — confirme o título real da página/obra "
                f"(WebFetch) e mova autor/ano para fora do itálico: "
                f"{[e[:60] for e in embedded_entries[:3]]}")

        # 5d. Entrada com itálico só do container (periódico/site) e nenhum
        # título aparente antes dele — ex.: "Schmidt, F. L. (1998). *Psychological
        # Bulletin*." sem o título real do artigo.
        container_only = re.compile(
            r"^\[\d+\]\s+[A-ZÀ-Ú][a-zà-úãõçêé]+.{0,80}\(\d{4}\)\.\s*\*[^*]+\*\.\s*(?:doi|https?|$)",
        )
        for e in ref_entries:
            if container_only.search(e) and not author_as_title.search(e):
                add("WARNING", "REF_MISSING_TITLE",
                    f"Entrada sem título aparente, só autor+ano+container: {e[:70]}")

    # -----------------------------------------------------------------------
    # 6. ## Conexões — presente e última H2
    # -----------------------------------------------------------------------
    if not re.search(r"^## Conexões$", content, re.MULTILINE):
        add("ERROR", "NO_CONEXOES", "Seção '## Conexões' ausente")
    else:
        after_conex = content.split("## Conexões")[-1]
        if re.search(r"^## [^#]", after_conex, re.MULTILINE):
            add("ERROR", "CONEXOES_NOT_LAST",
                "'## Conexões' não é a última seção H2 do essay")

    # -----------------------------------------------------------------------
    # 7. Wikilinks fora de Conexões
    # -----------------------------------------------------------------------
    # Sem as fences: `np.array([[1.0, 0.0], ...])` num exemplo de código não é
    # wikilink, é lista aninhada.
    body_before_conex = strip_fences(content).split("## Conexões")[0]
    wikilinks_in_body = re.findall(r"\[\[([^\]]+)\]\]", body_before_conex)
    if wikilinks_in_body:
        add("ERROR", "WIKILINKS_IN_BODY",
            f"{len(wikilinks_in_body)} [[wikilink(s)]] fora de Conexões: "
            f"{wikilinks_in_body[:3]}")

    # -----------------------------------------------------------------------
    # 8. Links externos (mínimo 10)
    # -----------------------------------------------------------------------
    ext_links = re.findall(r"\[([^\]]+)\]\((https?://[^\)]+)\)", content)
    if len(ext_links) < 10:
        add("WARNING", "FEW_EXT_LINKS",
            f"Apenas {len(ext_links)} link(s) externos (mínimo recomendado: 10)")

    # -----------------------------------------------------------------------
    # 9. Aspas ASCII suspeitas na prosa
    #    Regra: aspas retas (") e apóstrofos retos (') em prosa podem ser
    #    intencionais em código/URLs mas são suspeitas em texto corrido.
    #    Reportamos contagem para o revisor avaliar — não é erro, é WARNING.
    # -----------------------------------------------------------------------
    # trabalhar só no corpo (sem frontmatter, sem código)
    prose_body = re.sub(r"^---.*?---\n", "", content, count=1, flags=re.DOTALL)
    prose_body = strip_fences(prose_body)
    # remove URLs e inline code
    prose_body = re.sub(r"`[^`]+`", "", prose_body)
    prose_body = re.sub(r"\[[^\]]+\]\([^\)]+\)", "", prose_body)

    ascii_double = len(re.findall(r'"', prose_body))
    ascii_single = len(re.findall(r"'", prose_body))
    # só reportar se houver quantidade relevante (evita falsos positivos)
    if ascii_double > 3:
        add("WARNING", "ASCII_QUOTES",
            f"{ascii_double} aspas duplas ASCII (\") na prosa — considere aspas tipográficas "
            "(\u201c...\u201d) ou verifique se não quebram LaTeX")
    if ascii_single > 5:
        add("INFO", "ASCII_APOSTROPHES",
            f"{ascii_single} apóstrofos/aspas simples ASCII (') na prosa — ok se for contrações, "
            "verifique se intencional")

    # -----------------------------------------------------------------------
    # 10. Espaços duplos
    # -----------------------------------------------------------------------
    double_spaces = []
    for i, line in enumerate(lines_clean):
        if "  " in line and not line.startswith("```") and not line.startswith("|"):
            double_spaces.append(i + 1)
    if double_spaces:
        add("WARNING", "DOUBLE_SPACES",
            f"Espaços duplos em {len(double_spaces)} linha(s): {double_spaces[:5]}"
            + ("..." if len(double_spaces) > 5 else ""))

    # -----------------------------------------------------------------------
    # 11. Linhas em branco excessivas (≥3 consecutivas)
    # -----------------------------------------------------------------------
    blank_runs = re.findall(r"\n{4,}", content)  # 4+ newlines = ≥3 linhas em branco
    if blank_runs:
        add("WARNING", "EXCESS_BLANK_LINES",
            f"{len(blank_runs)} trecho(s) com ≥3 linhas em branco consecutivas")

    # -----------------------------------------------------------------------
    # 12. Travessões (—) — max 2 por essay
    # -----------------------------------------------------------------------
    # não conta · da byline nem — em display text de wikilinks/índice
    em_dash_count = content.count("—")
    # subtrai os da byline (·) — não são —, então não impacta
    # subtrai os em wikilinks [[X|Y — Z]] (convenção de índice)
    em_dashes_in_wikilinks = len(re.findall(r"\[\[[^\]]+—[^\]]+\]\]", content))
    effective_dashes = em_dash_count - em_dashes_in_wikilinks
    if effective_dashes > 2:
        add("WARNING", "TOO_MANY_EM_DASHES",
            f"{effective_dashes} travessão(ões) (—) no essay "
            "(máximo recomendado: 2; prefira vírgula, dois-pontos ou parênteses)")

    # -----------------------------------------------------------------------
    # 13. Bullets no corpo argumentativo
    #     Bullets são permitidos só em Sumário, Referências e tabelas.
    # -----------------------------------------------------------------------
    # Remove Sumário, Referências e Conexões para avaliar apenas o corpo
    body_for_bullets = content
    for section in ("## Sumário", "## Referências", "## Conexões"):
        parts_s = body_for_bullets.split(section, 1)
        if len(parts_s) == 2:
            # corta tudo a partir da próxima seção H2
            next_section = re.search(r"\n## ", parts_s[1])
            if next_section:
                body_for_bullets = (
                    parts_s[0] + parts_s[1][next_section.start():]
                )
            else:
                body_for_bullets = parts_s[0]

    body_for_bullets_clean = strip_fences(body_for_bullets)
    bullet_lines = [
        (i + 1, l)
        for i, l in enumerate(body_for_bullets_clean.splitlines())
        if re.match(r"^\s*[-*]\s+\S", l)
    ]
    if bullet_lines:
        add("WARNING", "BULLETS_IN_BODY",
            f"{len(bullet_lines)} linha(s) com bullet fora de Sumário/Referências — "
            f"use prosa argumentativa: linhas {[b[0] for b in bullet_lines[:5]]}"
            + ("..." if len(bullet_lines) > 5 else ""))

    # -----------------------------------------------------------------------
    # 14. HTML residual
    # -----------------------------------------------------------------------
    html_tags = re.findall(
        r"</?(?:div|span|p|br|hr|img|a|h[1-6]|ul|ol|li|table|tr|td|th|"
        r"thead|tbody|iframe|button|input|label|form|select|option)"
        r"(?:\s|/|>)[^>]*>|class=|style=",
        strip_fences(content),
        re.IGNORECASE,
    )
    if html_tags:
        add("ERROR", "HTML_RESIDUAL",
            f"{len(html_tags)} tag(s) HTML residuais: {html_tags[:3]}")

    # -----------------------------------------------------------------------
    # 15. Símbolos residuais
    # -----------------------------------------------------------------------
    RESIDUAL_SYMS = [
        ("◆",       "diamond ◆"),
        ("\ufffd",  "replacement char \ufffd"),
        ("\u00a0",  "non-breaking space (NBSP)"),
        ("&nbsp;",  "&nbsp;"),
        ("&amp;",   "&amp;"),
    ]
    for sym, desc in RESIDUAL_SYMS:
        occurrences = [i + 1 for i, l in enumerate(lines_clean) if sym in l]
        if occurrences:
            add("ERROR", "RESIDUAL_SYMBOL",
                f"Símbolo residual '{desc}' em {len(occurrences)} linha(s): {occurrences[:5]}")

    # -----------------------------------------------------------------------
    # 16. Idioma — parágrafos possivelmente em inglês
    # -----------------------------------------------------------------------
    body_no_fm = re.sub(r"^---.*?---\n", "", content, count=1, flags=re.DOTALL)
    # `## Referências` fica de fora: título de obra estrangeira é para ficar no
    # original, não para ser traduzido, e a bibliografia inteira disparava o
    # aviso de "parágrafo não traduzido" por isso.
    body_no_refs = re.split(r"(?m)^## Referências\s*$", body_no_fm)[0]
    body_no_code = re.sub(r"```.*?```", "", body_no_refs, flags=re.DOTALL)
    body_no_urls = re.sub(r"\[([^\]]*)\]\([^\)]*\)", r"\1", body_no_code)
    for para in body_no_urls.split("\n\n"):
        words = re.findall(r"[A-Za-zÀ-ÿ']+", para.lower())
        if len(words) < 12:
            continue
        en_hits = sum(1 for w in words if w in ENGLISH_ONLY_WORDS)
        pt_hits = sum(1 for w in words if w in PORTUGUESE_ONLY_WORDS)
        if en_hits >= 3 and en_hits > pt_hits * 2:
            snippet = para.strip().replace("\n", " ")[:90]
            add("WARNING", "ENGLISH_PARAGRAPH",
                f"Parágrafo possivelmente em inglês: \"{snippet}...\"")

    # -----------------------------------------------------------------------
    # 17. Loose chapter labels (ex: "01 — Introdução" como linha solta)
    # -----------------------------------------------------------------------
    for i, line in enumerate(lines_clean):
        if re.match(r"^\d+\s*[-—.]\s*\w+", line.strip()):
            add("WARNING", "LOOSE_CHAPTER_LABEL",
                f"Possível label de capítulo solto (linha {i+1}): '{line.strip()}'")

    return {"name": name, "issues": issues}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser():
    p = argparse.ArgumentParser(
        description="Verifica formatação de essays conforme conventions/SKILL.md"
    )
    p.add_argument(
        "--file", "-f",
        metavar="SLUG",
        help="Checar apenas este essay (slug, nome do arquivo, ou caminho completo)",
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="Saída em JSON (para o skill /format parsear)",
    )
    return p


def resolve_essay(slug: str) -> Path:
    # tenta como caminho direto
    p = Path(slug)
    if p.exists():
        return p.resolve()
    # tenta como nome de arquivo dentro de ESSAYS_DIR
    for ext in ("", ".md"):
        candidate = ESSAYS_DIR / (slug + ext)
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        f"Essay '{slug}' não encontrado em {ESSAYS_DIR} nem como caminho direto"
    )


def main():
    args = build_parser().parse_args()

    if args.file:
        try:
            target = resolve_essay(args.file)
            essay_paths = [target]
        except FileNotFoundError as e:
            print(f"ERRO: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        essay_paths = sorted(ESSAYS_DIR.glob("*.md"))
        if not essay_paths:
            print(f"Nenhum essay encontrado em {ESSAYS_DIR}", file=sys.stderr)
            sys.exit(0)

    results = [check_essay(p) for p in essay_paths]

    if args.json:
        output = {"essays": results}
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    # ---- saída human-readable ----
    severity_order = {"CRITICAL": 0, "ERROR": 1, "WARNING": 2, "INFO": 3}
    ICONS = {"CRITICAL": "🔴", "ERROR": "❌", "WARNING": "⚠️ ", "INFO": "ℹ️ "}

    total_issues = 0
    clean = 0

    for result in results:
        name = result["name"]
        issues = result["issues"]
        if not issues:
            print(f"✅ {name}")
            clean += 1
            continue
        # ordena por severidade
        issues_sorted = sorted(issues, key=lambda x: severity_order.get(x["severity"], 9))
        print(f"\n{'─'*60}")
        print(f"📄 {name}")
        for issue in issues_sorted:
            icon = ICONS.get(issue["severity"], "•")
            print(f"   {icon} [{issue['code']}] {issue['message']}")
        total_issues += len(issues)

    print(f"\n{'='*60}")
    total = len(results)
    print(
        f"Resultado: {clean}/{total} essay(s) limpo(s), "
        f"{total_issues} issue(s) no total"
    )


if __name__ == "__main__":
    main()
