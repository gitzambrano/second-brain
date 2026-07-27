#!/usr/bin/env python3
"""
graph.py - Generate a connection graph of the entire wiki.

Nodes: essays, concepts, entities, insights pages.
Edges: every [[wikilink]] found in a page's body, resolved by H1 title
(the wiki's own linking convention -- see conventions/SKILL.md).

Outputs:
    output/graph/graph.html  - rich interactive D3 force-directed graph
    output/graph/graph.md    - lightweight Mermaid fallback (no browser needed)
    output/graph/graph.json  - raw node/edge data, for reuse by other tools

Usage:
    python scripts/graph.py
"""

import json
import re
from collections import defaultdict
from pathlib import Path

import yaml

ROOT_DIR = Path(__file__).resolve().parent.parent
WIKI_ROOT = ROOT_DIR / "wiki"
ESSAYS_DIR = WIKI_ROOT / "essays"
CONCEPTS_DIR = WIKI_ROOT / "concepts"
ENTITIES_DIR = WIKI_ROOT / "entities"
INSIGHTS_DIR = WIKI_ROOT / "insights"
OUTPUT_DIR = ROOT_DIR / "output" / "graph"

DIRS = {
    "essay": ESSAYS_DIR,
    "concept": CONCEPTS_DIR,
    "entity": ENTITIES_DIR,
    "insights": INSIGHTS_DIR,
}


def load(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return f.read()


def get_h1(content):
    m = re.search(r"(?m)^# (.+)", content)
    return m.group(1).strip() if m else None


def get_frontmatter(content):
    m = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except Exception:
        return {}


def strip_frontmatter(content):
    return re.sub(r"^---\n.*?\n---\n?", "", content, count=1, flags=re.DOTALL)


def strip_fences(body):
    """Remove fenced code blocks so example wikilinks in docs don't become edges."""
    return re.sub(r"```.*?```", "", body, flags=re.DOTALL)


def build_graph():
    nodes = {}          # id -> node dict
    title_to_id = {}     # H1 title -> node id
    bodies = {}          # id -> body text (for edge extraction)

    for node_type, dir_path in DIRS.items():
        if not dir_path.exists():
            continue
        for file in sorted(dir_path.glob("*.md")):
            content = load(file)
            title = get_h1(content)
            if not title:
                continue
            fm = get_frontmatter(content)
            node_id = f"{node_type}:{file.stem}"
            subtype = None
            if node_type == "insights":
                subtype = f"maturidade:{fm.get('maturidade', 'desconhecida')}"
            nodes[node_id] = {
                "id": node_id,
                "title": title,
                "type": node_type,
                "subtype": subtype,
                "tags": fm.get("tags", []) if isinstance(fm.get("tags"), list) else [],
                "file": str(file.relative_to(ROOT_DIR)),
                "degree": 0,
            }
            title_to_id[title] = node_id
            bodies[node_id] = strip_fences(strip_frontmatter(content))

    edges = []
    seen_pairs = set()
    for node_id, body in bodies.items():
        links = re.findall(r"\[\[([^\]]+)\]\]", body)
        for raw in links:
            target_title = raw.split("|")[0].strip()
            if target_title.startswith("#"):
                continue
            target_id = title_to_id.get(target_title)
            if not target_id or target_id == node_id:
                continue
            pair = tuple(sorted((node_id, target_id)))
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            edges.append({"source": node_id, "target": target_id})
            nodes[node_id]["degree"] += 1
            nodes[target_id]["degree"] += 1

    isolated = [n["title"] for n in nodes.values() if n["degree"] == 0]
    return list(nodes.values()), edges, isolated


MERMAID_CLASS = {
    "essay": "essay",
    "concept": "concept",
    "entity": "entity",
    "insights": "insights",
}


def render_mermaid(nodes, edges):
    lines = ["```mermaid", "graph TD"]
    for n in nodes:
        safe_id = n["id"].replace(":", "_").replace("-", "_").replace(".", "_").replace(" ", "_")
        label = n["title"].replace('"', "'")
        lines.append(f'    {safe_id}["{label}"]:::{MERMAID_CLASS[n["type"]]}')
    for e in edges:
        s = e["source"].replace(":", "_").replace("-", "_").replace(".", "_").replace(" ", "_")
        t = e["target"].replace(":", "_").replace("-", "_").replace(".", "_").replace(" ", "_")
        lines.append(f"    {s} --- {t}")
    lines += [
        "    classDef essay fill:#4fa8ff,stroke:#1c3f66,color:#0b1220;",
        "    classDef concept fill:#5fd3c4,stroke:#1c4f47,color:#0b1220;",
        "    classDef entity fill:#e8b657,stroke:#6b4f16,color:#0b1220;",
        "    classDef insights fill:#b48ce8,stroke:#4a2f66,color:#0b1220;",
        "```",
    ]
    return "\n".join(lines)


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Grafo — Second Brain</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
  :root {
    --bg: #1b1e21;
    --panel: #24282c;
    --panel-border: #34393e;
    --ink: #e6e9ec;
    --ink-dim: #9aa3ab;
    --instrument-blue: #4fa8ff;
    --concept: #5fd3c4;
    --entity: #e8b657;
    --insight: #b48ce8;
    --edge: #454b52;
  }
  * { box-sizing: border-box; }
  body { margin:0; font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; background: var(--bg); color: var(--ink); overflow: hidden; }
  #graph { width: 100vw; height: 100vh; display: block; }
  #panel {
    position: fixed; top: 16px; left: 16px; width: 300px; max-height: calc(100vh - 32px);
    overflow-y: auto; background: var(--panel); border: 1px solid var(--panel-border);
    border-radius: 10px; padding: 16px; box-shadow: 0 8px 24px rgba(0,0,0,.35);
  }
  #panel h1 { font-size: 15px; margin: 0 0 4px 0; letter-spacing: .02em; color: var(--instrument-blue); }
  #panel .sub { font-size: 11px; color: var(--ink-dim); margin-bottom: 12px; }
  #search { width: 100%; padding: 8px 10px; border-radius: 6px; border: 1px solid var(--panel-border);
    background: #1b1e21; color: var(--ink); font-size: 13px; margin-bottom: 12px; }
  .legend-item { display: flex; align-items: center; gap: 8px; font-size: 12px; margin: 6px 0; color: var(--ink-dim); }
  .dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
  #info { margin-top: 14px; padding-top: 14px; border-top: 1px solid var(--panel-border); font-size: 12px; color: var(--ink-dim); }
  #info b { color: var(--ink); }
  #stats { font-size: 11px; color: var(--ink-dim); margin-top: 10px; line-height: 1.6; }
  .node-title { font-size: 10px; fill: var(--ink); pointer-events: none; opacity: .85; }
  .link { stroke: var(--edge); stroke-width: 1.2px; }
  .dim { opacity: .08; }
</style>
</head>
<body>
<svg id="graph"></svg>
<div id="panel">
  <h1>Grafo da Wiki</h1>
  <div class="sub">__NODE_COUNT__ páginas · __EDGE_COUNT__ conexões</div>
  <input id="search" type="text" placeholder="Buscar por título ou tag...">
  <div class="legend-item"><span class="dot" style="background:var(--instrument-blue)"></span> Essay</div>
  <div class="legend-item"><span class="dot" style="background:var(--concept)"></span> Concept</div>
  <div class="legend-item"><span class="dot" style="background:var(--entity)"></span> Entity</div>
  <div class="legend-item"><span class="dot" style="background:var(--insight)"></span> Insight</div>
  <div id="info">Clique num nó para ver detalhes e destacar vizinhos. Arraste pra reorganizar. Scroll pra zoom.</div>
  <div id="stats"></div>
</div>
<script>
const data = __DATA_JSON__;

const typeColor = (n) => {
  if (n.type === "essay") return "var(--instrument-blue)";
  if (n.type === "concept") return "var(--concept)";
  if (n.type === "entity") return "var(--entity)";
  if (n.type === "insights") return "var(--insight)";
  return "#888";
};

const width = window.innerWidth, height = window.innerHeight;
const svg = d3.select("#graph").attr("viewBox", [0, 0, width, height]);
const container = svg.append("g");

svg.call(d3.zoom().scaleExtent([0.1, 6]).on("zoom", (event) => {
  container.attr("transform", event.transform);
}));

const linkSel = container.append("g").selectAll("line")
  .data(data.edges).join("line").attr("class", "link");

const nodeSel = container.append("g").selectAll("circle")
  .data(data.nodes).join("circle")
  .attr("r", d => 5 + Math.sqrt(d.degree) * 3)
  .attr("fill", d => typeColor(d))
  .attr("stroke", "#0b1220")
  .attr("stroke-width", 1)
  .style("cursor", "pointer")
  .call(d3.drag()
    .on("start", dragstarted)
    .on("drag", dragged)
    .on("end", dragended));

const labelSel = container.append("g").selectAll("text")
  .data(data.nodes).join("text")
  .attr("class", "node-title")
  .attr("dy", d => -(7 + Math.sqrt(d.degree) * 3))
  .attr("text-anchor", "middle")
  .text(d => d.title);

const simulation = d3.forceSimulation(data.nodes)
  .force("link", d3.forceLink(data.edges).id(d => d.id).distance(70).strength(0.5))
  .force("charge", d3.forceManyBody().strength(-160))
  .force("center", d3.forceCenter(width / 2, height / 2))
  .force("collide", d3.forceCollide().radius(d => 12 + Math.sqrt(d.degree) * 3));

simulation.on("tick", () => {
  linkSel
    .attr("x1", d => d.source.x).attr("y1", d => d.source.y)
    .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
  nodeSel.attr("cx", d => d.x).attr("cy", d => d.y);
  labelSel.attr("x", d => d.x).attr("y", d => d.y);
});

function dragstarted(event, d) {
  if (!event.active) simulation.alphaTarget(0.3).restart();
  d.fx = d.x; d.fy = d.y;
}
function dragged(event, d) { d.fx = event.x; d.fy = event.y; }
function dragended(event, d) {
  if (!event.active) simulation.alphaTarget(0);
  d.fx = null; d.fy = null;
}

const neighborsOf = (id) => {
  const s = new Set([id]);
  data.edges.forEach(e => {
    const a = typeof e.source === "object" ? e.source.id : e.source;
    const b = typeof e.target === "object" ? e.target.id : e.target;
    if (a === id) s.add(b);
    if (b === id) s.add(a);
  });
  return s;
};

nodeSel.on("click", (event, d) => {
  const neighbors = neighborsOf(d.id);
  nodeSel.classed("dim", n => !neighbors.has(n.id));
  labelSel.classed("dim", n => !neighbors.has(n.id));
  linkSel.classed("dim", e => {
    const a = typeof e.source === "object" ? e.source.id : e.source;
    const b = typeof e.target === "object" ? e.target.id : e.target;
    return a !== d.id && b !== d.id;
  });
  document.getElementById("info").innerHTML =
    `<b>${d.title}</b><br>Tipo: ${d.type}${d.subtype ? " (" + d.subtype + ")" : ""}<br>` +
    `Conexões: ${d.degree}<br>Tags: ${(d.tags || []).join(", ") || "(nenhuma)"}<br>` +
    `Arquivo: ${d.file}`;
});

svg.on("click", (event) => {
  if (event.target.tagName === "svg") {
    nodeSel.classed("dim", false);
    labelSel.classed("dim", false);
    linkSel.classed("dim", false);
    document.getElementById("info").innerHTML =
      "Clique num nó para ver detalhes e destacar vizinhos. Arraste pra reorganizar. Scroll pra zoom.";
  }
});

document.getElementById("search").addEventListener("input", (e) => {
  const q = e.target.value.trim().toLowerCase();
  if (!q) {
    nodeSel.classed("dim", false);
    labelSel.classed("dim", false);
    linkSel.classed("dim", false);
    return;
  }
  const matchIds = new Set(data.nodes.filter(n =>
    n.title.toLowerCase().includes(q) || (n.tags || []).some(t => t.toLowerCase().includes(q))
  ).map(n => n.id));
  nodeSel.classed("dim", n => !matchIds.has(n.id));
  labelSel.classed("dim", n => !matchIds.has(n.id));
  linkSel.classed("dim", true);
});

const isolated = data.nodes.filter(n => n.degree === 0).length;
const byType = {};
data.nodes.forEach(n => { byType[n.type] = (byType[n.type] || 0) + 1; });
document.getElementById("stats").innerHTML =
  Object.entries(byType).map(([k, v]) => `${k}: ${v}`).join(" · ") +
  (isolated ? `<br>⚠ ${isolated} página(s) sem nenhuma conexão` : "");
</script>
</body>
</html>
"""


def render_html(nodes, edges):
    data_json = json.dumps({"nodes": nodes, "edges": edges}, ensure_ascii=False)
    html = HTML_TEMPLATE.replace("__DATA_JSON__", data_json)
    html = html.replace("__NODE_COUNT__", str(len(nodes)))
    html = html.replace("__EDGE_COUNT__", str(len(edges)))
    return html


def main():
    nodes, edges, isolated = build_graph()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    (OUTPUT_DIR / "graph.json").write_text(
        json.dumps({"nodes": nodes, "edges": edges}, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUTPUT_DIR / "graph.md").write_text(
        f"# Grafo da Wiki\n\n{len(nodes)} páginas, {len(edges)} conexões.\n\n" + render_mermaid(nodes, edges) + "\n",
        encoding="utf-8",
    )
    (OUTPUT_DIR / "graph.html").write_text(render_html(nodes, edges), encoding="utf-8")

    print(f"Grafo gerado: {len(nodes)} nós, {len(edges)} conexões.")
    print(f"  {OUTPUT_DIR / 'graph.html'} (interativo)")
    print(f"  {OUTPUT_DIR / 'graph.md'} (mermaid)")
    print(f"  {OUTPUT_DIR / 'graph.json'} (dados)")
    if isolated:
        print(f"\n⚠ {len(isolated)} página(s) sem nenhuma conexão:")
        for title in isolated:
            print(f"  - {title}")


if __name__ == "__main__":
    main()
