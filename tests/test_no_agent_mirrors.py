from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_single_agent_source_tree():
    assert (ROOT/".agents").exists()
    assert not (ROOT/".claude"/"skills").exists()
    assert not (ROOT/".claude"/"agents").exists()
    assert not (ROOT/".codex").exists()
    assert not (ROOT/"scripts"/"sync_skills.py").exists()
