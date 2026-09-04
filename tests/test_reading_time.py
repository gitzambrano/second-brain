"""Regressão do tempo de leitura do catálogo (`build_site.reading_minutes`).

O cálculo desconta fórmula e código de propósito — fórmula é lida, não escaneada
palavra por palavra. O risco não é descontar de menos: é descontar prosa junto.
Foi o que acontecia com matemática de display, e é isso que estes testes prendem.
Tudo aqui usa texto sintético inline, porque `data/` não existe na CI.
"""
from __future__ import annotations

import build_site
from conftest import SCRIPTS  # noqa: F401  (garante scripts/ no sys.path)

PROSA = (
    "A prosa entre os dois blocos precisa ser contada porque ela é o corpo do "
    "argumento e não parte da fórmula que a antecede nem da que vem depois disso."
)


def test_prosa_entre_dois_blocos_de_display_continua_contada():
    """O bug: `$$` deixava um cifrão órfão que pareava com o bloco seguinte.

    Sem a correção, tudo entre o fim do primeiro bloco e o começo do segundo era
    tratado como fórmula, e um essay de milhares de palavras virava "3 min".
    """
    texto = (
        r"$$ C_T = \frac{\sigma a}{2} $$"
        "\n\n" + PROSA + "\n\n"
        r"$$ \lambda_0 = \mu \tan\alpha $$"
        "\n"
    )
    sem_math = build_site.MATH_SPAN.sub(" ", texto)
    assert len(sem_math.split()) == len(PROSA.split())
    # Nenhum cifrão pode sobrar: cifrão órfão é o mecanismo do bug.
    assert "$" not in sem_math


def test_display_nao_derruba_o_tempo_de_leitura_do_essay():
    """Mesma prosa com e sem matemática de display dá o mesmo tempo."""
    corpo = " ".join([PROSA] * 40)
    com_math = "$$ a = b $$\n\n" + corpo + "\n\n$$ c = d $$\n"
    assert build_site.reading_minutes(com_math) == build_site.reading_minutes(corpo)
    assert build_site.reading_minutes(com_math) >= 4


def test_matematica_continua_saindo_da_contagem():
    """A intenção original vale: fórmula não conta, inline ou display."""
    assert build_site.MATH_SPAN.sub(" ", r"$$ \frac{a}{b} + \frac{c}{d} $$").split() == []
    assert build_site.MATH_SPAN.sub(" ", r"texto $\lambda_0$ texto").split() == ["texto", "texto"]
    assert build_site.MATH_SPAN.sub(" ", r"texto \[ \frac{a}{b} \] texto").split() == ["texto", "texto"]


def test_inline_nao_atravessa_quebra_de_linha():
    """Dois cifrões em parágrafos diferentes têm prosa no meio, não fórmula."""
    texto = "Valor de $x$ aqui.\n\n" + PROSA + "\n\nOutro $y$ ali."
    assert PROSA in build_site.MATH_SPAN.sub(" ", texto)


def test_cifrao_de_moeda_nao_engole_a_frase():
    """`R$ 50.000 e R$ 500.000` é dinheiro; a prosa entre eles precisa contar."""
    texto = "Pagar R$ 50.000 e R$ 500.000 por apresentação custa caro."
    assert build_site.MATH_SPAN.sub(" ", texto).split() == texto.split()


def test_essay_quase_todo_formula_ainda_tem_ao_menos_um_minuto():
    assert build_site.reading_minutes("$$ a = b $$") == 1
