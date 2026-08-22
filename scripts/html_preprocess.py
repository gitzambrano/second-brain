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
    if t.startswith(('(', '“', '"')) or t.endswith(('.', '?', '!', ':', ';', ')')):
        return False
    if _classify_label(t) or AVISO_RE.match(t):
        return True
    return len(t) <= 48 and not re.search(r'[.!?:;]\s*$', t)


def _is_label_candidate(grp):
    st = grp.stanzas()
    if len(st) != 1 or len(st[0]) != 1:
        return False
    t = st[0][0].strip()
    if t.startswith(('(', '“', '"')) or t.endswith(('.', '?', '!', ':', ';', ')')):
        return False
    if _classify_label(t) or AVISO_RE.match(t):
        return True
    return len(t) <= 48 and not re.search(r'[.!?:;]\s*$', t)


def _transform_group(grp, next_grp):
    """Retorna linhas geradas para um grupo de blockquote."""
    if next_grp is not None and _is_label_candidate(grp):
        label = _strip_bold(grp.stanzas()[0][0])
        cls = _classify_label(label) or 'generico'
        flat = [ln for st in next_grp.stanzas() for ln in st]
        title = flat[0] if flat else ''
        body_lines = flat[1:]
        body, verdicts = _extract_verdicts(body_lines)
        return emit_typed_box(cls, label, title, body, verdicts)

    st = grp.stanzas()
    flat = [ln for s in st for ln in s]

    # Callout estatistico: blockquote so com numero ("58%", "1997").
    if next_grp is None and len(flat) == 1 \
            and re.match(r'^\d+([.,]\d+)?%?$', flat[0].strip()):
        return ['<div class="stat">%s</div>' % flat[0].strip(), '']

    # Rotulo solto sem outro blockquote na sequencia: mini-cabecalho mono
    # antes de prosa/lista (ex.: "**Ideia 01**", avisos com lista fora).
    if next_grp is None and _is_label_candidate(grp):
        return _div('label-solo', [_strip_bold(flat[0])])

    # Card de filosofo: nome / datas·instituicao / bio
    if len(flat) >= 3 and PHILO_RE.match(flat[1].strip()):
        return emit_card('filosofo', flat[0], flat[1], flat[2:])

    # Card de livro/filme: titulo / Autor · Ano / corpo
    if len(flat) >= 2 and len(flat[0]) <= 60 \
            and BOOK_RE.match(flat[1].strip()) \
            and not PHILO_RE.match(flat[1].strip()):
        return emit_card('livro', flat[0], flat[1], flat[2:])

    # Pull quote: ultima linha e atribuicao (estrofe unica ou multipla)
    if len(flat) >= 2 and _is_attribution(flat[-1]):
        body_st = [s[:] for s in st]
        if body_st[-1][-1] is flat[-1]:
            body_st[-1].pop()
            if not body_st[-1]:
                body_st.pop()
        return emit_pull_quote(body_st, flat[-1])

    # Citação de uma linha só já com atribuição embutida: "..." — Autor
    if len(st) == 1 and len(st[0]) == 1:
        m = re.match(r'^(.+[”"])\s*[—–]\s*(.{3,60})$', st[0][0].strip())
        if m:
            return emit_pull_quote([[m.group(1)]], m.group(2))

    # Citação simples
    return emit_quote(st)


def transform_markdown(body):
    """Ponto de entrada: corpo markdown -> corpo com fenced divs semanticos."""
    lines = body.split('\n')
    blocks = parse_blocks(lines)
    out = []

    i = 0
    while i < len(blocks):
        kind, payload = blocks[i]

        if kind == 'quote':
            nxt = None
            j = i + 1
            while j < len(blocks) and blocks[j][0] == 'blank':
                j += 1
            if j < len(blocks) and blocks[j][0] == 'quote':
                nxt = blocks[j][1]
            out.extend(_transform_group(payload, nxt))
            i = (j + 1) if nxt is not None else i + 1
            continue

        if kind == 'raw':
            # Paragrafo-so-de-glifos vira ornamento.
            text = '\n'.join(payload).strip()
            if text and ORNAMENT_RE.match(text) and not HEADING_RE.match(payload[0]):
                glyph = text.split()[0]
                out.append('<div class="ornament">%s</div>' % glyph)
                out.append('')
                i += 1
                continue
            out.extend(payload)
            out.append('')
            i += 1
            continue

        # blank
        i += 1

    result = '\n'.join(out)
    # Normaliza 3+ linhas vazias.
    result = re.sub(r'\n{3,}', '\n\n', result)
    return result.strip() + '\n'
