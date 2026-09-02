"""Sentinel leak test for the public projection.

The site exposes two surfaces under two different rules, and this test pins both:

* the **map** (`graph.json`) names every page in the base and how they connect —
  that is deliberate — but must never carry a private page's body, summary or a
  link that opens it;
* everything else (rendered pages, reading index, manifest) is restricted to
  essays authorized with `publish: true`.

Do not weaken this test. Widening what the map may expose is a decision about
the owner's privacy, not a refactor.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SENTINEL = "SENTINELA_PRIVADA_49A1"
PRIVATE_SLUG = "segredo-ultra-privado"
PRIVATE_TITLE = "SEGREDO ULTRA PRIVADO"


def essay(path, title, publish, body="Corpo."):
    path.write_text(
        "---\ntags: [Teste]\ncreated: 2026-01-01\nupdated: 2026-01-01\n"
        f"summary: resumo de {title}\nstatus: draft\n"
        f"publish: {'true' if publish else 'false'}\n---\n"
        f"# {title}\n\n{body}\n",
        encoding="utf-8",
    )


def build(tmp_path):
    data = tmp_path / "data"
    site = tmp_path / "site"
    essays = data / "wiki" / "essays"
    essays.mkdir(parents=True)
    site.mkdir()
    (site / ".second-brain-site").write_text("marker", encoding="utf-8")

    essay(
        essays / "dutch-roll.md", "Dutch Roll", True,
        "Texto público. [[segredo-ultra-privado|conceito interno]].\n\n"
        "## Conexões\n- [[segredo-ultra-privado|SEGREDO ULTRA PRIVADO]]",
    )
    essay(essays / f"{PRIVATE_SLUG}.md", PRIVATE_TITLE, False, SENTINEL)

    env = os.environ.copy()
    env["SECOND_BRAIN_DATA_ROOT"] = str(data)
    env["SECOND_BRAIN_SITE_ROOT"] = str(site)

    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/build_site.py"), "--no-render"],
        cwd=ROOT, env=env, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return site, env


def test_private_body_never_reaches_the_site(tmp_path):
    site, _env = build(tmp_path)
    combined = "\n".join(
        p.read_text(encoding="utf-8", errors="ignore")
        for p in site.rglob("*") if p.is_file()
    )
    assert SENTINEL not in combined


def test_private_identity_is_absent_outside_the_map(tmp_path):
    site, _env = build(tmp_path)
    for path in site.rglob("*"):
        if not path.is_file() or path.name == "graph.json":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        assert PRIVATE_SLUG not in text, path.name
        assert PRIVATE_TITLE not in text, path.name


def test_map_names_the_private_essay_but_never_opens_it(tmp_path):
    site, _env = build(tmp_path)
    graph = json.loads((site / "graph.json").read_text(encoding="utf-8"))
    nodes = {n["id"]: n for n in graph["nodes"]}

    private = nodes[f"essay:{PRIVATE_SLUG}"]
    assert private["published"] is False
    assert "summary" not in private, "an unpublished page must not ship its summary"
    assert "url" not in private, "an unpublished page must not be openable"
    assert SENTINEL not in json.dumps(private, ensure_ascii=False)

    public = nodes["essay:dutch-roll"]
    assert public["published"] is True
    assert public["url"] == "essays/dutch-roll.html"

    # The connection between them is part of the map.
    pairs = {tuple(sorted((e["source"], e["target"]))) for e in graph["edges"]}
    assert tuple(sorted(("essay:dutch-roll", f"essay:{PRIVATE_SLUG}"))) in pairs


def test_reading_index_holds_only_authorized_essays(tmp_path):
    site, _env = build(tmp_path)
    search = json.loads((site / "search-index.json").read_text(encoding="utf-8"))
    assert [entry["slug"] for entry in search] == ["dutch-roll"]

    manifest = json.loads((site / "site-manifest.json").read_text(encoding="utf-8"))
    assert manifest["published"] == ["dutch-roll"]


def test_privacy_checker_accepts_the_generated_site(tmp_path):
    site, env = build(tmp_path)
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_site_privacy.py"), "--json"],
        cwd=ROOT, env=env, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert json.loads(proc.stdout)["status"] == "pass"
    assert site.exists()


def test_privacy_checker_rejects_a_leaked_summary(tmp_path):
    """The checker must actually fail when the map exposes readable content."""
    site, env = build(tmp_path)
    graph_path = site / "graph.json"
    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    for node in graph["nodes"]:
        if node["id"] == f"essay:{PRIVATE_SLUG}":
            node["summary"] = "conteúdo que não deveria vazar"
    graph_path.write_text(json.dumps(graph, ensure_ascii=False), encoding="utf-8")

    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_site_privacy.py"), "--json"],
        cwd=ROOT, env=env, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )
    assert proc.returncode == 1
    errors = json.loads(proc.stdout)["errors"]
    assert any("summary exposed" in e for e in errors), errors
