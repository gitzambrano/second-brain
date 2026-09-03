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


def test_update_preflight_validates_workspace_before_quality_gate():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    text = (root / ".agents/agents/update.md").read_text(encoding="utf-8")
    assert text.index("python scripts/check_git_isolation.py") < text.index("python scripts/check_repo.py --quick")
    assert text.index("python scripts/check_path_discipline.py") < text.index("python scripts/check_repo.py --quick")
    assert "NÃO EXECUTADO (gate falhou)" in text


def test_update_never_publishes_the_public_site():
    """`update` closes engine and data. Publication stays an explicit decision."""
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    text = (root / ".agents/agents/update.md").read_text(encoding="utf-8")
    assert "build_site.py" in text and "não commita em `site/`" in text
    assert "git -C data" in text and "git -C ." in text


def test_no_agent_file_mentions_the_removed_mirror_system():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    stale = [
        p for p in (root / ".agents").rglob("*.md")
        if "sync_skills" in p.read_text(encoding="utf-8")
    ]
    assert not stale, [str(p) for p in stale]
