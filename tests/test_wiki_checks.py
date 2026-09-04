import json

import pytest
from conftest import legacy_script_available, recursive_severities, run_script

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


def _manifest_codes(mini_brain, virou_line):
    """Run check_wiki over a manifest whose imported source has this Virou line."""
    sources = mini_brain / "wiki" / "sources"
    (sources / "ensaio-importado").mkdir(parents=True, exist_ok=True)
    (sources / "ensaio-importado" / "white-paper.docx").write_text("x", encoding="utf-8")
    manifest = sources / "manifest.md"
    manifest.write_text(
        manifest.read_text(encoding="utf-8")
        + "\n## [2026-01-01] white-paper.docx\n"
          "Tipo: Ensaio Completo Importado.\n"
          "Tags: [Teste]\n"
          "Pasta: wiki/sources/ensaio-importado/\n"
        + virou_line
        + "Verificação: não verificado — checar antes de citar em outro essay.\n",
        encoding="utf-8",
    )
    proc = run_script("check_wiki.py", "--json")
    return [c for _, c in recursive_severities(json.loads(proc.stdout))]


def test_imported_source_without_virou_is_an_error(installed_mini_brain):
    if not legacy_script_available("check_wiki.py"):
        pytest.skip("checker absent")
    assert "MANIFEST_IMPORTED_NO_ESSAY" in _manifest_codes(installed_mini_brain, "")


def test_virou_none_records_a_decision_and_is_accepted(installed_mini_brain):
    """`Virou: None` means "examined, became no essay" — a answer, not a gap."""
    if not legacy_script_available("check_wiki.py"):
        pytest.skip("checker absent")
    for spelling in ("Virou: None\n", "Virou: nenhum\n", "Virou: —\n"):
        codes = _manifest_codes(installed_mini_brain, spelling)
        assert "MANIFEST_IMPORTED_NO_ESSAY" not in codes, spelling
