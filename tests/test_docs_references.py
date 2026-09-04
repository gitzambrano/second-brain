"""The docs must point at files that exist.

A renamed script silently leaves a dead path in AGENTS.md or a skill, and the
next reader — human or agent — follows it into nothing.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = sorted(list(ROOT.glob("*.md")) + list(ROOT.glob(".agents/**/*.md")))
PATH_RE = re.compile(r"\bscripts/[A-Za-z0-9_./-]+\.(?:py|css|js|html|lua)\b")
COMMAND_RE = re.compile(r"`/([a-z-]+)`")


def test_documented_script_paths_exist():
    missing = []
    for doc in DOCS:
        for ref in sorted(set(PATH_RE.findall(doc.read_text(encoding="utf-8")))):
            if not (ROOT / ref).is_file():
                missing.append(f"{doc.relative_to(ROOT)}: {ref}")
    assert not missing, "docs reference missing files:\n" + "\n".join(missing)


def test_every_command_in_agents_md_has_a_skill():
    referenced = set(COMMAND_RE.findall((ROOT / "AGENTS.md").read_text(encoding="utf-8")))
    available = {p.name for p in (ROOT / ".agents/skills").iterdir() if p.is_dir()}
    assert not referenced - available, sorted(referenced - available)


def test_scripts_root_holds_commands_or_two_line_shims():
    """No implementation may drift back out of `scripts/lib/`.

    A file in `scripts/` is either a command the user runs or a shim that
    re-exports its `lib/` twin; the shims exist only because many scripts
    import those modules before `repo_paths` puts `lib/` on the path.
    """
    lib = {p.stem for p in (ROOT / "scripts/lib").glob("*.py")} - {"__init__"}
    fat_shims = []
    for name in sorted(lib):
        twin = ROOT / "scripts" / f"{name}.py"
        if not twin.is_file():
            continue
        body = [ln for ln in twin.read_text(encoding="utf-8").splitlines()
                if ln.strip() and not ln.strip().startswith(("#", '"""'))]
        if len(body) > 6:
            fat_shims.append(f"{name}.py ({len(body)} lines)")
    assert not fat_shims, "implementation living outside scripts/lib: " + ", ".join(fat_shims)
