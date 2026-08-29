#!/usr/bin/env python3
"""
export_essay_pdf.py - Exporta essays para PDF via Pandoc + LaTeX (filtro
pdf_boxes.lua mapeia fenced divs em caixas tcolorbox). Remove `## Conexões`,
preserva `## Referências`, converte frontmatter em página de título.

Lê:
    wiki/essays/*.md (ou um essay via argumento); wiki/handouts/ com --handout
    html_preprocess.py, scripts/pdf_boxes.lua

Gera:
    output/pdf/<slug>.pdf          (output/handouts/<slug>.pdf com --handout)

Uso:
    python scripts/export_essay_pdf.py <arquivo-ou-slug>
    python scripts/export_essay_pdf.py --all                  # todos os essays
    python scripts/export_essay_pdf.py --list                 # lista disponíveis
    python scripts/export_essay_pdf.py <slug> --handout       # handout

Flags:
    essay        essay/handout alvo (posicional)
    --all        exporta todos os essays
    --list       lista essays disponíveis e sai
    --handout    lê de wiki/handouts/ e grava em output/handouts/
    --output/-o  caminho de saída alternativo
"""

import re
import os
import sys
import yaml
import subprocess
import tempfile
import argparse
from pathlib import Path
from unidecode import unidecode

from check_wiki import heading_anchor

import console_encoding  # noqa: F401  (UTF-8 no console; ver o módulo)

# Mesmo preprocessador do export HTML: converte blockquotes padrao do corpus
# (caixas tipadas, cards, pull-quotes, rotulos) em fenced divs semanticos,
# que o filtro scripts/pdf_boxes.lua mapeia para ambientes tcolorbox no LaTeX.
from html_preprocess import transform_markdown

ROOT_DIR = Path(__file__).resolve().parent.parent
LUA_FILTER = Path(__file__).resolve().parent / "pdf_boxes.lua"
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


def convert_section_separators(body):
    """`---` antes de heading some; a linha do capitulo vem do proprio `##`.

    O filete de capitulo e desenhado dentro da caixa do titulo (comando
    \\chaptersepinner no before-code de \\subsection em HEADER_TEX), entao
    o `---` do markdown nao precisa virar comando nenhum — e removido para
    nao duplicar a linha. Um `---` sem heading na sequencia mantem o hrule
    padrao do Pandoc (`***`).
    """
    lines = body.split('\n')
    out = []
    for i, line in enumerate(lines):
        if not re.match(r'^---\s*$', line):
            out.append(line)
            continue
        j = i + 1
        while j < len(lines) and lines[j].strip() == '':
            j += 1
        nxt = lines[j] if j < len(lines) else ''
        if re.match(r'^#{2,}\s', nxt):
            pass
        else:
            out.append('***')
    return '\n'.join(out)


def extract_title(body):
    """Extract H1 title from markdown body."""
    for line in body.split('\n'):
        m = re.match(r'^# (.+)', line)
        if m:
            return m.group(1).strip()
    return "Untitled"


def remove_h1_and_byline(body):
    """Remove the H1 title and byline (> ...) from body since Pandoc generates title on cover."""
    lines = body.split('\n')
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Skip H1 title
        if re.match(r'^#\s+', line):
            i += 1
            # Skip blank lines after title
            while i < len(lines) and lines[i].strip() == '':
                i += 1
            # Skip all byline lines (> ...) immediately following H1
            while i < len(lines) and lines[i].startswith('>'):
                i += 1
            # Skip blank lines after byline
            while i < len(lines) and lines[i].strip() == '':
                i += 1
            continue
        result.append(line)
        i += 1
    
    return '\n'.join(result)


def resolve_image_paths(text, essay_dir):
    """Convert relative image paths to absolute paths for PDF export.

    SVG cai para o PNG irmao quando existe: o caminho LaTeX (pacote svg)
    converte .svg via rsvg-convert, que nao existe em toda maquina Windows.
    O essay mantem o link .svg (Obsidian renderiza nativo); o export usa o
    .png pre-gerado ao lado (mesmo nome, gerado uma vez a 2x).
    """
    def replace_img(m):
        alt = m.group(1)
        path = m.group(2)
        if path.startswith('http://') or path.startswith('https://'):
            return m.group(0)  # leave URLs alone
        abs_path = (essay_dir / path).resolve()
        if abs_path.suffix.lower() == '.svg':
            png = abs_path.with_suffix('.png')
            if png.exists():
                abs_path = png
        return f'![{alt}]({abs_path})'

    return re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_img, text)


# NOTE: havia aqui uma primeira copia morta de `prepare_for_pandoc`
# (sobrescrita pela definicao real mais abaixo). Foi removida — manter duas
# versoes desse tamanho no mesmo arquivo fez esta sessao quase editar a
# copia errada.

HEADER_TEX = r"""\usepackage{fancyhdr}
\usepackage{xcolor}
\usepackage{needspace}
% `\needspace` NAO serve aqui: ele planta um `\penalty -100` cujo custo
% cai para ~900 sempre que o espaco restante fica dentro de duas ou tres
% vezes do pedido — barato o bastante para o TeX preferir essa quebra a
% qualquer outra, e o capitulo pulava de pagina com um terco de folha em
% branco. Aqui a conta e explicita: compara o que sobra na pagina com o que
% o bloco precisa e so entao emite \newpage, sem oferecer ponto de quebra
% nenhum. O `\if@nobreak` (verdadeiro so logo apos um titulo, desligado
% pelo `\everypar` no primeiro paragrafo) evita que um `### X.1` colado num
% `## X` reserve espaco de novo e deixe o titulo de capitulo sozinho.
\makeatletter
\newif\ifsb@needbreak
\newif\ifsb@skipnext
% Ligada pelo Python imediatamente antes de um `###` colado num `##` (ou de
% um `####` colado num `###`). O `\if@nobreak` do LaTeX deveria bastar, mas o
% titlesec nao o mantem de forma confiavel, e um unico ponto de quebra entre
% os dois titulos ja deixa o de cima sozinho no pe da pagina.
\newcommand{\sbskipnextneed}{\global\sb@skipnexttrue\sbnobreak}
% Apelido publico de `\@nobreaktrue`: o `\sbkicker` e definido fora de um
% bloco `\makeatletter` e nao pode citar a versao com arroba.
\newcommand{\sbnobreak}{\@nobreaktrue}
\newlength{\sb@needlen}
% Altura exata do bloco de abertura de capitulo, para decidir se ele cabe no
% que resta da pagina. #1 = rotulo do kicker, #2 = titulo do capitulo,
% #3 = subtitulo colado logo abaixo (vazio quando nao ha nenhum).
%
% O bloco e composto de verdade num \vbox descartado logo em seguida: e a
% unica forma de saber quantas linhas o titulo ocupa sem estimar largura media
% de caractere. Medir so o titulo e somar constantes para filete, rotulo e
% subtitulo, como antes, errava para os dois lados — ora pulava pagina a toa,
% ora deixava o titulo sozinho no pe.
%
% A linha de corpo entra por fora: o criterio combinado e titulo mais uma
% linha, e e o \clubpenalty relaxado logo abaixo que torna isso possivel.
\newcommand{\sbchapterneed}[3]{%
  \begingroup
    % Linha fantasma sozinha: serve de referencia para descontar.
    \setbox\tw@=\vbox{\hsize=\linewidth
      \noindent\strut\par}%
    % A mesma linha fantasma seguida do bloco inteiro e de uma linha de corpo.
    \setbox\z@=\vbox{\hsize=\linewidth
      \noindent\strut\par
      \vspace{2.2em}%
      {\noindent\rule{\linewidth}{0.7pt}}\par
      \vspace{0.55em}%
      {\noindent\small\addfontfeatures{LetterSpace=28}\MakeUppercase{#1}}\par
      \vspace{0.4em}%
      {\fontsize{18pt}{22pt}\selectfont\addfontfeatures{LetterSpace=-1.5}\bfseries\raggedright
       \hyphenpenalty=10000\exhyphenpenalty=10000
       \noindent #2\par}%
      \if\relax\detokenize{#3}\relax\else
        \vspace{1.2em}%
        {\fontsize{13pt}{16pt}\selectfont\sffamily\bfseries\raggedright
         \hyphenpenalty=10000\exhyphenpenalty=10000
         \noindent #3\par}%
        \vspace{0.35em}%
      \fi
      \vspace{0.45em}%
      \noindent\strut\par}%
    \global\sb@needlen=\ht\z@
    \global\advance\sb@needlen by \dp\z@
    \global\advance\sb@needlen by -\ht\tw@
    \global\advance\sb@needlen by -\dp\tw@
  \endgroup
  \sbneedspace{\sb@needlen}%
}
\newcommand{\sbneedspace}[1]{%
  \par
  \sb@needbreakfalse
  \ifsb@skipnext\global\sb@skipnextfalse\@nobreaktrue\fi
  % `\if@nobreak` e verdadeiro so no ponto imediatamente posterior a um
  % titulo, e o `\everypar` do LaTeX o desliga no primeiro paragrafo. Tudo
  % o que segue precisa ficar DENTRO deste ramo: quando um `## X` e seguido
  % direto de um `### X.1`, ate o `\penalty\z@` de medicao seria um ponto
  % de quebra legal logo apos o titulo de capitulo — e era assim que o titulo
  % acabava sozinho no pe da pagina.
  \if@nobreak\else
    % `\pagetotal` so vale depois que o construtor de pagina rodou, e ele so
    % roda ate um ponto de quebra LEGAL: com `\penalty\@M` o construtor
    % segurava material alem do pe da pagina e `\pagetotal` chegava a passar
    % de `\pagegoal`. Disparar `\newpage` nesse estado quebrava duas vezes e
    % deixava uma pagina com duas linhas. `\penalty\z@` e ponto de quebra
    % legal de custo neutro: fecha a pagina pendente antes da medicao sem
    % privilegiar a quebra em relacao as vizinhas.
    \penalty\z@
    \dimen@=#1\relax
    \ifdim\pagegoal<\maxdimen
      \dimen@ii=\pagegoal
      \advance\dimen@ii-\pagetotal
      \ifdim\dimen@ii<\dimen@ \sb@needbreaktrue\fi
    \fi
  \fi
  \ifsb@needbreak\newpage\fi
}
\makeatother
\usepackage{titlesec}
\clubpenalty=10000
\widowpenalty=10000
\displaywidowpenalty=10000
% O LaTeX proibe quebrar pagina logo antes de uma equacao em display
% (predisplaypenalty = 10000). Num essay tecnico isso solda titulo de
% capitulo, primeiro paragrafo e primeira equacao num bloco unico de quase
% 300pt: se ele nao cabe no que resta da pagina, o capitulo inteiro pula
% para a proxima e sobra um terco de pagina em branco. 100 mantem a quebra
% desencorajada, sem torna-la impossivel.
\predisplaypenalty=100
% Repetido em \AtBeginDocument porque amsmath e setspace ajustam
% penalidades de display no inicio do documento e sobrescreveriam o valor
% definido aqui no preambulo.
\AtBeginDocument{\predisplaypenalty=100\relax}
% Ultimo recurso do quebrador de linha antes de deixar a caixa vazar para
% fora da margem: sem isto, um link longo e nao hifenizavel (`\uline` bloqueia
% hifenizacao) obrigava o TeX a escolher entre um espacamento horrendo e uma
% linha overfull, e ele escolhia a overfull.
\setlength{\emergencystretch}{3em}
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
\setkeys{Gin}{width=\linewidth,height=0.55\textheight,keepaspectratio}
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
% Corpo em serifa de paper técnico: Latin Modern casa com a fonte das
% equações (unicode-math usa Latin Modern Math por padrão no LuaLaTeX),
% dando unidade texto↔fórmula. Fallback cobre símbolos/emoji que a LM
% não tem (⚠, ✦, setas etc.).
\IfFontExistsTF{LibertinusSerif}{%
  \setmainfont{LibertinusSerif}[RawFeature={fallback=mainfallback}]%
  \setsansfont{LibertinusSans}[RawFeature={fallback=mainfallback}]%
  \setmathfont{LibertinusMath-Regular.otf}%
}{}
\setmonofont{Consolas}[RawFeature={fallback=mainfallback}]

\usepackage[normalem]{ulem}
\renewcommand{\ULthickness}{0.6pt}
\renewcommand{\ULdepth}{2.2pt}

% Paleta premium — contrastada, nítida e elegante
\definecolor{sblink}{HTML}{171310}
\definecolor{sbink}{HTML}{8A6B33}
\definecolor{sburl}{HTML}{8A6B33}
\definecolor{sbgraphite}{HTML}{2B2824}
\definecolor{subtlegray}{HTML}{4B5563}
\definecolor{codebg}{HTML}{F8FAFC}
\definecolor{codeframe}{HTML}{CBD5E1}
\definecolor{boxbg}{HTML}{F9F9F7}
\definecolor{boxline}{HTML}{4B5563}
\definecolor{quoteline}{HTML}{8A6B33}
\definecolor{boxexp}{HTML}{8E4636}
\definecolor{boxev}{HTML}{35708A}
\definecolor{boxmap}{HTML}{8A6B33}
\definecolor{boxav}{HTML}{7A5A18}
\definecolor{boxid}{HTML}{7A6135}

\hypersetup{
  colorlinks=true,
  linkcolor=sblink,
  urlcolor=sburl,
  citecolor=sburl
}

% Legendas de figura reais (ambiente figure) ficam menores que o corpo.
\usepackage{caption}
\captionsetup{font=small,labelfont=bf,width=.95\linewidth}

% Tabelas (longtable do Pandoc): linhas horizontais suaves e espacamento equilibrado
\usepackage{booktabs}
\usepackage{colortbl}
\definecolor{tableborder}{HTML}{E2E8F0}
\arrayrulecolor{tableborder}
\setlength{\heavyrulewidth}{0.8pt}
\setlength{\lightrulewidth}{0.4pt}
\usepackage{etoolbox}
% A longtable que comeca no pe da pagina imprime o cabecalho, descobre que
% nenhuma linha do corpo cabe, quebra a pagina e reimprime o cabecalho — o
% primeiro fica para tras, orfao. Reservar cabecalho mais duas linhas resolve
% isso; mais que isso arrastava tabela grande inteira para a pagina seguinte
% e deixava meia folha em branco. O `\endhead` do Pandoc repete o cabecalho
% em cada continuacao, entao partir a tabela nao custa legibilidade.
\BeforeBeginEnvironment{longtable}{\sbneedspace{4\baselineskip}}
\AtBeginEnvironment{longtable}{%
  \small
  \setlength{\emergencystretch}{3em}%
  \hyphenpenalty=50\exhyphenpenalty=50%
  \setlength{\tabcolsep}{5pt}%
  \renewcommand{\arraystretch}{1.25}%
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

% Bloco cercado SEM linguagem vira `verbatim`, nao `Shaded` (que o Pandoc so
% emite quando ha realce de sintaxe). Sem isto, diagramas ASCII e pseudocodigo
% saiam soltos na pagina, sem moldura nenhuma, enquanto um bloco ```python ao
% lado aparecia encaixotado. Mesma moldura para os dois.
\newtcolorbox{sbcodebox}{enhanced,breakable,
  colback=codebg,colframe=codeframe,boxrule=0.6pt,
  arc=4pt,outer arc=4pt,
  top=6pt,bottom=6pt,left=8pt,right=8pt}
\BeforeBeginEnvironment{verbatim}{\begin{sbcodebox}}
\AfterEndEnvironment{verbatim}{\end{sbcodebox}}
% \footnotesize (nao \small): diagramas e listagens do corpus chegam a 100
% colunas, e cada ponto a menos e uma linha a menos quebrada pelo `breaklines`.
\RecustomVerbatimEnvironment{verbatim}{Verbatim}{%
  breaklines=true,%
  breakanywhere=true,%
  fontsize=\footnotesize%
}

\renewenvironment{quote}{%
  \begin{tcolorbox}[
    enhanced,
    breakable,
    frame hidden,
    arc=0pt,
    interior style={fill=boxbg},
    borderline west={2.5pt}{0pt}{quoteline},
    boxrule=0pt,
    top=7pt,
    bottom=7pt,
    left=12pt,
    right=10pt,
    parbox=false
  ]%
}{%
  \end{tcolorbox}%
}

% ---------------------------------------------------------------------
% Caixas semanticas (fenced divs -> pdf_boxes.lua). Mesma estrutura que
% o template HTML estiliza: wikibox (rotulo+titulo+corpo+veredicto),
% wikiquote, wikipull, wikicard. Tipografia contida: mesma serifa do
% corpo, hierarquia por peso/tamanho, nada de troca de familia.
% parbox=false mantem o espacamento de paragrafo natural dentro da caixa.
% ---------------------------------------------------------------------
\newtcolorbox{wikibox}[1]{enhanced,breakable,
  colback=boxbg,colframe=boxbg,frame hidden,
  borderline west={2.5pt}{0pt}{#1},
  left=10pt,right=10pt,top=8pt,bottom=8pt,parbox=false,
  before upper={\colorlet{wbtype}{#1}}}

\newtcolorbox{wikiquote}{enhanced,breakable,
  frame hidden,arc=0pt,
  interior style={fill=boxbg},
  borderline west={2.5pt}{0pt}{quoteline},
  left=12pt,right=10pt,top=7pt,bottom=7pt,parbox=false}

\newenvironment{wikipull}
  {\begin{tcolorbox}[enhanced,breakable,
     frame hidden,arc=0pt,
     interior style={fill=boxbg},
     borderline west={3pt}{0pt}{quoteline},
     left=12pt,right=10pt,top=8pt,bottom=7pt,parbox=false]\itshape}
  {\end{tcolorbox}}

\newtcolorbox{wikicard}{enhanced,breakable,
  frame hidden,arc=0pt,
  interior style={fill=boxbg},
  borderline west={3pt}{0pt}{boxline},
  left=12pt,right=10pt,top=8pt,bottom=8pt,parbox=false}

\newcommand{\wbbadge}[1]{\par\noindent{\footnotesize\bfseries\color{wbtype}\addfontfeatures{LetterSpace=18}\MakeUppercase{#1}}\par\nobreak\vspace{2pt}\nobreak}
\newcommand{\wbtitle}[1]{\par\noindent{\large\bfseries\color{sblink} #1}\par\nobreak\vspace{4pt}\nobreak}
\newcommand{\cardname}[1]{\par\noindent{\bfseries\color{sblink}#1}\par\nobreak\vspace{1pt}\nobreak}
\newcommand{\cardmeta}[1]{\par\noindent{\footnotesize\color{subtlegray}#1}\par\vspace{0.6em}}
\newcommand{\parahead}[1]{\par\vspace{0.9em}\noindent{\footnotesize\bfseries\color{sbink}#1}\par\nobreak\vspace{0.35em}\nobreak}
\newcommand{\ornamentglyph}[1]{{\setlength{\fboxsep}{0pt}#1}}

% Sem cabecalho e sem filete no rodape: autor vive so na capa (\maketitle).
% Numero de pagina discreto no canto inferior direito, empurrado para perto
% da borda (\footskip) para nao roubar area util da mancha.
\pagestyle{fancy}
\fancyhf{}
\fancyfoot[R]{\footnotesize\textcolor{subtlegray}{\thepage}}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}
\setlength{\footskip}{30pt}
% Paginas em estilo plain (capa, via \maketitle) seguem o mesmo padrao.
\fancypagestyle{plain}{%
  \fancyhf{}%
  \fancyfoot[R]{\footnotesize\textcolor{subtlegray}{\thepage}}%
  \renewcommand{\headrulewidth}{0pt}%
  \renewcommand{\footrulewidth}{0pt}%
}

% Capa propria (\sbcover) e supressao do \maketitle padrao
\newcommand{\sbcover}[4]{%
  \thispagestyle{empty}%
  \noindent{\color{sbink}\rule{\linewidth}{0.8pt}}\par
  \vspace{0.14\textheight}%
  \begin{center}
    {\Huge\bfseries\color{sblink}\hyphenpenalty=10000\exhyphenpenalty=10000 #1\par}
    \vspace{1.6em}%
    {\color{sbink}\rule{64pt}{1pt}}\par
    \vspace{1.5em}%
    {\normalsize\addfontfeatures{LetterSpace=20}\scshape\color{sblink} #2\par}
    \vspace{1.1em}%
    {\large\color{subtlegray} #3\par}
  \end{center}
  \vfill
  \if\relax\detokenize{#4}\relax\else
    \begin{center}
      {\small\color{subtlegray}\addfontfeatures{LetterSpace=12}#4\par}
    \end{center}
  \fi
  \vspace{1.5em}%
  \clearpage
}
\renewcommand{\maketitle}{}

% Sumario tipografico — limpo, compacto e sem linhas intermediarias
\newenvironment{sbtoc}{%
  \par\vspace{0.6em}%
  \begingroup
  \setlength{\parindent}{0pt}%
  \setlength{\parskip}{0.3em}%
}{%
  \endgroup\par\vspace{0.8em}%
}
% #1 = numeral da goteira, #2 = titulo (inlines do Pandoc, com matematica e
% enfase preservadas — o filtro nao achata mais em texto). O recuo pendente
% mantem a segunda linha de um titulo longo alinhada ao texto, nunca sob o
% numeral.
\newcommand{\sbtocopen}[2]{%
  \par\noindent
  \makebox[1.8em][r]{\mbox{\footnotesize\color{sbink}\rmfamily #1}}%
  \hspace{0.8em}%
  \begin{minipage}[t]{\dimexpr\linewidth-2.6em\relax}#2\end{minipage}\par
}
\newcommand{\sbtocopenlast}[2]{\sbtocopen{#1}{#2}}

% Kicker de capitulo — inserido por Python antes de cada ##
% 12 linhas, nao 7: o kicker so ocupa uma linha, mas o que vem colado nele e
% um `\subsection` de 18pt que pode gastar duas linhas sozinho. Com 7 o titulo
% de capitulo cabia no pe da pagina e o corpo comecava na pagina seguinte,
% deixando o titulo sozinho.
\makeatletter
% Altura exata do bloco de um subtitulo: #1 = nivel (3 para `###`, 4 para
% `####`), #2 = o texto do titulo. Mesma ideia do \sbchapterneed — compor de
% verdade e medir, em vez de arbitrar um numero de entrelinhas que ora sobra
% ora falta.
\newcommand{\sbsubneed}[2]{%
  \begingroup
    \setbox\tw@=\vbox{\hsize=\linewidth
      \noindent\strut\par}%
    \setbox\z@=\vbox{\hsize=\linewidth
      \noindent\strut\par
      \ifnum#1=3
        \vspace{1.2em}%
        \fontsize{13pt}{16pt}\selectfont\sffamily\bfseries
      \else
        \vspace{0.9em}%
        \fontsize{13pt}{16pt}\selectfont\bfseries
      \fi
      \raggedright\hyphenpenalty=10000\exhyphenpenalty=10000
      \noindent #2\par
      \ifnum#1=3\vspace{0.35em}\else\vspace{0.25em}\fi
      \normalfont\normalsize\noindent\strut\par}%
    \global\sb@needlen=\ht\z@
    \global\advance\sb@needlen by \dp\z@
    \global\advance\sb@needlen by -\ht\tw@
    \global\advance\sb@needlen by -\dp\tw@
  \endgroup
  \sbneedspace{\sb@needlen}%
}

% O \@afterheading do LaTeX crava \clubpenalty em 10000 depois de todo titulo,
% o que proibe deixar UMA linha de corpo sob o titulo no pe da pagina — a menor
% unidade indivisivel vira titulo mais duas linhas. Como o criterio combinado e
% titulo mais uma linha, a penalidade precisa ser alta mas finita: continua
% desencorajada, deixa de ser impossivel. O \widowpenalty segue infinito, entao
% um paragrafo de duas linhas ainda nao se parte.
\renewcommand{\@afterheading}{%
  \@nobreaktrue
  \everypar{%
    \if@nobreak
      \@nobreakfalse
      \clubpenalty 300\relax
      \if@afterindent\else
        {\setbox\z@\lastbox}%
      \fi
    \else
      \clubpenalty\@clubpenalty
      \everypar{}%
    \fi}}
\makeatother
\newcommand{\sbkicker}[1]{%
  \vspace{2.2em}%
  {\noindent\color{sbink}\rule{\linewidth}{0.7pt}}\par\nobreak
  \vspace{0.55em}%
  % Corpo \small (nao \footnotesize): um numeral solto — "I", "V" — em
  % footnotesize sumia ao lado de um titulo de 18pt e lia como sujeira de
  % pagina em vez de rotulo. Espacejamento maior pelo mesmo motivo.
  {\noindent\small\addfontfeatures{LetterSpace=28}\color{sbink}\MakeUppercase{#1}}\par\nobreak
  \vspace{0.4em}%
  % O titlesec emite `\addpenalty{\@secpenalty}` antes do titulo, e no TeX
  % todo no de penalidade e ponto de quebra legal: era por ali que a pagina
  % terminava com o filete dourado e o titulo abria a pagina seguinte. O
  % `\addpenalty` do LaTeX se abstem quando `\@nobreak` esta ligado, e o
  % `\everypar` o desliga sozinho no primeiro paragrafo do capitulo.
  \sbnobreak
}

% Referencias com recuo pendente
% Referencias com recuo pendente.
% `\hangindent` vale para UM paragrafo e e zerado no `\par` seguinte — como
% o Pandoc emite o texto da referencia como bloco proprio, o recuo se perdia
% e todas as linhas saiam rentes a margem. `\leftskip` + `\parindent`
% negativo sao parametros de forma de paragrafo: valem para todo `\par`
% dentro do grupo, entao o recuo sobrevive a quantos blocos o Pandoc gerar.
\newenvironment{sbrefitem}{%
  \par\begingroup\small
  \setlength{\leftskip}{2.2em}%
  \setlength{\parindent}{-2.2em}%
  \setlength{\parskip}{0pt}%
}{%
  \par\endgroup\vspace{0.45em}%
}

% Hierarquia de titulos (Titulo 1 = 18pt > Titulo 2 = 15.5pt > Titulo 3 = 13pt) — sem hifenizacao
\titleformat{\section}{\huge\bfseries\color{sblink}\raggedright\hyphenpenalty=10000\exhyphenpenalty=10000}{}{0em}{}
\titleformat{\subsection}{\fontsize{18pt}{22pt}\selectfont\addfontfeatures{LetterSpace=-1.5}\bfseries\color{sblink}\raggedright\hyphenpenalty=10000\exhyphenpenalty=10000}{}{0em}{}
% `###` distingue-se de `##` por FAMILIA e COR, nao so por corpo: 15,5pt
% bold serif preto contra 18pt bold serif preto eram praticamente o mesmo
% titulo, e um `###` no pe da pagina lia como abertura de capitulo.
% Libertinus Sans em grafite resolve sem introduzir cor nova.
\titleformat{\subsubsection}{\fontsize{13pt}{16pt}\selectfont\sffamily\bfseries\color{sbgraphite}\raggedright\hyphenpenalty=10000\exhyphenpenalty=10000}{}{0em}{}
\titleformat{\paragraph}{\fontsize{13pt}{16pt}\selectfont\bfseries\color{sblink}\raggedright\hyphenpenalty=10000\exhyphenpenalty=10000}{}{0em}{}
\titlespacing*{\section}{0pt}{2em}{0.8em}
\titlespacing*{\subsection}{0pt}{0pt}{0.45em}
\titlespacing*{\subsubsection}{0pt}{1.2em}{0.35em}
\titlespacing*{\paragraph}{0pt}{0.9em}{0.25em}
\setlength{\parskip}{0.6em}
\setlength{\parindent}{0pt}
\onehalfspacing
"""


def insert_page_break_after_sumario(body):
    """Pagina 1 = titulo + Sumario; o ensaio comeca na pagina 2.

    Roda DEPOIS de convert_section_separators, que ja removeu o `---` de
    fecho do Sumario. Quando existe Sumario, a primeira secao seguinte
    recebe \\newpage: a pagina 1 fica so com titulo/autor/subtitulo/Sumario
    e o capitulo 1 abre a pagina 2 (com o filete do proprio titulo). Se o
    essay nao tiver Sumario (caso dos handouts), nada muda.
    """
    lines = body.split('\n')
    sumario_idx = None
    for i, line in enumerate(lines):
        if re.match(r'^##\s+Sum[áa]rio\s*$', line, flags=re.IGNORECASE):
            sumario_idx = i
            break
    if sumario_idx is None:
        return body

    for j in range(sumario_idx + 1, len(lines)):
        if re.match(r'^##\s', lines[j]):
            lines[j] = '\\newpage\n' + lines[j]
            return '\n'.join(lines)
    return body


# ---------------------------------------------------------------------------
# Chapter kickers (semantic labels for ## headings in PDF)
# ---------------------------------------------------------------------------
# Palavras que nomeiam a seção inteira. Casadas ANCORADAS no início do título
# (com número/rótulo opcional antes), como no template HTML: sem a âncora,
# "Previsão de Conclusão com Modelos" viraria um capítulo rotulado CONCLUSÃO.
SEMANTIC_RE = re.compile(
    r'^\s*(?:(?:secao|capitulo|parte)\s*)?(?:\d+|[IVXLC]+)?\s*[.:\-]?\s*'
    r'(introducao|conclusao|conclusion|referencias|references|bibliography|'
    r'sumario|summary|abstract|resumo(?:\s+executivo)?|prefacio|prologo|'
    r'epilogo|posfacio|agradecimentos|apendice|anexos?)\b'
)

# Seções que são aparato do documento, não capítulos — excluídas da
# contagem de capítulos da capa.
#
# Casa o título INTEIRO, não o prefixo: com `\b` no fim, o capítulo
# "Índice de Experimentos Mentais e Evidências Empíricas" (um capítulo de
# verdade, em quem-e-voce) era lido como sumário e sumia da contagem.
# O sufixo opcional cobre as variantes reais ("Referências Bibliográficas")
# sem abrir a porta para qualquer continuação.
SEMANTIC_APARATO_RE = re.compile(
    r'^(?:sumario|summary|indice|referencias|references|bibliography)'
    r'(?:\s+(?:bibliograficas?|citadas?|consultadas?))?$'
)

SEMANTIC_LABELS = {
    'introducao': 'Introdução', 'conclusao': 'Conclusão',
    'conclusion': 'Conclusão', 'referencias': 'Referências',
    'references': 'Referências', 'bibliography': 'Referências',
    'sumario': 'Sumário', 'summary': 'Sumário',
    'abstract': 'Resumo', 'resumo': 'Resumo',
    'resumo executivo': 'Resumo Executivo',
    'prefacio': 'Prefácio', 'prologo': 'Prólogo', 'epilogo': 'Epílogo',
    'posfacio': 'Posfácio', 'agradecimentos': 'Agradecimentos',
    'apendice': 'Apêndice', 'anexo': 'Anexo', 'anexos': 'Anexos',
}

SECTION_RE = re.compile(
    r'^(#{1,4})\s+(?:(\d+(?:\.\d+)*)\.\s*)?(.+?)\s*$'
)

ROMAN_MAP = {'1':'I','2':'II','3':'III','4':'IV','5':'V',
             '6':'VI','7':'VII','8':'VIII','9':'IX','10':'X',
             '11':'XI','12':'XII','13':'XIII','14':'XIV','15':'XV',
             '16':'XVI','17':'XVII','18':'XVIII','19':'XIX','20':'XX'}


# Prefixo de numeração do próprio título, árabe OU romano:
# "## 3. Título", "## 3.1 Título", "## VI. Título", "## IV - Título".
# `SECTION_RE` só enxerga o árabe; sem esta segunda passada o romano
# sobrevivia no título e o PDF imprimia "VI" no kicker e "VI. Teoria..."
# logo abaixo — a numeração duas vezes na mesma abertura de capítulo.
HEADING_NUM_RE = re.compile(
    r'^(#{2})\s+(?:(\d+(?:\.\d+)*)|([IVXLC]+))\s*[.\-–:]\s*(.+?)\s*$'
)


def _detect_self_numbered(heading_text):
    """Numeral escrito pelo autor no título, na grafia original, ou None."""
    m = HEADING_NUM_RE.match(heading_text)
    if not m:
        return None
    return m.group(2) or m.group(3)


def _semantic_label(heading_text):
    """Palavra que nomeia a seção (Introdução, Conclusão...), ou None."""
    m = SECTION_RE.match(heading_text)
    if not m:
        return None
    _, _, title = m.groups()
    slug = re.sub(r'\s+', ' ', unidecode(title).lower().strip())
    sem = SEMANTIC_RE.match(slug)
    if not sem:
        return None
    return SEMANTIC_LABELS.get(sem.group(1), sem.group(1).capitalize())


def _roman(num):
    parts = str(num).split('.')
    label = ROMAN_MAP.get(parts[0], parts[0])
    if len(parts) > 1:
        label = f"{label}.{parts[1]}"
    return label


_LATEX_ESCAPE = {
    '\\': r'{\textbackslash}', '{': r'\{', '}': r'\}', '$': r'\$',
    '&': r'\&', '#': r'\#', '%': r'\%', '_': r'\_',
    '~': r'{\textasciitilde}', '^': r'{\textasciicircum}',
}


def _titulo_para_medicao(titulo):
    """Titulo em texto plano, seguro para ir num argumento de macro.

    Serve so para medir altura, entao enfase, links e matematica podem virar o
    proprio texto: o que muda a contagem de linhas e a quantidade de caracteres,
    nao a marcacao.
    """
    texto = re.sub(r'\[\[(?:[^\]|]*\|)?([^\]]*)\]\]', r'\1', titulo)
    texto = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', texto)
    texto = re.sub(r'[*`]+', '', texto)
    return ''.join(_LATEX_ESCAPE.get(c, c) for c in texto)


def _subtitulo_colado(lines, idx):
    """Texto do `###` colado logo abaixo do `##`, ou string vazia.

    Colado quer dizer sem corpo entre os dois. Nesse caso os dois titulos e
    as primeiras linhas de texto formam um bloco unico, e a reserva precisa
    cobrir tambem o subtitulo.
    """
    j = idx + 1
    while j < len(lines) and not lines[j].strip():
        j += 1
    if j >= len(lines):
        return ''
    m = re.match(r'^###\s+(.*)$', lines[j])
    return m.group(1).strip() if m else ''


def _sob_titulo_pai(lines, idx):
    """O titulo em `idx` vem colado logo abaixo de um titulo um nivel acima?

    Nesse caso ele ja esta dentro do bloco medido pelo titulo de cima, e
    reservar espaco de novo por conta propria plantaria um ponto de quebra
    exatamente onde nao pode haver um.
    """
    m = re.match(r'^(#{3,4})\s', lines[idx])
    if not m:
        return False
    j = idx - 1
    while j >= 0 and not lines[j].strip():
        j -= 1
    if j < 0:
        return False
    pai = re.match(r'^(#{2,3})\s', lines[j])
    return bool(pai) and len(pai.group(1)) == len(m.group(1)) - 1


def _titulo_colado(lines, idx):
    """A linha `idx` e um titulo seguido, sem corpo entre eles, por um titulo
    um nivel mais fundo?

    Nesse caso os dois formam um bloco unico, e o `\\sbneedspace` do titulo de
    baixo precisa ser suprimido: a penalidade que ele planta para medir a pagina
    seria o unico ponto de quebra entre os dois, e era por ela que o titulo de
    cima acabava sozinho no pe da pagina.
    """
    m = re.match(r'^(#{2,3})\s', lines[idx])
    if not m:
        return False
    nivel = len(m.group(1))
    j = idx + 1
    while j < len(lines) and not lines[j].strip():
        j += 1
    if j >= len(lines):
        return False
    n = re.match(r'^(#{3,4})\s', lines[j])
    return bool(n) and len(n.group(1)) == nivel + 1


def inject_chapter_kickers(body):
    """Insere `\\sbkicker{}` antes de cada `##`.

    Todo `##` recebe kicker — é o comando que desenha o filete de capítulo e
    o respiro acima do título (`\\titlespacing` do `\\subsection` é 0pt de
    propósito). Um `##` sem kicker colaria no parágrafo anterior.

    O rótulo é a palavra semântica quando o título a nomeia (Introdução,
    Conclusão, Referências...); caso contrário é o numeral do capítulo.

    O numeral respeita a grafia do autor: `## 3. Título` vira kicker "3",
    `## VI. Título` vira "VI". Quando o essay não numera, o contador
    sequencial usa ARÁBICO — as subseções (`### 3.1`) são sempre arábicas, e
    um kicker "III" acima de um "3.1" punha dois sistemas de numeração na
    mesma página.

    Capítulo numerado tem o prefixo removido do título: o numeral já vive no
    kicker e apareceria duas vezes.
    """
    lines = body.split('\n')
    out = []
    chapter_no = 0
    for idx, line in enumerate(lines):
        m = SECTION_RE.match(line)
        if not (m and len(m.group(1)) == 2):
            sub = re.match(r'^(#{3,4})\s+(.*)$', line)
            if sub and not _sob_titulo_pai(lines, idx):
                out.append(
                    f'\\sbsubneed{{{len(sub.group(1))}}}'
                    f'{{{_titulo_para_medicao(sub.group(2).strip())}}}')
            out.append(line)
            if _titulo_colado(lines, idx):
                out.append('\\sbskipnextneed')
            continue

        num = _detect_self_numbered(line)
        label = _semantic_label(line)
        heading = line

        if num:
            # O prefixo sai do título SEMPRE que existe — inclusive em
            # "## 9. Conclusão", onde o rótulo é a palavra e o "9." ficaria
            # sobrando ao lado dela.
            nm = HEADING_NUM_RE.match(line)
            heading = f'## {nm.group(4)}'
            if nm.group(2):
                chapter_no = int(nm.group(2).split('.')[0])
            if label is None:
                label = num
        elif label is None:
            chapter_no += 1
            label = str(chapter_no)

        anchor = heading_anchor(line)
        out.append(f'\\hypertarget{{{anchor}}}{{}}')
        out.append(
            f'\\sbchapterneed{{{label}}}'
            f'{{{_titulo_para_medicao(heading[3:].strip())}}}'
            f'{{{_titulo_para_medicao(_subtitulo_colado(lines, idx))}}}')
        out.append(f'\\sbkicker{{{label}}}')
        out.append(heading)
        if _titulo_colado(lines, idx):
            out.append('\\sbskipnextneed')
    return '\n'.join(out)


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
    
    # Separadores de secao com largura proporcional ao nivel do titulo
    body = convert_section_separators(body)

    # Pagina 1 = titulo + Sumario; ensaio comeca na pagina 2
    body = insert_page_break_after_sumario(body)
    
    # Resolve image paths to absolute
    body = resolve_image_paths(body, Path(filepath).parent)
    
    # Caixas de realce -> fenced divs semanticos (mesmo preprocessador do
    # HTML; o filtro pdf_boxes.lua os converte em ambientes LaTeX). Roda
    # DEPOIS de remove_h1_and_byline — senao as bylines `> Ensaio` /
    # `> Gustavo Zambrano ...` seriam classificadas como rotulo+conteudo
    # e virariam caixa.
    body = transform_markdown(body)
    
    # Chapter kickers: semantic labels (Introdução, Conclusão, Referências)
    # inserted as \sbkicker{} before each ## heading.
    body = inject_chapter_kickers(body)
    
    # Escape quotes in title for YAML and format for raw LaTeX cover
    safe_title = title.replace('"', '\\"')
    safe_title_latex = re.sub(r'[_*]([^\n_*]+)[_*]', r'\\textit{\1}', title)
    safe_title_latex = (safe_title_latex.replace('&', '\\&').replace('%', '\\%').replace('#', '\\#'))
    safe_title_latex = re.sub(r'(?<!\\)_', r'\\_', safe_title_latex)
    
    # Stats for cover meta-line
    word_count = len(re.findall(r'\b\w+\b', body))
    reading_time = max(1, round(word_count / 250))
    # Só capítulos de conteúdo: `## Sumário` e `## Referências` são aparato,
    # não capítulos. Contá-los dava "13 cap." num essay de 11 — e o HTML,
    # que já os exclui, mostrava um número diferente para o mesmo essay.
    chapter_count = sum(
        1 for h in re.findall(r'^##\s+(.+)$', body, flags=re.MULTILINE)
        if not SEMANTIC_APARATO_RE.match(unidecode(h).lower().strip())
    )
    # Rascunho ocupa o LUGAR do tempo de leitura (mesma regra do export HTML
    # e do leitor do grafo): num draft a duração ainda não significa nada, e
    # o estado significa. Só `draft` é marcado; `finalizado` não recebe nada.
    if str(meta.get('status') or '').strip().lower() == 'draft':
        meta_line = "Rascunho"
    else:
        meta_parts = []
        if chapter_count:
            meta_parts.append(f"{chapter_count} cap.")
        meta_parts.append(f"{reading_time} min de leitura")
        meta_line = " · ".join(meta_parts)
    
    # Escape subtitle for LaTeX
    safe_subtitle = ''
    if subtitle:
        safe_subtitle = (subtitle.replace('&', '\\&').replace('#', '\\#')
                         .replace('%', '\\%').replace('_', '\\_'))
    
    # Include-before: cover page as raw LaTeX (directly in YAML block scalar)
    include_before = f"\\sbcover{{{safe_title_latex}}}{{{author_date}}}{{{safe_subtitle}}}{{{meta_line}}}"
    include_before_indented = "\n".join("    " + line for line in include_before.split("\n"))
    
    # Wrapped in a ```{=latex} fence so Pandoc's Markdown reader treats this
    # YAML block-scalar as raw LaTeX verbatim, instead of parsing it as
    # Markdown first. Without the fence, sequences like `}[...]` right after
    # a closing brace (e.g. \setmainfont{X}[RawFeature={...}]) get
    # misread as a Markdown link reference and come out corrupted
    # (stray {[} / {]} / escaped braces) in the final LaTeX.
    header_body = "```{=latex}\n" + HEADER_TEX.strip() + "\n```"
    header_indented = "\n".join("    " + line for line in header_body.split("\n"))

    # Build new YAML frontmatter for Pandoc
    pandoc_meta = f"""---
title: "{safe_title}"
author: "{author_date}"
lang: pt-BR
documentclass: article
classoption:
  - 12pt
  - a4paper
geometry:
  - top=17mm
  - bottom=19mm
  - left=19mm
  - right=19mm
header-includes:
  - |
{header_indented}
include-before:
  - |
{include_before_indented}
---

"""
    
    return pandoc_meta + body


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
        '-V', 'urlcolor=sburl',
        '-V', 'linkcolor=sblink',
        '-V', 'citecolor=sburl',
        f'--resource-path={filepath.parent}',
        # Fenced divs semanticos -> ambientes tcolorbox (wikibox/wikiquote/
        # wikipull/wikicard) + legendas "Fig. N" em corpo menor.
        f'--lua-filter={LUA_FILTER}',
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
        # Sem +hard_line_breaks (mesma decisão do export HTML): as quebras
        # duras agora são aplicadas apenas DENTRO das caixas pelo
        # pré-processador; globalmente, transformavam todo parágrafo corrido
        # em uma pilha de quebras de linha.
                # +lists_without_preceding_blankline: 28 listas em 10 essays do corpus
        # são escritas coladas no parágrafo que as introduz ("...pode:" seguido
        # direto de "- Ler ..."). Sem a extensão o Pandoc não deixa a lista
        # interromper o parágrafo e ela sai como prosa corrida com hífens
        # literais no meio da frase, nos DOIS exports. Ligar aqui corrige o
        # corpus inteiro sem editar um `.md` sequer.
        '-f', 'markdown+smart+tex_math_dollars+pipe_tables+strikeout+superscript+subscript-implicit_figures+gfm_auto_identifiers+lists_without_preceding_blankline',
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
