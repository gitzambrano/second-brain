import pytest

from conftest import ROOT, run_script, legacy_script_available

pytestmark = [pytest.mark.export, pytest.mark.pdf]


def test_markdown_html_pdf_semantic_parity(installed_mini_brain):
    if not (legacy_script_available("export_essay_pdf.py") and legacy_script_available("export_essay_html.py")):
        pytest.skip("exporters absent in overlay-only tree")
    html = run_script("export_essay_html.py", "kitchen-sink", timeout=300)
    pdf = run_script("export_essay_pdf.py", "kitchen-sink", timeout=600)
    assert html.returncode == 0, html.stdout + html.stderr
    assert pdf.returncode == 0, pdf.stdout + pdf.stderr
    hp = ROOT / "output" / "html" / "kitchen-sink.html"
    pp = ROOT / "output" / "pdf" / "kitchen-sink.pdf"
    assert hp.exists() and hp.stat().st_size > 500, "HTML exporter returned success without artifact"
    assert pp.exists() and pp.stat().st_size > 1000, "PDF exporter returned success without artifact"
    parity = run_script("check_export_parity.py", "kitchen-sink", "--json")
    assert parity.returncode == 0, parity.stdout + parity.stderr
