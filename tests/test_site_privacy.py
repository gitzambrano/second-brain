"""Sentinel leak test for the public projection.

The owner's published surface is deliberately wide and its floor is hard:

* the catalogue and the map name **every** essay, with title, summary, tags and
  draft status — that is the point of an atlas;
* the **body** of an unpublished essay never leaves the private repository, it
  gets no rendered page, and nothing on the site links to it.

Do not weaken this test. Widening what the site may expose is a decision about
the owner's privacy, not a refactor.
"""
import base64
import json
import os
import re
import subprocess
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SENTINEL = "SENTINELA_PRIVADA_49A1_UMA_FRASE_LONGA_E_DISTINTA_DO_CORPO_PRIVADO"
PRIVATE_SLUG = "segredo-ultra-privado"
PRIVATE_TITLE = "SEGREDO ULTRA PRIVADO"
EMBEDDED_PAYLOAD = re.compile(r'id="sb-graph-data">([^<]*)<')


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


def map_nodes(site):
    """Inflate the payload the browser actually receives."""
    match = EMBEDDED_PAYLOAD.search((site / "graph.html").read_text(encoding="utf-8"))
    assert match, "graph.html carries no embedded payload"
    payload = json.loads(zlib.decompress(base64.b64decode(match.group(1)), -15))
    return {node["id"]: node for node in payload["nodes"]}


def test_private_body_never_reaches_the_site(tmp_path):
    site, _env = build(tmp_path)
    combined = "\n".join(
        p.read_text(encoding="utf-8", errors="ignore")
        for p in site.rglob("*") if p.is_file()
    )
    assert SENTINEL not in combined


def test_unpublished_essay_has_no_page_and_nothing_links_to_it(tmp_path):
    site, _env = build(tmp_path)
    assert not (site / "essays" / f"{PRIVATE_SLUG}.html").exists()
    for path in site.rglob("*"):
        if path.is_file() and path.suffix in {".html", ".json"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
            assert f"essays/{PRIVATE_SLUG}.html" not in text, path.name


def test_map_catalogues_the_private_essay_but_never_opens_it(tmp_path):
    site, _env = build(tmp_path)
    nodes = map_nodes(site)

    private = nodes[f"essay:{PRIVATE_SLUG}"]
    assert private["public"] is False
    assert not private.get("htmlFile"), "an unpublished essay must not be openable"
    assert not private.get("file"), "no path into the private repository"
    assert SENTINEL not in json.dumps(private, ensure_ascii=False)

    public = nodes["essay:dutch-roll"]
    assert public["public"] is True
    assert public["htmlFile"] == "essays/dutch-roll.html"


def test_catalogue_lists_every_essay_but_only_publishes_bodies(tmp_path):
    site, _env = build(tmp_path)
    search = json.loads((site / "search-index.json").read_text(encoding="utf-8"))
    by_slug = {entry["slug"]: entry for entry in search}
    assert set(by_slug) == {"dutch-roll", PRIVATE_SLUG}

    private = by_slug[PRIVATE_SLUG]
    assert private["published"] is False
    assert "text" not in private, "the body of an unpublished essay is never indexed"
    assert "url" not in private, "an unpublished essay is not linkable"

    published = by_slug["dutch-roll"]
    assert published["published"] is True
    assert published["url"] == "essays/dutch-roll.html"

    manifest = json.loads((site / "site-manifest.json").read_text(encoding="utf-8"))
    assert manifest["published"] == ["dutch-roll"]
    assert manifest["catalogue"] == 2


def test_privacy_checker_accepts_the_generated_site(tmp_path):
    _site, env = build(tmp_path)
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_site_privacy.py"), "--json"],
        cwd=ROOT, env=env, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert json.loads(proc.stdout)["status"] == "pass"


def test_privacy_checker_rejects_a_forged_read_link(tmp_path):
    """The checker must actually fail when the map offers a way in."""
    site, env = build(tmp_path)
    graph_path = site / "graph.json"
    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    for node in graph["nodes"]:
        if node["id"] == f"essay:{PRIVATE_SLUG}":
            node["htmlFile"] = f"essays/{PRIVATE_SLUG}.html"
    graph_path.write_text(json.dumps(graph, ensure_ascii=False), encoding="utf-8")

    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_site_privacy.py"), "--json"],
        cwd=ROOT, env=env, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )
    assert proc.returncode == 1
    errors = json.loads(proc.stdout)["errors"]
    assert any("unauthorized read link" in e for e in errors), errors
