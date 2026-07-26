import os
import re
import yaml
import subprocess
from pathlib import Path

WIKI_ROOT = Path(__file__).resolve().parent.parent
ESSAYS_DIR = WIKI_ROOT / "essays"
CONCEPTS_DIR = WIKI_ROOT / "concepts"
ENTITIES_DIR = WIKI_ROOT / "entities"
SOURCES_DIR = WIKI_ROOT / "sources"
SYNTHESIS_DIR = WIKI_ROOT / "synthesis"

# Categories/dirs to lint (sources excluded — they are original immutable documents)
DIRS = {
    "essays": ESSAYS_DIR,
    "concepts": CONCEPTS_DIR,
    "entities": ENTITIES_DIR,
    "synthesis": SYNTHESIS_DIR
}

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
    report = []
    
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
    for file in ESSAYS_DIR.glob("*.md"):
        essays_count += 1
        rel_path = f"essays/{file.name}"
        content = load_file_content(file)
        lines = content.splitlines()
        
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
                # Line 1 format: > Tipo · Categoria Temática
                # Line 2 format: > Gustavo Zambrano · Mês de Ano
                # Tipo is: Ensaio, White Paper, Brainstorm, Estudo ou Análise
                match1 = re.match(r"^>\s*(Ensaio|White Paper|Brainstorm|Estudo|Análise)\s*·\s*(.+)$", line1)
                match2 = re.match(r"^>\s*Gustavo Zambrano\s*·\s*([A-Za-z]+ de \d{4})$", line2)
                
                if not match1:
                    report.append(f"ERROR: {rel_path} byline line 1 invalid format: '{line1}'. Expected '> [Tipo] · [Categoria]' where Tipo is Ensaio|White Paper|Brainstorm|Estudo|Análise")
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
        body_before_conex = parts[0]
        wikilinks_in_body = re.findall(r"\[\[([^\]]+)\]\]", body_before_conex)
        if wikilinks_in_body:
            report.append(f"ERROR: {rel_path} contains {len(wikilinks_in_body)} wikilinks inline in the body. Only external links are allowed in the body. Found: {wikilinks_in_body[:5]}...")
            
        # Spacing: blank line between every heading and text following it
        for idx, line in enumerate(lines):
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
        for idx, line in enumerate(lines):
            if re.match(r"^\d+\s*[-—.]\s*\w+", line.strip()):
                report.append(f"WARNING: {rel_path} has possible loose chapter label on line {idx+1}: '{line}'")
                
        # Residual symbols
        residual_symbols = ["◆", "\ufffd", " ", "&nbsp;", "&amp;"] # note the second space is NBSP in some files
        for idx, line in enumerate(lines):
            for sym in residual_symbols:
                if sym in line:
                    report.append(f"ERROR: {rel_path} contains residual symbol '{sym}' on line {idx+1}: '{line.strip()}'")
                    
        # Residual HTML
        # Looking for things like <div, <span, <p, </div, etc.
        html_matches = re.findall(r"</?(?:div|span|p|br|hr|img|a|h[1-6]|ul|ol|li|table|tr|td|th|thead|tbody|iframe|button|input|label|form|select|option)(?:\s|/|>)[^>]*>|class=|style=", content, re.IGNORECASE)
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

    # 3. Check concepts, entities, sources, synthesis frontmatter and H1
    report.append("\n=== SUPPORT PAGES LINT (CONCEPTS, ENTITIES, SYNTHESIS) ===")
    for category in ["concepts", "entities", "synthesis"]:
        dir_path = DIRS[category]
        if not dir_path.exists():
            continue
        for file in dir_path.glob("*.md"):
            rel_path = f"{category}/{file.name}"
            content = load_file_content(file)
            lines = content.splitlines()
            
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
            for idx, line in enumerate(lines):
                if re.match(r"^#{1,6} ", line):
                    if idx + 1 < len(lines) and lines[idx+1].strip() != "" and not lines[idx+1].strip().startswith("#"):
                        report.append(f"ERROR: {rel_path} heading '{line}' on line {idx+1} is not followed by a blank line.")
                        
            # Residual symbols/HTML
            for idx, line in enumerate(lines):
                for sym in ["◆", "\ufffd", " ", "&nbsp;", "&amp;"]:
                    if sym in line:
                        report.append(f"ERROR: {rel_path} contains residual symbol '{sym}' on line {idx+1}: '{line.strip()}'")
                html_matches = re.findall(r"</?(?:div|span|p|br|hr|img|a|h[1-6]|ul|ol|li|table|tr|td|th|thead|tbody|iframe|button|input|label|form|select|option)(?:\s|/|>)[^>]*>|class=|style=", line, re.IGNORECASE)
                for match in html_matches:
                    report.append(f"ERROR: {rel_path} contains residual HTML tag/attribute: '{match}'")

    # 4. Check for dead wikilinks
    report.append("\n=== DEAD WIKILINKS ===")
    dead_links = {}
    for category, dir_path in DIRS.items():
        if not dir_path.exists():
            continue
        for file in dir_path.glob("*.md"):
            content = load_file_content(file)
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
        
        # Extract all wikilinks in index.md
        index_links = re.findall(r"\[\[([^\]]+)\]\]", index_content)
        for idx_link in index_links:
            target = idx_link.split("|")[0].strip()
            display = idx_link.split("|")[1].strip() if "|" in idx_link else target
            
            # Check Obsidian compatibility: no colons in display text
            if ":" in display:
                report.append(f"ERROR: index.md wikilink display text has a colon: '{idx_link}'")
                
            # index.md contains ONLY essays
            if target not in essay_stems:
                report.append(f"ERROR: index.md contains non-essay or dead link: '{target}'")
                
        # Check if any actual essay is NOT in index.md
        for essay_title in sorted(essay_titles):
            # Get filename for essay_title
            filename = title_to_file[essay_title].split("/")[-1]
            stem = filename.replace(".md", "")
            pattern_stem = re.compile(r"\[\[" + re.escape(stem) + r"\|")
            if not pattern_stem.search(index_content):
                report.append(f"ERROR: Essay '{essay_title}' (essays/{filename}) is missing or incorrectly linked in index.md! (Expected target: [[{stem}|...]])")
    else:
        report.append("ERROR: index.md does not exist!")
        
    # Write report to output
    output_report_path = WIKI_ROOT / "comprehensive_lint_output.txt"
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
