import json
import pytest

from conftest import ROOT, run_script, legacy_script_available

pytestmark = [pytest.mark.export, pytest.mark.html]


def test_html_fixture_export_and_validation(installed_mini_brain):
    if not legacy_script_available("export_essay_html.py"):
        pytest.skip("exporter absent in overlay-only tree")
    export = run_script("export_essay_html.py", "kitchen-sink", timeout=300)
    assert export.returncode == 0, export.stdout + export.stderr
    html_path = ROOT / "output" / "html" / "kitchen-sink.html"
    assert html_path.exists() and html_path.stat().st_size > 500, (
        "exporter returned success without producing real HTML"
    )
    structural = run_script("check_html_export.py", "kitchen-sink", "--json")
    assert structural.returncode == 0, structural.stdout + structural.stderr
    payload = json.loads(structural.stdout)
    issues = [i for values in payload["issues"].values() for i in values]
    assert not [i for i in issues if i["severity"] == "ERROR"], issues
    rendered = run_script("check_html_render.py", "kitchen-sink", "--json", timeout=300)
    assert rendered.returncode == 0, rendered.stdout + rendered.stderr
