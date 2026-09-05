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
ROOT = Path(__file__).resolve().parents[1]


def skill_frontmatter(name: str) -> dict:
    text = (ROOT / ".agents" / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
    raw = text.split("\n---\n", 1)[0].removeprefix("---\n")
    return yaml.safe_load(raw)


def all_skill_frontmatters() -> dict[str, dict]:
    return {
        path.parent.name: skill_frontmatter(path.parent.name)
        for path in sorted((ROOT / ".agents" / "skills").glob("*/SKILL.md"))
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
    skill_files = sorted((ROOT / ".agents" / "skills").glob("*/SKILL.md"))
    assert skill_files
    for path in skill_files:
        text = path.read_text(encoding="utf-8")
        raw = text.split("\n---\n", 1)[0].removeprefix("---\n")
        meta = yaml.safe_load(raw)
        assert REQUIRED_METADATA <= set(meta["metadata"]), path
        assert all(isinstance(v, str) for v in meta["metadata"].values()), path
        assert len(meta["description"]) <= 1024, path


def test_declared_skill_routes_resolve_without_direct_cycles():
    skills = all_skill_frontmatters()
    for source, frontmatter in skills.items():
        target = frontmatter["metadata"].get("second-brain-routes-to")
        if not target:
            continue
        assert target in skills, f"/{source} routes to unknown skill /{target}"
        assert target != source, f"/{source} routes to itself"
        reverse = skills[target]["metadata"].get("second-brain-routes-to")
        assert reverse != source, f"direct routing cycle: /{source} <-> /{target}"


def test_query_is_read_only_by_contract():
    meta = skill_frontmatter("query")
    assert meta["metadata"]["second-brain-mode"] == "read"
    tools = set(meta["allowed-tools"].split())
    assert not tools & {"Write", "Edit"}


def test_expand_and_chapter_have_one_way_structural_handoff():
    expand = skill_frontmatter("expand")
    chapter = skill_frontmatter("chapter")
    assert expand["metadata"]["second-brain-role"] == "content-editor"
    assert expand["metadata"]["second-brain-routes-to"] == "chapter"
    assert chapter["metadata"]["second-brain-role"] == "structure-editor"
    assert chapter["metadata"].get("second-brain-routes-to") != "expand"
    chapter_tools = set(chapter["allowed-tools"].split())
    assert {"WebSearch", "WebFetch"} <= chapter_tools


def test_write_orchestrators_are_declared_as_write_workflows():
    for name in ("organize", "sweep"):
        assert skill_frontmatter(name)["metadata"]["second-brain-mode"] == "write"


def test_update_preflight_validates_workspace_before_quality_gate():
    text = (ROOT / ".agents/agents/update.md").read_text(encoding="utf-8")
    assert text.index("python scripts/sync_skills.py") < text.index("python scripts/check_repo.py --quick")
    assert text.index("python scripts/check_git_isolation.py") < text.index("python scripts/check_repo.py --quick")
    assert text.index("python scripts/check_path_discipline.py") < text.index("python scripts/check_repo.py --quick")
    assert "NÃO EXECUTADO (gate falhou)" in text


def test_update_never_publishes_the_public_site():
    text = (ROOT / ".agents/agents/update.md").read_text(encoding="utf-8")
    assert "build_site.py" in text and "não commita em `site/`" in text
    assert "git -C data" in text and "git -C ." in text
