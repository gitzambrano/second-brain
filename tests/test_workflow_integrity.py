import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_workflow_script_paths_exist():
    missing = []
    for workflow in (ROOT / ".github/workflows").glob("*.y*ml"):
        source = workflow.read_text(encoding="utf-8")
        refs = set(re.findall(r"\bscripts/[A-Za-z0-9_./-]+\.py\b", source))
        for rel in sorted(refs):
            if not (ROOT / rel).is_file():
                missing.append(f"{workflow.name}: {rel}")
    assert not missing, "workflow references missing scripts:\n" + "\n".join(missing)
