#!/usr/bin/env python3
"""
export_essay_html.py - Exporta essays para HTML standalone via Pandoc +
essay_template.html: arquivo único offline (CSS/fontes/imagens embutidas),
responsivo, MathJax para fórmulas (CDN). Remove `## Conexões`, preserva
`## Referências` e `## Sumário`, converte frontmatter em masthead.

Lê:
    wiki/essays/*.md (ou um essay via argumento); wiki/handouts/ com --handout
    scripts/essay_template.html; html_preprocess.py; fetch_fonts.py

Gera:
    output/html/<slug>.html        (output/handouts/<slug>.html com --handout)

Uso:
    python scripts/export_essay_html.py <arquivo-ou-slug>
    python scripts/export_essay_html.py --all                  # todos os essays
    python scripts/export_essay_html.py --list                 # lista disponíveis
    python scripts/export_essay_html.py <slug> --handout       # handout

Flags:
    essay        essay/handout alvo (posicional)
    --all        exporta todos os essays
    --list       lista essays disponíveis e sai
    --handout    lê de wiki/handouts/ e grava em output/handouts/
    --output/-o  caminho de saída alternativo

Invariantes do pipeline (leia antes de editar):

1.  Compartilha com `export_essay_pdf.py` o `html_preprocess` e as funcoes de
    frontmatter: mudanca la afeta os dois exports. O filtro `pdf_boxes.lua` NAO
    roda aqui — o que ele faz no PDF, o CSS do template faz no HTML.

2.  Arquivo unico offline: CSS, fontes e imagens embutidas. Nao introduza
    dependencia externa de rede fora do MathJax, que ja e a unica excecao.

3.  Tabela e `pre` rolam DENTRO de si mesmos (`overflow-x:auto`), em qualquer
    largura de tela. Tirar isso faz uma tabela larga empurrar a pagina inteira e
    o texto corrido sair da tela junto.

4.  Codigo em linha usa `overflow-wrap:anywhere`, e `pre code` desfaz a regra:
    dentro do bloco a rolagem horizontal e o comportamento desejado.

5.  Depois de mexer aqui, rode `python scripts/check_html_export.py`. Para
    layout renderizado (vazamento lateral, ancora quebrada, imagem faltando),
    abra os arquivos e meca no navegador — o script so le o HTML.
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

from repo_paths import (
    CODE_ROOT,
    ESSAYS_DIR,
    HANDOUTS_DIR,
    HANDOUT_OUTPUT_DIR,
    HTML_DIR,
)

ROOT_DIR = CODE_ROOT
OUTPUT_DIR = HTML_DIR
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


def trim_sumario_to_h2(body):
    """O Índice mostra apenas capítulos (##): linhas de subcapítulo somem do
    bloco Sumário — inclusive sub-bullets aninhados em texto puro
    ("   - 2.1 X"), que não usam wikilink. O .md continua intacto fora do
    export; essays cujo índice não usa a forma Obsidian [[#...]] ficam
    intocados (nada é varrido por engano)."""
    h2_texts = {h.strip() for h in re.findall(r'(?m)^## (.+)$', body)}
    m = re.search(r'(?ms)^(## Sumário\s*\n)(.*?)(?=^---)', body)
    if not m:
        return body
    keep = []
    kept_links = 0
    dropped = 0
    for line in m.group(2).split('\n'):
        s = line.strip()
        if not s:
            keep.append(line)
            continue
        lm = re.match(r'^(?:[-*+]|\d+[.)])\s+\[\[#([^\]\|]+)(?:\|[^\]]+)?\]\]', s)
        if lm:
            if lm.group(1).strip() in h2_texts:
                keep.append(line)
                kept_links += 1
            else:
                dropped += 1
        else:
            dropped += 1
    if not kept_links or not dropped:
        return body
    novo = m.group(1) + '\n'.join(keep)
    return body[:m.start()] + novo + body[m.end():]


H3_STRIP_RE = re.compile(r'^(###\s+)(\d+(?:\.\d+)+)\s*[.:\u2013\u2014-]?\s+(.*)$', re.M)


def strip_h3_numbers(body):
    """Subtítulos (###) perdem a numeração no export: "### 2.1 X" -> "### X".
    Links [[#2.1 X]] são reescritos para o novo texto para não quebrarem
    (o .md fonte permanece numerado, como no h2, onde o número só some
    visualmente via kicker)."""
    mapping = {}

    def _head(m):
        num, title = m.group(2), m.group(3)
        mapping[num] = title
        return m.group(1) + title

    body = H3_STRIP_RE.sub(_head, body)
    if not mapping:
        return body

    def _link(m):
        alvo, disp = m.group(1).strip(), m.group(2)
        first = alvo.split(None, 1)[0] if alvo else ''
        key = first.rstrip('.:—–-')
        if key in mapping:
            return '[[#' + mapping[key] + ('|' + disp + ']]' if disp else ']]')
        return m.group(0)

    return re.sub(r'\[\[#([^\]\|]+)(?:\|([^\]]+))?\]\]', _link, body)


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
    body = trim_sumario_to_h2(body)
    body = strip_h3_numbers(body)
    body = convert_heading_wikilinks(body)
    body = clean_residual_wikilinks(body)
    body = remove_h1_and_byline(body)
    body = resolve_image_paths(body, Path(filepath).parent)

    return body, meta, title, subtitle, author_date


def prepare_for_pandoc(filepath):
    """Prepare a markdown file for Pandoc HTML conversion.

    Returns (markdown_text, title, subtitle, author_date, summary, status)."""
    body, meta, title, subtitle, author_date = prepare_body(filepath)

    # Caixas de realce -> fenced divs semanticos (ver html_preprocess.py).
    body = transform_markdown(body)

    summary = str(meta.get('summary', '') or '')
    # `status:` do frontmatter (draft | maduro | finalizado). Vai para o
    # template como `data-status` no <html>; so `draft` muda alguma coisa
    # (troca a meta-row da capa pela marca de rascunho).
    status = str(meta.get('status', '') or '').strip().lower()
    return body, title, subtitle, author_date, summary, status


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

    body, title, subtitle, author_date, summary, status = prepare_for_pandoc(filepath)

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
        *(['-V', f'status={status}'] if status else []),
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
                # +lists_without_preceding_blankline: 28 listas em 10 essays do corpus
        # são escritas coladas no parágrafo que as introduz ("...pode:" seguido
        # direto de "- Ler ..."). Sem a extensão o Pandoc não deixa a lista
        # interromper o parágrafo e ela sai como prosa corrida com hífens
        # literais no meio da frase, nos DOIS exports. Ligar aqui corrige o
        # corpus inteiro sem editar um `.md` sequer.
        #
        # -implicit_figures: mesma razão do export_essay_pdf.py — o autor já
        # escreve a legenda em prosa ("Figura 4. Variação..."). Com a extensão
        # ligada, o Pandoc também envolve a imagem num <figure> com <figcaption>
        # tirada do alt text, duplicando a legenda acima da que o autor escreveu.
        '-f', 'markdown+smart+tex_math_dollars+pipe_tables+strikeout+superscript+subscript-implicit_figures+gfm_auto_identifiers+lists_without_preceding_blankline',

    ]

    # Fontes: baixa so subsets latinos para cache local (fetch_fonts.py).
    # Offline -> None e o template cai nas serifas do sistema.
    fonts_css = ensure_local_fonts(output_dir)
    if fonts_css:
        # ~460KB de woff2 (latin/latin-ext) em vez dos ~1.5MB que o
        # --embed-resources baixaria do css2 completo (todas as subsets).
        cmd += ['--css', str(fonts_css)]

    # Only pull in MathJax (CDN once embedded) for essays that actually use math.
    # Keeps non-technical essays small and exportable without network access.
    #
    # tex-SVG-full: saida SVG embute os TRACOS dos glifos no proprio script —
    # nenhuma fonte woff e baixada ao abrir o arquivo. O build CHTML dependia
    # do CDN na hora da VISUALIZACAO (fontURL -> jsdelivr); sem rede, chave
    # de underbrace e o vinculo da raiz viravam quadros vazios. O sufixo
    # -full ja embute todas as extensoes ([tex]/boldsymbol etc.), evitando
    # carga dinamica relativa que quebra com --embed-resources.
    needs_math = body_has_math(body)
    if needs_math:
        # Prefer the copy already downloaded by build_graph.py.  This keeps
        # standalone exports reproducible when Pandoc cannot validate the
        # Windows certificate store (or when the machine is offline).
        local_mathjax = OUTPUT_DIR.parent / 'graph' / '_mathjax_cache.js'
        mathjax_source = str(local_mathjax) if local_mathjax.exists() else \
            'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg-full.js'
        cmd.insert(6, f'--mathjax={mathjax_source}')

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
            for _ in range(5):
                try:
                    temp_path.unlink()
                    break
                except OSError:
                    import time
                    time.sleep(0.1)


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
