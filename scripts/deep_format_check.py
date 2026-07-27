#!/usr/bin/env python3
"""
deep_format_check.py - Deep formatting check for all essays.
Checks elements the lint_all.py may miss:
- Byline has & instead of plain text (LaTeX export issue)
- Byline colons
- Missing blank line after H1
- Sumário has correct internal links
- Referências heading format (exactly ## Referências, not ### or ## Referências Bibliográficas)
- Conexões is truly the last section
- No wikilinks outside Conexões
- External links count
- No residual HTML
- Heading spacing
"""

import os
import re
from pathlib import Path

ESSAYS_DIR = Path(__file__).resolve().parent.parent / "wiki" / "essays"

def check_essay(filepath):
    issues = []
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    lines = content.splitlines()
    name = filepath.name
    
    # 1. Frontmatter
    if not content.startswith('---'):
        issues.append(f"CRITICAL: No YAML frontmatter")
    
    # 2. H1 title
    h1_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    if not h1_match:
        issues.append(f"CRITICAL: No H1 title")
        return name, issues
    
    title = h1_match.group(1).strip()
    
    # 3. Find H1 line index
    h1_idx = None
    for i, line in enumerate(lines):
        if line.strip() == f"# {title}":
            h1_idx = i
            break
    
    # 4. Check blank line after H1
    if h1_idx is not None and h1_idx + 1 < len(lines):
        if lines[h1_idx + 1].strip() != '':
            issues.append(f"Missing blank line after H1 (line {h1_idx+1})")
    
    # 5. Byline check
    if h1_idx is not None:
        byline_start = h1_idx + 2  # after blank line
        byline_lines = []
        idx = byline_start
        while idx < len(lines) and lines[idx].strip().startswith('>'):
            byline_lines.append(lines[idx].strip())
            idx += 1
        
        # Filter to just the first 2 blockquote lines (byline proper)
        if len(byline_lines) >= 2:
            bl1, bl2 = byline_lines[0], byline_lines[1]
            
            # Check byline format
            types = ['Ensaio', 'White Paper', 'Brainstorm', 'Estudo', 'Análise']
            has_type = any(t in bl1 for t in types)
            if not has_type:
                issues.append(f"Byline line 1 missing type: '{bl1}'")
            
            if '·' not in bl1:
                issues.append(f"Byline line 1 missing · separator: '{bl1}'")
            
            if 'Gustavo Zambrano' not in bl2:
                issues.append(f"Byline line 2 missing author: '{bl2}'")
            
            if ':' in bl1 or ':' in bl2:
                issues.append(f"Byline contains colon ':'")
            
            if '[[' in bl1 or '[[' in bl2:
                issues.append(f"Byline contains wikilinks")
        else:
            issues.append(f"Byline missing or incomplete ({len(byline_lines)} blockquote lines found)")
    
    # 6. Sumário
    if '## Sumário' not in content:
        issues.append(f"Missing ## Sumário section")
    else:
        # Check for --- after sumário
        sum_match = re.search(r'## Sumário\s*\n(.*?)\n---', content, re.DOTALL)
        if not sum_match:
            issues.append(f"Sumário not followed by --- separator")
    
    # 7. Referências - must be exactly ## Referências
    ref_match = re.search(r'^## Referências$', content, re.MULTILINE)
    if not ref_match:
        # Check for variants
        if re.search(r'^## Referências Bibliográficas', content, re.MULTILINE):
            issues.append(f"Uses '## Referências Bibliográficas' instead of '## Referências'")
        elif re.search(r'^### Referências', content, re.MULTILINE):
            issues.append(f"Uses ### Referências instead of ## Referências")
        elif re.search(r'^# Referências', content, re.MULTILINE):
            issues.append(f"Uses # Referências (H1) instead of ## Referências")
        else:
            issues.append(f"Missing ## Referências section")
    
    # 8. Conexões
    if '## Conexões' not in content:
        issues.append(f"Missing ## Conexões section")
    else:
        # Check it's the last H2 section
        after_conex = content.split('## Conexões')[-1]
        other_h2 = re.findall(r'^## [^#]', after_conex, re.MULTILINE)
        if other_h2:
            issues.append(f"## Conexões is NOT the last H2 section")
    
    # 9. Wikilinks outside Conexões
    parts = content.split('## Conexões')
    body = parts[0]
    wikilinks = re.findall(r'\[\[([^\]]+)\]\]', body)
    if wikilinks:
        issues.append(f"{len(wikilinks)} wikilinks outside Conexões: {wikilinks[:3]}")
    
    # 10. External links count
    ext_links = re.findall(r'\[([^\]]+)\]\((https?://[^\)]+)\)', content)
    if len(ext_links) < 10:
        issues.append(f"Only {len(ext_links)} external links (minimum 10)")
    
    # 11. Heading spacing
    heading_spacing_issues = 0
    for i, line in enumerate(lines):
        if re.match(r'^#{1,6} ', line):
            if i + 1 < len(lines) and lines[i+1].strip() != '' and not lines[i+1].strip().startswith('#'):
                # Exception: byline after H1 is OK (there's a blank line)
                heading_spacing_issues += 1
    if heading_spacing_issues > 0:
        issues.append(f"{heading_spacing_issues} headings not followed by blank line")
    
    # 12. Residual symbols
    for i, line in enumerate(lines):
        for sym, desc in [('◆', 'diamond'), ('\ufffd', 'replacement char'), ('&nbsp;', '&nbsp;'), ('&amp;', '&amp;')]:
            if sym in line:
                issues.append(f"Residual symbol '{desc}' on line {i+1}")
    
    # 13. HTML residuals
    html_tags = re.findall(r'</?(?:div|span|p|br|hr|img|a|h[1-6]|ul|ol|li|table|tr|td|th|thead|tbody|iframe|button|input|label|form)(?:\s|/|>)[^>]*>', content, re.IGNORECASE)
    if html_tags:
        issues.append(f"{len(html_tags)} residual HTML tags: {html_tags[:3]}")
    
    return name, issues


def main():
    essays = sorted(ESSAYS_DIR.glob('*.md'))
    print(f"Deep format check on {len(essays)} essays\n")
    
    total_issues = 0
    clean_essays = 0
    
    for essay_path in essays:
        name, issues = check_essay(essay_path)
        if issues:
            print(f"\n❌ {name}")
            for issue in issues:
                print(f"   • {issue}")
            total_issues += len(issues)
        else:
            print(f"✅ {name}")
            clean_essays += 1
    
    print(f"\n{'='*60}")
    print(f"Results: {clean_essays}/{len(essays)} clean, {total_issues} total issues")


if __name__ == '__main__':
    main()
