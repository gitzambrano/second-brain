import pytest

from conftest import ROOT, run_script, legacy_script_available

pytestmark = [pytest.mark.export, pytest.mark.pdf]


def test_pdf_fixture_export_content_and_layout(installed_mini_brain):
    if not legacy_script_available("export_essay_pdf.py"):
        pytest.skip("exporter absent in overlay-only tree")
    export = run_script("export_essay_pdf.py", "kitchen-sink", timeout=600)
    assert export.returncode == 0, export.stdout + export.stderr
    pdf_path = ROOT / "output" / "pdf" / "kitchen-sink.pdf"
    assert pdf_path.exists() and pdf_path.stat().st_size > 1000, "exporter returned success without producing real PDF"
    content = run_script("check_pdf_content.py", "kitchen-sink", "--json")
    assert content.returncode == 0, content.stdout + content.stderr
    layout = run_script("check_pdf_layout.py", "kitchen-sink", "--json")
    assert layout.returncode == 0, layout.stdout + layout.stderr
