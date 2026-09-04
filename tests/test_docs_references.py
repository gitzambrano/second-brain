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


# `python scripts/foo.py --flag` na documentação: o script e a flag têm de
# existir. Uma flag renomeada some do código e fica na instrução, e o agente
# que seguir a instrução recebe "unrecognized arguments" no meio de um fluxo.
INVOCATION_RE = re.compile(
    r"python\s+(scripts/[A-Za-z0-9_./-]+\.py)((?:\s+--?[A-Za-z0-9][\w-]*)*)"
)
DOC_FILE_RE = re.compile(r"`([A-Za-z0-9_][\w./-]*\.(?:py|md|json|toml|txt|yml|yaml|css|js|html))`")

# Caminhos que a documentação cita como conteúdo, não como arquivo do engine:
# vivem no repo privado `data/` ou são gerados na publicação.
DATA_PREFIXES = ("wiki/", "plan/", "raw/", "output/", "data/", "site/")


def _declared_flags(script: Path) -> set[str]:
    """As flags que o script declara, lidas do fonte sem executá-lo."""
    source = script.read_text(encoding="utf-8", errors="replace")
    return set(re.findall(r'add_argument\(\s*"(--[A-Za-z0-9][\w-]*)"', source))


def test_documented_flags_exist():
    unknown = []
    for doc in DOCS:
        for script_ref, flags in INVOCATION_RE.findall(doc.read_text(encoding="utf-8")):
            script = ROOT / script_ref
            if not script.is_file():
                continue  # já coberto por test_documented_script_paths_exist
            declared = _declared_flags(script)
            for flag in re.findall(r"--[A-Za-z0-9][\w-]*", flags):
                if flag not in declared and flag not in {"--help"}:
                    unknown.append(f"{doc.relative_to(ROOT)}: {script_ref} {flag}")
    assert not unknown, "docs use flags the script does not declare:\n" + "\n".join(unknown)


def test_documented_repo_files_exist():
    """Arquivo do engine citado em crase existe. Conteúdo privado é ignorado."""
    missing = []
    for doc in DOCS:
        for ref in sorted(set(DOC_FILE_RE.findall(doc.read_text(encoding="utf-8")))):
            if ref.startswith(DATA_PREFIXES) or "/" not in ref:
                continue
            # `conventions/SKILL.md` e afins são citados relativos à árvore de
            # skills, que é como uma skill se refere à outra.
            candidates = (ROOT / ref, ROOT / ".agents" / "skills" / ref)
            if not any(c.exists() for c in candidates):
                missing.append(f"{doc.relative_to(ROOT)}: {ref}")
    assert not missing, "docs reference missing repo files:\n" + "\n".join(missing)
