from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_status_skill_excludes_explicitly_unconverted_sources_from_pending_verification():
    skill = (ROOT / ".agents" / "skills" / "status" / "SKILL.md").read_text(encoding="utf-8")

    assert "`Virou:` for `None`" in skill
    assert "não entram na pendência" in skill
