#!/usr/bin/env python3
"""
export_essay_html.py - Export Second Brain essays to standalone HTML via Pandoc.

Usage:
    python export_essay_html.py <essay_filename_or_path>    # Export single essay
    python export_essay_html.py --all                        # Export all essays
    python export_essay_html.py --list                       # List available essays

Features (mirrors export_essay_pdf.py so PDF and HTML stay in sync):
    - Strips ## Conexões section (internal wiki links, not for export)
    - Preserves ## Referências, ## Sumário
    - Converts YAML frontmatter into a title/subtitle/byline header block
    - Removes any residual [[wikilinks]]
    - Renders LaTeX math via MathJax, code blocks via Pandoc syntax highlighting
    - Embeds images/CSS into a single self-contained .html file
      (--embed-resources --standalone) so the output works offline and is a
      single file to share, on desktop or mobile (responsive CSS, no JS
      required except the MathJax CDN script for essays that use math)

This script imports its frontmatter/Conexões/wikilink helpers from
export_essay_pdf.py (same folder) instead of duplicating them. Byline parsing
(`parse_byline`) is NOT shared — it's a local duplicate kept in sync by
hand with `prepare_for_pandoc` in export_essay_pdf.py; if you change the byline
format, update both.
"""

import re
import sys
import subprocess
import argparse
from pathlib import Path

import console_encoding  # noqa: F401  (UTF-8 no console; ver o módulo)

# Reuse the shared preparation logic from the PDF exporter.
sys.path.insert(0, str(Path(__file__).parent))
from export_essay_pdf import (
    extract_frontmatter,
    strip_conexoes_section,
    clean_residual_wikilinks,
    convert_heading_wikilinks,
    extract_title,
    resolve_image_paths,
    AUTHOR,
)
from html_preprocess import transform_markdown
from fetch_fonts import ensure_local_fonts

ROOT_DIR = Path(__file__).resolve().parent.parent
ESSAYS_DIR = ROOT_DIR / "wiki" / "essays"
HANDOUTS_DIR = ROOT_DIR / "wiki" / "handouts"
OUTPUT_DIR = ROOT_DIR / "output" / "html"
HANDOUT_OUTPUT_DIR = ROOT_DIR / "output" / "handouts"
TEMPLATE_PATH = Path(__file__).parent / "essay_template.html"


def parse_byline(body):
    """Extract (subtitle, author_date) from the two blockquote byline lines."""
    subtitle = ''
    author_date = ''
    for line in body.split('\n'):
        # Byline is always in the preamble — stop at first section heading
        if re.match(r'^##', line):
            break
        line_stripped = line.strip()
        if line_stripped.startswith('>'):
            clean = line_stripped.lstrip('> ').strip()
            if any(kw in clean for kw in ['Ensaio', 'White Paper', 'Estudo', 'Análise', 'Brainstorm']):
                subtitle = clean
            elif 'Zambrano' in clean or 'Gustavo' in clean:
                author_date = clean
    return subtitle, author_date


def remove_h1_and_byline(body):
    """Remove the H1 title and byline blockquote lines (header is rebuilt by the template)."""
    lines = body.split('\n')
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('# '):
            i += 1
            while i < len(lines) and lines[i].strip() == '':
                i += 1
            while i < len(lines) and lines[i].startswith('>') and ('Ensaio' in lines[i] or 'White Paper' in lines[i]
                                                                     or 'Estudo' in lines[i] or 'Análise' in lines[i]
                                                                     or 'Brainstorm' in lines[i] or 'Gustavo' in lines[i]):
                i += 1
            while i < len(lines) and lines[i].strip() == '':
                i += 1
            continue
        result.append(line)
        i += 1
    return '\n'.join(result)


def prepare_body(filepath):
    """Limpeza comum: frontmatter fora, wikilinks, H1/byline, imagens."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    meta, body = extract_frontmatter(content)
    title = extract_title(body)
    subtitle, author_date = parse_byline(body)

    if not author_date:
        date = meta.get('updated', meta.get('created', ''))
        author_date = f"{AUTHOR} · {date}" if date else AUTHOR

    body = strip_conexoes_section(body)
    body = convert_heading_wikilinks(body)
    body = clean_residual_wikilinks(body)
    body = remove_h1_and_byline(body)
    body = resolve_image_paths(body, Path(filepath).parent)

    return body, meta, title, subtitle, author_date


def prepare_for_pandoc(filepath):
    """Prepare a markdown file for Pandoc HTML conversion.

    Returns (markdown_text, title, subtitle, author_date, summary)."""
    body, meta, title, subtitle, author_date = prepare_body(filepath)

    # Caixas de realce -> fenced divs semanticos (ver html_preprocess.py).
    body = transform_markdown(body)

    summary = str(meta.get('summary', '') or '')
    return body, title, subtitle, author_date, summary


MATH_PATTERN = re.compile(r'(?<!\\)\$[^\s$][^$]*\$|\\\[.*?\\\]|\\\(.*?\\\)', re.DOTALL)


def body_has_math(body):
    """Heuristic: does the essay body contain any $...$ / \\[...\\] math?"""
    return bool(MATH_PATTERN.search(body))


def export_essay(filepath, output_dir=None, source_dir=None):
    """Export a single essay (or handout, if source_dir=HANDOUTS_DIR) to a standalone HTML file."""
    source_dir = source_dir or ESSAYS_DIR
    filepath = Path(filepath)
    if not filepath.exists():
        filepath = source_dir / filepath
    if not filepath.exists():
        filepath = source_dir / (str(filepath) + '.md')
    if not filepath.exists():
        print(f"ERROR: File not found: {filepath}")
        return False

    if output_dir is None:
        output_dir = OUTPUT_DIR
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    body, title, subtitle, author_date, summary = prepare_for_pandoc(filepath)

    temp_path = output_dir / f"_temp_{filepath.stem}.md"
    with open(temp_path, 'w', encoding='utf-8') as f:
        f.write(body)

    html_path = output_dir / f"{filepath.stem}.html"
    safe_subtitle = subtitle.replace('"', '\\"')
    safe_author = author_date.replace('"', '\\"')
    safe_summary = summary.replace('"', "'").replace('\n', ' ')

    cmd = [
        'pandoc',
        str(temp_path),
        '-o', str(html_path),
        '--standalone',
        '--embed-resources',
        f'--template={TEMPLATE_PATH}',
        '--highlight-style=pygments',
        '-V', f'title={title}',
        '-V', f'subtitle={safe_subtitle}',
        '-V', f'author={safe_author}',
        '-V', f'summary={safe_summary}',
        f'--resource-path={filepath.parent}',
        # +gfm_auto_identifiers: o Sumário dos essays é escrito na convenção do
        # GitHub/Obsidian, que preserva o número do capítulo no anchor
        # (`## 1. Visão Geral` -> `#1-visão-geral`). A regra nativa do Pandoc
        # descarta tudo antes da primeira letra e geraria `#visão-geral`,
        # quebrando silenciosamente todos os links internos no export.
        #
        # Sem +hard_line_breaks desde a reformulação das caixas: as quebras
        # duras agora são aplicadas apenas DENTRO das citações pelo
        # pré-processador (html_preprocess.py); globalmente, elas transformavam
        # todo parágrafo corrido em uma pilha de <br>.
        '-f', 'markdown+smart+tex_math_dollars+pipe_tables+strikeout+superscript+subscript+implicit_figures+gfm_auto_identifiers',

    ]

    # Fontes: baixa so subsets latinos para cache local (fetch_fonts.py).
    # Offline -> None e o template cai nas serifas do sistema.
    fonts_css = ensure_local_fonts(output_dir)
    if fonts_css:
        # ~460KB de woff2 (latin/latin-ext) em vez dos ~1.5MB que o
        # --embed-resources baixaria do css2 completo (todas as subsets).
        cmd += ['--css', str(fonts_css)]

    # Only pull in MathJax (CDN, ~3MB once embedded) for essays that actually use math.
    # Keeps non-technical essays small and exportable without network access.
    needs_math = body_has_math(body)
    if needs_math:
        cmd.insert(6, '--mathjax=https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js')

    print(f"  Exporting: {filepath.name} -> {html_path.name}")

    try:
        result = subprocess.run(cmd, capture_output=True, timeout=300,
                                 encoding='utf-8', errors='replace')
        if result.returncode != 0:
            print(f"  ERROR: Pandoc failed for {filepath.name}")
            print(f"  STDERR: {result.stderr[:500]}")
            return False
        size_kb = html_path.stat().st_size / 1024
        print(f"  OK: {html_path.name} ({size_kb:.0f} KB)")
        # --embed-resources fetches the MathJax script over the network at
        # export time. If that fetch fails (offline, firewall, CDN down),
        # Pandoc still exits 0 and silently drops the script -- the essay
        # looks exported fine but formulas won't render in the browser.
        # Catch that case here instead of leaving it to be discovered later.
        if needs_math:
            html_text = html_path.read_text(encoding='utf-8', errors='replace')
            if 'mathjax' not in html_text.lower():
                print(f"  WARNING: math detected in {filepath.name} but the MathJax script "
                      f"was not embedded (likely no network access to the CDN at export time). "
                      f"Formulas will show as raw LaTeX (e.g. \\(x\\)) instead of rendering.")
        return True
    except FileNotFoundError:
        print("  ERROR: Pandoc not found. Install from https://pandoc.org/installing.html")
        return False
    except subprocess.TimeoutExpired:
        print(f"  ERROR: Pandoc timed out for {filepath.name}")
        return False
    finally:
        if temp_path.exists():
            temp_path.unlink()


def list_essays():
    essays = sorted(ESSAYS_DIR.glob('*.md'))
    print(f"\nAvailable essays ({len(essays)}):\n")
    for e in essays:
        with open(e, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('# '):
                    print(f"  {e.stem:<50s} {line[2:].strip()}")
                    break
    print("\nUsage: python export_essay_html.py <filename>")
    print("       python export_essay_html.py --all")


def list_handouts():
    handouts = sorted(HANDOUTS_DIR.glob('*.md')) if HANDOUTS_DIR.exists() else []
    print(f"\nAvailable handouts ({len(handouts)}):\n")
    for h in handouts:
        with open(h, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('# '):
                    print(f"  {h.stem:<50s} {line[2:].strip()}")
                    break
    print("\nUsage: python export_essay_html.py <slug> --handout")


def main():
    parser = argparse.ArgumentParser(description='Export Second Brain essays to standalone HTML')
    parser.add_argument('essay', nargs='?', help='Essay (or handout, with --handout) filename or path')
    parser.add_argument('--all', action='store_true', help='Export all essays')
    parser.add_argument('--list', action='store_true', help='List available essays')
    parser.add_argument('--handout', action='store_true', help='Export from wiki/handouts/ instead of wiki/essays/')
    parser.add_argument('--output', '-o', help='Output directory', default=None)
    args = parser.parse_args()

    source_dir = HANDOUTS_DIR if args.handout else ESSAYS_DIR
    default_output = HANDOUT_OUTPUT_DIR if args.handout else OUTPUT_DIR
    output_dir = args.output or str(default_output)

    if args.list:
        list_handouts() if args.handout else list_essays()
        return 0

    # Sem argumento nenhum, o comportamento útil é exportar tudo — imprimir o
    # help e sair com erro fazia o caso mais comum (`python export_essay_html.py`)
    # não produzir nada. Mesmo default de check_wiki.py e fix_lint.py.
    if args.all or not args.essay:
        items = sorted(source_dir.glob('*.md')) if source_dir.exists() else []
        kind = "handouts" if args.handout else "essays"
        print(f"Exporting {len(items)} {kind} to HTML...\n")
        success = failed = 0
        for e in items:
            if export_essay(e, output_dir, source_dir=source_dir):
                success += 1
            else:
                failed += 1
        print(f"\nDone: {success} exported, {failed} failed")
        return 0 if failed == 0 else 1

    if args.essay:
        ok = export_essay(args.essay, output_dir, source_dir=source_dir)
        return 0 if ok else 1

    parser.print_help()
    return 1


if __name__ == '__main__':
    sys.exit(main())
