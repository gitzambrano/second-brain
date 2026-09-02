import json,pytest
from conftest import recursive_severities,run_script,legacy_script_available
pytestmark=pytest.mark.slow
def test_synthetic_essay_has_no_blocking_wiki_issues(installed_mini_brain):
    if not legacy_script_available("check_wiki.py"):pytest.skip("checker absent")
    b=run_script("build_index.py");assert b.returncode==0,b.stdout+b.stderr
    p=run_script("check_wiki.py","kitchen-sink","--json");assert p.returncode==0,p.stdout+p.stderr
    blocking=[(s,c) for s,c in recursive_severities(json.loads(p.stdout)) if s in {"CRITICAL","ERROR"}];assert not blocking,blocking
def test_dead_wikilink_regression(installed_mini_brain):
    if not legacy_script_available("check_wiki.py"):pytest.skip("checker absent")
    essay=installed_mini_brain/"wiki"/"essays"/"kitchen-sink.md";o=essay.read_text(encoding="utf-8")
    essay.write_text(o.replace("[[segundo-essay|Segundo Essay]]","[[pagina-inexistente|Segundo Essay]]"),encoding="utf-8")
    p=run_script("check_wiki.py","kitchen-sink","--json");codes=[c for _,c in recursive_severities(json.loads(p.stdout))]
    assert "DEAD_WIKILINK" in codes
