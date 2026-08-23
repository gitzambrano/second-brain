#!/usr/bin/env python3
"""
html_preprocess.py - Converte os padroes de caixa do corpus em fenced divs
semanticos que o template HTML estiliza como componentes.

Roda DEPOIS de remove_h1_and_byline e ANTES do Pandoc, apenas no fluxo HTML
(o PDF mantem seu proprio pipeline e nao passa por aqui).

Padroes reconhecidos (genericos valem para qualquer essay futuro):

1. Rotulo + bloco      "> Experimento Mental I"   /  "> Evidencia Empirica II"
   (blockquote de uma  "> Mapa Conceitual", "> Precisao Conceitual"
   linha so, seguido   "> Ataque I", "> Nivel III", "**Ideia 01**",
   de outro bloco)     avisos com ⚠/🚫  ->  ::: .box .<tipo>
                        com badge, titulo, corpo em paragrafos proprios
                        e faixa de veredito (**Veredicto:** extraido).

2. Card de filosofo    nome / "AAAA – AAAA · instituicao" / bio
                       -> ::: .card .filosofo

3. Card de obra        titulo / "Autor · Ano" (+ corpo, inclusive em
   continuacao         continuacao preguicosa de blockquote)
   preguicosa          -> ::: .card .livro

4. Citacao destacada   ultima linha casa padrao de atribuicao
                       ("Autor, Obra (ano)", "(parafrase)", "- Autor")
                       -> ::: .pull-quote com .pq-cite

5. Bloco de citacao    qualquer outro blockquote -> ::: .quote
   simples             preservando versos via quebra dura dentro do paragrafo.

6. Rotulo solto        rotulo de uma linha NAO seguido de outro blockquote
                       -> ::: .label-solo (mini-cabecalho mono antes de listas)

7. Ornamento           paragrafo so de glifos ("· · ·", "infinito") ->
                       <div class="ornament">

Tudo que nao casa sai intocado: o transformador e no-op seguro para essays
sem caixas (handouts, por exemplo).
"""

import re

# ---------------------------------------------------------------------------
# Classificadores
# ---------------------------------------------------------------------------

BOX_LABEL_RULES = [
    (re.compile(r'^\*{0,2}Experimento Mental', re.I), 'experimento'),
    (re.compile(r'^\*{0,2}Evid[eê]ncia Emp[ií]rica', re.I), 'evidencia'),
    (re.compile(r'^\*{0,2}(Mapa|Precis[aã]o) Conceitual$', re.I), 'mapa'),
    (re.compile(r'^\*{0,2}Ataque\s+[IVXLC]', re.I), 'ataque'),
    (re.compile(r'^\*{0,2}N[ií]vel\s+[IVXLC]', re.I), 'nivel'),
    (re.compile(r'^\*{0,2}Ideia\s*\d+\*{0,2}$', re.I), 'ideia'),
]

AVISO_RE = re.compile(r'^\*{0,2}(?:⚠|🚫|❗|Aten[cç][aã]o)', re.I)

PHILO_RE = re.compile(r"^\d{4}\s*[–—]\s*(?:\d{4}|presente)\b\s*·\s*\S")

BOOK_RE = re.compile(r'^[^·\n]{2,60}·\s*\d{4}$')

VERDICT_RE = re.compile(
    r'^\*\*(Veredicto(?:\s+provis[oó]rio)?)[:\*]*\*\*:?\s*(.*)$',
    re.IGNORECASE,
)

ORNAMENT_RE = re.compile(r'^[·•∙∞⑂✻❦🌍🫧\s]{1,15}$')

# Glifos de origem com cobertura fontes fragil -> substitutos universais.
# Mapa extensivel: chave = glifo problemático no fonte, valor = seguro.
GLYPH_MAP = {
    '\u2442': '\u2234',   # OCR fork -> therefore
}


def _safe_glyph(g):
    return GLYPH_MAP.get(g, g)

# Linha-meta de ficha de agente/ferramenta: "Modelos: a · b", "Backend: x · y"
META_LINE_RE = re.compile(r'^[A-Za-zÀ-ÿ][\wÀ-ÿ ]{0,18}:\s')

ATTRIB_MAX_LEN = 100


def _is_attribution(text):
    """Ultima linha de citacao que identifica o autor/obra."""
    t = text.strip()
    if len(t) > ATTRIB_MAX_LEN or len(t) < 4:
        return False
    if t.startswith(('—', '–')):
        return True
    if t.startswith('Adaptado de'):
        return True
    if re.search(r'\(\d{4}\)\s*(\(par[aá]frase\))?$', t):
        return True
    if re.search(r'\(par[aá]frase\)$', t):
        return True
    # "Heráclito de Éfeso, séc. V a.C." / "Buddhaghosa, Visuddhimagga, séc. V d.C."
    if 'séc.' in t and ',' in t:
        return True
    return False


def _classify_label(text):
    """Texto do rotulo -> classe css do tipo de caixa (ou None)."""
    t = text.strip()
    if AVISO_RE.match(t):
        return 'aviso'
    for rx, cls in BOX_LABEL_RULES:
        if rx.search(t):
            return cls
    return None


def _strip_bold(text):
    return re.sub(r'^\*{1,2}(.*?)\*{1,2}$', r'\1', text.strip())


def _title_like(t):
    """Linha curta, sem pontuacao final e sem marca de citacao/enfase:
    candidato a titulo de caixa. Regra de FORMA, nao de conteudo."""
    t = t.strip()
    if not t or len(t) > 60:
        return False
    if re.search(r'[.!?:;,]$', t):
        return False
    if re.match(r'^[*_“”"\x27‘’—–\-•·]', t):
        return False
    if HEADING_RE.match(t):
        return False
    return True


def _split_titled(stanzas):
    """Divide um bloco de citacao em caixas guiadas por linhas-titulo.

    Regra generica de forma: cada segmento abre com linha-titulo e contem
    ao menos uma linha de corpo (nao-titulo); glifos-ornamento entre
    segmentos sao devolvidos para emissao intermediaria. Se o padrao nao
    cobre o bloco INTEIRO, retorna ([], {}) e o chamador cai para citação
    simples — nunca pela metade.
    """
    lines = [ln.strip() for s in stanzas for ln in s if ln.strip()]
    items = []                       # ('seg', [linhas]) | ('orn', glifo)
    cur = None

    def close():
        nonlocal cur
        if cur:
            items.append(('seg', cur))
            cur = None

    for ln in lines:
        if ORNAMENT_RE.match(ln):
            close()
            items.append(('orn', ln.split()[0]))
            continue
        if cur is not None and _title_like(ln) \
                and any(not _title_like(x) for x in cur):
            close()                  # titulo no meio do corpo: novo segmento
        if cur is None:
            cur = [ln]
        else:
            cur.append(ln)
    close()

    segs = [it[1] for it in items if it[0] == 'seg']
    if not segs:
        return [], {}

    def _seg_kind(s):
        if s and _title_like(s[0]) and any(not _title_like(x) for x in s[1:]):
            return 'box'          # titulo + corpo: caixa propriamente dita
        if s and all(_title_like(x) for x in s):
            return 'intro'        # so linhas-titulo: lenda/caption do conjunto
        return 'plain'

    kinds = [_seg_kind(s) for s in segs]
    if kinds.count('box') < 1 or any(k == 'plain' for k in kinds):
        return [], {}

    ornaments = {}
    pending, idx = None, 0
    for kind_i, val in items:
        if kind_i == 'orn':
            pending = val
        else:
            if pending and idx > 0:
                ornaments[idx] = _safe_glyph(pending)
            pending = None
            idx += 1
    return segs, ornaments


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

class QuoteGroup:
    """Grupo de linhas de blockquote.

    lines: lista de tuplas ('br', None) para quebra de estrofe ou
           ('ln', texto) para linha logica.
    """

    def __init__(self):
        self.lines = []

    def add_break(self):
        if self.lines and self.lines[-1][0] == 'ln':
            self.lines.append(('br', None))

    def add_line(self, text):
        text = text.rstrip()
        if text.strip() == '':
            self.add_break()
        else:
            self.lines.append(('ln', text))

    def stanzas(self):
        """Lista de estrofes; cada estrofe e lista de linhas logicas."""
        out, cur = [], []
        for kind, val in self.lines:
            if kind == 'br':
                if cur:
                    out.append(cur)
                    cur = []
            else:
                cur.append(val)
        if cur:
            out.append(cur)
        return out


FENCE_RE = re.compile(r'^\s*```')
HEADING_RE = re.compile(r'^#{1,6}\s')
QUOTE_RE = re.compile(r'^\s*>')


def parse_blocks(lines):
    """Divide o corpo em blocos: ('quote', QuoteGroup), ('raw', [lines])."""
    blocks = []
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        if FENCE_RE.match(line):
            j = i + 1
            while j < n and not FENCE_RE.match(lines[j]):
                j += 1
            j = min(j + 1, n)
            blocks.append(('raw', lines[i:j]))
            i = j
            continue
        if QUOTE_RE.match(line):
            grp = QuoteGroup()
            while i < n:
                cur = lines[i]
                if QUOTE_RE.match(cur):
                    grp.add_line(re.sub(r'^\s*>\s?', '', cur))
                    i += 1
                elif (grp.lines
                      and cur.strip() != ''
                      and not HEADING_RE.match(cur)
                      and not FENCE_RE.match(cur)
                      and _prev_was_quote(lines, i)):
                    # Continuacao preguicosa: linha solta colada no blockquote.
                    grp.add_line(cur)
                    i += 1
                else:
                    break
            blocks.append(('quote', grp))
            continue
        # Paragrafo solto (inclui listas, tabelas, prosa): agrupa ate linha vazia.
        j = i
        while j < n and lines[j].strip() != '' and not QUOTE_RE.match(lines[j]):
            j += 1
        if j > i:
            blocks.append(('raw', lines[i:j]))
        i = j
        # Consome a linha vazia separadora, se houver.
        if i < n and lines[i].strip() == '':
            i += 1
    return blocks


def _prev_was_quote(lines, i):
    """A linha fisica anterior era de blockquote? (p/ continuacao preguicosa)"""
    k = i - 1
    while k >= 0 and lines[k].strip() == '':
        k -= 1
    return k >= 0 and QUOTE_RE.match(lines[k])


def _section_boundary(blk):
    """Bloco inicia nova secao? H1/H2 ou regua horizontal (---)."""
    first = blk[0].strip() if blk else ''
    if not first:
        return False
    if re.match(r'^(-{3,}|_{3,}|\*{3,})$', first):
        return True
    m = HEADING_RE.match(first)
    return bool(m and len(first) - len(first.lstrip('#')) <= 2)


# ---------------------------------------------------------------------------
# Emissores
# ---------------------------------------------------------------------------

def _paras(stanzas, hard_break=False):
    """Estrofes -> paragrafos markdown prontos para fenced div."""
    out = []
    for s in stanzas:
        sep = '  \n' if hard_break else '\n'
        out.append(sep.join(s))
    return out


def _div(cls, inner_lines):
    return ['', '::: {.%s}' % cls, ''] + inner_lines + [':::', '']


def emit_verdict(verdict_matches):
    """[(tag, resto), ...] -> linhas do footer .box-verdict."""
    out = ['', '::: {.box-verdict}', '']
    first = True
    for tag, resto in verdict_matches:
        if not first:
            out.append('')
        out.append('[%s]{.verdict-tag}' % tag)
        if resto.strip():
            out.append('')
            out.append(resto.strip())
        first = False
    out += [':::', '']
    return out


def emit_typed_box(cls, badge, title, body_lines, verdicts):
    out = ['', '::: {.box .%s}' % cls, '']
    if badge:
        out += ['::: {.box-badge}', '', badge, ':::', '']
    if title:
        out += ['::: {.box-title}', '', title, ':::', '']
    for p in body_lines:
        if p.strip():
            out += ['', p.strip()]
    if verdicts:
        out += emit_verdict(verdicts)
    out += [':::', '']
    return out


def emit_pull_quote(stanzas, cite):
    out = ['', '::: {.pull-quote}', '']
    for p in _paras(stanzas, hard_break=True):
        out += [p, '']
    if cite:
        out += ['::: {.pq-cite}', '', cite.strip(), ':::', '']
    out += [':::', '']
    return out


def emit_quote(stanzas):
    return _div('quote', sum(([p, ''] for p in _paras(stanzas, hard_break=True)), []))


def emit_card(kind, name, meta, body_lines):
    out = ['', '::: {.card .%s}' % kind, '']
    out += ['::: {.card-name}', '', name.strip(), ':::', '']
    if meta:
        out += ['::: {.card-meta}', '', meta.strip(), ':::', '']
    for p in body_lines:
        if p.strip():
            out += ['', p.strip()]
    out += [':::', '']
    return out


# ---------------------------------------------------------------------------
# Transformacao principal
# ---------------------------------------------------------------------------

def _extract_verdicts(paras):
    """Separa paragrafos-veredito do corpo. Retorna (corpo, vereditos)."""
    body, verdicts = [], []
    for p in paras:
        flat = p.replace('  \n', ' ').replace('\n', ' ')
        m = VERDICT_RE.match(flat.strip())
        if m:
            verdicts.append((m.group(1), m.group(2)))
        else:
            body.append(p)
    return body, verdicts


def _is_label_candidate(grp):
    st = grp.stanzas()
    if len(st) != 1 or len(st[0]) != 1:
        return False
    t = st[0][0].strip()
    if t.startswith(('(', '“', '"')):
        return False
    # Itálico (*texto* / _texto_): é citação, não rótulo.
    # ('**Negrito**' continua candidato — ex.: "**Ideia 01**".)
    if re.match(r'^(\*[^*\s]|_[^\s])', t):
        return False
    # Numero puro ("58%", "1997") nunca é rótulo.
    if not re.search(r'[^\W\d_]', t):
        return False
    if _classify_label(t) or AVISO_RE.match(t):
        return True
    return len(t) <= 48 and not re.search(r'[.!?:;]\s*$', t)


def _transform_group(grp, next_grp, raw_chain=None):
    """Transforma um grupo de blockquote.

    Retorna (linhas, used) onde `used` informa quantos blocos ALEM do
    proprio grupo foram consumidos: 0 = nada; 'q' = o next_quote (fusao
    de caixa); N = os N primeiros blocos de raw_chain (caixa rotulo+conteudo).
    O chamador avanca o cursor de acordo — assim regras que NAO usam o
    contexto seguinte (stat, card, quote simples) nunca engolem conteudo."""
    raw_chain = raw_chain or []

    # 1. Rotulo + bloco de citacao na sequencia -> caixa tipada fundida.
    #    (Se o bloco seguinte tambem e rotulo, nao funde: cada um com seu
    #    proprio destino.)
    if next_grp is not None and _is_label_candidate(grp) \
            and not _is_label_candidate(next_grp):
        label = _strip_bold(grp.stanzas()[0][0])
        cls = _classify_label(label) or 'generico'
        flat = [ln for s in next_grp.stanzas() for ln in s]
        title = flat[0] if flat else ''
        body_lines = flat[1:]
        body, verdicts = _extract_verdicts(body_lines)
        return emit_typed_box(cls, label, title, body, verdicts), 'q'

    st = grp.stanzas()
    flat = [ln for s in st for ln in s]
    is_label = _is_label_candidate(grp)

    # 3. Rotulo + prosa/lista/heading -> caixa generica (badge + conteudo).
    #    Linhas de um mesmo bloco entram com quebra dura: listas associativas
    #    ("A" -> risco / "B" -> risco) nao colapsam em prosa corrida.
    if is_label and raw_chain:
        label = _strip_bold(flat[0])
        cls = _classify_label(label) or 'generico'
        body_lines = []
        for blk in raw_chain:
            body = '  \n'.join(ln.rstrip() for ln in blk if ln.strip())
            if body:
                body_lines.append(body)
        body, verdicts = _extract_verdicts(body_lines)
        return emit_typed_box(cls, label, '', body, verdicts), len(raw_chain)

    # 4. Rotulo solto sem conteudo aproveitado: mini-cabecalho mono.
    if is_label:
        return _div('label-solo', [_strip_bold(flat[0])]), 0

    # Card de filosofo: nome / datas·instituicao / bio
    if len(flat) >= 3 and PHILO_RE.match(flat[1].strip()):
        return emit_card('filosofo', flat[0], flat[1], flat[2:]), 0

    # Card de livro/filme: titulo / Autor · Ano / corpo
    if len(flat) >= 2 and len(flat[0]) <= 60 \
            and BOOK_RE.match(flat[1].strip()) \
            and not PHILO_RE.match(flat[1].strip()):
        return emit_card('livro', flat[0], flat[1], flat[2:]), 0

    # Pull quote: ultima linha e atribuicao (estrofe unica ou multipla)
    if len(flat) >= 2 and _is_attribution(flat[-1]):
        body_st = [s[:] for s in st]
        if body_st[-1][-1] is flat[-1]:
            body_st[-1].pop()
            if not body_st[-1]:
                body_st.pop()
        return emit_pull_quote(body_st, flat[-1]), 0

    # Citação de uma linha só já com atribuição embutida: "..." — Autor
    if len(st) == 1 and len(st[0]) == 1:
        m = re.match(r'^(.+[”"])\s*[—–]\s*(.{3,60})$', st[0][0].strip())
        if m:
            return emit_pull_quote([[m.group(1)]], m.group(2)), 0

    # Divisao em caixas por linha-titulo (genérica): citações contínuas
    # estruturadas por linhas-título ("Nível I — ...", "A Analogia do Dado")
    # viram caixas simples título+corpo; legendas sem corpo viram citação
    # simples; glifos entre elas viram ornamentos.
    segments, ornaments = _split_titled(st)
    if segments:
        out_lines = []
        for idx, seg in enumerate(segments):
            if idx > 0 and ornaments.get(idx):
                out_lines += ['<div class="ornament">%s</div>' % ornaments[idx], '']
            is_intro = all(_title_like(x) for x in seg)
            if is_intro:
                out_lines += emit_quote([seg])
            else:
                body_p, verdicts = _extract_verdicts(['  \n'.join(seg[1:])])
                out_lines += emit_typed_box('generico', '', seg[0], body_p, verdicts)
        return out_lines, 0

    # Citação simples
    return emit_quote(st), 0


def transform_markdown(body):
    """Ponto de entrada: corpo markdown -> corpo com fenced divs semanticos."""
    lines = body.split('\n')
    blocks = parse_blocks(lines)
    out = []

    i = 0
    while i < len(blocks):
        kind, payload = blocks[i]

        if kind == 'quote':
            j = i + 1
            nxt_quote, raw_chain = None, []
            if j < len(blocks):
                if blocks[j][0] == 'quote':
                    nxt_quote = blocks[j][1]
                elif blocks[j][0] == 'raw':
                    # Cadeia de blocos brutos consecutivos (prosa/lista/
                    # headings): candidatos a conteudo de caixa de um rotulo.
                    # Fronteira generica: H1/H2 ou regua horizontal encerram
                    # a cadeia — sao inicio de nova secao, nao conteudo da
                    # caixa (H3+ pode: subsecoes internas sao comuns).
                    raw_chain.append(blocks[j][1])
                    k = j + 1
                    while k < len(blocks) and blocks[k][0] == 'raw' \
                            and not _section_boundary(blocks[k][1]):
                        raw_chain.append(blocks[k][1])
                        k += 1
            lines_out, used = _transform_group(payload, nxt_quote, raw_chain)
            out.extend(lines_out)
            if used == 'q':
                i = j + 1          # grupo + quote fundidos
            elif isinstance(used, int) and used > 0:
                i = j + used       # grupo + N blocos brutos na caixa
            else:
                i = i + 1          # nada consumido alem do proprio grupo
            continue

        if kind == 'raw':
            # Paragrafo-so-de-glifos vira ornamento.
            text = '\n'.join(payload).strip()
            if text and ORNAMENT_RE.match(text) and not HEADING_RE.match(payload[0]):
                glyph = _safe_glyph(text.split()[0])
                out.append('<div class="ornament">%s</div>' % glyph)
                out.append('')
                i += 1
                continue

            # Subtitulo de agente/ferramenta: linha-nome curta seguida de
            # linha-meta "Label: ... · ..." (ex.: "Claude Code Anthropic" /
            # "Modelos: ... · ..."). O nome vira heading (###); regra simples,
            # bate 5/5 agentes no corpus, 0 falsos positivos.
            nxt2 = blocks[i + 1] if i + 1 < len(blocks) else None
            meta_line = '\n'.join(nxt2[1]).strip() \
                if (nxt2 and nxt2[0] == 'raw' and len(nxt2[1]) == 1) else ''
            if ('\n' not in text and len(text) <= 44 and len(text.split()) <= 5
                    and not re.search(r'[.:!?;,)\]]$', text)
                    and not HEADING_RE.match(payload[0])
                    and META_LINE_RE.match(meta_line) and '·' in meta_line
                    and len(meta_line) <= 70):
                out += ['### ' + text, '']
                i += 1
                continue

            out.extend(payload)
            out.append('')
            i += 1
            continue
        # blank
        i += 1

    result = '\n'.join(out)
    # Citacoes simples identicas adjacentes viram uma so — fontes as vezes
    # duplicam o callout; empilhadas, parecem numeros perdidos.
    result = re.sub(
        r'(::: \{\.quote\}\n\n([^\n]+)\n\n:::\n)'
        r'(?:\s*::: \{\.quote\}\n\n\2\n\n:::\n?)+',
        r'\1', result)
    # Normaliza 3+ linhas vazias.
    result = re.sub(r'\n{3,}', '\n\n', result)
    # Glifos fragis (GLYPH_MAP) viram substitutos universais em QUALQUER
    # posicao — podem viver em titulos de caixa, nao so em linhas-ornamento.
    for _bad, _good in GLYPH_MAP.items():
        result = result.replace(_bad, _good)
    return result.strip() + '\n'
