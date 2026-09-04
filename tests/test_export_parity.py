import sys
from pathlib import Path

import pytest
from conftest import legacy_script_available, run_script

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

pytestmark = [pytest.mark.export, pytest.mark.pdf]


def test_markdown_html_pdf_semantic_parity(installed_mini_brain):
    if not (legacy_script_available("export_essay_pdf.py")
            and legacy_script_available("export_essay_html.py")):
        pytest.skip("exporters absent")
    h = run_script("export_essay_html.py", "kitchen-sink", timeout=300)
    p = run_script("export_essay_pdf.py", "kitchen-sink", timeout=600)
    assert h.returncode == 0, h.stdout + h.stderr
    assert p.returncode == 0, p.stdout + p.stderr

    hp = installed_mini_brain / "output" / "html" / "kitchen-sink.html"
    pp = installed_mini_brain / "output" / "pdf" / "kitchen-sink.pdf"
    assert hp.exists() and hp.stat().st_size > 500
    assert pp.exists() and pp.stat().st_size > 1000

    parity = run_script("check_export_parity.py", "kitchen-sink", "--json")
    assert parity.returncode == 0, parity.stdout + parity.stderr


@pytest.mark.parametrize("heading,expected", [
    (r"A Natureza de $\dot{\beta}$: O Verdadeiro Amortecedor",
     ["a natureza de", "o verdadeiro amortecedor"]),
    (r"Efeitos de Primeira Ordem: $C_{n_\beta}$, $C_{n_r}$ e $I_z$",
     ["efeitos de primeira ordem"]),
    ("Introdução sem matemática", ["introducao sem matematica"]),
])
def test_headings_with_inline_math_compare_on_prose(heading, expected):
    """Regression: inline TeX in a heading is never present in rendered text.

    Comparing the literal heading reported every math heading as missing. The
    checker now compares the prose fragments around each math span.
    """
    from check_export_parity import prose_fragments

    assert prose_fragments(heading) == expected


def test_letter_spaced_headings_are_still_found():
    """Regression: the PDF template tracks headings ("S U M A R I O")."""
    from check_export_parity import loose
    from sanity_common import text_contains

    rendered = loose("S U M Á R I O\nIntrodução")
    assert text_contains(rendered, loose("Sumário"))
    assert not text_contains(rendered, loose("Referências"))


def test_the_word_conexoes_in_prose_is_not_an_exported_section():
    """Regression: the checker matched the bare substring, so an essay whose
    summary mentioned "conexões" was reported as leaking the private section."""
    from check_export_parity import has_standalone_line

    prose = "reune estrutura, links, referencias e conexoes em um documento"
    assert not has_standalone_line(prose, "Conexões")
    assert has_standalone_line("Referências\nConexões\n- [[outro]]", "Conexões")
    # The PDF template tracks headings into spaced-out capitals.
    assert has_standalone_line("C O N E X Õ E S", "Conexões")
