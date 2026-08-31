import json
import pytest

from conftest import ROOT, recursive_severities, run_script, legacy_script_available

pytestmark = pytest.mark.slow


def test_synthetic_essay_has_no_blocking_wiki_issues(installed_mini_brain):
    if not legacy_script_available("check_wiki.py"):
        pytest.skip("legacy checker absent in overlay-only tree")
    proc = run_script("check_wiki.py", "kitchen-sink", "--json")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    payload = json.loads(proc.stdout)
    blocking = [(s, c) for s, c in recursive_severities(payload) if s in {"CRITICAL", "ERROR"}]
    assert not blocking, blocking


def test_dead_wikilink_regression(installed_mini_brain):
    if not legacy_script_available("check_wiki.py"):
        pytest.skip("legacy checker absent in overlay-only tree")
    essay = ROOT / "wiki" / "essays" / "kitchen-sink.md"
    original = essay.read_text(encoding="utf-8")
    essay.write_text(
        original.replace("[[segundo-essay|Segundo Essay]]", "[[pagina-inexistente|Segundo Essay]]"),
        encoding="utf-8",
    )
    proc = run_script("check_wiki.py", "kitchen-sink", "--json")
    payload = json.loads(proc.stdout)
    codes = [c for _, c in recursive_severities(payload)]
    assert "DEAD_WIKILINK" in codes
