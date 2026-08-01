#!/usr/bin/env python3
"""
build_graph.py - Generate a connection graph of the entire wiki.

Nodes: essays, concepts, entities, insights pages, e referências (a partir
de wiki/references.json, geradas por build_references.py — uma por
domain_group de origem, ver conventions/SKILL.md).
Edges: todo [[wikilink]] encontrado no corpo de uma página, resolvido por
título H1 (a convenção de link da própria wiki — ver conventions/SKILL.md);
e essay -> referência para cada `cited_by` de wiki/references.json.

Outputs:
    output/graph/graph.html  - rich interactive D3 force-directed graph
    output/graph/graph.md    - lightweight Mermaid fallback (no browser needed)
    output/graph/graph.json  - raw node/edge data, for reuse by other tools

Recursos do HTML interativo:
  - Legenda clicável (Essay/Concept/Entity/Insight/Reference): cada tipo
    entra e sai da tela. Reference começa oculto — são centenas de nós-folha
    que afogam a estrutura entre essays, concepts e entities.
  - O raio de cada bolinha reflete o grau **visível**: ocultar um tipo
    recalcula os graus e reduz as bolinhas que perderam vizinhos, para o
    tamanho não mentir sobre a centralidade no grafo que está na tela.
  - Duplo clique num nó: abre o arquivo (file:// + caminho relativo) ou,
    para referência, a própria URL, em nova aba.
  - Botão "Índice": modal com abas por tipo, busca por título, filtro por
    tag (chips combináveis por E) e ordenação por coluna. Clicar numa linha
    fecha o modal e seleciona o nó no grafo.
  - Navegação: roda do mouse dá zoom, arrastar com o botão esquerdo move um
    nó, e arrastar com o botão do meio (clique na rodinha) faz pan do grafo
    inteiro, inclusive começando em cima de um nó.
  - Responsivo: em tela pequena o painel vira folha inferior recolhível por
    um botão, o modal do índice ocupa a tela toda e a tabela vira lista de
    cartões com barra de ordenação. Nada disso altera o desktop — mora todo
    dentro de media query.
  - Painel de Gaps: componentes conectados (union-find) sobre nós+arestas,
    cruzado com `tags` de cada nó — reporta pares de tags cujos essays
    nunca caem no mesmo componente conectado (silo temático).

Usage:
    python scripts/build_graph.py
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
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
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
  /* `dvh` acompanha a barra de endereço do navegador móvel, que muda de altura
     ao rolar; `vh` deixaria o grafo cortado atrás dela. */
  #graph { width: 100vw; height: 100vh; height: 100dvh; display: block; touch-action: none; }

  /* Botão de recolher o painel. Só aparece em tela pequena, onde o painel
     compete com o grafo pelo espaço todo. */
  #panel-toggle {
    display: none; position: fixed; z-index: 12; top: 10px; left: 10px;
    width: 40px; height: 40px; border-radius: 10px; cursor: pointer;
    border: 1px solid var(--panel-border); background: var(--panel); color: var(--ink);
    font-size: 17px; line-height: 1; align-items: center; justify-content: center;
    box-shadow: 0 4px 14px rgba(0,0,0,.4);
  }
  #panel {
    position: fixed; top: 16px; left: 16px; width: 320px; max-height: calc(100vh - 32px);
    overflow-y: auto; background: var(--panel); border: 1px solid var(--panel-border);
    border-radius: 10px; padding: 16px; box-shadow: 0 8px 24px rgba(0,0,0,.35);
  }
  #panel h1 { font-size: 13px; margin: 0 0 12px 0; letter-spacing: .08em; text-transform: uppercase;
    color: var(--ink-dim); font-weight: 600; }
  #search { width: 100%; padding: 8px 10px; border-radius: 6px; border: 1px solid var(--panel-border);
    background: #1b1e21; color: var(--ink); font-size: 13px; margin-bottom: 12px; }
  #search:focus { outline: none; border-color: var(--instrument-blue); }
  .legend-item { display: flex; align-items: center; gap: 8px; font-size: 12px; margin: 4px 0; color: var(--ink-dim);
    cursor: pointer; padding: 3px 6px; border-radius: 5px; user-select: none; }
  .legend-item:hover { background: rgba(255,255,255,.05); }
  .legend-item.active { background: rgba(79,168,255,.15); color: var(--ink); }
  .legend-item.disabled { opacity: 0.5; text-decoration: line-through; }
  .legend-item.disabled .dot { background: #000000 !important; border: 1px solid var(--panel-border); }
  .dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
  .btn { width: 100%; padding: 7px 10px; margin-top: 6px; border-radius: 6px; border: 1px solid var(--panel-border);
    background: #1b1e21; color: var(--ink); font-size: 12px; cursor: pointer; text-align: left; }
  .btn:hover { background: rgba(255,255,255,.06); border-color: var(--instrument-blue); }
  #detail { margin-top: 14px; padding-top: 14px; border-top: 1px solid var(--panel-border); }
  .detail-title { font-size: 13px; color: var(--ink); line-height: 1.35; }
  .detail-tags { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 8px; }
  .detail-tags span, .idx-tagcell span {
    font-size: 10px; color: var(--ink-dim); background: rgba(255,255,255,.05);
    border-radius: 4px; padding: 2px 6px; white-space: nowrap; }
  .detail-open { display: inline-block; margin-top: 10px; font-size: 11px;
    color: var(--instrument-blue); text-decoration: none; }
  .detail-open:hover { text-decoration: underline; }
  .node-title { font-size: 10px; fill: var(--ink); pointer-events: none; opacity: .85; }
  .link { stroke: var(--edge); stroke-width: 1.2px; }
  .link.reference { stroke: var(--edge-ref); stroke-dasharray: 3,3; }
  .dim { opacity: .08; }
  .hidden-node { display: none; }
  #modal-overlay { display:none; position: fixed; inset: 0; background: rgba(0,0,0,.55); z-index: 20; }
  #modal-overlay.open { display: flex; align-items: center; justify-content: center; }
  #modal { width: min(760px, 92vw); max-height: 82vh; overflow-y: auto; background: var(--panel);
    border: 1px solid var(--panel-border); border-radius: 10px; padding: 18px; }
  #modal h2 { margin: 0 0 14px 0; font-size: 13px; letter-spacing: .08em; text-transform: uppercase;
    color: var(--ink-dim); font-weight: 600; }
  #modal table { width: 100%; border-collapse: collapse; font-size: 12px; }
  #modal th { text-align: left; color: var(--ink-dim); cursor: pointer; padding: 6px 8px; border-bottom: 1px solid var(--panel-border); position: sticky; top:0; background: var(--panel); font-weight: 500; }
  #modal th:hover { color: var(--ink); }
  #modal th.sorted { color: var(--instrument-blue); }
  #modal td { padding: 7px 8px; border-bottom: 1px solid #2b2f33; vertical-align: top; }
  #modal tbody tr { cursor: pointer; }
  #modal tbody tr:hover td { background: rgba(79,168,255,.08); }
  #modal .close { float: right; cursor: pointer; color: var(--ink-dim); font-size: 11px; }
  #modal .close:hover { color: var(--ink); }

  .idx-tabs { display: flex; gap: 4px; margin-bottom: 12px; flex-wrap: wrap; }
  .idx-tab { padding: 5px 12px; border-radius: 999px; border: 1px solid var(--panel-border);
    background: transparent; color: var(--ink-dim); font-size: 11px; cursor: pointer; font-family: inherit; }
  .idx-tab:hover { color: var(--ink); }
  .idx-tab.active { background: var(--instrument-blue); border-color: var(--instrument-blue); color: #0b1220; font-weight: 600; }
  #idx-search { width: 100%; padding: 7px 10px; border-radius: 6px; border: 1px solid var(--panel-border);
    background: #1b1e21; color: var(--ink); font-size: 12px; margin-bottom: 10px; font-family: inherit; }
  #idx-search:focus { outline: none; border-color: var(--instrument-blue); }
  .idx-tags { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 14px; }
  .idx-chip { font-size: 10px; padding: 3px 9px; border-radius: 999px; cursor: pointer; font-family: inherit;
    border: 1px solid var(--panel-border); background: transparent; color: var(--ink-dim); }
  .idx-chip:hover { color: var(--ink); border-color: var(--ink-dim); }
  .idx-chip.on { background: rgba(79,168,255,.18); border-color: var(--instrument-blue); color: var(--instrument-blue); }
  .idx-tagcell { display: flex; flex-wrap: wrap; gap: 3px; }
  .idx-empty { font-size: 12px; color: var(--ink-dim); padding: 18px 4px; }

  /* ---- Tela pequena ----------------------------------------------------
     Nada aqui altera o desktop: tudo mora dentro da media query. O painel
     lateral vira folha inferior recolhível, porque numa tela de celular ele
     cobriria metade do grafo; e o modal do índice passa a ocupar a tela
     inteira, já que uma tabela em 92vw de largura fica ilegível. */
  @media (max-width: 720px), (pointer: coarse) and (max-width: 900px) {
    #panel-toggle {
      display: flex;
      top: calc(10px + env(safe-area-inset-top));
      left: calc(10px + env(safe-area-inset-left));
    }
    #panel {
      top: auto; bottom: 0; left: 0; width: 100vw; border-radius: 14px 14px 0 0;
      max-height: 58dvh; padding: 14px 16px calc(16px + env(safe-area-inset-bottom));
      border-left: none; border-right: none; border-bottom: none;
    }
    /* Esconder é `display: none`, não `transform` nem `visibility`: o painel
       precisa sumir de fato, inclusive parar de receber toque, e é a única
       forma que não depende de o renderizador resolver porcentagem de
       transform. O JS também aplica isto inline, para não ficar refém da
       cascata. Sem animação de deslizar, de propósito. */
    #panel.collapsed { display: none; }
    #panel h1 { display: none; }
    /* 16px evita o zoom automático que o iOS aplica em campo de texto menor. */
    #search, #idx-search { font-size: 16px; padding: 10px 12px; }
    .legend-item { font-size: 13px; padding: 7px 8px; }
    .dot { width: 12px; height: 12px; }
    .btn { padding: 10px 12px; font-size: 13px; }
    #modal-overlay.open { align-items: stretch; justify-content: stretch; }
    #modal {
      width: 100vw; max-width: none; max-height: 100dvh; height: 100dvh;
      border-radius: 0; border: none; padding: 14px 14px calc(14px + env(safe-area-inset-bottom));
    }
    #modal .close { font-size: 14px; padding: 4px 8px; }
    .idx-tab { padding: 8px 14px; font-size: 12px; }
    .idx-chip { padding: 6px 11px; font-size: 11px; }
    /* A lista de tags pode ficar longa; limita a altura e rola só ela. */
    .idx-tags { max-height: 22dvh; overflow-y: auto; }
    /* Tabela em coluna: cabeçalho de tabela não cabe em tela estreita. */
    #modal table, #modal tbody, #modal tbody tr, #modal td { display: block; width: 100%; }
    /* O cabeçalho vira barra de ordenação em vez de sumir: sem ele o índice
       perderia a ordenação por coluna justamente onde a lista é mais longa. */
    #modal thead { display: block; }
    #modal thead tr { display: flex; gap: 6px; }
    #modal th { flex: 1; text-align: center; font-size: 10px; padding: 9px 4px;
      border-radius: 6px; background: rgba(255,255,255,.05); border-bottom: none; position: static; }
    #modal tbody tr { border-bottom: 1px solid #2b2f33; padding: 10px 2px; }
    #modal td { border: none; padding: 2px; }
    #modal td:last-child { color: var(--ink-dim); font-size: 11px; }
    #modal td:last-child::before { content: "conexões: "; }
    .node-title { font-size: 12px; }
  }
  .gap-item { font-size: 12px; margin: 4px 0; color: var(--ink-dim); }
  .gap-item b { color: var(--ink); }
</style>
</head>
<body>
<svg id="graph"></svg>
<button id="panel-toggle" aria-label="Mostrar ou esconder o painel" aria-expanded="true">☰</button>
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

let width = window.innerWidth, height = window.innerHeight;
const svg = d3.select("#graph").attr("viewBox", [0, 0, width, height]);
const container = svg.append("g");

// Fica marcado assim que o próprio usuário mexe no zoom/pan (toque, roda ou
// arrasto), para nunca mais sobrescrever o enquadramento que ele escolheu —
// nem no fit-to-screen inicial do mobile, nem numa rotação de tela depois.
let userAdjustedView = false;

const zoom = d3.zoom()
  .scaleExtent([0.1, 6])
  .filter((event) => {
    // Toque (touchstart/touchmove/touchend/touchcancel) não tem `.button`
    // — sem este ramo, todo evento de toque cai no `return event.button...`
    // abaixo, que dá `undefined === 0`, ou seja `false`, e zoom/pan morrem
    // por completo no celular. Toque sempre libera: pinça dá zoom e um dedo
    // só dá pan; arrastar um nó continua funcionando porque o d3.drag do
    // próprio nó intercepta o evento antes (nopropagation) e ele nem chega
    // a subir até aqui.
    if (event.type.startsWith("touch")) return true;
    // O filtro padrão do d3 aceita só o botão esquerdo (`!event.button`).
    // Liberar o botão do meio dá o pan por clique-na-rodinha sem tirar o
    // arrastar de nó, que continua no esquerdo: o d3.drag ignora o botão 1,
    // então o evento sobe até aqui e vira pan mesmo começando sobre um nó.
    if (event.type === "wheel") return !event.ctrlKey;
    return event.button === 0 || event.button === 1;
  })
  .on("zoom", (event) => {
    container.attr("transform", event.transform);
    // `sourceEvent` só existe quando a transformação veio de uma interação
    // real (toque, roda, arrasto) — chamadas programáticas como o
    // fitToScreen() não têm, então não acionam esta marca.
    if (event.sourceEvent) userAdjustedView = true;
  });

svg.call(zoom);

// Sem isto o navegador entra em auto-scroll (aquele ícone de setas) no
// clique do meio, e o pan nunca chega a acontecer.
svg.on("mousedown", (event) => { if (event.button === 1) event.preventDefault(); });
svg.on("auxclick", (event) => { if (event.button === 1) event.preventDefault(); });

// Rotação de tela e troca de janela: sem isto o viewBox fica com a dimensão
// de carregamento e o grafo aparece cortado ou centralizado fora da tela.
function ajustarViewport() {
  width = window.innerWidth;
  height = window.innerHeight;
  svg.attr("viewBox", [0, 0, width, height]);
  simulation.force("center", d3.forceCenter(width / 2, height / 2));
  simulation.alpha(0.15).restart();
  // Ao voltar para tela grande o painel reaparece: `collapsed` é inerte fora
  // da media query, mas deixar a classe pendurada faria o botão reaparecer
  // com o rótulo errado se a janela encolhesse de novo.
  if (!telaPequena()) definirPainel(true);
  // Girar o celular muda completamente o que cabe na tela; reencaixa o
  // grafo, a menos que o usuário já tenha escolhido o próprio enquadramento.
  else fitToScreen(true);
}
window.addEventListener("resize", ajustarViewport);
window.addEventListener("orientationchange", ajustarViewport);

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

// ---- Painel recolhível (tela pequena) ----
const panelEl = document.getElementById("panel");
const toggleEl = document.getElementById("panel-toggle");
const telaPequena = () => getComputedStyle(toggleEl).display !== "none";

function definirPainel(aberto) {
  const esconder = !aberto && telaPequena();
  panelEl.classList.toggle("collapsed", !aberto);
  // O inline vence a cascata e não depende de a media query ser reavaliada.
  panelEl.style.display = esconder ? "none" : "";
  toggleEl.setAttribute("aria-expanded", String(aberto));
  toggleEl.textContent = aberto ? "✕" : "☰";
}

toggleEl.addEventListener("click", () => {
  definirPainel(panelEl.classList.contains("collapsed"));
});

// Em tela pequena o painel começa fechado: quem abre o grafo no celular quer
// ver o grafo, não a legenda. No desktop a media query esconde o botão e a
// classe `collapsed` não tem efeito nenhum, então nada muda.
if (telaPequena()) definirPainel(false);

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
  // O cartão de detalhe mora dentro do painel, mas o painel só deve abrir
  // por ação explícita no botão ☰ — nunca sozinho por causa de um toque no
  // grafo. Num celular com o painel recolhido, o destaque no próprio grafo
  // (nós vizinhos) já é o feedback da seleção; o cartão de detalhe fica
  // pronto e some ao abrir o painel manualmente.
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

// ---- Fit-to-screen inicial (mobile) ------------------------------------
// No desktop o grafo nasce em torno do centro e cabe razoavelmente numa
// tela grande. No celular a viewport é estreita e a simulação de forças
// espalha os nós livremente pelo espaço "de mundo" (que não tem relação
// nenhuma com o tamanho da tela) — sem isto, quem abre o grafo no celular
// vê só um pedaço cortado e precisa dar zoom out à mão antes de enxergar
// qualquer estrutura.
function fitToScreen(instant) {
  if (userAdjustedView || !telaPequena()) return;
  const visible = data.nodes.filter(n => n.x != null && n.y != null && isNodeVisible(n));
  if (!visible.length) return;

  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  visible.forEach(n => {
    minX = Math.min(minX, n.x); maxX = Math.max(maxX, n.x);
    minY = Math.min(minY, n.y); maxY = Math.max(maxY, n.y);
  });
  const bboxW = Math.max(1, maxX - minX);
  const bboxH = Math.max(1, maxY - minY);
  const padding = 48;
  const [minScale, maxScale] = zoom.scaleExtent();
  const scale = Math.max(minScale, Math.min(
    maxScale,
    0.92 / Math.max(bboxW / (width - padding * 2), bboxH / (height - padding * 2))
  ));
  const cx = (minX + maxX) / 2, cy = (minY + maxY) / 2;
  const transform = d3.zoomIdentity.translate(width / 2, height / 2).scale(scale).translate(-cx, -cy);

  (instant ? svg : svg.transition().duration(280)).call(zoom.transform, transform);
}

if (telaPequena()) {
  // A simulação esfria e emite "end" sozinha (alphaDecay padrão) — nesse
  // ponto os nós já pararam de se mexer e o bounding box é definitivo.
  simulation.on("end.fit", () => fitToScreen(false));
  // Rede de segurança: grafos grandes podem demorar mais que o usuário tem
  // paciência de esperar olhando para um canto cortado do grafo. Reencaixa
  // de qualquer jeito depois de 1.2s, mesmo que a simulação ainda não tenha
  // acabado — melhor um enquadramento aproximado cedo do que o exato tarde.
  setTimeout(() => fitToScreen(true), 1200);
}

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
  let html = `<h2>Gaps entre tags</h2>`;
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
