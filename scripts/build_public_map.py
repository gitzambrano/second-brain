#!/usr/bin/env python3
"""Generate the public map — graph and sphere — with the wiki's own renderers.

`build_graph.py` and `build_sphere.py` already produce the interactive map the
wiki uses — index panel, expandable summaries, draft badges, search, styling.
This script does not reimplement any of that. It takes the same node set, strips
what must not be public, and hands it to the same renderers.

What crosses into the public map:
    title, type, tags, summary (essays), draft status, degree, size, layout,
    every connection, and the external URL of a bibliography entry.

What never crosses:
    the body of any page, the `file` path into the private repository, and a
    read link for anything that is not an authorized essay. An unpublished node
    is on the map and cannot be opened.

A static site cannot hide what it serves: a title or summary here is public.
That is the deliberate trade — the catalogue is public, the text is not.

No-argument default: write the public map into SITE_ROOT.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import build_graph
import build_sphere
from repo_paths import SITE_ROOT
from site_common import collect_public

# Node fields that would leak content or point back at the private repository.
FORBIDDEN_NODE_FIELDS = ("file", "body", "text", "path")

# Summaries are published for essays only; the renderer shows no others.
SUMMARY_TYPES = {"essay"}

MD_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
MD_EMPHASIS = re.compile(r"[*_]{1,3}")


def clean_citation(text: str) -> str:
    """Render an AIAA citation as plain text for a map label."""
    text = MD_LINK.sub(
        lambda m: "" if m.group(1).strip().lower() == "link" else m.group(1), text
    )
    text = MD_EMPHASIS.sub("", text)
    return re.sub(r"\s+", " ", text).strip(" .,;")


def essay_slug(node_id: str) -> str:
    kind, _, slug = str(node_id).partition(":")
    return slug if kind == "essay" else ""


def sanitize(nodes, published: set[str]):
    """Return public copies of the wiki nodes, in place of the private ones."""
    public_nodes = []
    for node in nodes:
        slug = essay_slug(node["id"])
        is_public = bool(slug) and slug in published

        clean = dict(node)
        for field in FORBIDDEN_NODE_FIELDS:
            clean.pop(field, None)

        # A read link exists only for an authorized essay.
        clean["htmlFile"] = f"essays/{slug}.html" if is_public else None
        clean["public"] = is_public

        if node["type"] not in SUMMARY_TYPES:
            clean.pop("summary", None)
        if node["type"] == "reference":
            clean["title"] = clean_citation(node["title"])
        else:
            # Only a bibliography entry keeps an outbound URL.
            clean["url"] = None

        public_nodes.append(clean)
    return public_nodes


# Chrome added only to the public copies: a way back to the Atlas, a switch
# between the two maps, and a theme that follows the site. The map's own index
# panel stays — it already highlights a node on click and opens the public page.
PUBLIC_CHROME = """
<style>
  /* z-index baixo (8): o cromo fica sob a caixa de opções/Estilo (modal
     z-index 20 e popover 30) e sob o painel, então a última linha do painel
     expandido nunca fica escondida atrás dos botões de voltar. */
  #sb-back {
    position: fixed; left: 16px; bottom: 16px; z-index: 8;
    display: inline-flex; align-items: center; gap: 8px;
    padding: 9px 15px; border-radius: 999px;
    border: 1px solid rgba(255,255,255,.16);
    background: rgba(12,20,33,.82); backdrop-filter: blur(10px);
    color: #e8eef7; font: 600 13px/1 Inter, system-ui, sans-serif;
    text-decoration: none;
  }
  #sb-back:hover { border-color: rgba(255,255,255,.4); }
  #sb-map-switch {
    position: fixed; right: 16px; bottom: 16px; z-index: 8;
    display: inline-flex; gap: 8px;
  }
  #sb-map-switch a {
    padding: 9px 15px; border-radius: 999px;
    border: 1px solid rgba(255,255,255,.16);
    background: rgba(12,20,33,.82); backdrop-filter: blur(10px);
    color: #e8eef7; font: 600 13px/1 Inter, system-ui, sans-serif;
    text-decoration: none;
  }
  #sb-map-switch a:hover, #sb-theme:hover { border-color: rgba(255,255,255,.4); }
  #sb-theme {
    padding: 9px 13px; border-radius: 999px;
    border: 1px solid rgba(255,255,255,.16);
    background: rgba(12,20,33,.82); backdrop-filter: blur(10px);
    color: #e8eef7; font: 600 13px/1 Inter, system-ui, sans-serif; cursor: pointer;
  }
  /* In the light Atlas the floating chrome inverts with it. */
  :root[data-theme="light"] #sb-back,
  :root[data-theme="light"] #sb-map-switch a,
  :root[data-theme="light"] #sb-theme {
    background: rgba(255,255,255,.9);
    border-color: rgba(16,28,46,.16);
    color: #101c2e;
  }
  #sb-map-switch a[aria-current="page"] { color: #7aabff; border-color: #7aabff; }
  /* The options panel must end above the floating chrome, never behind it. */
  @media (max-width: 760px) {
    #panel, .panel, aside { padding-bottom: 64px; }
    #sb-back, #sb-map-switch a, #sb-theme { padding: 7px 11px; font-size: 12px; }
  }
  /* Tema claro: o fundo e os controles do mapa seguem o tema do site. O
     fundo do canvas também é pintado por JS (ver script ao final), então
     este bloco só alinha painéis/controles que usam CSS variable. */
  html[data-theme="light"] {
    --bg: #ffffff;
    --panel: #ffffff;
    --panel-border: #d7dde4;
    --ink: #1a1f24;
    --ink-dim: #5b6570;
    --edge: #5b6570;
    --edge-ref: #b0b8c0;
    --reference: #6b7280;
  }
  html[data-theme="light"] #search,
  html[data-theme="light"] .btn,
  html[data-theme="light"] .idx-expand,
  html[data-theme="light"] #idx-search,
  html[data-theme="light"] .idx-range input[type="number"],
  html[data-theme="light"] #idx-maturidade,
  html[data-theme="light"] .idx-read { background: #ffffff; }
  html[data-theme="light"] .legend-item:hover,
  html[data-theme="light"] #modal .close { background: rgba(0,0,0,.05); }
</style>
<a id="sb-back" href="index.html">&larr; Second Brain Atlas</a>
<nav id="sb-map-switch" aria-label="Trocar de mapa">
  <a href="graph.html"__GRAPH_CURRENT__>Grafo</a>
  <a href="sphere.html"__SPHERE_CURRENT__>Globo</a>
  <button type="button" id="sb-theme" aria-label="Alternar tema" aria-pressed="false">&#9680;</button>
</nav>
<script>
  // The map follows the Atlas: same stored theme key, same background.
  // The map must open showing the whole base. Its own control does exactly
  // that, so press it once the layout has settled instead of duplicating it.
  (function () {
    var fit = function () {
      var button = [].slice.call(document.querySelectorAll('button'))
        .filter(function (el) { return /ajustar/i.test(el.textContent); })[0];
      if (button) button.click();
    };
    if (document.readyState === 'complete') setTimeout(fit, 400);
    else window.addEventListener('load', function () { setTimeout(fit, 400); });
  })();
  (function () {
    var apply = function (theme) {
      document.documentElement.setAttribute('data-theme', theme);
      document.documentElement.style.background = theme === 'light' ? '#f7f9fc' : '#060d18';
      document.body.style.background = theme === 'light' ? '#f7f9fc' : '#060d18';
      var button = document.getElementById('sb-theme');
      if (button) button.setAttribute('aria-pressed', String(theme === 'light'));
    };
    var stored = null;
    try { stored = localStorage.getItem('sb-theme'); } catch (e) { /* private mode */ }
    if (!stored) {
      stored = (window.matchMedia && matchMedia('(prefers-color-scheme: light)').matches)
        ? 'light' : 'dark';
    }
    apply(stored);
    document.addEventListener('click', function (event) {
      if (!event.target.closest('#sb-theme')) return;
      var next = document.documentElement.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
      try { localStorage.setItem('sb-theme', next); } catch (e) { /* private mode */ }
      apply(next);
    });
  })();

  // Tema: o fundo do mapa acompanha o tema do site (claro/escuro) por padrão;
  // um estilo salvo com cor de fundo fixada neste navegador continua mandando.
  (function () {
    var root = document.documentElement;
    var theme = null;
    try { theme = localStorage.getItem('sb-theme'); } catch (e) {}
    if (theme !== 'light' && theme !== 'dark') {
      theme = (window.matchMedia && matchMedia('(prefers-color-scheme: light)').matches)
        ? 'light' : 'dark';
    }
    root.dataset.theme = theme;
    try {
      // Scope the style check to THIS map (Grafo vs Globo), so a style saved on
      // one map never suppresses the theme background on the other.
      var current = document.querySelector('#sb-map-switch a[aria-current="page"]');
      var styleKey = current && current.textContent.trim() === 'Globo'
        ? 'sb-sphere-style-v1' : 'sb-graph-style-v1';
      var saved = JSON.parse(localStorage.getItem(styleKey) || 'null');
      var pinned = saved && saved.colors && saved.colors.background;
      if (!pinned && typeof styleConfig !== 'undefined' && typeof applyStyle === 'function') {
        styleConfig.colors.background = theme === 'light' ? '#ffffff' : '#0a0a0a';
        applyStyle(styleConfig, { silent: true });
      }
    } catch (e) {}
  })();
</script>
"""


def with_public_chrome(html: str, current: str) -> str:
    """Add the site navigation to a generated map and drop its index panel."""
    chrome = (PUBLIC_CHROME
              .replace("__GRAPH_CURRENT__", ' aria-current="page"' if current == "graph" else "")
              .replace("__SPHERE_CURRENT__", ' aria-current="page"' if current == "sphere" else ""))
    if "</body>" in html:
        return html.replace("</body>", chrome + "</body>", 1)
    return html + chrome


def build(width: int = 1900, height: int = 1200):
    nodes, edges, isolated = build_graph.build_graph()
    tag_gaps = build_graph.compute_tag_gaps(nodes, edges)

    # The two renderers read different coordinates — the graph uses x0/y0, the
    # sphere ux/uy/uz — so both layouts run over the same nodes.
    build_graph.compute_layout(nodes, edges, width=width, height=height)
    build_sphere.compute_sphere_layout(nodes, edges)

    published = {e.slug for e in collect_public()}
    public_nodes = sanitize(nodes, published)
    return public_nodes, edges, tag_gaps, isolated


def data_payload(nodes, edges, isolated) -> dict:
    counts: dict[str, int] = {}
    for node in nodes:
        counts[node["type"]] = counts.get(node["type"], 0) + 1
    return {
        "nodes": nodes,
        "edges": edges,
        "counts": counts,
        "published": sum(1 for n in nodes if n.get("public")),
        "isolated": len(isolated),
    }


def write(root: Path, nodes, edges, tag_gaps, isolated) -> list[tuple[str, float]]:
    root.mkdir(parents=True, exist_ok=True)
    empty_reader = {"essays": {}, "mathjax": "", "css": ""}
    written = []

    (root / "graph.json").write_text(
        json.dumps(data_payload(nodes, edges, isolated),
                   ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    written.append(("graph.json", (root / "graph.json").stat().st_size / 1024 / 1024))

    for name, renderer, current in (
        ("graph.html", build_graph.render_html, "graph"),
        ("sphere.html", build_sphere.render_sphere_html, "sphere"),
    ):
        path = root / name
        html = with_public_chrome(renderer(nodes, edges, tag_gaps, empty_reader), current)
        path.write_text(html, encoding="utf-8")
        written.append((name, path.stat().st_size / 1024 / 1024))

    return written


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, default=SITE_ROOT,
                    help="directory to write into (default: SITE_ROOT)")
    ap.add_argument("--json", action="store_true",
                    help="print the sanitized data instead of writing")
    args = ap.parse_args()

    nodes, edges, tag_gaps, isolated = build()

    if args.json:
        print(json.dumps(data_payload(nodes, edges, isolated),
                         ensure_ascii=False, indent=2))
        return 0

    written = write(args.output, nodes, edges, tag_gaps, isolated)
    readable = sum(1 for n in nodes if n.get("public"))
    print(f"public map: {len(nodes)} nodes, {len(edges)} edges, {readable} readable")
    for name, size in written:
        print(f"  {name:12s} {size:.1f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
