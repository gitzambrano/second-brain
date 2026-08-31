import json

from conftest import run_script


def test_real_skill_contracts_have_no_blocking_errors():
    proc = run_script("check_skills.py", "--json")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["errors"] == 0


def test_known_contract_regressions_are_absent():
    proc = run_script("check_skills.py", "--json")
    payload = json.loads(proc.stdout)
    codes = [issue["code"] for issue in payload["issues"]]
    assert "TOOL_NOT_ALLOWED" not in codes
    assert "DUPLICATE_RULE" not in codes


def test_update_preflight_syncs_generated_mirrors_before_quality_gate():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    text = (root / ".agents/agents/update.md").read_text(encoding="utf-8")
    assert text.index("python scripts/sync_skills.py") < text.index("python scripts/check_repo.py --quick")
    assert "NÃO EXECUTADO (gate falhou)" in text
