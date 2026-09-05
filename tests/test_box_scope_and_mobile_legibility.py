"""Escopo das caixas de realce e legibilidade no celular.

Três defeitos reais, todos invisíveis para os gates que existiam:

* um callout no meio de um capítulo engolia o resto do capítulo, porque só
  H1/H2 encerravam a cadeia de blocos que o rótulo absorve;
* o bloco de código sugado para dentro da caixa perdia as linhas em branco e
  ganhava quebra dura no fim de cada linha;
* dentro de célula de tabela, a `max-width:100%` do MathJax reduzia uma
  equação de 35ex a 4px de altura — ilegível, e sem disparar a checagem de
  overflow, já que encolher é justamente o que evita o overflow.
"""
import re
import sys
from pathlib import Path

import pytest
from conftest import SCRIPTS

sys.path.insert(0, str(SCRIPTS))
from html_preprocess import transform_markdown  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "scripts/essay_template.html"
SITE_ESSAY_JS = ROOT / "scripts/site_src/essay.js"


def _boxes(out: str) -> list[str]:
    """Corpo de cada fenced div `.box`, na ordem em que aparecem."""
    boxes, depth, cur = [], 0, None
    for line in out.split("\n"):
        opening = line.startswith("::: {")
        if opening and line.startswith("::: {.box}") is False and ".box" in line \
                and ".box-" not in line and cur is None:
            cur, depth = [], 1
            continue
        if cur is not None:
            if opening:
                depth += 1
            elif line.strip() == ":::":
                depth -= 1
                if depth == 0:
                    boxes.append("\n".join(cur))
                    cur = None
                    continue
            cur.append(line)
    return boxes


def test_callout_no_meio_da_prosa_fecha_no_primeiro_heading():
    md = (
        "## Seção\n\nProsa antes do rótulo.\n\n> **⚠ Atenção**\n\n"
        "Só este parágrafo é do callout.\n\n"
        "#### Subseção\n\nEsta prosa está fora da caixa.\n"
    )
    box = _boxes(transform_markdown(md))[0]
    assert "Só este parágrafo é do callout." in box
    assert "Subseção" not in box
    assert "fora da caixa" not in box


def test_rotulo_que_abre_a_secao_ainda_enquadra_as_subsecoes():
    """Padrão do corpus: `## Ideia 2` / `> **Ideia 02**` / subseções dentro."""
    md = (
        "## Ideia 2\n\n> **Ideia 02**\n\n### O Problema\n\nDiagnóstico.\n\n"
        "### A Abordagem\n\nProposta.\n\n---\n\n## Outra Seção\n\nFora.\n"
    )
    box = _boxes(transform_markdown(md))[0]
    assert "O Problema" in box and "A Abordagem" in box
    assert "Outra Seção" not in box


def test_rotulo_nao_engole_o_heading_de_secao_colado_nele():
    md = "Prosa.\n\n> **⚠ Atenção**\n\n## Próxima Seção\n\nCorpo da seção.\n"
    out = transform_markdown(md)
    assert not _boxes(out) or "Próxima Seção" not in _boxes(out)[0]


def test_bloco_de_codigo_dentro_da_caixa_sai_verbatim():
    md = (
        "Prosa.\n\n> **⚠ Atenção**\n\nParágrafo do callout.\n\n"
        "```\nprimeira linha\n\nlinha após vazia\n```\n"
    )
    box = _boxes(transform_markdown(md))[0]
    assert "primeira linha\n\nlinha após vazia" in box
    assert "primeira linha  \n" not in box


@pytest.mark.parametrize(
    "rule",
    [
        # Fórmula em célula fica no tamanho natural; quem rola é a tabela.
        ':is(td,th) mjx-container:not([display="true"]) svg{max-width:none;}',
        # Código dentro de caixa com o mesmo recuo dos parágrafos.
        ".box > pre,.card > pre,.quote > pre{margin:1.1rem 1.3rem;}",
        # `<pre><code>` do Pandoc: o corpo do bloco é só o do `pre`, sem que o
        # `.82em` do `code` multiplique — no celular dava 9,7px.
        "pre code{background:none;padding:0;font-size:inherit;}",
    ],
)
def test_template_mantem_as_regras_de_caixa_e_de_formula(rule):
    assert rule in TEMPLATE.read_text(encoding="utf-8")


def test_h5_tem_estilo_explicito_e_legivel():
    """H5 não pode cair no tamanho default pequeno do navegador."""
    css = TEMPLATE.read_text(encoding="utf-8")
    block = css.split("h5{", 1)[1].split("}", 1)[0]
    assert "font-size:1rem" in block
    assert "font-weight:700" in block


def test_math_inline_fica_mais_proxima_da_baseline():
    css = TEMPLATE.read_text(encoding="utf-8")
    block = css.split('mjx-container:not([display="true"]){', 1)[1].split("}", 1)[0]
    assert "vertical-align:-.15em;" in block
    assert "vertical-align:-.25em;" not in block


def test_display_math_mobile_reduz_dez_porcento_sem_tocar_inline():
    css = TEMPLATE.read_text(encoding="utf-8")
    mobile = css.split("@media (max-width:640px){", 1)[1].split("\n}", 1)[0]
    assert 'mjx-container[display="true"]{font-size:90%;}' in mobile
    assert 'mjx-container:not([display="true"]){font-size:90%;}' not in mobile


def test_public_runtime_patch_mantem_paginas_ja_publicadas_consistentes():
    """O site carrega essay.js externamente; ele corrige HTMLs já gerados."""
    js = SITE_ESSAY_JS.read_text(encoding="utf-8")
    assert ".content h5{" in js and "font-size:1rem" in js
    assert 'mjx-container:not([display="true"]){vertical-align:-.15em;}' in js
    assert '@media (max-width:640px){mjx-container[display="true"]{font-size:90%;}}' in js


@pytest.mark.parametrize(
    "selector,minimum",
    [
        ("th", 0.80),
        ("pre", 0.86),
        ("code", 0.86),
        (".quote p", 0.98),
        (".box-verdict p", 0.94),
        (".box-badge", 0.76),
        (".verdict-tag", 0.74),
        (".label-solo", 0.72),
        (".card-meta", 0.76),
        (".pq-cite", 0.88),
        (r".pull-quote.epigraph p:last-child", 0.76),
    ],
)
def test_pisos_de_corpo_no_celular(selector, minimum):
    """As vozes menores da folha caíam para 9,9-12px a 375px de largura."""
    css = TEMPLATE.read_text(encoding="utf-8")
    block = css.split("@media (max-width:640px){", 1)[1].split("\n}", 1)[0]
    m = re.search(re.escape(selector) + r"\{[^}]*font-size:([\d.]+)(rem|em)", block)
    assert m, f"{selector} sem piso de corpo no bloco de celular"
    assert float(m.group(1)) >= minimum, f"{selector} = {m.group(1)}{m.group(2)}"
