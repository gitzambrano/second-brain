#!/usr/bin/env python3
"""
graph.py - Generate a connection graph of the entire wiki.

Nodes: essays, concepts, entities, insights pages, e referências (a partir
de wiki/references.json, geradas por references_index.py — uma por
domain_group de origem, ver conventions/SKILL.md).
Edges: todo [[wikilink]] encontrado no corpo de uma página, resolvido por
título H1 (a convenção de link da própria wiki — ver conventions/SKILL.md);
e essay -> referência para cada `cited_by` de wiki/references.json.

Outputs:
    output/graph/graph.html  - rich interactive D3 force-directed graph
    output/graph/graph.md    - lightweight Mermaid fallback (no browser needed)
    output/graph/graph.json  - raw node/edge data, for reuse by other tools

Recursos do HTML interativo:
  - Legenda clicável (Essay/Concept/Entity/Insight/Reference por
    domain_group): clique simples isola aquele tipo/grupo; clique de novo
    remove o filtro.
  - Duplo clique num nó: abre o arquivo (file:// + caminho relativo) ou,
    para referência, a própria URL, em nova aba.
  - Botão "Índice" no painel lateral: modal com lista completa por tipo
    (título, tags, contagem de conexões), ordenável por coluna.
  - Painel de Gaps: componentes conectados (union-find) sobre nós+arestas,
    cruzado com `tags` de cada nó — reporta pares de tags cujos essays
    nunca caem no mesmo componente conectado (silo temático).

Usage:
    python scripts/graph.py
"""

import json
import re
from collections import defaultdict
from pathlib import Path

import yaml

import console_encoding  # noqa: F401  (UTF-8 no console; ver o módulo)

ROOT_DIR = Path(__file__).resolve().parent.parent
WIKI_ROOT = ROOT_DIR / "wiki"
ESSAYS_DIR = WIKI_ROOT / "essays"
CONCEPTS_DIR = WIKI_ROOT / "concepts"
ENTITIES_DIR = WIKI_ROOT / "entities"
INSIGHTS_DIR = WIKI_ROOT / "insights"
REFERENCES_JSON_PATH = WIKI_ROOT / "references.json"
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


def load_references():
    if not REFERENCES_JSON_PATH.exists():
        return []
    try:
        data = json.loads(REFERENCES_JSON_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    return data.get("references", [])


def build_graph():
    nodes = {}          # id -> node dict
    title_to_id = {}     # H1 title -> node id
    bodies = {}          # id -> body text (for edge extraction)
    slug_to_id = {}       # essay slug (filename stem) -> node id

    for node_type, dir_path in DIRS.items():
        if not dir_path.exists():
            continue
        for file in sorted(dir_path.glob("*.md")):
            if file.name == ".gitkeep":
                continue
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
                "url": None,
                "degree": 0,
            }
            title_to_id[title] = node_id
            bodies[node_id] = strip_fences(strip_frontmatter(content))
            if node_type == "essay":
                slug_to_id[file.stem] = node_id

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
            edges.append({"source": node_id, "target": target_id, "kind": "wikilink"})
            nodes[node_id]["degree"] += 1
            nodes[target_id]["degree"] += 1

    # Nós de referência (a partir de wiki/references.json) + arestas essay -> referência
    for i, ref in enumerate(load_references()):
        ref_id = f"reference:{i}"
        domain_group = ref.get("domain_group", "institucional")
        nodes[ref_id] = {
            "id": ref_id,
            "title": ref.get("citation_aiaa", ref_id),
            "type": "reference",
            "subtype": f"domain_group:{domain_group}",
            "tags": [],
            "file": None,
            "url": ref.get("url"),
            "degree": 0,
        }
        for slug in ref.get("cited_by", []):
            essay_id = slug_to_id.get(slug)
            if not essay_id:
                continue
            edges.append({"source": essay_id, "target": ref_id, "kind": "reference"})
            nodes[essay_id]["degree"] += 1
            nodes[ref_id]["degree"] += 1

    isolated = [n["title"] for n in nodes.values() if n["degree"] == 0]
    return list(nodes.values()), edges, isolated


def union_find_components(nodes, edges):
    """Union-find simples sobre ids de nó. Retorna dict id -> component_id."""
    parent = {n["id"]: n["id"] for n in nodes}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for e in edges:
        union(e["source"], e["target"])

    return {node_id: find(node_id) for node_id in parent}


def compute_tag_gaps(nodes, edges):
    """Pares de tags cujos essays nunca caem no mesmo componente conectado
    (nem transitivamente) — sinal de silo temático (ver plano de
    implementação, seção 3.4). Só considera nós com `tags` (essays hoje).
    """
    components = union_find_components(nodes, edges)
    tag_components = defaultdict(set)
    for n in nodes:
        for tag in n.get("tags") or []:
            tag_components[tag].add(components[n["id"]])

    tags = sorted(tag_components.keys())
    gaps = []
    for i in range(len(tags)):
        for j in range(i + 1, len(tags)):
            a, b = tags[i], tags[j]
            if tag_components[a].isdisjoint(tag_components[b]):
                gaps.append((a, b))
    return gaps


MERMAID_CLASS = {
    "essay": "essay",
    "concept": "concept",
    "entity": "entity",
    "insights": "insights",
    "reference": "reference",
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
        style = "-.-" if e.get("kind") == "reference" else "---"
        lines.append(f"    {s} {style} {t}")
    lines += [
        "    classDef essay fill:#4fa8ff,stroke:#1c3f66,color:#0b1220;",
        "    classDef concept fill:#5fd3c4,stroke:#1c4f47,color:#0b1220;",
        "    classDef entity fill:#e8b657,stroke:#6b4f16,color:#0b1220;",
        "    classDef insights fill:#b48ce8,stroke:#4a2f66,color:#0b1220;",
        "    classDef reference fill:#8a8f96,stroke:#3a3d40,color:#0b1220;",
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
    --reference: #8a8f96;
    --edge: #454b52;
    --edge-ref: #5a5f66;
  }
  * { box-sizing: border-box; }
  body { margin:0; font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; background: var(--bg); color: var(--ink); overflow: hidden; }
  #graph { width: 100vw; height: 100vh; display: block; }
  #panel {
    position: fixed; top: 16px; left: 16px; width: 320px; max-height: calc(100vh - 32px);
    overflow-y: auto; background: var(--panel); border: 1px solid var(--panel-border);
    border-radius: 10px; padding: 16px; box-shadow: 0 8px 24px rgba(0,0,0,.35);
  }
  #panel h1 { font-size: 15px; margin: 0 0 4px 0; letter-spacing: .02em; color: var(--instrument-blue); }
  #panel .sub { font-size: 11px; color: var(--ink-dim); margin-bottom: 12px; }
  #search { width: 100%; padding: 8px 10px; border-radius: 6px; border: 1px solid var(--panel-border);
    background: #1b1e21; color: var(--ink); font-size: 13px; margin-bottom: 12px; }
  .legend-item { display: flex; align-items: center; gap: 8px; font-size: 12px; margin: 4px 0; color: var(--ink-dim);
    cursor: pointer; padding: 3px 6px; border-radius: 5px; user-select: none; }
  .legend-item:hover { background: rgba(255,255,255,.05); }
  .legend-item.active { background: rgba(79,168,255,.15); color: var(--ink); }
  .legend-item.disabled { opacity: 0.5; text-decoration: line-through; }
  .legend-item.disabled .dot { background: #000000 !important; border: 1px solid var(--panel-border); }
  .dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
  #ref-groups { margin-left: 18px; display: none; }
  #ref-groups.open { display: block; }
  .btn { width: 100%; padding: 7px 10px; margin-top: 6px; border-radius: 6px; border: 1px solid var(--panel-border);
    background: #1b1e21; color: var(--ink); font-size: 12px; cursor: pointer; text-align: left; }
  .btn:hover { background: rgba(255,255,255,.06); }
  #info { margin-top: 14px; padding-top: 14px; border-top: 1px solid var(--panel-border); font-size: 12px; color: var(--ink-dim); }
  #info b { color: var(--ink); }
  #stats { font-size: 11px; color: var(--ink-dim); margin-top: 10px; line-height: 1.6; }
  .node-title { font-size: 10px; fill: var(--ink); pointer-events: none; opacity: .85; }
  .link { stroke: var(--edge); stroke-width: 1.2px; }
  .link.reference { stroke: var(--edge-ref); stroke-dasharray: 3,3; }
  .dim { opacity: .08; }
  .hidden-node { display: none; }
  #modal-overlay { display:none; position: fixed; inset: 0; background: rgba(0,0,0,.55); z-index: 20; }
  #modal-overlay.open { display: flex; align-items: center; justify-content: center; }
  #modal { width: min(760px, 92vw); max-height: 82vh; overflow-y: auto; background: var(--panel);
    border: 1px solid var(--panel-border); border-radius: 10px; padding: 18px; }
  #modal h2 { margin: 0 0 10px 0; font-size: 15px; color: var(--instrument-blue); }
  #modal table { width: 100%; border-collapse: collapse; font-size: 12px; }
  #modal th { text-align: left; color: var(--ink-dim); cursor: pointer; padding: 6px 8px; border-bottom: 1px solid var(--panel-border); position: sticky; top:0; background: var(--panel); }
  #modal td { padding: 6px 8px; border-bottom: 1px solid #2b2f33; vertical-align: top; }
  #modal tr:hover td { background: rgba(255,255,255,.03); }
  #modal .close { float: right; cursor: pointer; color: var(--ink-dim); }
  .gap-item { font-size: 12px; margin: 4px 0; color: var(--ink-dim); }
  .gap-item b { color: var(--ink); }
</style>
</head>
<body>
<svg id="graph"></svg>
<div id="panel">
  <h1>Grafo da Wiki</h1>
  <input id="search" type="text" placeholder="Buscar por título ou tag…">

  <div class="legend-item" data-type="essay"><span class="dot" style="background:var(--instrument-blue)"></span> Essay</div>
  <div class="legend-item" data-type="concept"><span class="dot" style="background:var(--concept)"></span> Concept</div>
  <div class="legend-item" data-type="entity"><span class="dot" style="background:var(--entity)"></span> Entity</div>
  <div class="legend-item" data-type="insights"><span class="dot" style="background:var(--insight)"></span> Insight</div>
  <div class="legend-item disabled" data-type="reference"><span class="dot" style="background:var(--reference)"></span> Reference</div>

  <button class="btn" id="btn-index">Índice</button>
  <button class="btn" id="btn-gaps">Gaps entre tags</button>

  <div id="detail" hidden></div>
</div>

<div id="modal-overlay">
  <div id="modal"><span class="close" id="modal-close">✕ fechar</span><div id="modal-body"></div></div>
</div>

<script>
const data = __DATA_JSON__;

const typeColor = (n) => {
  if (n.type === "essay") return "var(--instrument-blue)";
  if (n.type === "concept") return "var(--concept)";
  if (n.type === "entity") return "var(--entity)";
  if (n.type === "insights") return "var(--insight)";
  if (n.type === "reference") return "var(--reference)";
  return "#888";
};

const width = window.innerWidth, height = window.innerHeight;
const svg = d3.select("#graph").attr("viewBox", [0, 0, width, height]);
const container = svg.append("g");

svg.call(d3.zoom().scaleExtent([0.1, 6]).on("zoom", (event) => {
  container.attr("transform", event.transform);
}));

const linkSel = container.append("g").selectAll("line")
  .data(data.edges).join("line")
  .attr("class", d => "link" + (d.kind === "reference" ? " reference" : ""));

// O raio comunica quantas conexões o nó tem *entre as que estão à vista*. Se um
// tipo inteiro é ocultado pela legenda, as arestas que iam até ele deixam de
// existir para o leitor, e manter a bolinha do tamanho antigo mentiria sobre a
// centralidade daquele nó no grafo que está de fato na tela.
const nodeById = new Map(data.nodes.map(n => [n.id, n]));
const endpoint = (v) => (typeof v === "object" ? v : nodeById.get(v));

function recomputeVisibleDegrees() {
  data.nodes.forEach(n => { n.visibleDegree = 0; });
  data.edges.forEach(e => {
    const s = endpoint(e.source), t = endpoint(e.target);
    if (!s || !t || !isNodeVisible(s) || !isNodeVisible(t)) return;
    s.visibleDegree++;
    t.visibleDegree++;
  });
}

const radiusOf = (d) => 5 + Math.sqrt(d.visibleDegree ?? d.degree) * 3;

const nodeSel = container.append("g").selectAll("circle")
  .data(data.nodes).join("circle")
  .attr("r", radiusOf)
  .attr("fill", d => typeColor(d))
  .attr("stroke", "#0b1220")
  .attr("stroke-width", 1)
  .style("cursor", "pointer")
  .call(d3.drag()
    .on("start", dragstarted)
    .on("drag", dragged)
    .on("end", dragended));

const labelSel = container.append("g").selectAll("text")
  .data(data.nodes.filter(n => n.type !== "reference")).join("text")
  .attr("class", "node-title")
  .attr("dy", d => -(2 + radiusOf(d)))
  .attr("text-anchor", "middle")
  .text(d => d.title);

const simulation = d3.forceSimulation(data.nodes)
  .force("link", d3.forceLink(data.edges).id(d => d.id).distance(70).strength(0.5))
  .force("charge", d3.forceManyBody().strength(-160))
  .force("center", d3.forceCenter(width / 2, height / 2))
  .force("collide", d3.forceCollide().radius(d => 7 + radiusOf(d)));

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

const detailEl = document.getElementById("detail");

function resetHighlight() {
  nodeSel.classed("dim", false);
  labelSel.classed("dim", false);
  linkSel.classed("dim", false);
  detailEl.hidden = true;
}

function selectNode(d) {
  // Vindo do índice, o nó pode ser de um tipo que está oculto na legenda.
  // Reexibir é menos surpreendente do que clicar e não ver nada acontecer.
  if (hiddenTypes.has(d.type)) {
    hiddenTypes.delete(d.type);
    const chip = document.querySelector(`.legend-item[data-type="${d.type}"]`);
    if (chip) chip.classList.remove("disabled");
    updateVisibility();
  }

  const neighbors = neighborsOf(d.id);
  nodeSel.classed("dim", n => !neighbors.has(n.id));
  labelSel.classed("dim", n => !neighbors.has(n.id));
  linkSel.classed("dim", e => {
    const a = typeof e.source === "object" ? e.source.id : e.source;
    const b = typeof e.target === "object" ? e.target.id : e.target;
    return a !== d.id && b !== d.id;
  });

  const target = d.type === "reference" ? d.url : (d.file ? "../../" + d.file : null);
  detailEl.hidden = false;
  detailEl.innerHTML =
    `<div class="detail-title">${escapeHtml(d.title)}</div>` +
    `<div class="detail-tags">${(d.tags || []).map(x => `<span>${escapeHtml(x)}</span>`).join("")}</div>` +
    (target ? `<a class="detail-open" href="${escapeHtml(target)}" target="_blank">abrir</a>` : "");
}

function openNode(d) {
  if (d.type === "reference") {
    if (d.url) window.open(d.url, "_blank");
    return;
  }
  if (d.file) {
    window.open("../../" + d.file, "_blank");
  }
}

nodeSel.on("click", (event, d) => {
  selectNode(d);
}).on("dblclick", (event, d) => {
  event.stopPropagation();
  openNode(d);
});

svg.on("click", (event) => {
  if (event.target.tagName === "svg") resetHighlight();
});

document.getElementById("search").addEventListener("input", (e) => {
  const q = e.target.value.trim().toLowerCase();
  if (!q) { resetHighlight(); return; }
  const matchIds = new Set(data.nodes.filter(n =>
    n.title.toLowerCase().includes(q) || (n.tags || []).some(t => t.toLowerCase().includes(q))
  ).map(n => n.id));
  nodeSel.classed("dim", n => !matchIds.has(n.id));
  labelSel.classed("dim", n => !matchIds.has(n.id));
  linkSel.classed("dim", true);
});

// ---- Legenda clicável com visibilidade independente para cada tipo ----
// Reference começa oculto: são centenas de nós-folha que afogam a estrutura
// entre essays, concepts e entities, que é o que o grafo existe para mostrar.
const hiddenTypes = new Set(["reference"]);

function isNodeVisible(n) {
  return !hiddenTypes.has(n.type);
}

function updateVisibility() {
  recomputeVisibleDegrees();

  nodeSel.classed("hidden-node", n => !isNodeVisible(n))
    .attr("r", radiusOf);
  labelSel.classed("hidden-node", n => !isNodeVisible(n))
    .attr("dy", d => -(2 + radiusOf(d)));
  linkSel.classed("hidden-node", e => {
    const s = endpoint(e.source), t = endpoint(e.target);
    return !s || !t || !isNodeVisible(s) || !isNodeVisible(t);
  });

  // Reacomoda o layout: bolinhas menores pedem menos espaço entre si.
  simulation.force("collide", d3.forceCollide().radius(d => 7 + radiusOf(d)));
  simulation.alpha(0.35).restart();
}

document.querySelectorAll(".legend-item[data-type]").forEach(el => {
  el.addEventListener("click", () => {
    const type = el.getAttribute("data-type");
    if (hiddenTypes.has(type)) {
      hiddenTypes.delete(type);
      el.classList.remove("disabled");
    } else {
      hiddenTypes.add(type);
      el.classList.add("disabled");
    }
    updateVisibility();
  });
});

updateVisibility();

// ---- Modal: Índice por tipo ----
const modalOverlay = document.getElementById("modal-overlay");
const modalBody = document.getElementById("modal-body");
document.getElementById("modal-close").addEventListener("click", () => modalOverlay.classList.remove("open"));
modalOverlay.addEventListener("click", (e) => { if (e.target === modalOverlay) modalOverlay.classList.remove("open"); });

const TYPE_LABELS = {
  essay: "Essays", concept: "Concepts", entity: "Entities",
  insights: "Insights", reference: "Referências",
};

function escapeHtml(s) {
  return String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}

function renderTypeIndex() {
  const state = { type: "essay", tags: new Set(), query: "", col: "degree", dir: -1 };

  modalBody.innerHTML = `
    <h2>Índice</h2>
    <div class="idx-tabs"></div>
    <input id="idx-search" type="text" placeholder="Filtrar por título…">
    <div class="idx-tags"></div>
    <table id="idx-table">
      <thead><tr>
        <th data-col="title">Título</th><th data-col="tags">Tags</th><th data-col="degree">Conexões</th>
      </tr></thead>
      <tbody></tbody>
    </table>
    <div class="idx-empty" hidden>Nada corresponde a esse filtro.</div>`;

  const tabsEl = modalBody.querySelector(".idx-tabs");
  const tagsEl = modalBody.querySelector(".idx-tags");
  const tbody = modalBody.querySelector("tbody");
  const emptyEl = modalBody.querySelector(".idx-empty");

  Object.keys(TYPE_LABELS).forEach(t => {
    const b = document.createElement("button");
    b.className = "idx-tab" + (t === state.type ? " active" : "");
    b.textContent = TYPE_LABELS[t];
    b.addEventListener("click", () => {
      state.type = t;
      state.tags.clear();
      tabsEl.querySelectorAll(".idx-tab").forEach(x => x.classList.toggle("active", x === b));
      drawTags();
      draw();
    });
    tabsEl.appendChild(b);
  });

  // As tags oferecidas são só as que existem no tipo em exibição: filtro que
  // não pode dar resultado vazio é filtro que não precisa estar ali.
  function drawTags() {
    const counts = new Map();
    data.nodes.filter(n => n.type === state.type).forEach(n => {
      (n.tags || []).forEach(t => counts.set(t, (counts.get(t) || 0) + 1));
    });
    const ordered = [...counts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
    tagsEl.innerHTML = "";
    ordered.forEach(([tag]) => {
      const chip = document.createElement("button");
      chip.className = "idx-chip";
      chip.textContent = tag;
      chip.addEventListener("click", () => {
        state.tags.has(tag) ? state.tags.delete(tag) : state.tags.add(tag);
        chip.classList.toggle("on", state.tags.has(tag));
        draw();
      });
      tagsEl.appendChild(chip);
    });
    tagsEl.hidden = ordered.length === 0;
  }

  function draw() {
    const q = state.query.toLowerCase();
    // Múltiplas tags selecionadas combinam por E: cada clique estreita o
    // resultado, que é como se procura o cruzamento entre dois assuntos.
    let rows = data.nodes.filter(n =>
      n.type === state.type
      && (!q || n.title.toLowerCase().includes(q))
      && [...state.tags].every(t => (n.tags || []).includes(t))
    );

    const value = (n) => state.col === "title" ? n.title.toLowerCase()
      : state.col === "tags" ? (n.tags || []).join(",").toLowerCase()
      : n.degree;
    rows.sort((a, b) => {
      const av = value(a), bv = value(b);
      return av < bv ? -state.dir : av > bv ? state.dir : 0;
    });

    tbody.innerHTML = rows.map(n => `<tr data-id="${escapeHtml(n.id)}">
      <td>${escapeHtml(n.title)}</td>
      <td class="idx-tagcell">${(n.tags || []).map(t => `<span>${escapeHtml(t)}</span>`).join("")}</td>
      <td>${n.degree}</td></tr>`).join("");
    emptyEl.hidden = rows.length > 0;

    tbody.querySelectorAll("tr").forEach(tr => {
      tr.addEventListener("click", () => {
        const node = nodeById.get(tr.getAttribute("data-id"));
        if (!node) return;
        modalOverlay.classList.remove("open");
        selectNode(node);
      });
    });
  }

  modalBody.querySelector("#idx-search").addEventListener("input", (e) => {
    state.query = e.target.value.trim();
    draw();
  });
  modalBody.querySelectorAll("th[data-col]").forEach(th => {
    th.addEventListener("click", () => {
      const col = th.getAttribute("data-col");
      state.dir = (state.col === col) ? -state.dir : -1;
      state.col = col;
      modalBody.querySelectorAll("th").forEach(x => x.classList.remove("sorted"));
      th.classList.add("sorted");
      draw();
    });
  });

  drawTags();
  draw();
}

document.getElementById("btn-index").addEventListener("click", () => {
  renderTypeIndex();
  modalOverlay.classList.add("open");
});

// ---- Painel de Gaps (calculado no Python, embutido nos dados) ----
document.getElementById("btn-gaps").addEventListener("click", () => {
  const gaps = data.tag_gaps || [];
  let html = `<h2>Painel de Gaps — tags que nunca se conectam</h2>`;
  html += `<div style="font-size:12px; color: var(--ink-dim); margin-bottom:10px;">Pares de tags cujos essays nunca caem no mesmo componente conectado do grafo (nem transitivamente via outros essays/conceitos/referências) — sinal de silo temático. Calculado sobre componentes conexos (union-find) de todos os nós e arestas.</div>`;
  if (!gaps.length) {
    html += "<div class=\\"gap-item\\">Nenhum par de tags isolado — todo o grafo conectado por tags está num único componente (or não há tags suficientes ainda).</div>";
  } else {
    gaps.forEach(([a, b]) => {
      html += `<div class="gap-item"><b>${a}</b> nunca se conecta com <b>${b}</b></div>`;
    });
  }
  modalBody.innerHTML = html;
  modalOverlay.classList.add("open");
});

</script>
</body>
</html>
"""


def render_html(nodes, edges, tag_gaps):
    data_json = json.dumps(
        {"nodes": nodes, "edges": edges, "tag_gaps": tag_gaps},
        ensure_ascii=False,
    )
    html = HTML_TEMPLATE.replace("__DATA_JSON__", data_json)
    return html


def main():
    nodes, edges, isolated = build_graph()
    tag_gaps = compute_tag_gaps(nodes, edges)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    (OUTPUT_DIR / "graph.json").write_text(
        json.dumps({"nodes": nodes, "edges": edges, "tag_gaps": tag_gaps}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (OUTPUT_DIR / "graph.md").write_text(
        f"# Grafo da Wiki\n\n{len(nodes)} páginas, {len(edges)} conexões.\n\n" + render_mermaid(nodes, edges) + "\n",
        encoding="utf-8",
    )
    (OUTPUT_DIR / "graph.html").write_text(render_html(nodes, edges, tag_gaps), encoding="utf-8")

    print(f"Grafo gerado: {len(nodes)} nós, {len(edges)} conexões.")
    print(f"  {OUTPUT_DIR / 'graph.html'} (interativo)")
    print(f"  {OUTPUT_DIR / 'graph.md'} (mermaid)")
    print(f"  {OUTPUT_DIR / 'graph.json'} (dados)")
    if isolated:
        print(f"\n⚠ {len(isolated)} página(s) sem nenhuma conexão:")
        for title in isolated:
            print(f"  - {title}")
    if tag_gaps:
        print(f"\n⚠ {len(tag_gaps)} par(es) de tags que nunca se conectam (ver painel de Gaps no HTML):")
        for a, b in tag_gaps:
            print(f"  - {a} / {b}")


if __name__ == "__main__":
    main()
