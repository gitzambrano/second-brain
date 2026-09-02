import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def essay(path, title, publish=None):
    pub = "" if publish is None else f"publish: {'true' if publish else 'false'}\n"
    path.write_text(
        f"---\ntags: [Teste]\ncreated: 2026-01-01\nupdated: 2026-01-01\n"
        f"summary: teste\nstatus: draft\n{pub}---\n# {title}\n\nCorpo.\n",
        encoding="utf-8",
    )


def test_exclusive_dutch_roll(tmp_path):
    d = tmp_path / "wiki" / "essays"
    d.mkdir(parents=True)
    essay(d / "a.md", "Essay Privado", True)
    essay(d / "dutch-roll.md", "Dutch Roll: Dinâmica Látero-Direcional")

    env = os.environ.copy()
    env["SECOND_BRAIN_DATA_ROOT"] = str(tmp_path)

    p = subprocess.run(
        [sys.executable, str(ROOT / "scripts/publication.py"), "set-exclusive", "Dutch Roll"],
        cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert p.returncode == 0, p.stdout + p.stderr

    c = subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_publication.py"),
         "--expect-only", "Dutch Roll"],
        cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert c.returncode == 0, c.stdout + c.stderr
    assert "publish: true" not in (d / "a.md").read_text(encoding="utf-8")
    assert "publish: true" in (d / "dutch-roll.md").read_text(encoding="utf-8")


def test_setting_publish_never_touches_the_body(tmp_path):
    """Regression: a greedy frontmatter delimiter reflowed blank lines in the body.

    Toggling `publish` is metadata surgery. Everything after the closing `---`
    line must survive byte for byte, whatever whitespace surrounds it.
    """
    import publication

    variants = {
        "no-blank": "---\ntags: [A]\n---\n# T\n\nCorpo.\n",
        "one-blank": "---\ntags: [A]\n---\n\n# T\n\nCorpo.\n",
        "two-blank": "---\ntags: [A]\n---\n\n\n# T\n\nCorpo.\n",
        "trailing-space": "---\ntags: [A]   \n---\n\n# T\n\nCorpo.\n",
    }
    for name, text in variants.items():
        for enabled in (True, False):
            path = tmp_path / f"{name}-{enabled}.md"
            path.write_text(text, encoding="utf-8")
            publication.set_publish(path, enabled)
            after = path.read_text(encoding="utf-8")
            marker = "\n---\n"
            assert after[after.index(marker) + len(marker):] == \
                text[text.index(marker) + len(marker):], name


def test_setting_publish_is_idempotent(tmp_path):
    import publication

    path = tmp_path / "e.md"
    path.write_text("---\ntags: [A]\n---\n\n# T\n\nCorpo.\n", encoding="utf-8")
    assert publication.set_publish(path, True) is True
    assert publication.set_publish(path, True) is False
    assert publication.set_publish(path, False) is True
    assert publication.set_publish(path, False) is False
