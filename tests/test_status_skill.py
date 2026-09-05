from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_status_skill_excludes_explicitly_unconverted_sources_from_pending_verification():
    skill = (ROOT / ".agents" / "skills" / "status" / "SKILL.md").read_text(encoding="utf-8")

    pending_rule = next(line for line in skill.splitlines() if "`Verificação: não verificado`" in line)
    assert "exceto" in pending_rule
    assert "`Virou:`" in pending_rule
    for value in ("`None`", "`nenhum`", "`nenhuma`", "`-`", "`—`"):
        assert value in pending_rule
