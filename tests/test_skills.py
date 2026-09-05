import json
from pathlib import Path

import yaml
from conftest import run_script


REQUIRED_METADATA = {
    "second-brain-role",
    "second-brain-mode",
    "second-brain-scope",
    "second-brain-approval",
    "second-brain-closure",
}


def test_real_skill_contracts_have_no_blocking_errors():
    proc = run_script("check_skills.py", "--json")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["errors"] == 0


def test_known_contract_regressions_are_absent():
    proc = run_script("check_skills.py", "--json")
    payload = json.loads(proc.stdout)
    codes = [issue["code"] for issue in payload["issues"]]
    for forbidden in (
        "TOOL_NOT_ALLOWED",
        "DUPLICATE_RULE",
        "METADATA_MISSING",
        "METADATA_KEY_MISSING",
        "READ_SKILL_HAS_WRITE_TOOL",
        "DESCRIPTION_STALE_HISTORY",
    ):
        assert forbidden not in codes


def test_every_skill_has_structured_second_brain_metadata():
    root = Path(__file__).resolve().parents[1]
    skill_files = sorted((root / ".agents" / "skills").glob("*/SKILL.md"))
    assert skill_files
    for path in skill_files:
        text = path.read_text(encoding="utf-8")
        raw = text.split("\n---\n", 1)[0].removeprefix("---\n")
        meta = yaml.safe_load(raw)
        assert REQUIRED_METADATA <= set(meta["metadata"]), path
        assert all(isinstance(v, str) for v in meta["metadata"].values()), path
        assert len(meta["description"]) <= 1024, path


def test_query_is_read_only_by_contract():
    root = Path(__file__).resolve().parents[1]
    text = (root / ".agents/skills/query/SKILL.md").read_text(encoding="utf-8")
    assert 'second-brain-mode: "read"' in text
    frontmatter = text.split("\n---\n", 1)[0]
    assert "Write" not in frontmatter and "Edit" not in frontmatter


def test_expand_and_chapter_have_one_way_structural_handoff():
    root = Path(__file__).resolve().parents[1]
    expand = (root / ".agents/skills/expand/SKILL.md").read_text(encoding="utf-8")
    chapter = (root / ".agents/skills/chapter/SKILL.md").read_text(encoding="utf-8")
    assert "encaminhe o brief já resolvido para `/chapter`" in expand
    assert "não devolve o conteúdo de uma seção nova para `/expand`" in chapter
    assert "WebSearch WebFetch" in chapter.split("\n---\n", 1)[0]


def test_update_preflight_validates_workspace_before_quality_gate():
    root = Path(__file__).resolve().parents[1]
    text = (root / ".agents/agents/update.md").read_text(encoding="utf-8")
    assert text.index("python scripts/sync_skills.py") < text.index("python scripts/check_repo.py --quick")
    assert text.index("python scripts/check_git_isolation.py") < text.index("python scripts/check_repo.py --quick")
    assert text.index("python scripts/check_path_discipline.py") < text.index("python scripts/check_repo.py --quick")
    assert "NÃO EXECUTADO (gate falhou)" in text


def test_update_never_publishes_the_public_site():
    root = Path(__file__).resolve().parents[1]
    text = (root / ".agents/agents/update.md").read_text(encoding="utf-8")
    assert "build_site.py" in text and "não commita em `site/`" in text
    assert "git -C data" in text and "git -C ." in text
