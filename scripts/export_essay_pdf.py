#!/usr/bin/env python3
"""
export_essay_pdf.py - Export Second Brain essays to beautiful PDFs via Pandoc.

Usage:
    python export_essay_pdf.py <essay_filename_or_path>    # Export single essay
    python export_essay_pdf.py --all                        # Export all essays
    python export_essay_pdf.py --list                       # List available essays

Features:
    - Strips ## Conexões section (internal wiki links, not for PDF)
    - Preserves ## Referências (bibliographic references)
    - Converts YAML frontmatter to elegant title block with author/date
    - Removes any residual [[wikilinks]]
    - Generates professional PDF via Pandoc + LaTeX
"""

import re
import os
import sys
import yaml
import subprocess
import tempfile
import argparse
from pathlib import Path

import console_encoding  # noqa: F401  (UTF-8 no console; ver o módulo)

ROOT_DIR = Path(__file__).resolve().parent.parent
ESSAYS_DIR = ROOT_DIR / "wiki" / "essays"
HANDOUTS_DIR = ROOT_DIR / "wiki" / "handouts"
OUTPUT_DIR = ROOT_DIR / "output" / "pdf"
HANDOUT_OUTPUT_DIR = ROOT_DIR / "output" / "handouts"
TEMPLATE_DIR = ROOT_DIR / "output"

AUTHOR = "Gustavo Zambrano"


def extract_frontmatter(content):
    """Extract YAML frontmatter and body from markdown content.

    O delimitador de fechamento precisa ser uma linha so com '---'. Um split
    ingenuo em '---' quebrava frontmatter cujo summary continha a sequencia
    dentro do texto citado (ex.: "... ele roda? ---"), truncando o bloco e
    invalidando o YAML inteiro."""
    if content.startswith('---'):
        lines = content.split('\n')
        for i in range(1, len(lines)):
            if re.match(r'^---\s*$', lines[i]):
                fm_text = '\n'.join(lines[1:i])
                body = '\n'.join(lines[i + 1:])
                try:
                    meta = yaml.safe_load(fm_text)
                    return meta, body.lstrip('\n')
                except yaml.YAMLError:
                    pass
                break
    return {}, content


def strip_conexoes_section(body):
    """Remove the ## Conexões section and everything after it (but preserve ## Referências if before)."""
    lines = body.split('\n')
    result = []
    in_conexoes = False
    
    for line in lines:
        # Check if this is the start of Conexões
        if re.match(r'^## Conex', line):
            in_conexoes = True
            continue
        
        # If we're in Conexões and hit another ## section that's not a sub-heading
        if in_conexoes:
            # Conexões is always the last section, so skip everything after it
            continue
        
        result.append(line)
    
    # Clean trailing whitespace
    while result and result[-1].strip() == '':
        result.pop()
    
    return '\n'.join(result) + '\n'


def convert_heading_wikilinks(text):
    """`[[#Heading]]` / `[[#Heading|Display]]` -> `[Display](#slug-pandoc)`.

    O `## Sumário` é escrito na forma nativa do Obsidian, a única que aquele
    leitor resolve: `[texto](#slug-github)` não navega lá. O Pandoc é o oposto,
    só entende o slug. A fonte guarda a forma do Obsidian e a tradução acontece
    aqui, no mesmo espírito com que o export já remove `## Conexões` e limpa
    wikilinks residuais.

    Precisa rodar ANTES de `clean_residual_wikilinks`, que apagaria a sintaxe
    `[[...]]` e deixaria só o texto, sem link nenhum.

    O padrão tolera um link markdown aninhado dentro do alvo/display
    (`[[#Capítulo: Vida como [Termo](url)]]`) usando lookahead em vez da
    classe negada — colchetes internos antes encerravam a captura cedo demais,
    sobrando o wikil inteiro como texto literal no HTML/PDF.
    """
    from check_wiki import heading_anchor

    def _strip_md_links(s):
        """Remove `[texto](url)` mantendo o texto — para alvo e display."""
        return re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', s)

    def repl(m):
        alvo = m.group(1).strip()
        display = m.group(2) if m.group(2) else alvo
        return '[%s](#%s)' % (
            _strip_md_links(display),
            heading_anchor(_strip_md_links(alvo)),
        )

    return re.sub(
        r'\[\[#((?:(?!\]\])(?!\|).)+)(?:\|((?:(?!\]\]).)+))?\]\]',
        repl, text,
    )


def clean_residual_wikilinks(text):
    """Remove any remaining [[wikilinks]] converting to plain text."""
    # [[Target|Display]] -> Display
    text = re.sub(r'\[\[([^\]|]+)\|([^\]]+)\]\]', r'\2', text)
    # [[Target]] -> Target
    text = re.sub(r'\[\[([^\]]+)\]\]', r'\1', text)
    return text


def strip_italic_from_headings(text):
    """Remove italic/bold markers from H2/H3 titles so the PDF TOC gets plain text.

    LuaLaTeX collapses the space between a colon and a following \\textit{} in
    TOC entries (e.g. 'Título: *Subtítulo*' becomes 'Título:Subtítulo').
    Stripping the markers at the Markdown level avoids the issue entirely.
    """
    def _strip_heading(m):
        hashes = m.group(1)   # e.g. '##'
        title  = m.group(2)   # everything after '## '

        # Trechos de math ($...$) saem de cena antes da limpeza e voltam depois:
        # dentro deles o `_` é SUBSCRITO, não ênfase. Removê-lo transformava
        # `$C_{n_\beta}$` em `$C_{n\beta}$`, o que apagava o subscrito no PDF e
        # ainda mudava o id da seção, quebrando o link do Sumário só no PDF.
        math = []

        def _guardar(mm):
            math.append(mm.group(0))
            return "\x00MATH%d\x00" % (len(math) - 1)

        title = re.sub(r'\$[^$\n]*\$', _guardar, title)

        # Remove **bold** and *italic* markers (but not inside inline code)
        title = re.sub(r'\*{1,2}([^*]+)\*{1,2}', r'\1', title)
        title = re.sub(r'_{1,2}([^_]+)_{1,2}', r'\1', title)

        title = re.sub(r'\x00MATH(\d+)\x00', lambda mm: math[int(mm.group(1))], title)
        return f'{hashes} {title}'

    return re.sub(r'^(#{2,3}) (.+)$', _strip_heading, text, flags=re.MULTILINE)


def extract_title(body):
    """Extract H1 title from markdown body."""
    for line in body.split('\n'):
        m = re.match(r'^# (.+)', line)
        if m:
            return m.group(1).strip()
    return "Untitled"


def remove_h1_and_byline(body):
    """Remove the H1 title and byline (> Ensaio ...) from body since Pandoc generates title."""
    lines = body.split('\n')
    result = []
    skip_next_blank = False
    i = 0
    while i < len(lines):
        line = lines[i]
        # Skip H1 title
        if re.match(r'^# ', line):
            i += 1
            # Skip blank lines after title
            while i < len(lines) and lines[i].strip() == '':
                i += 1
            # Skip byline (> Ensaio · ... or > White Paper ·...)
            while i < len(lines) and lines[i].startswith('>') and ('Ensaio' in lines[i] or 'White Paper' in lines[i] or 'Gustavo' in lines[i]):
                i += 1
            # Skip blank lines after byline
            while i < len(lines) and lines[i].strip() == '':
                i += 1
            continue
        result.append(line)
        i += 1
    
    return '\n'.join(result)


def resolve_image_paths(text, essay_dir):
    """Convert relative image paths to absolute paths for PDF export."""
    def replace_img(m):
        alt = m.group(1)
        path = m.group(2)
        if path.startswith('http://') or path.startswith('https://'):
            return m.group(0)  # leave URLs alone
        # Resolve relative to essay directory
        abs_path = (essay_dir / path).resolve()
        return f'![{alt}]({abs_path})'
    
    return re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_img, text)


def prepare_for_pandoc(filepath):
    """Prepare a markdown file for Pandoc PDF conversion."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    meta, body = extract_frontmatter(content)
    
    # Extract title from H1
    title = extract_title(body)
    
    # Parse byline from the body to get subtitle and author/date line
    subtitle = ''
    author_date = ''
    for line in body.split('\n'):
        # Byline is always in the preamble — stop at first section heading
        if re.match(r'^##', line):
            break
        line_stripped = line.strip()
        if line_stripped.startswith('>'):
            clean = line_stripped.lstrip('> ').strip()
            # First byline: "Ensaio" (sem categoria — ver conventions/SKILL.md)
            if any(kw in clean for kw in ['Ensaio', 'White Paper', 'Estudo', 'Análise', 'Brainstorm']):
                subtitle = clean
            # Second byline: "Gustavo Zambrano · Mês de Ano"
            elif 'Zambrano' in clean or 'Gustavo' in clean:
                author_date = clean
    
    # Fallback: use frontmatter date if no byline date found
    if not author_date:
        date = meta.get('updated', meta.get('created', ''))
        if date:
            author_date = f"{AUTHOR} · {date}"
        else:
            author_date = AUTHOR
    
    # Strip Conexões section
    body = strip_conexoes_section(body)
    
    # Clean residual wikilinks
    body = convert_heading_wikilinks(body)
    body = clean_residual_wikilinks(body)
    
    # Strip italic/bold markers from headings to fix TOC spacing in LuaLaTeX
    body = strip_italic_from_headings(body)
    
    # Remove H1 and byline (Pandoc will generate from metadata)
    body = remove_h1_and_byline(body)
    
    # Replace --- horizontal rules with *** to avoid Pandoc YAML block parsing
    body = re.sub(r'^---\s*$', '***', body, flags=re.MULTILINE)
    
    # Resolve image paths to absolute
    body = resolve_image_paths(body, Path(filepath).parent)
    
    # Escape quotes in title for YAML
HEADER_TEX = r"""\usepackage{fancyhdr}
\usepackage{xcolor}
\usepackage{titlesec}
\usepackage{enumitem}
\setlist{topsep=0.3em, parsep=0em, itemsep=0.2em}
\setlength{\listparindent}{0pt}
\usepackage{microtype}
\microtypesetup{spacing=false}
\usepackage{graphicx}
% Figura fica ONDE foi escrita, não flutuando: por padrão o LaTeX empurra
% floats para onde couber, e os plots de um anexo no fim do essay acabavam
% caindo no meio de `## Referências`, longe do texto que os descreve.
\usepackage{float}
\floatplacement{figure}{H}
% Teto de altura para a imagem: os plots de anexo são quase tão altos quanto a
% mancha e, em tamanho natural, ocupavam a página inteira, empurrando a legenda
% escrita pelo autor ("Fig. 2 - ...") para a página seguinte, órfã do gráfico.
\setkeys{Gin}{width=\linewidth,height=0.78\textheight,keepaspectratio}
\usepackage{setspace}
\usepackage{fontspec}
\usepackage{fvextra}
\usepackage[most]{tcolorbox}
\usepackage{hyperref}

\directlua{
luaotfload.add_fallback
  ("mainfallback",
   {
     "Segoe UI Symbol:mode=node;",
     "Segoe UI Emoji:mode=node;"
   }
  )
}
\setmainfont{Segoe UI}[RawFeature={fallback=mainfallback}]
\setmonofont{Consolas}[RawFeature={fallback=mainfallback}]

\definecolor{linkblue}{HTML}{2563EB}
\definecolor{titleblue}{HTML}{1E3A5F}
\definecolor{subtlegray}{HTML}{6B7280}
\definecolor{codebg}{HTML}{F8FAFC}
\definecolor{codeframe}{HTML}{CBD5E1}
\definecolor{blockquotebg}{HTML}{F8FAFC}
\definecolor{blockquoteborder}{HTML}{2563EB}

\hypersetup{
  colorlinks=true,
  linkcolor=linkblue,
  urlcolor=linkblue,
  citecolor=linkblue
}

\fvset{
  breaklines=true,
  breakanywhere=true,
  fontsize=\small
}

% Pandoc only defines the "Shaded" environment (via highlighting-macros)
% when the document actually contains a fenced code block. For essays with
% no code, it is never defined, so \renewenvironment would fail with
% "Environment Shaded undefined". \ifdefined\Shaded checks whether Pandoc
% already created it and falls back to \newenvironment otherwise, so this
% works whether or not the essay has code blocks.
\ifdefined\Shaded
  \renewenvironment{Shaded}{%
    \begin{tcolorbox}[
      enhanced,
      breakable,
      colback=codebg,
      colframe=codeframe,
      boxrule=0.6pt,
      arc=4pt,
      outer arc=4pt,
      top=6pt,
      bottom=6pt,
      left=10pt,
      right=10pt
    ]%
  }{%
    \end{tcolorbox}%
  }
\else
  \newenvironment{Shaded}{%
    \begin{tcolorbox}[
      enhanced,
      breakable,
      colback=codebg,
      colframe=codeframe,
      boxrule=0.6pt,
      arc=4pt,
      outer arc=4pt,
      top=6pt,
      bottom=6pt,
      left=10pt,
      right=10pt
    ]%
  }{%
    \end{tcolorbox}%
  }
\fi

\RecustomVerbatimEnvironment{verbatim}{Verbatim}{%
  breaklines=true,%
  breakanywhere=true,%
  fontsize=\small%
}

\renewenvironment{quote}{%
  \begin{tcolorbox}[
    enhanced,
    breakable,
    frame hidden,
    interior hidden,
    boxrule=0pt,
    leftrule=3.5pt,
    colback=blockquotebg,
    colframe=blockquoteborder,
    arc=0pt,
    outer arc=0pt,
    top=6pt,
    bottom=6pt,
    left=12pt,
    right=10pt,
    parbox=false
  ]%
}{%
  \end{tcolorbox}%
}

\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\textcolor{subtlegray}{AUTHOR_PLACEHOLDER}}
\fancyhead[R]{\small\textcolor{subtlegray}{\thepage}}
\renewcommand{\headrulewidth}{0.4pt}
\titleformat{\section}{\Large\bfseries\color{titleblue}}{}{0em}{}
\titleformat{\subsection}{\large\bfseries\color{titleblue!80}}{}{0em}{}
\titleformat{\subsubsection}{\normalsize\bfseries\color{titleblue!60}}{}{0em}{}
\titlespacing*{\section}{0pt}{2em}{0.8em}
\titlespacing*{\subsection}{0pt}{1.5em}{0.5em}
\titlespacing*{\subsubsection}{0pt}{1em}{0.3em}
\setlength{\parskip}{0.6em}
\setlength{\parindent}{0pt}
\onehalfspacing
"""


def prepare_for_pandoc(filepath):
    """Prepare a markdown file for Pandoc PDF conversion."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    meta, body = extract_frontmatter(content)
    
    # Extract title from H1
    title = extract_title(body)
    
    # Parse byline from the body to get subtitle and author/date line
    subtitle = ''
    author_date = ''
    for line in body.split('\n'):
        # Byline is always in the preamble — stop at first section heading
        if re.match(r'^##', line):
            break
        line_stripped = line.strip()
        if line_stripped.startswith('>'):
            clean = line_stripped.lstrip('> ').strip()
            # First byline: "Ensaio" (sem categoria — ver conventions/SKILL.md)
            if any(kw in clean for kw in ['Ensaio', 'White Paper', 'Estudo', 'Análise', 'Brainstorm']):
                subtitle = clean
            # Second byline: "Gustavo Zambrano · Mês de Ano"
            elif 'Zambrano' in clean or 'Gustavo' in clean:
                author_date = clean
    
    # Fallback: use frontmatter date if no byline date found
    if not author_date:
        date = meta.get('updated', meta.get('created', ''))
        if date:
            author_date = f"{AUTHOR} · {date}"
        else:
            author_date = AUTHOR
    
    # Strip Conexões section
    body = strip_conexoes_section(body)
    
    # Clean residual wikilinks
    body = convert_heading_wikilinks(body)
    body = clean_residual_wikilinks(body)
    
    # Strip italic/bold markers from headings to fix TOC spacing in LuaLaTeX
    body = strip_italic_from_headings(body)
    
    # Remove H1 and byline (Pandoc will generate from metadata)
    body = remove_h1_and_byline(body)
    
    # Replace --- horizontal rules with *** to avoid Pandoc YAML block parsing
    body = re.sub(r'^---\s*$', '***', body, flags=re.MULTILINE)
    
    # Resolve image paths to absolute
    body = resolve_image_paths(body, Path(filepath).parent)
    
    # Escape quotes in title for YAML
    safe_title = title.replace('"', '\\"')
    
    # Wrapped in a ```{=latex} fence so Pandoc's Markdown reader treats this
    # YAML block-scalar as raw LaTeX verbatim, instead of parsing it as
    # Markdown first. Without the fence, sequences like `}[...]` right after
    # a closing brace (e.g. \setmainfont{X}[RawFeature={...}]) get
    # misread as a Markdown link reference and come out corrupted
    # (stray {[} / {]} / escaped braces) in the final LaTeX.
    header_body = "```{=latex}\n" + HEADER_TEX.replace("AUTHOR_PLACEHOLDER", AUTHOR).strip() + "\n```"
    header_indented = "\n".join("    " + line for line in header_body.split("\n"))

    # Build new YAML frontmatter for Pandoc
    # NOTE: subtitle is injected as body text below, not in YAML, to control spacing
    pandoc_meta = f"""---
title: "{safe_title}"
author: "{author_date}"
documentclass: article
classoption:
  - 12pt
  - a4paper
geometry:
  - top=30mm
  - bottom=30mm
  - left=25mm
  - right=25mm
header-includes:
  - |
{header_indented}
---

"""
    
    # Inject subtitle as styled text right after the YAML block
    subtitle_block = ""
    if subtitle:
        # Escape LaTeX special characters in subtitle
        safe_subtitle = subtitle.replace('&', '\\&').replace('#', '\\#').replace('%', '\\%').replace('_', '\\_')
        subtitle_block = f"""\\begin{{center}}
\\textcolor{{subtlegray}}{{\\large {safe_subtitle}}}
\\end{{center}}

\\vspace{{0.5em}}

"""
    
    return pandoc_meta + subtitle_block + body


def export_essay(filepath, output_dir=None, source_dir=None):
    """Export a single essay (or handout, if source_dir=HANDOUTS_DIR) to PDF."""
    filepath = Path(filepath)
    if source_dir is None:
        source_dir = ESSAYS_DIR
    if not filepath.exists():
        # Try relative to source dir
        filepath = source_dir / filepath
    if not filepath.exists():
        # Try adding .md
        filepath = source_dir / (str(filepath.name) + '.md')
    if not filepath.exists():
        print(f"ERROR: File not found: {filepath}")
        return False
    
    if output_dir is None:
        output_dir = OUTPUT_DIR
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Prepare content
    prepared = prepare_for_pandoc(filepath)
    
    # Write to temp file
    temp_path = output_dir / f"_temp_{filepath.stem}.md"
    with open(temp_path, 'w', encoding='utf-8') as f:
        f.write(prepared)
    
    # Output PDF path
    pdf_path = output_dir / f"{filepath.stem}.pdf"
    
    # Run Pandoc
    cmd = [
        'pandoc',
        str(temp_path),
        '-o', str(pdf_path),
        '--pdf-engine=lualatex',
        '--highlight-style=pygments',
        '-V', 'colorlinks=true',
        '-V', 'urlcolor=blue',
        '-V', 'linkcolor=blue',
        '-V', 'citecolor=blue',
        f'--resource-path={filepath.parent}',
        # +gfm_auto_identifiers: o Sumário dos essays é escrito na convenção do
        # GitHub/Obsidian, que preserva o número do capítulo no anchor
        # (`## 1. Visão Geral` -> `#1-visão-geral`). A regra nativa do Pandoc
        # descarta tudo antes da primeira letra e geraria `#visão-geral`,
        # quebrando silenciosamente todos os links internos no export.
        # -implicit_figures: o autor escreve a própria legenda em prosa
        # (`Fig. 2 - Variação do flapping...`). Com a extensão ligada, o Pandoc
        # ainda envolvia a imagem num float com legenda automática tirada do alt
        # (`Figure 7: Rotor Analysis 3`), duplicando a legenda e soltando o float
        # para longe do texto — os plots do anexo caíam dentro de `## Referências`.
        '-f', 'markdown+smart+tex_math_dollars+pipe_tables+strikeout+superscript+subscript-implicit_figures+hard_line_breaks+gfm_auto_identifiers',
    ]
    
    print(f"  Exporting: {filepath.name} -> {pdf_path.name}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=600,
                                encoding='utf-8', errors='replace')
        if result.returncode != 0:
            print(f"  ERROR: Pandoc failed for {filepath.name}")
            print(f"  STDERR: {result.stderr[:500]}")
            return False
        else:
            size_kb = pdf_path.stat().st_size / 1024
            print(f"  OK: {pdf_path.name} ({size_kb:.0f} KB)")
            return True
    except FileNotFoundError:
        print("  ERROR: Pandoc not found. Install from https://pandoc.org/installing.html")
        return False
    except subprocess.TimeoutExpired:
        print(f"  ERROR: Pandoc timed out for {filepath.name}")
        return False
    finally:
        # Clean up temp file
        if temp_path.exists():
            temp_path.unlink()


def list_essays():
    """List all available essays."""
    essays = sorted(ESSAYS_DIR.glob('*.md'))
    print(f"\nAvailable essays ({len(essays)}):\n")
    for e in essays:
        with open(e, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('# '):
                    title = line[2:].strip()
                    print(f"  {e.stem:<50s} {title}")
                    break
    print(f"\nUsage: python export_essay_pdf.py <filename>")
    print(f"       python export_essay_pdf.py --all")


def list_handouts():
    """List all available handouts."""
    handouts = sorted(HANDOUTS_DIR.glob('*.md')) if HANDOUTS_DIR.exists() else []
    print(f"\nAvailable handouts ({len(handouts)}):\n")
    for h in handouts:
        with open(h, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('# '):
                    title = line[2:].strip()
                    print(f"  {h.stem:<50s} {title}")
                    break
    print(f"\nUsage: python export_essay_pdf.py <slug> --handout")


def main():
    parser = argparse.ArgumentParser(description='Export Second Brain essays to PDF')
    parser.add_argument('essay', nargs='?', help='Essay (or handout, with --handout) filename or path')
    parser.add_argument('--all', action='store_true', help='Export all essays')
    parser.add_argument('--list', action='store_true', help='List available essays')
    parser.add_argument('--handout', action='store_true', help='Export from wiki/handouts/ instead of wiki/essays/')
    parser.add_argument('--output', '-o', help='Output directory', default=None)

    args = parser.parse_args()

    source_dir = HANDOUTS_DIR if args.handout else ESSAYS_DIR
    default_output = HANDOUT_OUTPUT_DIR if args.handout else OUTPUT_DIR
    output_dir = args.output if args.output else default_output

    if args.list:
        list_handouts() if args.handout else list_essays()
        return 0

    # Sem argumento nenhum, o comportamento útil é exportar tudo — imprimir o
    # help e sair com erro fazia o caso mais comum (`python export_essay_pdf.py`)
    # não produzir nada. Mesmo default de check_wiki.py e fix_lint.py.
    if args.all or not args.essay:
        items = sorted(source_dir.glob('*.md'))
        kind = "handouts" if args.handout else "essays"
        print(f"Exporting {len(items)} {kind} to PDF...\n")
        success = 0
        failed = 0
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
