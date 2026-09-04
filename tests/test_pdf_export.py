import pytest
from conftest import legacy_script_available, run_script

pytestmark=[pytest.mark.export,pytest.mark.pdf]
def test_pdf_fixture_export_content_and_layout(installed_mini_brain):
    if not legacy_script_available("export_essay_pdf.py"): pytest.skip("exporter absent")
    export=run_script("export_essay_pdf.py","kitchen-sink",timeout=600)
    assert export.returncode==0,export.stdout+export.stderr
    pp=installed_mini_brain/"output"/"pdf"/"kitchen-sink.pdf"
    assert pp.exists() and pp.stat().st_size>1000
    c=run_script("check_pdf_content.py","kitchen-sink","--json");assert c.returncode==0,c.stdout+c.stderr
    l=run_script("check_pdf_layout.py","kitchen-sink","--json");assert l.returncode==0,l.stdout+l.stderr
