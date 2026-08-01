#!/usr/bin/env python3
"""
check_wiki.py — Lint estrutural completo da wiki (ou de um único essay).

Complementa check_format.py (regras de formatação de prosa/byline/tipografia)
e check_references.py (formato da seção ## Referências): aqui o foco é
integridade estrutural e consistência entre arquivos, não formatação dentro
de um único essay. Cobre, num relatório único:

    - Frontmatter YAML de essays/concepts/entities/insights: campos
      obrigatórios, status válido
    - H1 + byline: presença, formato, blank line entre título e byline
    - ## Sumário, ## Referências, ## Conexões: presença, ## Conexões deve
      ser a última seção
    - Wikilinks fora de ## Conexões (só é permitido inline em concepts/entities)
    - Wikilinks mortos (target sem página correspondente) e órfãos
    - Mínimo de links externos no corpo
    - Blank line após heading, símbolos residuais, HTML residual
    - wiki/index.md: título correto, links mortos, essays faltando no índice
    - wiki/sources/manifest.md: entradas batendo com os arquivos em disco,
      subpastas do vocabulário controlado, Tags: preenchido
    - plan/plano.md: vocabulário fechado de seções e de Status
    - insights/*.md: campo maturidade válido, ao menos um wikilink em Conexões

Escreve o relatório completo em output/comprehensive_lint_output.txt e
imprime um resumo (contagem de ERROR/WARNING) no console. Nota: sempre
sai com exit code 0 (exceto se --essay apontar para um arquivo inexistente,
sys.exit(1)) — o sinal de "há problemas" é o resumo impresso e o conteúdo
do relatório, não o exit code.

Usage:
    python scripts/check_wiki.py                  # lint do corpus inteiro
    python scripts/check_wiki.py --essay SLUG      # lint só deste essay (pula
                                                    # seções que são inerentemente
                                                    # de corpus inteiro: índice,
                                                    # manifesto, plano, órfãos)
"""

import os
import re
import sys
import yaml
import argparse
import subprocess
from pathlib import Path

import console_encoding  # noqa: F401  (UTF-8 no console; ver o módulo)

ROOT_DIR = Path(__file__).resolve().parent.parent
WIKI_ROOT = ROOT_DIR / "wiki"
ESSAYS_DIR = WIKI_ROOT / "essays"
CONCEPTS_DIR = WIKI_ROOT / "concepts"
ENTITIES_DIR = WIKI_ROOT / "entities"
SOURCES_DIR = WIKI_ROOT / "sources"
INSIGHTS_DIR = WIKI_ROOT / "insights"

# Categories/dirs to lint (sources excluded — they are original immutable documents)
DIRS = {
    "essays": ESSAYS_DIR,
    "concepts": CONCEPTS_DIR,
    "entities": ENTITIES_DIR,
    "insights": INSIGHTS_DIR
}


def build_parser():
    p = argparse.ArgumentParser(
        description="Lint completo da wiki (corpus inteiro) ou de um único essay."
    )
    p.add_argument(
        "--essay", "-e",
        metavar="SLUG",
        help=(
            "Checa apenas este essay (slug, nome do arquivo, ou caminho completo), "
            "em vez do corpus inteiro. As seções que são inerentemente de corpus "
            "inteiro (índice, manifesto, plano, tags, órfãos) são puladas "
            "nesse modo, exceto a checagem de wikilinks mortos, que é filtrada "
            "para mostrar apenas links originados neste essay."
        ),
    )
    return p


def resolve_essay(slug):
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

def strip_fences(text):
    """Esvazia o interior de blocos ```...```, preservando a contagem de linhas.

    As regras de prosa (heading, label de capítulo, símbolo residual, HTML) não
    valem dentro de código: um comentário Python `# nota` na coluna zero não é
    heading, e `<div` num exemplo de template não é HTML residual do essay.
    Mesmo tratamento de `check_format.py` e `check_references.py`.
    """
    out, in_fence = [], False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            out.append("")
        else:
            out.append("" if in_fence else line)
    return "\n".join(out)


def load_file_content(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return f.read()

def get_h1(content):
    match = re.search(r"(?m)^# (.+)", content)
    if match:
        return match.group(1).strip()
    return None

# Heurística de idioma: palavras funcionais que só existem em inglês vs. em português.
# Não é um detector de idioma robusto, é um sinal barato para pegar parágrafos/páginas
# esquecidos em inglês (comum ao colar de uma fonte em raw/ sem terminar a tradução).
ENGLISH_ONLY_WORDS = {
    "the", "and", "with", "this", "that", "these", "those", "from", "have",
    "has", "been", "were", "was", "which", "their", "there", "where", "when",
    "because", "however", "therefore", "although", "between", "through",
    "into", "onto", "about", "should", "would", "could", "cannot", "doesn't",
    "isn't", "aren't", "wasn't", "weren't", "don't", "does", "did", "than",
}
PORTUGUESE_ONLY_WORDS = {
    "não", "com", "para", "uma", "isso", "está", "então", "porque", "entre",
    "sobre", "quando", "onde", "porém", "contudo", "embora", "através",
    "seus", "suas", "então", "já", "também", "mais", "menos", "muito",
}

def check_language_ptbr(content, rel_path):
    """Sinaliza parágrafos que parecem estar em inglês (não traduzidos)."""
    issues = []
    # Ignora frontmatter, blocos de código e URLs para não gerar falso positivo.
    body = re.sub(r"^---.*?---", "", content, count=1, flags=re.DOTALL)
    body = re.sub(r"```.*?```", "", body, flags=re.DOTALL)
    body = re.sub(r"\[([^\]]*)\]\([^\)]*\)", r"\1", body)  # mantém o texto-âncora, remove a URL
    paragraphs = [p for p in body.split("\n\n") if len(p.split()) >= 12]
    for p in paragraphs:
        words = re.findall(r"[A-Za-zÀ-ÿ']+", p.lower())
        if not words:
            continue
        en_hits = sum(1 for w in words if w in ENGLISH_ONLY_WORDS)
        pt_hits = sum(1 for w in words if w in PORTUGUESE_ONLY_WORDS)
        # Só sinaliza quando o sinal de inglês é claramente maior que o de português
        # e há massa suficiente de palavras-função para não ser ruído de um termo técnico solto.
        if en_hits >= 3 and en_hits > pt_hits * 2:
            snippet = p.strip().replace("\n", " ")[:100]
            issues.append(
                f"WARNING: {rel_path} parágrafo possivelmente não traduzido para PT-BR: \"{snippet}...\""
            )
    return issues

def main():
    args = build_parser().parse_args()
    target_essay = None
    if args.essay:
        try:
            target_essay = resolve_essay(args.essay)
        except FileNotFoundError as e:
            print(f"ERROR: {e}")
            sys.exit(1)

    report = []
    if target_essay:
        report.append(f"Modo: --essay {target_essay.name} (seções de corpus inteiro puladas — ver nota em cada uma).")
    
    # 1. Build map of all files and their titles (H1)
    title_to_file = {}
    file_to_title = {}
    essay_titles = set()
    all_titles = set()
    
    for category, dir_path in DIRS.items():
        if not dir_path.exists():
            continue
        for file in dir_path.glob("*.md"):
            rel_path = f"{category}/{file.name}"
            content = load_file_content(file)
            title = get_h1(content)
            if title:
                title_to_file[title] = rel_path
                file_to_title[rel_path] = title
                all_titles.add(title)
                if category == "essays":
                    essay_titles.add(title)
            else:
                report.append(f"CRITICAL: {rel_path} has NO H1 TITLE (# Title)!")

    report.append(f"Loaded {len(title_to_file)} page titles across the wiki.")
    
    # 2. Check each essay
    report.append("\n=== DETAILED ESSAY LINT ===")
    essays_count = 0
    essays_to_check = [target_essay] if target_essay else sorted(ESSAYS_DIR.glob("*.md"))
    for file in essays_to_check:
        essays_count += 1
        rel_path = f"essays/{file.name}"
        content = load_file_content(file)
        lines = content.splitlines()
        lines_clean = strip_fences(content).splitlines()
        
        # Check Frontmatter
        has_fm = content.startswith("---")
        fm_data = {}
        if has_fm:
            parts = content.split("---", 2)
            if len(parts) >= 3:
                try:
                    fm_data = yaml.safe_load(parts[1]) or {}
                except Exception as e:
                    report.append(f"ERROR: {rel_path} has invalid YAML frontmatter: {e}")
            else:
                report.append(f"ERROR: {rel_path} has malformed frontmatter block.")
        else:
            report.append(f"ERROR: {rel_path} has NO YAML frontmatter.")
            
        # Verify required frontmatter fields
        for field in ["tags", "sources", "created", "updated"]:
            if field not in fm_data:
                report.append(f"ERROR: {rel_path} frontmatter missing field: '{field}'")
            elif field in ["tags", "sources"] and not isinstance(fm_data[field], list):
                report.append(f"ERROR: {rel_path} frontmatter field '{field}' must be a list (got {type(fm_data[field])})")

        # Verify essay status field (controlled vocabulary, essays only)
        VALID_STATUS = {"draft", "maduro", "finalizado"}
        status = fm_data.get("status")
        if status is None:
            report.append(f"ERROR: {rel_path} frontmatter missing field: 'status' (expected one of {sorted(VALID_STATUS)})")
        elif status not in VALID_STATUS:
            report.append(f"ERROR: {rel_path} frontmatter field 'status' has invalid value '{status}' (expected one of {sorted(VALID_STATUS)})")

        # Check H1 Title and Byline
        title = get_h1(content)
        if not title:
            continue
            
        # Byline check: must be two blockquote lines immediately below H1 (with one blank line in between)
        h1_line_idx = -1
        for idx, line in enumerate(lines):
            if line.strip() == f"# {title}":
                h1_line_idx = idx
                break
                
        if h1_line_idx != -1:
            # Check for a blank line after H1
            if h1_line_idx + 1 < len(lines) and lines[h1_line_idx + 1].strip() != "":
                report.append(f"ERROR: {rel_path} must have a blank line between H1 title and byline.")
            
            # Check byline blockquotes
            byline_lines = []
            idx = h1_line_idx + 2
            while idx < len(lines) and lines[idx].strip().startswith(">"):
                byline_lines.append(lines[idx].strip())
                idx += 1
                
            if len(byline_lines) != 2:
                report.append(f"ERROR: {rel_path} must have a standardized byline with exactly 2 blockquote lines (found {len(byline_lines)}).")
            else:
                line1, line2 = byline_lines[0], byline_lines[1]
                # Line 1 format: > Tipo
                # Line 2 format: > Gustavo Zambrano · Mês de Ano
                # Tipo is: Ensaio, White Paper, Brainstorm, Estudo ou Análise
                match1 = re.match(r"^>\s*(Ensaio|White Paper|Brainstorm|Estudo|Análise)\s*$", line1)
                match2 = re.match(r"^>\s*Gustavo Zambrano\s*·\s*([A-Za-z]+ de \d{4})$", line2)
                
                if not match1:
                    report.append(f"ERROR: {rel_path} byline line 1 invalid format: '{line1}'. Expected '> [Tipo]' where Tipo is Ensaio|White Paper|Brainstorm|Estudo|Análise")
                if not match2:
                    report.append(f"ERROR: {rel_path} byline line 2 invalid format: '{line2}'. Expected '> Gustavo Zambrano · [Mês de Ano]' (e.g. '> Gustavo Zambrano · Junho de 2026')")
                    
                # No wikilinks in byline
                if "[[" in line1 or "[[" in line2:
                    report.append(f"ERROR: {rel_path} byline contains wikilinks [[...]]. Must be plain text.")
                # No colons in byline
                if ":" in line1 or ":" in line2:
                    report.append(f"ERROR: {rel_path} byline contains colons ':'. Obsidian interprets as block separator.")
                    
        # Check ## Sumário
        has_sumario = "## Sumário" in content
        if not has_sumario:
            report.append(f"ERROR: {rel_path} is missing '## Sumário' section.")
        else:
            # Check if it has a horizontal rule '---' or similar right after the sumario list
            sum_match = re.search(r"## Sumário\s*\n(.*?)\n---", content, re.DOTALL)
            if not sum_match:
                report.append(f"ERROR: {rel_path} Sumário section must end with '---' separator.")
                
        # Check ## Referências
        has_ref = re.search(r"^## Referências$", content, re.MULTILINE)
        if not has_ref:
            report.append(f"ERROR: {rel_path} is missing '## Referências' section (must be exactly H2 and named '## Referências').")
            
        # Check ## Conexões as last section
        has_conex = re.search(r"^## Conexões$", content, re.MULTILINE)
        if not has_conex:
            report.append(f"ERROR: {rel_path} is missing '## Conexões' section.")
        else:
            # Check if it is the last major H2 section
            content_after_conex = content.split("## Conexões")[-1]
            if re.search(r"(?m)^## [^#]", content_after_conex):
                report.append(f"ERROR: {rel_path} '## Conexões' must be the last section in the essay.")
                
        # Idioma: wiki inteira deve ser PT-BR (ver AGENTS.md, Regras Gerais item 8)
        report.extend(check_language_ptbr(content, rel_path))

        # External links count (min 10)
        ext_links = re.findall(r"\[([^\]]+)\]\((https?://[^\)]+)\)", content)
        # Filter out links in Referências or Conexões? The rule says "mínimo 10 links externos por essay".
        if len(ext_links) < 10:
            report.append(f"ERROR: {rel_path} has too few external links ({len(ext_links)} found, minimum is 10).")
            
        # Wikilinks outside of Conexões
        # Let's split content by "## Conexões" to look at body before Conexões
        parts = content.split("## Conexões")
        # Sem as fences: `np.array([[1.0, 0.0], ...])` num exemplo de código não
        # é wikilink, é lista aninhada.
        body_before_conex = strip_fences(parts[0])
        wikilinks_in_body = re.findall(r"\[\[([^\]]+)\]\]", body_before_conex)
        if wikilinks_in_body:
            report.append(f"ERROR: {rel_path} contains {len(wikilinks_in_body)} wikilinks inline in the body. Only external links are allowed in the body. Found: {wikilinks_in_body[:5]}...")
            
        # Spacing: blank line between every heading and text following it
        for idx, line in enumerate(lines_clean):
            if re.match(r"^#{1,6} ", line):
                if idx + 1 < len(lines) and lines[idx+1].strip() != "" and not lines[idx+1].strip().startswith("#"):
                    # Check if byline or sumario is exception. Byline has blank line before it. Sumario has list.
                    # Wait, if heading is followed immediately by non-blank, it's a violation.
                    # Exception: if it's the H1 followed by byline blockquote? No, rule 5: "byline padronizada com DUAS linhas de blockquote logo abaixo do # Título, com uma linha vazia entre o título e a byline"
                    # So H1 is followed by blank line, then byline.
                    # What about other headings? "Linha em branco obrigatória entre todo heading e o texto seguinte."
                    # Let's log it.
                    report.append(f"ERROR: {rel_path} heading '{line}' on line {idx+1} is not followed by a blank line.")

        # Loose chapter labels (e.g. "01 — Introdução" or "01. Introdução")
        for idx, line in enumerate(lines_clean):
            if re.match(r"^\d+\s*[-—.]\s*\w+", line.strip()):
                report.append(f"WARNING: {rel_path} has possible loose chapter label on line {idx+1}: '{line}'")
                
        # Residual symbols
        residual_symbols = ["◆", "\ufffd", " ", "&nbsp;", "&amp;"] # note the second space is NBSP in some files
        for idx, line in enumerate(lines_clean):
            for sym in residual_symbols:
                if sym in line:
                    report.append(f"ERROR: {rel_path} contains residual symbol '{sym}' on line {idx+1}: '{line.strip()}'")
                    
        # Residual HTML
        # Looking for things like <div, <span, <p, </div, etc.
        html_matches = re.findall(r"</?(?:div|span|p|br|hr|img|a|h[1-6]|ul|ol|li|table|tr|td|th|thead|tbody|iframe|button|input|label|form|select|option)(?:\s|/|>)[^>]*>|class=|style=", strip_fences(content), re.IGNORECASE)
        # Allow alerts like > [!NOTE] but block standard html tags
        for match in html_matches:
            report.append(f"ERROR: {rel_path} contains residual HTML tag/attribute: '{match}'")
                
        # Blockquotes checking:
        # Blockquotes can only be: byline, quotes, or special callouts.
        # Check all blockquotes. If a blockquote is not one of these, report.
        for idx, line in enumerate(lines):
            if line.strip().startswith(">"):
                # Check if byline (lines h1+2, h1+3)
                is_byline = (idx == h1_line_idx + 2 or idx == h1_line_idx + 3)
                is_callout = re.match(r"^>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]", line)
                # If it's normal text blockquote without a clear attribution or quotation marks, issue warning/error.
                # Since this is harder to automate perfectly, we just report if it doesn't look like byline or callout or quote
                # Simple heuristic: if it contains normal prose without quotation marks, or is very long.
                # Let's skip strict check on this unless it's obviously bad, but let's check for standard patterns.

    # 3. Check concepts, entities, sources, insights frontmatter and H1
    report.append("\n=== SUPPORT PAGES LINT (CONCEPTS, ENTITIES, INSIGHTS) ===")
    if target_essay:
        report.append("(pulado — modo --essay: só faz sentido no corpus inteiro.)")
    else:
        for category in ["concepts", "entities", "insights"]:
            dir_path = DIRS[category]
            if not dir_path.exists():
                continue
            for file in dir_path.glob("*.md"):
                rel_path = f"{category}/{file.name}"
                content = load_file_content(file)
                lines = content.splitlines()
                lines_clean = strip_fences(content).splitlines()
            
                # Check Frontmatter
                has_fm = content.startswith("---")
                fm_data = {}
                if has_fm:
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        try:
                            fm_data = yaml.safe_load(parts[1]) or {}
                        except Exception as e:
                            report.append(f"ERROR: {rel_path} has invalid YAML frontmatter: {e}")
                    else:
                        report.append(f"ERROR: {rel_path} has malformed frontmatter block.")
                else:
                    report.append(f"ERROR: {rel_path} has NO YAML frontmatter.")
                
                # Verify required frontmatter fields
                for field in ["tags", "sources", "created", "updated"]:
                    if field not in fm_data:
                        # sources is not strictly required for sources themselves? But GEMINI.md says:
                        # "Every wiki page MUST include YAML frontmatter with tags, sources, created, and updated fields."
                        report.append(f"ERROR: {rel_path} frontmatter missing field: '{field}'")
            
                # Idioma: wiki inteira deve ser PT-BR (ver AGENTS.md, Regras Gerais item 8)
                report.extend(check_language_ptbr(content, rel_path))

                # Check for spacing between headings and text
                for idx, line in enumerate(lines_clean):
                    if re.match(r"^#{1,6} ", line):
                        if idx + 1 < len(lines) and lines[idx+1].strip() != "" and not lines[idx+1].strip().startswith("#"):
                            report.append(f"ERROR: {rel_path} heading '{line}' on line {idx+1} is not followed by a blank line.")
                        
                # Residual symbols/HTML
                for idx, line in enumerate(lines_clean):
                    for sym in ["◆", "\ufffd", " ", "&nbsp;", "&amp;"]:
                        if sym in line:
                            report.append(f"ERROR: {rel_path} contains residual symbol '{sym}' on line {idx+1}: '{line.strip()}'")
                    html_matches = re.findall(r"</?(?:div|span|p|br|hr|img|a|h[1-6]|ul|ol|li|table|tr|td|th|thead|tbody|iframe|button|input|label|form|select|option)(?:\s|/|>)[^>]*>|class=|style=", line, re.IGNORECASE)
                    for match in html_matches:
                        report.append(f"ERROR: {rel_path} contains residual HTML tag/attribute: '{match}'")

    # 4. Check for dead wikilinks
    report.append("\n=== DEAD WIKILINKS ===")
    dead_links = {}
    if target_essay:
        dead_link_scope = {"essays": [target_essay]}
    else:
        dead_link_scope = {cat: sorted(d.glob("*.md")) for cat, d in DIRS.items() if d.exists()}
    for category, files in dead_link_scope.items():
        for file in files:
            content = strip_fences(load_file_content(file))
            # Find all [[wikilink]] or [[wikilink|display]]
            links = re.findall(r"\[\[([^\]]+)\]\]", content)
            for raw_link in links:
                # strip target and display text
                target = raw_link.split("|")[0].strip()
                display = raw_link.split("|")[1].strip() if "|" in raw_link else target
                
                # Check if target starts with #
                if target.startswith("#"):
                    continue
                
                # Check Obsidian compatibility: no colons in display text
                if ":" in display:
                    report.append(f"ERROR: Wikilink display text in {category}/{file.name} has a colon: '{raw_link}'")
                
                # Verify if target is in our titles
                if target not in all_titles:
                    if target not in dead_links:
                        dead_links[target] = []
                    dead_links[target].append(f"{category}/{file.name}")
                    
    for target, sources in sorted(dead_links.items()):
        report.append(f"DEAD WIKILINK: '{target}' referenced in: {', '.join(set(sources))}")
        
    # 5. Check for orphan concepts/entities (not linked by any essay)
    report.append("\n=== ORPHAN PAGES ===")
    if target_essay:
        report.append("(pulado — modo --essay: precisa do corpus inteiro para saber o que é órfão.)")
    else:
        essay_content = ""
        for file in ESSAYS_DIR.glob("*.md"):
            essay_content += load_file_content(file)

        for category in ["concepts", "entities"]:
            dir_path = DIRS[category]
            if not dir_path.exists():
                continue
            for file in dir_path.glob("*.md"):
                content = load_file_content(file)
                title = get_h1(content)
                if title:
                    # Check if [[Title]] is in essay_content (with or without display text)
                    pattern = re.compile(r"\[\[" + re.escape(title) + r"(\|[^\]]+)?\]\]")
                    if not pattern.search(essay_content):
                        report.append(f"ORPHAN {category.upper()}: '{title}' ({category}/{file.name}) is not referenced by any essay!")

    # 6. Verify index.md consistency
    report.append("\n=== INDEX.MD AUDIT ===")
    index_path = WIKI_ROOT / "index.md"
    if index_path.exists():
        index_content = load_file_content(index_path)
        
        # Check title
        if get_h1(index_content) != "Índice":
            report.append("ERROR: index.md title must be '# Índice'")
            
        # Build essay stems
        essay_stems = {file.stem for file in ESSAYS_DIR.glob("*.md")}

        # index.md é artefato gerado por build_index.py: lista plana com link
        # markdown `[Título](essays/arquivo.md)`, não mais `[[wikilink]]`.
        index_links = re.findall(r"\]\(essays/([^\)]+?)\.md\)", index_content)
        for target in index_links:
            # index.md contém APENAS essays
            if target not in essay_stems:
                report.append(f"ERROR: index.md contains non-essay or dead link: '{target}'")

        # Wikilink em index.md é resíduo do formato antigo, editado à mão.
        if re.search(r"\[\[[^\]]+\]\]", index_content):
            report.append(
                "ERROR: index.md tem [[wikilinks]] — formato antigo. "
                "Rode `python scripts/build_index.py` para regenerar."
            )
                
        # Check if any actual essay is NOT in index.md
        essay_titles_to_check = {get_h1(load_file_content(target_essay))} if target_essay else sorted(essay_titles)
        for essay_title in essay_titles_to_check:
            if not essay_title or essay_title not in title_to_file:
                continue
            # Get filename for essay_title
            filename = title_to_file[essay_title].split("/")[-1]
            stem = filename.replace(".md", "")
            pattern_stem = re.compile(r"\]\(essays/" + re.escape(stem) + r"\.md\)")
            if not pattern_stem.search(index_content):
                report.append(
                    f"ERROR: Essay '{essay_title}' (essays/{filename}) não aparece em "
                    f"index.md — rode `python scripts/build_index.py` para regenerar."
                )
    else:
        report.append("ERROR: index.md does not exist!")
        
    # 7-9. Sources & manifest, plano, insights — audits de corpo inteiro
    if target_essay:
        report.append("\n=== SOURCES & MANIFEST / PLANO / INSIGHTS ===")
        report.append("(pulado — modo --essay: essas seções auditam o corpus inteiro, não um essay isolado.)")
    else:
        # 7. Sources & manifest audit (genérico: pega tudo que falta, nos dois sentidos)
        report.append("\n=== SOURCES & MANIFEST AUDIT ===")
        HANDOUTS_DIR = WIKI_ROOT / "handouts"
        manifest_path = SOURCES_DIR / "manifest.md"
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
        utility_source_folders = {"resumos"}

        if not manifest_path.exists():
            report.append("ERROR: wiki/sources/manifest.md não existe!")
            manifest_entries = {}
        else:
            manifest_content = load_file_content(manifest_path)
            # Each entry: "## [YYYY-MM-DD] filename" heading, followed by Tipo:/Tags:/Pasta:/Virou:/Verificação: lines
            entry_blocks = re.split(r"(?m)^## \[(\d{4}-\d{2}-\d{2})\]\s+(.+)$", manifest_content)
            # entry_blocks alternates: [preamble, date, filename, body, date, filename, body, ...]
            manifest_entries = {}
            for i in range(1, len(entry_blocks), 3):
                date, filename, body = entry_blocks[i], entry_blocks[i + 1], entry_blocks[i + 2]
                tipo_m = re.search(r"(?m)^Tipo:\s*(.+?)\.?$", body)
                tags_m = re.search(r"(?m)^Tags:\s*(.+?)\.?$", body)
                pasta_m = re.search(r"(?m)^Pasta:\s*(.+?)\.?$", body)
                virou_m = re.search(r"(?m)^Virou:\s*(.+?)\.?$", body)
                tags_raw = tags_m.group(1).strip() if tags_m else None
                if tags_raw and tags_raw.startswith("[") and tags_raw.endswith("]"):
                    tags_raw = tags_raw[1:-1]
                tags = [t.strip().strip('"').strip("'") for t in tags_raw.split(",")] if tags_raw else []
                tags = [t for t in tags if t]
                manifest_entries[filename.strip()] = {
                    "tipo": tipo_m.group(1).strip() if tipo_m else None,
                    "tags": tags,
                    "tags_present": tags_m is not None,
                    "pasta": pasta_m.group(1).strip() if pasta_m else None,
                    "virou": virou_m.group(1).strip() if virou_m else None,
                }

            # 7a. Every file on disk under wiki/sources/<tipo>/ has a manifest entry, and vice-versa
            files_on_disk = set()
            if SOURCES_DIR.exists():
                for sub in SOURCES_DIR.iterdir():
                    if not sub.is_dir() or sub.name in utility_source_folders:
                        continue
                    for f in sub.iterdir():
                        if f.name == ".gitkeep" or f.is_dir():
                            continue
                        files_on_disk.add(f.name)
                        if f.name not in manifest_entries:
                            report.append(f"ERROR: wiki/sources/{sub.name}/{f.name} existe no disco mas não tem entrada em manifest.md.")
                        if sub.name not in SOURCE_TYPE_TO_FOLDER.values():
                            report.append(f"ERROR: wiki/sources/{sub.name}/ não é uma subpasta do vocabulário controlado (ver AGENTS.md).")

            for filename, entry in manifest_entries.items():
                if filename not in files_on_disk:
                    report.append(f"ERROR: manifest.md tem entrada para '{filename}' mas o arquivo não existe em wiki/sources/**.")
                # 7b. "Ensaio Completo Importado" deve sempre ter virado um essay concreto
                if entry["tipo"] == "Ensaio Completo Importado":
                    if not entry["virou"] or "[[" not in (entry["virou"] or ""):
                        report.append(f"ERROR: source '{filename}' é Tipo: Ensaio Completo Importado mas manifest.md não registra 'Virou: [[Essay]]' — fonte importada sem essay correspondente.")
                    elif entry["virou"]:
                        virou_target = re.search(r"\[\[([^\]|]+)", entry["virou"])
                        if virou_target and virou_target.group(1).strip() not in essay_titles:
                            report.append(f"ERROR: source '{filename}' Virou: aponta para '{virou_target.group(1).strip()}', que não existe como título de essay.")
                # 7d. Tags: é obrigatório em toda entrada — mesmo vocabulário controlado dos essays
                # (ver ## Tags — Vocabulário Controlado em conventions/SKILL.md). Vocabulário em si é
                # lista aberta/editorial (vive em prosa, não hardcoded aqui) — só a presença/não-vazio
                # é auditada mecanicamente; quase-duplicata de grafia é julgamento de /organize.
                if not entry["tags_present"]:
                    report.append(f"WARNING: source '{filename}' não tem campo 'Tags:' em manifest.md — adicione (mesmo vocabulário controlado dos essays).")
                elif not entry["tags"]:
                    report.append(f"WARNING: source '{filename}' tem 'Tags:' vazio em manifest.md.")

        # 7c. Estrutura canônica: todas as subpastas de tipo devem existir (mesmo vazias)
        for tipo, subpasta in SOURCE_TYPE_TO_FOLDER.items():
            if not (SOURCES_DIR / subpasta).exists():
                report.append(f"WARNING: wiki/sources/{subpasta}/ (Tipo: {tipo}) não existe — crie com .gitkeep, mesmo vazia, para manter a estrutura canônica.")
        if not HANDOUTS_DIR.exists():
            report.append("WARNING: wiki/handouts/ não existe — crie com .gitkeep.")

        # 8. Plano audit (5 seções fixas, vocabulário de Status)
        report.append("\n=== PLANO AUDIT (plan/plano.md) ===")
        PLAN_SECOES = ["Tarefas", "Fontes para Ingerir", "Revisões", "Estudos", "Essays Futuros"]
        plano_path = ROOT_DIR / "plan" / "plano.md"
        if not plano_path.exists():
            report.append("WARNING: plan/plano.md não existe ainda (normal se o Usuário nunca usou /plan).")
        else:
            plano_content = load_file_content(plano_path)
            secoes_found = set()
            parts = re.split(r"(?m)^## ", plano_content)[1:]
            for part in parts:
                heading = part.split("\n", 1)[0].strip()
                if heading in PLAN_SECOES:
                    secoes_found.add(heading)
                elif heading != "Índice":
                    report.append(f"ERROR: plan/plano.md tem uma seção '## {heading}' fora do vocabulário fechado ({', '.join(PLAN_SECOES)}).")
            for secao in PLAN_SECOES:
                if secao not in secoes_found:
                    report.append(f"ERROR: plan/plano.md está sem a seção '## {secao}' (as 5 seções devem sempre existir, mesmo vazias).")
            status_values = re.findall(r"(?m)^- Status:\s*(.+)$", plano_content)
            for sv in status_values:
                if sv.strip() not in ("Pendente", "Em Andamento"):
                    report.append(f"ERROR: plan/plano.md tem um item com Status: '{sv.strip()}' fora do vocabulário (Pendente | Em Andamento).")

        # 9. Insights audit (maturidade válida, órfãs)
        report.append("\n=== INSIGHTS AUDIT (wiki/insights/) ===")
        MATURIDADES_VALIDAS = ("solta", "germinando", "madura", "absorvida")
        if INSIGHTS_DIR.exists():
            for file in sorted(INSIGHTS_DIR.glob("*.md")):
                content = load_file_content(file)
                fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
                fm_data = {}
                if fm_match:
                    try:
                        fm_data = yaml.safe_load(fm_match.group(1)) or {}
                    except Exception:
                        pass
                maturidade = fm_data.get("maturidade")
                if maturidade not in MATURIDADES_VALIDAS:
                    report.append(f"ERROR: insights/{file.name} tem 'maturidade:' inválida ou ausente ('{maturidade}'), esperado {'|'.join(MATURIDADES_VALIDAS)}.")
                conexoes_match = re.search(r"## Conexões\s*\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
                if conexoes_match and not re.search(r"\[\[", conexoes_match.group(1)):
                    report.append(f"WARNING: insights/{file.name} não tem nenhum [[wikilink]] em Conexões — candidata a ficar órfã.")

    output_report_path = ROOT_DIR / "output" / "comprehensive_lint_output.txt"
    with open(output_report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report))
        
    print(f"Lint completed. Report written to {output_report_path}")
    print("\nSummary of errors/warnings:")
    errors = [line for line in report if "ERROR:" in line or "CRITICAL:" in line]
    warnings = [line for line in report if "WARNING:" in line or "DEAD WIKILINK:" in line or "ORPHAN" in line]
    print(f"Total Critical/Errors: {len(errors)}")
    print(f"Total Warnings/Orphans/Dead links: {len(warnings)}")

if __name__ == "__main__":
    main()
