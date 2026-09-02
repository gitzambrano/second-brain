import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_temporal_old_claim_warns(tmp_path):
    essays = tmp_path / "wiki" / "essays"
    essays.mkdir(parents=True)
    # The corpus is always UTF-8; write the fixture the same way.
    (essays / "a.md").write_text(
        "---\nupdated: 2020-01-01\n---\n# A\nAtualmente este é o modelo mais recente.\n",
        encoding="utf-8",
    )

    env = os.environ.copy()
    env["SECOND_BRAIN_DATA_ROOT"] = str(tmp_path)
    p = subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_freshness.py"), "--json", "--days", "30"],
        cwd=ROOT, env=env, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )
    assert p.returncode == 0, p.stdout + p.stderr
    payload = json.loads(p.stdout)
    assert payload["warnings"] == 1
    assert payload["issues"][0]["code"] == "STALE_CANDIDATE"


def test_recent_essay_is_not_flagged(tmp_path):
    essays = tmp_path / "wiki" / "essays"
    essays.mkdir(parents=True)
    (essays / "a.md").write_text(
        "---\nupdated: 2020-01-01\n---\n# A\nAtualmente este é o modelo mais recente.\n",
        encoding="utf-8",
    )

    env = os.environ.copy()
    env["SECOND_BRAIN_DATA_ROOT"] = str(tmp_path)
    p = subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_freshness.py"), "--json", "--days", "999999"],
        cwd=ROOT, env=env, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )
    assert p.returncode == 0, p.stdout + p.stderr
    assert json.loads(p.stdout)["warnings"] == 0
