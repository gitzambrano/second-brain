from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import ROOT


def test_sync_skills_is_idempotent(tmp_path: Path):
    source = ROOT / "scripts" / "sync_skills.py"
    enc = ROOT / "scripts" / "console_encoding.py"
    if not source.exists():
        pytest.skip("sync_skills.py not present in this overlay-only test tree")
    if "def sync_pair" not in source.read_text(encoding="utf-8", errors="replace"):
        pytest.skip("sync_skills.py is only a placeholder in the overlay validation tree")
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    shutil.copy2(source, repo / "scripts" / "sync_skills.py")
    if enc.exists():
        shutil.copy2(enc, repo / "scripts" / "console_encoding.py")
    else:
        (repo / "scripts" / "console_encoding.py").write_text("", encoding="utf-8")
    skill = repo / ".agents" / "skills" / "demo" / "SKILL.md"
    agent = repo / ".agents" / "agents" / "demo.md"
    skill.parent.mkdir(parents=True); agent.parent.mkdir(parents=True)
    skill.write_text("---\nname: demo\n---\n# Demo\n", encoding="utf-8")
    agent.write_text("---\nname: demo\n---\n# Demo\n", encoding="utf-8")
    cmd = [sys.executable, str(repo / "scripts" / "sync_skills.py")]
    first = subprocess.run(cmd, cwd=repo, capture_output=True, text=True)
    assert first.returncode == 0
    check = subprocess.run([*cmd, "--check"], cwd=repo, capture_output=True, text=True)
    assert check.returncode == 0, check.stdout + check.stderr
    second = subprocess.run(cmd, cwd=repo, capture_output=True, text=True)
    assert second.returncode == 0
    assert "já sincronizados" in second.stdout or "sincronizados" in second.stdout
