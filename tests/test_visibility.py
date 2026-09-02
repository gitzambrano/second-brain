"""Essay visibility: the three levels and the tool that writes them.

    public   readable on the public site
    private  catalogued and mapped by name and summary; text not published
    hidden   absent everywhere, wiki index and wiki graph included
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def essay(path, title, level=None, legacy_publish=None):
    field = ""
    if level is not None:
        field = f"visibility: {level}\n"
    elif legacy_publish is not None:
        field = f"publish: {'true' if legacy_publish else 'false'}\n"
    path.write_text(
        f"---\ntags: [Teste]\ncreated: 2026-01-01\nupdated: 2026-01-01\n"
        f'summary: "resumo de {title}"\nstatus: draft\n{field}---\n'
        f"# {title}\n\nCorpo.\n",
        encoding="utf-8",
    )


def run(script, *args, data_root):
    env = os.environ.copy()
    env["SECOND_BRAIN_DATA_ROOT"] = str(data_root)
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / script), *args],
        cwd=ROOT, env=env, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )


def test_levels_are_read_from_frontmatter():
    import visibility

    assert visibility.of({"visibility": "public"}) == visibility.PUBLIC
    assert visibility.of({"visibility": "private"}) == visibility.PRIVATE
    assert visibility.of({"visibility": "hidden"}) == visibility.HIDDEN
    # Portuguese spellings are accepted; the corpus is written in Portuguese.
    assert visibility.of({"visibility": "oculto"}) == visibility.HIDDEN
    assert visibility.of({"visibility": "público"}) == visibility.PUBLIC
    # Legacy boolean still means public.
    assert visibility.of({"publish": True}) == visibility.PUBLIC
    # Absence, falsehood and nonsense are all private.
    assert visibility.of({}) == visibility.PRIVATE
    assert visibility.of({"publish": False}) == visibility.PRIVATE
    assert visibility.of({"publish": "true"}) == visibility.PRIVATE
    assert visibility.of({"visibility": "sim"}) == visibility.PRIVATE


def test_exclusive_publication(tmp_path):
    essays = tmp_path / "wiki" / "essays"
    essays.mkdir(parents=True)
    essay(essays / "a.md", "Essay Antigo", legacy_publish=True)
    essay(essays / "dutch-roll.md", "Dutch Roll: Dinâmica Látero-Direcional")
    essay(essays / "secreto.md", "Secreto", level="hidden")

    p = run("publication.py", "set-exclusive", "Dutch Roll", data_root=tmp_path)
    assert p.returncode == 0, p.stdout + p.stderr

    c = run("check_publication.py", "--expect-only", "Dutch Roll", data_root=tmp_path)
    assert c.returncode == 0, c.stdout + c.stderr

    assert "visibility: public" in (essays / "dutch-roll.md").read_text(encoding="utf-8")
    assert "visibility: private" in (essays / "a.md").read_text(encoding="utf-8")
    # A hidden essay is left alone: publishing one must not surface another.
    assert "visibility: hidden" in (essays / "secreto.md").read_text(encoding="utf-8")


def test_hidden_essay_is_absent_from_catalogue_and_index(tmp_path, monkeypatch):
    essays = tmp_path / "wiki" / "essays"
    essays.mkdir(parents=True)
    essay(essays / "visivel.md", "Visível", level="private")
    essay(essays / "secreto.md", "Secreto", level="hidden")

    monkeypatch.setenv("SECOND_BRAIN_DATA_ROOT", str(tmp_path))
    for module in ("repo_paths", "site_common", "visibility"):
        sys.modules.pop(module, None)
    from site_common import collect_all

    slugs = {e.slug for e in collect_all()}
    assert slugs == {"visivel"}

    for module in ("repo_paths", "site_common", "visibility"):
        sys.modules.pop(module, None)


def test_writing_visibility_never_touches_the_body(tmp_path):
    """Regression: a greedy frontmatter delimiter reflowed blank lines in the body.

    Setting visibility is metadata surgery. Everything after the closing `---`
    line must survive byte for byte, whatever whitespace surrounds it.
    """
    import publication

    variants = {
        "no-blank": "---\ntags: [A]\n---\n# T\n\nCorpo.\n",
        "one-blank": "---\ntags: [A]\n---\n\n# T\n\nCorpo.\n",
        "two-blank": "---\ntags: [A]\n---\n\n\n# T\n\nCorpo.\n",
        "trailing-space": "---\ntags: [A]   \n---\n\n# T\n\nCorpo.\n",
        "legacy-field": "---\ntags: [A]\npublish: true\n---\n\n# T\n\nCorpo.\n",
    }
    for name, text in variants.items():
        for level in ("public", "private", "hidden"):
            path = tmp_path / f"{name}-{level}.md"
            path.write_text(text, encoding="utf-8")
            publication.set_level(path, level)
            after = path.read_text(encoding="utf-8")
            marker = "\n---\n"
            assert after[after.index(marker) + len(marker):] == \
                text[text.index(marker) + len(marker):], name
            assert f"visibility: {level}" in after
            # The legacy field is replaced, never left to contradict the new one.
            assert "publish:" not in after.split(marker)[0]


def test_setting_visibility_is_idempotent(tmp_path):
    import publication

    path = tmp_path / "e.md"
    path.write_text("---\ntags: [A]\n---\n\n# T\n\nCorpo.\n", encoding="utf-8")
    assert publication.set_level(path, "public") is True
    assert publication.set_level(path, "public") is False
    assert publication.set_level(path, "hidden") is True
    assert publication.set_level(path, "hidden") is False


def test_checker_reports_an_unusable_value(tmp_path):
    essays = tmp_path / "wiki" / "essays"
    essays.mkdir(parents=True)
    essay(essays / "ruim.md", "Ruim", level="talvez")

    c = run("check_publication.py", "--json", data_root=tmp_path)
    assert c.returncode == 1
    payload = json.loads(c.stdout)
    assert payload["invalid"], payload
    assert payload["public"] == []
