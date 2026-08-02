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
  - iPhone/Safari: pinch/pan tratados à parte do Android/Chrome — Safari
    ignora `touch-action` de forma inconsistente e tem gesto próprio de
    pinch-zoom de página (`gesturestart`/`gesturechange`) que não existe em
    outros navegadores; sem neutralizar os dois, o grafo funciona no Android
    e "trava" ou pula no iPhone. Ver comentários em torno de
    `desligarGestoNativoIOS()` no HTML gerado.
  - Painel de Gaps: componentes conectados (union-find) sobre nós+arestas,
    cruzado com `tags` de cada nó — reporta pares de tags cujos essays
    nunca caem no mesmo componente conectado (silo temático).
  - Painel de Estilo: cores por tipo de nó, cor/opacidade das arestas, raio
    base e escala por grau, tamanho de rótulo — tudo ajustável ao vivo pelo
    modal "Estilo" no HTML gerado (persistido em localStorage do navegador,
    por wiki) ou, para um padrão permanente, editando `GRAPH_STYLE` abaixo
    antes de rodar o script.

Usage:
    python scripts/build_graph.py
"""

import json
import math
import random
import re
import time
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

# Aparência padrão do grafo. Editável aqui para um novo padrão permanente
# (todo mundo que abrir o HTML do zero recebe estas cores/tamanhos), ou
# ajustável ao vivo no navegador via o modal "Estilo" — nesse caso a escolha
# fica salva em localStorage e sobrescreve este padrão só naquele navegador.
GRAPH_STYLE = {
    "colors": {
        "essay": "#4fa8ff",
        "concept": "#5fd3c4",
        "entity": "#e8b657",
        "insights": "#b48ce8",
        "reference": "#8a8f96",
        "edge": "#454b52",
        "background": "#1b1e21",
    },
    "edgeOpacity": 0.55,
    "radiusBase": 5,
    "radiusScale": 3,
    "labelSize": 10,
    # "off" | "leve" (halo sem blur, barato) | "alto" (drop-shadow com blur,
    # mais bonito porém pesado em SVG — cada nó vira uma rasterização à
    # parte; em grafos grandes ou no Chrome mobile isso é o maior vilão de
    # FPS que existe aqui). "leve" é o padrão por ser barato E ainda dar
    # uma sensação de brilho.
    "glow": "leve",
    "starfield": True,
    "gradient": True,
    # "degree" (nº de conexões visíveis), "bytes" ou "lines" (tamanho do
    # corpo do arquivo). Só afeta essay/concept/entity/insights — reference
    # não tem arquivo e sempre usa o raio base.
    "sizeMode": "degree",
    # Multiplicador de distância entre bolinhas (colisão + arestas + carga).
    # 1 = padrão; acima disso, o grafo "respira" mais quando fica denso
    # demais pra ler.
    "spacing": 1,
    # "auto" | "alta" | "media" | "baixa" — ver PERFORMANCE_TIERS no HTML
    # gerado. "auto" decide pelo tamanho do grafo e pelo aparelho (celular
    # entra em "baixa"/"média" sozinho); as wikis grandes se beneficiam
    # de deixar em "auto" e não pensar mais nisso.
    "performance": "auto",
}

# Aplicado por cima de GRAPH_STYLE no navegador, só quando o próprio
# navegador se identifica como celular/tablet (toque ou tela pequena) — e só
# se o usuário nunca salvou uma preferência própria naquele aparelho. Glow e
# céu estrelado são os itens puramente decorativos mais caros de render;
# desligá-los por padrão no celular evita que a maioria dos usuários mobile
# precise descobrir o painel de Estilo só pra destravar performance.
GRAPH_STYLE_MOBILE_OVERRIDES = {
    "glow": "off",
    "starfield": False,
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
                "maturidade": fm.get("maturidade") if node_type == "insights" else None,
                "tags": fm.get("tags", []) if isinstance(fm.get("tags"), list) else [],
                "file": str(file.relative_to(ROOT_DIR)),
                "url": None,
                "degree": 0,
            }
            title_to_id[title] = node_id
            # O slug do arquivo também indexa o nó. A forma canônica de wikilink
            # na wiki é `[[slug|Título]]`, porque é a única que o Obsidian
            # resolve, então o alvo que aparece no texto é o SLUG. Indexar só
            # pelo H1 derrubava o grafo de ~2500 para ~780 arestas, e nós sem
            # aresta somem da tela.
            title_to_id.setdefault(file.stem, node_id)
            body_text = strip_fences(strip_frontmatter(content))
            bodies[node_id] = body_text
            # Tamanho do essay como proxy de "densidade" — alternativa ao grau
            # como métrica de raio da bolinha no grafo (ver GRAPH_STYLE/sizeMode
            # e o painel "Estilo" no HTML: nem todo nó denso é bem conectado
            # ainda, e vice-versa; o usuário escolhe qual conta mais para ele).
            nodes[node_id]["sizeBytes"] = len(body_text.encode("utf-8"))
            nodes[node_id]["sizeLines"] = len([ln for ln in body_text.splitlines() if ln.strip()])
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
            "sizeBytes": 0,
            "sizeLines": 0,
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


def compute_layout(nodes, edges, width=1600, height=1000, iterations=None, seed=42):
    """Layout força-dirigida (Fruchterman-Reingold simplificado), em Python
    puro, sem dependências novas.

    Por quê fazer isto no build em vez de deixar o navegador calcular: o
    d3.forceSimulation no cliente começa de posições aleatórias e precisa de
    ~300 ticks (cada um recalculando repulsão de todo par de nós) até
    "assentar" — e cada tick redesenha o SVG inteiro. Isso roda toda vez que
    alguém abre o HTML, inclusive no celular, onde é sensivelmente mais
    lento que no desktop. Pré-calcular aqui, uma vez, no build, e embutir
    x/y prontos no JSON faz o navegador abrir quase já assentado — o
    d3.forceSimulation no cliente só precisa de umas dezenas de ticks pra
    resolver sobreposição fina, não o layout inteiro do zero.

    O algoritmo é O(nós² × iterações) — aceitável em build time (roda uma
    vez quando o Usuário chama o script, não a cada carregamento de página).
    `iterations=None` escala automaticamente pelo tamanho do grafo (menos
    iterações em wikis grandes) pra manter o build na casa de segundos;
    passe um número explícito pra forçar mais precisão.
    """
    rng = random.Random(seed)
    n = len(nodes)
    if n == 0:
        return
    if n == 1:
        nodes[0]["x0"] = width / 2
        nodes[0]["y0"] = height / 2
        return

    if iterations is None:
        if n <= 300:
            iterations = 250
        elif n <= 800:
            iterations = 120
        else:
            iterations = 60

    area = width * height
    k = math.sqrt(area / n)  # distância "ideal" de equilíbrio entre nós

    pos = {node["id"]: [rng.uniform(0, width), rng.uniform(0, height)] for node in nodes}
    node_ids = [node["id"] for node in nodes]

    for it in range(iterations):
        temp = (1 - it / iterations) * (width / 10)  # esfria: passos grandes no início, finos no fim
        disp = {nid: [0.0, 0.0] for nid in node_ids}

        # Repulsão entre todos os pares — o termo O(n²) do algoritmo.
        for i in range(n):
            xi, yi = pos[node_ids[i]]
            for j in range(i + 1, n):
                xj, yj = pos[node_ids[j]]
                dx, dy = xi - xj, yi - yj
                dist = math.hypot(dx, dy) or 0.01
                force = (k * k) / dist
                fx, fy = (dx / dist) * force, (dy / dist) * force
                disp[node_ids[i]][0] += fx
                disp[node_ids[i]][1] += fy
                disp[node_ids[j]][0] -= fx
                disp[node_ids[j]][1] -= fy

        # Atração ao longo das arestas.
        for e in edges:
            a, b = e["source"], e["target"]
            if a not in pos or b not in pos:
                continue
            xa, ya = pos[a]
            xb, yb = pos[b]
            dx, dy = xa - xb, ya - yb
            dist = math.hypot(dx, dy) or 0.01
            force = (dist * dist) / k
            fx, fy = (dx / dist) * force, (dy / dist) * force
            disp[a][0] -= fx
            disp[a][1] -= fy
            disp[b][0] += fx
            disp[b][1] += fy

        for nid in node_ids:
            dx, dy = disp[nid]
            dist = math.hypot(dx, dy) or 0.01
            step = min(dist, temp)
            pos[nid][0] += (dx / dist) * step
            pos[nid][1] += (dy / dist) * step
            # Mantém dentro da área — evita que outliers fujam pro infinito
            # em grafos muito assimétricos (um nó com grau 1 isolado longe
            # do resto), o que faria o fit-to-screen do cliente zoom out
            # demais no primeiro carregamento.
            pos[nid][0] = min(width, max(0, pos[nid][0]))
            pos[nid][1] = min(height, max(0, pos[nid][1]))

    for node in nodes:
        x, y = pos[node["id"]]
        node["x0"] = round(x, 1)
        node["y0"] = round(y, 1)


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
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
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
    --edge-opacity: 0.55;
    --radius-base: 5;
    --radius-scale: 3;
    --label-size: 10px;
    --node-glow: drop-shadow(0 0 0 transparent);
  }
  * { box-sizing: border-box; }
  /* `html` também precisa da trava de toque/scroll: no iPhone, sem isto, um
     arrasto que começa fora do <svg> (ex.: numa fração de pixel da borda)
     ainda faz o corpo da página fazer o "bounce" elástico do Safari, o que
     no Android nunca acontece — Chrome não tem esse gesto de página. */
  html, body {
    margin: 0; height: 100%; overflow: hidden; overscroll-behavior: none;
    touch-action: none; -webkit-user-select: none; user-select: none;
    -webkit-touch-callout: none; -webkit-tap-highlight-color: transparent;
  }
  body { font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; background: var(--bg); color: var(--ink); }
  /* `dvh` acompanha a barra de endereço do navegador móvel, que muda de altura
     ao rolar; `vh` deixaria o grafo cortado atrás dela. */
  #graph { width: 100vw; height: 100vh; height: 100dvh; display: block; touch-action: none; -webkit-user-select: none; }

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
  .node-title { font-size: var(--label-size); fill: var(--ink); pointer-events: none; opacity: .85; }
  .link { stroke: var(--edge); stroke-width: 1.2px; opacity: var(--edge-opacity); }
  .link.reference { stroke: var(--edge-ref); stroke-dasharray: 3,3; }
  /* Vinheta sutil atrás do grafo — puramente decorativa, custa zero em JS/perf
     porque é só um gradiente de fundo do body, não redesenha por nó. */
  #graph { background: radial-gradient(ellipse at center, color-mix(in srgb, var(--bg) 92%, white) 0%, var(--bg) 72%); }
  circle.node-glow { filter: var(--node-glow); }
  .dim { opacity: .08; }
  circle { transition: opacity .25s ease, filter .2s ease, stroke-width .15s ease; }
  circle:hover { stroke-width: 2px; }
  /* Escala no hover só quando parado (sem `.dragging`) — durante o arrasto
     o d3.drag já reposiciona `cx`/`cy` a cada frame; empilhar uma transform
     de escala por cima brigaria com isso e o nó "tremeria" ao ser puxado. */
  g.node:not(.dragging) circle:hover { transform: scale(1.12); transform-box: fill-box; transform-origin: center; }
  .link { transition: opacity .25s ease; }
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
    background: #1b1e21; color: var(--ink); font-size: 12px; font-family: inherit; margin-bottom: 8px; }
  #idx-search:focus { outline: none; border-color: var(--instrument-blue); }

  /* `<details>` nativo — some sozinho a lógica de abrir/fechar, sem estado
     em JS. Fecha por padrão no celular (o JS decide o atributo `open` na
     hora de montar o HTML, olhando o mesmo sinal de "tela pequena" que o
     resto do layout responsivo usa) e some com o filtro fino até o usuário
     pedir por ele — é o que sobra pra lista de verdade quando a tela é
     estreita. No desktop, tudo continua visível por padrão, como antes. */
  .idx-more { margin-bottom: 10px; }
  .idx-more summary { cursor: pointer; font-size: 11px; color: var(--ink-dim); padding: 4px 0;
    list-style: none; user-select: none; }
  .idx-more summary::-webkit-details-marker { display: none; }
  .idx-more summary::before { content: "▸ "; }
  .idx-more[open] summary::before { content: "▾ "; }
  .idx-more summary:hover { color: var(--ink); }
  .idx-more[open] summary { margin-bottom: 6px; }

  .idx-filters { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin-bottom: 10px; }
  .idx-range { display: flex; align-items: center; gap: 5px; font-size: 11px; color: var(--ink-dim); }
  .idx-range input[type="number"] { width: 52px; padding: 6px 6px; border-radius: 6px; border: 1px solid var(--panel-border);
    background: #1b1e21; color: var(--ink); font-size: 12px; font-family: inherit; }
  #idx-maturidade { padding: 6px 8px; border-radius: 6px; border: 1px solid var(--panel-border);
    background: #1b1e21; color: var(--ink); font-size: 11px; font-family: inherit; cursor: pointer; }
  .idx-clear { margin-top: 0; padding: 6px 10px; font-size: 11px; }

  .idx-tags { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 4px; }
  .idx-chip { font-size: 10px; padding: 3px 9px; border-radius: 999px; cursor: pointer; font-family: inherit;
    border: 1px solid var(--panel-border); background: transparent; color: var(--ink-dim); }
  .idx-chip:hover { color: var(--ink); border-color: var(--ink-dim); }
  .idx-chip.on { background: rgba(79,168,255,.18); border-color: var(--instrument-blue); color: var(--instrument-blue); }
  .idx-tagcell { display: flex; flex-wrap: wrap; gap: 3px; }
  .idx-empty { font-size: 12px; color: var(--ink-dim); padding: 18px 4px; }
  .idx-count { font-size: 11px; color: var(--ink-dim); margin-bottom: 6px; }
  #modal mark { background: rgba(79,168,255,.35); color: var(--ink); border-radius: 2px; padding: 0 1px; }
  /* Setinha de direção no cabeçalho ordenado — sinal visual rápido de qual
     coluna manda e em que sentido, sem precisar clicar de novo pra saber. */
  #modal th.sorted.asc::after { content: " ▲"; font-size: 9px; }
  #modal th.sorted.desc::after { content: " ▼"; font-size: 9px; }

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
    #search, #idx-search, .idx-range input, #idx-maturidade { font-size: 16px; padding: 10px 12px; }
    .idx-filters { flex-direction: column; align-items: stretch; }
    .idx-range { justify-content: space-between; }
    .idx-range input[type="number"] { flex: 1; width: auto; }
    .idx-clear { width: 100%; }
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
    /* Linha única, rolando na horizontal — bem mais compacto na vertical do
       que deixar as tags quebrarem linha e empilharem. Isto já mora dentro
       do <details> fechado por padrão, então some da vista até o usuário
       pedir "Mais filtros" mesmo. */
    .idx-tags { flex-wrap: nowrap; overflow-x: auto; max-height: none; padding-bottom: 4px; }
    .idx-chip { flex: none; }
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
    #modal td[data-label]:not([data-label="Título"]):not([data-label="Tags"]) { color: var(--ink-dim); font-size: 11px; }
    #modal td[data-label]:not([data-label="Título"]):not([data-label="Tags"])::before { content: attr(data-label) ": "; }
    .node-title { font-size: 12px; }
  }
  .gap-item { font-size: 12px; margin: 4px 0; color: var(--ink-dim); }
  .gap-item b { color: var(--ink); }

  .style-section { margin-bottom: 16px; }
  .style-row { display: flex; align-items: center; justify-content: space-between; gap: 12px;
    font-size: 12px; color: var(--ink-dim); padding: 7px 2px; border-bottom: 1px solid #2b2f33; }
  .style-row span { flex: 1; }
  .style-row input[type="color"] { width: 40px; height: 26px; padding: 0; border: 1px solid var(--panel-border);
    border-radius: 6px; background: none; cursor: pointer; }
  .style-slider input[type="range"] { flex: 1.4; accent-color: var(--instrument-blue); }
  .style-row input[type="checkbox"] { width: 16px; height: 16px; accent-color: var(--instrument-blue); cursor: pointer; }
  .style-actions { display: flex; gap: 8px; margin-top: 4px; }
  .style-actions .btn { margin-top: 0; text-align: center; }
  .style-primary { background: var(--instrument-blue) !important; color: #0b1220 !important; font-weight: 600;
    border-color: var(--instrument-blue) !important; }
  .style-row select { background: var(--panel); color: var(--ink); border: 1px solid var(--panel-border);
    border-radius: 6px; padding: 5px 8px; font-size: 12px; font-family: inherit; cursor: pointer; }
  .style-hint { font-size: 11px; color: var(--ink-dim); margin: -4px 0 10px 0; line-height: 1.4; }
  .theme-row { display: flex; gap: 8px; flex-wrap: wrap; }
  .theme-btn { flex: 1; min-width: 90px; margin-top: 0; }
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
  <button class="btn" id="btn-style">Estilo</button>

  <div id="detail" hidden></div>
</div>

<div id="modal-overlay">
  <div id="modal"><span class="close" id="modal-close">✕ fechar</span><div id="modal-body"></div></div>
</div>

<script>
const data = __DATA_JSON__;

// Toque grosso (dedo, não mouse) OU tela pequena — cobre tablet/celular
// mesmo quando `matchMedia("pointer: coarse")` falha (alguns Android
// antigos). É intencionalmente mais amplo que `telaPequena()` (que só olha
// largura de tela pra decidir layout do painel): aqui a pergunta é "este
// aparelho tem menos fôlego de CPU/GPU pra física e SVG", não "a tela é
// estreita" — as duas coisas costumam andar juntas mas não são a mesma.
function isMobileDevice() {
  const coarse = window.matchMedia && window.matchMedia("(pointer: coarse)").matches;
  const small = Math.min(window.innerWidth, window.innerHeight) < 820;
  return coarse || small;
}
const DEVICE_IS_MOBILE = isMobileDevice();

// ---- Estilo (cores, raio, rótulo) --------------------------------------
// `defaultStyle` vem do Python (GRAPH_STYLE) — é o padrão "de fábrica" da
// wiki. `localStorage` guarda só o que o usuário mudou neste navegador; se
// o Python mudar o padrão depois, quem nunca customizou nada recebe o novo
// padrão automaticamente (não fica preso a uma cópia congelada). No celular,
// por cima do padrão do Python ainda entram os `mobileOverrides` — glow e
// cenário custam mais no Chrome mobile do que no desktop, então o ponto de
// partida já nasce mais leve lá, sem o usuário precisar descobrir isso
// sozinho abrindo o painel de Estilo.
const STYLE_VARS = {
  essay: "--instrument-blue", concept: "--concept", entity: "--entity",
  insights: "--insight", reference: "--reference", edge: "--edge", background: "--bg",
};
const STYLE_KEY = "sb-graph-style-v1";
const FACTORY_STYLE = data.defaultStyle || {
  colors: { essay: "#4fa8ff", concept: "#5fd3c4", entity: "#e8b657", insights: "#b48ce8",
    reference: "#8a8f96", edge: "#454b52", background: "#1b1e21" },
  edgeOpacity: 0.55, radiusBase: 5, radiusScale: 3, labelSize: 10,
  glow: "leve", starfield: true, gradient: true, sizeMode: "degree",
  spacing: 1, performance: "auto",
};
const MOBILE_OVERRIDES = data.defaultStyleMobileOverrides || { glow: "off", starfield: false };
const defaultStyle = DEVICE_IS_MOBILE ? { ...FACTORY_STYLE, ...MOBILE_OVERRIDES } : FACTORY_STYLE;

function loadSavedStyle() {
  try {
    const raw = localStorage.getItem(STYLE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch { return null; }
}

function mergeWithDefaults(saved) {
  return {
    ...defaultStyle,
    ...(saved || {}),
    colors: { ...defaultStyle.colors, ...((saved || {}).colors || {}) },
  };
}

let styleConfig = mergeWithDefaults(loadSavedStyle());

// ---- Nível de desempenho da simulação/renderização ---------------------
// "auto" decide sozinho a partir de aparelho + tamanho do grafo. Os outros
// três (alta/média/baixa) são escolha explícita do usuário, sobrepondo o
// automático. `theta` é o parâmetro de aproximação Barnes-Hut do
// forceManyBody do d3 (quanto maior, mais aproximado e mais rápido, com
// leve perda de precisão no layout); `distanceMax` limita o alcance da
// repulsão entre nós distantes, que em grafos grandes é boa parte do custo
// por tick mesmo com a árvore já aproximando; `collideIterations` é quantas
// vezes o d3 relaxa colisões por tick (mais = menos sobreposição, mais CPU).
const PERFORMANCE_TIERS = {
  alta: { theta: 0.82, distanceMax: Infinity, collideIterations: 2, labelsAlways: true },
  media: { theta: 1.0, distanceMax: 700, collideIterations: 1, labelsAlways: true },
  baixa: { theta: 1.3, distanceMax: 420, collideIterations: 1, labelsAlways: false },
};
function resolvePerformanceTier(cfg) {
  if (cfg.performance && cfg.performance !== "auto") return cfg.performance;
  const n = data.nodes.length;
  if (DEVICE_IS_MOBILE) return n > 200 ? "baixa" : "media";
  if (n > 600) return "baixa";
  if (n > 250) return "media";
  return "alta";
}

function applyStyle(cfg, opts) {
  styleConfig = cfg;
  const root = document.documentElement.style;
  Object.entries(STYLE_VARS).forEach(([key, cssVar]) => {
    if (cfg.colors[key]) root.setProperty(cssVar, cfg.colors[key]);
  });
  root.setProperty("--edge-opacity", cfg.edgeOpacity);
  root.setProperty("--radius-base", cfg.radiusBase);
  root.setProperty("--radius-scale", cfg.radiusScale);
  root.setProperty("--label-size", cfg.labelSize + "px");
  // "alto" usa filter: drop-shadow (bonito, caro — rasteriza cada nó à
  // parte). "leve" usa um halo desenhado como círculo comum, sem filter —
  // visualmente mais simples mas praticamente de graça em qualquer
  // aparelho. "off" desliga os dois.
  root.setProperty("--node-glow", cfg.glow === "alto" ? "drop-shadow(0 0 4px currentColor)" : "none");

  starfieldSel.style("display", cfg.starfield ? null : "none");

  // Sempre reaplica fill/raio/halo — são só atributos em poucas dezenas ou
  // centenas de elementos, baratos mesmo na carga inicial. O que É caro
  // (reiniciar a simulação) fica isolado abaixo, atrás do `silent`.
  nodeSel.attr("r", radiusOf)
    .classed("node-glow", cfg.glow === "alto")
    .style("color", d => typeColorRaw(d))
    .attr("fill", d => cfg.gradient ? `url(#grad-${d.type})` : typeColorRaw(d));
  haloSel
    .attr("r", d => radiusOf(d) * 1.7)
    .attr("fill", d => typeColorRaw(d))
    .style("opacity", cfg.glow === "leve" ? 0.28 : 0);
  labelSel.attr("dy", d => -(2 + radiusOf(d)));

  if (!opts || !opts.silent) {
    applyForces(cfg);
    simulation.alpha(0.3).restart();
  }
}

function typeColorRaw(n) {
  return (styleConfig.colors && styleConfig.colors[n.type]) || "#888";
}

let width = window.innerWidth, height = window.innerHeight;
const svg = d3.select("#graph").attr("viewBox", [0, 0, width, height]);

// Gradiente radial por tipo — usa var() no próprio atributo `style` do
// `<stop>`, então quando applyStyle() muda a cor no :root, o degradê
// acompanha sozinho, sem nenhum JS extra por nó. O centro claro (color-mix
// com branco) e a borda na cor cheia dão o efeito de "esfera com luz",
// mais bonito que um preenchimento chapado, e custa zero por tick — é
// definido uma vez, os nós só referenciam por `url(#grad-tipo)`.
const defs = svg.append("defs");
Object.entries(STYLE_VARS).forEach(([type, cssVar]) => {
  if (type === "background" || type === "edge") return;
  const grad = defs.append("radialGradient")
    .attr("id", `grad-${type}`).attr("cx", "35%").attr("cy", "32%").attr("r", "70%");
  grad.append("stop").attr("offset", "0%")
    .attr("style", `stop-color: color-mix(in srgb, var(${cssVar}) 55%, white)`);
  grad.append("stop").attr("offset", "100%")
    .attr("style", `stop-color: var(${cssVar})`);
});

// Campo de estrelas decorativo, fixo atrás do grafo (fora do <g> que recebe
// pan/zoom, então não se move — é cenário, não conteúdo). Só desenhado uma
// vez no carregamento: são elementos estáticos, sem listener, sem custo por
// frame, então não pesa mesmo em wikis grandes.
const starfieldSel = svg.append("g").attr("class", "starfield").attr("aria-hidden", "true");
const STAR_COUNT = 140;
for (let i = 0; i < STAR_COUNT; i++) {
  starfieldSel.append("circle")
    .attr("cx", Math.random() * width).attr("cy", Math.random() * height)
    .attr("r", Math.random() * 1.1 + 0.2)
    .attr("fill", "#ffffff")
    .attr("opacity", Math.random() * 0.5 + 0.08);
}

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
    updateLabelVisibility(event.transform.k);
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

// Bytes/linhas variam muito mais que grau (um essay grande pode ter 15000
// bytes vs. um insight solto com 200) — por isso os modos "bytes"/"lines"
// normalizam pelo máximo do dataset (0 a 1) antes de aplicar a escala,
// senão o slider "Escala por conexões" precisaria de valores completamente
// diferentes dependendo do modo escolhido. O modo "degree" fica como estava
// (sem normalizar), pra não mudar o visual de quem já usa o padrão.
const maxSizeBytes = Math.max(1, ...data.nodes.map(n => n.sizeBytes || 0));
const maxSizeLines = Math.max(1, ...data.nodes.map(n => n.sizeLines || 0));
const SIZE_NORM_K = 4; // calibrado pra "bytes"/"lines" ocuparem faixa visual parecida com "degree"

const radiusOf = (d) => {
  const base = styleConfig.radiusBase, scale = styleConfig.radiusScale;
  if (styleConfig.sizeMode === "bytes") {
    return base + Math.sqrt((d.sizeBytes || 0) / maxSizeBytes) * scale * SIZE_NORM_K;
  }
  if (styleConfig.sizeMode === "lines") {
    return base + Math.sqrt((d.sizeLines || 0) / maxSizeLines) * scale * SIZE_NORM_K;
  }
  return base + Math.sqrt(d.visibleDegree ?? d.degree) * scale;
};

// Semeia com o layout já calculado no build (ver compute_layout() no
// Python) em vez de deixar o d3 começar de posições aleatórias. Isso é o
// que faz o celular não precisar rodar a simulação inteira do zero — só
// uma passada curta de ajuste fino (colisão) por cima de um layout que já
// está quase certo.
// ...mas semeando COMPRIMIDO em direção ao centro, não na posição final.
// Semear exato deixava a simulação sem nada a resolver: ela rodava, e o
// grafo aparecia congelado, sem movimento nem colisão visível. Começando
// contraído, os nós se abrem até o lugar certo em ~2s, o que devolve a
// animação orgânica sem pagar o custo de descobrir o layout do zero — a
// topologia já está certa, só a escala é que se resolve na tela.
const BLOOM = 0.55;          // 1 = já na posição final (estático)
const JITTER = 18;           // quebra simetria, senão nós coincidentes travam
data.nodes.forEach(n => {
  const bx = n.x0 ?? width / 2;
  const by = n.y0 ?? height / 2;
  n.x = width / 2 + (bx - width / 2) * BLOOM + (Math.random() - 0.5) * JITTER;
  n.y = height / 2 + (by - height / 2) * BLOOM + (Math.random() - 0.5) * JITTER;
});

// Um <g> por nó com UMA transform por tick, em vez de cx/cy no círculo e
// x/y no texto separadamente — metade das escritas de atributo por frame.
// Isso importa mais no celular: o Chrome mobile tem bem menos margem de
// CPU/GPU que desktop pra reescrever atributos SVG a 60fps.
const nodeGroup = container.append("g").selectAll("g.node")
  .data(data.nodes).join("g")
  .attr("class", "node")
  .attr("transform", d => `translate(${d.x},${d.y})`)
  .call(d3.drag()
    .on("start", dragstarted)
    .on("drag", dragged)
    .on("end", dragended));

// Halo do glow "leve" — círculo simples sem filter, desenhado atrás do nó
// principal (ordem de criação = ordem de pintura em SVG). Sempre existe;
// applyStyle() só liga/desliga via opacidade, então trocar de nível de
// glow não recria elementos, só reescreve alguns atributos.
const haloSel = nodeGroup.append("circle").attr("class", "node-halo").style("pointer-events", "none");

const nodeSel = nodeGroup.append("circle")
  .attr("r", radiusOf)
  .attr("fill", d => `url(#grad-${d.type})`)
  .attr("stroke", "#0b1220")
  .attr("stroke-width", 1)
  .style("cursor", "pointer")
  .style("color", d => typeColorRaw(d));

const labelSel = nodeGroup.filter(d => d.type !== "reference").append("text")
  .attr("class", "node-title")
  .attr("dy", d => -(2 + radiusOf(d)))
  .attr("text-anchor", "middle")
  .text(d => d.title);

// Estado do nível de desempenho atual — lido pela visibilidade de rótulos
// no zoom (abaixo) e recalculado toda vez que spacing/performance mudam.
let currentTier = PERFORMANCE_TIERS[resolvePerformanceTier(styleConfig)];
let labelsShown = true;

// Some com os rótulos quando o tier não é "sempre mostrar" e o zoom está
// afastado — em wikis de centenas de nós, texto é uma das coisas mais caras
// de desenhar/remedir no SVG; ilegível de longe mesmo, então não custa nada
// escondê-lo até o usuário aproximar ou selecionar um nó específico.
function updateLabelVisibility(k) {
  const show = currentTier.labelsAlways || k > 1.4;
  if (show !== labelsShown) {
    labelSel.style("display", show ? null : "none");
    labelsShown = show;
  }
}

// Recria link/charge/collide a partir de spacing + tier de desempenho —
// chamada na criação e de novo sempre que o usuário mexe nesses dois
// controles no painel de Estilo.
function applyForces(cfg) {
  currentTier = PERFORMANCE_TIERS[resolvePerformanceTier(cfg)];
  const spacing = cfg.spacing || 1;
  simulation
    .force("link", d3.forceLink(data.edges).id(d => d.id).distance(70 * spacing).strength(0.5))
    .force("charge", d3.forceManyBody().strength(-160 * spacing)
      .theta(currentTier.theta).distanceMax(currentTier.distanceMax))
    .force("collide", d3.forceCollide().radius(d => (7 + radiusOf(d)) * spacing)
      .iterations(currentTier.collideIterations));
  updateLabelVisibility(d3.zoomTransform(svg.node()).k);
}

const simulation = d3.forceSimulation(data.nodes)
  // Padrão do d3 é alpha=1 decaindo a 0.0228 (~300 ticks até parar) —
  // pensado pra layout começando do zero. Como já chegamos quase prontos,
  // um alpha inicial baixo + decaimento mais rápido faz a simulação gastar
  // só uns 40-60 ticks resolvendo sobreposição fina, não o layout inteiro.
  .force("center", d3.forceCenter(width / 2, height / 2))
  // Alpha cheio com decaimento suave: são ~180 ticks (uns 3s) de assentamento
  // VISÍVEL, que é o ponto — com 0.5/0.06 o grafo assentava antes de o olho
  // pegar e parecia estático. O custo continua baixo porque a semente já traz
  // a topologia certa (ver BLOOM acima); o que roda aqui é expansão e
  // colisão, não descoberta de layout.
  .alpha(1)
  .alphaDecay(0.025)
  .velocityDecay(0.35);

applyForces(styleConfig);

simulation.on("tick", () => {
  linkSel
    .attr("x1", d => d.source.x).attr("y1", d => d.source.y)
    .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
  nodeGroup.attr("transform", d => `translate(${d.x},${d.y})`);
});

// Aplica cores/raio/rótulo/halo salvos (ou o padrão vindo do Python) agora
// que nodeSel/haloSel/labelSel/simulation existem — silencioso porque as
// escritas de atributo já bastam pra ficar certo visualmente, sem precisar
// reiniciar a simulação que acabou de nascer quase assentada.
applyStyle(styleConfig, { silent: true });

function dragstarted(event, d) {
  if (!event.active) simulation.alphaTarget(0.3).restart();
  d.fx = d.x; d.fy = d.y;
  d3.select(this).classed("dragging", true);
}
function dragged(event, d) { d.fx = event.x; d.fy = event.y; }
function dragended(event, d) {
  if (!event.active) simulation.alphaTarget(0);
  d.fx = null; d.fy = null;
  d3.select(this).classed("dragging", false);
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
  simulation.force("collide", d3.forceCollide().radius(d => (7 + radiusOf(d)) * (styleConfig.spacing || 1))
    .iterations(currentTier.collideIterations));
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

const MATURIDADE_LABELS = { solta: "Solta", germinando: "Germinando", madura: "Madura", absorvida: "Absorvida" };

function highlightMatch(text, q) {
  const safe = escapeHtml(text);
  if (!q) return safe;
  const i = text.toLowerCase().indexOf(q.toLowerCase());
  if (i === -1) return safe;
  return escapeHtml(text.slice(0, i)) + "<mark>" + escapeHtml(text.slice(i, i + q.length)) + "</mark>" + escapeHtml(text.slice(i + q.length));
}

function renderTypeIndex() {
  const state = {
    type: "essay", tags: new Set(), query: "", col: "degree", dir: -1,
    minDegree: "", maxDegree: "", maturidade: "",
  };

  modalBody.innerHTML = `
    <h2>Índice</h2>
    <div class="idx-tabs"></div>
    <input id="idx-search" type="text" placeholder="Filtrar por título…">
    <details class="idx-more" ${telaPequena() ? "" : "open"}>
      <summary>Mais filtros</summary>
      <div class="idx-filters">
        <div class="idx-range">
          <span>Conexões</span>
          <input id="idx-min-degree" type="number" min="0" placeholder="mín">
          <span>–</span>
          <input id="idx-max-degree" type="number" min="0" placeholder="máx">
        </div>
        <select id="idx-maturidade" hidden></select>
        <button class="btn idx-clear" id="idx-clear">Limpar filtros</button>
      </div>
      <div class="idx-tags"></div>
    </details>
    <div class="idx-count"></div>
    <table id="idx-table">
      <thead><tr>
        <th data-col="title">Título</th><th data-col="tags">Tags</th>
        <th data-col="degree">Conexões</th><th data-col="size">Tamanho</th>
      </tr></thead>
      <tbody></tbody>
    </table>
    <div class="idx-empty" hidden>Nada corresponde a esse filtro.</div>`;

  const tabsEl = modalBody.querySelector(".idx-tabs");
  const tagsEl = modalBody.querySelector(".idx-tags");
  const tbody = modalBody.querySelector("tbody");
  const emptyEl = modalBody.querySelector(".idx-empty");
  const countEl = modalBody.querySelector(".idx-count");
  const maturidadeEl = modalBody.querySelector("#idx-maturidade");

  Object.keys(TYPE_LABELS).forEach(t => {
    const b = document.createElement("button");
    b.className = "idx-tab" + (t === state.type ? " active" : "");
    b.textContent = TYPE_LABELS[t];
    b.addEventListener("click", () => {
      state.type = t;
      state.tags.clear();
      state.maturidade = "";
      tabsEl.querySelectorAll(".idx-tab").forEach(x => x.classList.toggle("active", x === b));
      drawTags();
      drawMaturidadeFilter();
      draw();
    });
    tabsEl.appendChild(b);
  });

  // Filtro de maturidade só faz sentido pra Insights — os outros tipos nem
  // têm o campo. Reaproveita o mesmo <select> em vez de um bloco de HTML
  // condicional separado, pra não duplicar o vocabulário em dois lugares.
  function drawMaturidadeFilter() {
    const show = state.type === "insights";
    maturidadeEl.hidden = !show;
    if (!show) return;
    maturidadeEl.innerHTML = `<option value="">Toda maturidade</option>` +
      Object.entries(MATURIDADE_LABELS).map(([k, label]) =>
        `<option value="${k}">${label}</option>`).join("");
  }

  // As tags oferecidas são só as que existem no tipo em exibição: filtro que
  // não pode dar resultado vazio é filtro que não precisa estar ali.
  function drawTags() {
    const counts = new Map();
    data.nodes.filter(n => n.type === state.type).forEach(n => {
      (n.tags || []).forEach(t => counts.set(t, (counts.get(t) || 0) + 1));
    });
    const ordered = [...counts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
    tagsEl.innerHTML = "";
    ordered.forEach(([tag, count]) => {
      const chip = document.createElement("button");
      chip.className = "idx-chip";
      chip.textContent = `${tag} · ${count}`;
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
    const min = state.minDegree === "" ? -Infinity : Number(state.minDegree);
    const max = state.maxDegree === "" ? Infinity : Number(state.maxDegree);
    // Múltiplas tags selecionadas combinam por E: cada clique estreita o
    // resultado, que é como se procura o cruzamento entre dois assuntos.
    const totalOfType = data.nodes.filter(n => n.type === state.type).length;
    let rows = data.nodes.filter(n =>
      n.type === state.type
      && (!q || n.title.toLowerCase().includes(q))
      && [...state.tags].every(t => (n.tags || []).includes(t))
      && n.degree >= min && n.degree <= max
      && (!state.maturidade || n.maturidade === state.maturidade)
    );

    const sizeOf = (n) => n.sizeLines || 0;
    const value = (n) => state.col === "title" ? n.title.toLowerCase()
      : state.col === "tags" ? (n.tags || []).join(",").toLowerCase()
      : state.col === "size" ? sizeOf(n)
      : n.degree;
    rows.sort((a, b) => {
      const av = value(a), bv = value(b);
      return av < bv ? -state.dir : av > bv ? state.dir : 0;
    });

    tbody.innerHTML = rows.map(n => `<tr data-id="${escapeHtml(n.id)}">
      <td data-label="Título">${highlightMatch(n.title, state.query)}</td>
      <td class="idx-tagcell" data-label="Tags">${(n.tags || []).map(t => `<span>${escapeHtml(t)}</span>`).join("")}</td>
      <td data-label="Conexões">${n.degree}</td>
      <td data-label="Tamanho">${sizeOf(n) ? sizeOf(n) + " linhas" : "—"}</td></tr>`).join("");
    emptyEl.hidden = rows.length > 0;
    countEl.textContent = rows.length === totalOfType
      ? `${rows.length} ${TYPE_LABELS[state.type].toLowerCase()}`
      : `${rows.length} de ${totalOfType} exibidos`;

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
  modalBody.querySelector("#idx-min-degree").addEventListener("input", (e) => { state.minDegree = e.target.value; draw(); });
  modalBody.querySelector("#idx-max-degree").addEventListener("input", (e) => { state.maxDegree = e.target.value; draw(); });
  maturidadeEl.addEventListener("change", (e) => { state.maturidade = e.target.value; draw(); });
  modalBody.querySelector("#idx-clear").addEventListener("click", () => {
    state.tags.clear(); state.query = ""; state.minDegree = ""; state.maxDegree = ""; state.maturidade = "";
    modalBody.querySelector("#idx-search").value = "";
    modalBody.querySelector("#idx-min-degree").value = "";
    modalBody.querySelector("#idx-max-degree").value = "";
    maturidadeEl.value = "";
    tagsEl.querySelectorAll(".idx-chip.on").forEach(c => c.classList.remove("on"));
    draw();
  });
  modalBody.querySelectorAll("th[data-col]").forEach(th => {
    th.addEventListener("click", () => {
      const col = th.getAttribute("data-col");
      state.dir = (state.col === col) ? -state.dir : -1;
      state.col = col;
      modalBody.querySelectorAll("th").forEach(x => { x.classList.remove("sorted", "asc", "desc"); });
      th.classList.add("sorted", state.dir === 1 ? "asc" : "desc");
      draw();
    });
  });

  drawTags();
  drawMaturidadeFilter();
  draw();
}

let styleModalOpen = false;

document.getElementById("btn-index").addEventListener("click", () => {
  styleModalOpen = false;
  renderTypeIndex();
  modalOverlay.classList.add("open");
});

// ---- Painel de Gaps (calculado no Python, embutido nos dados) ----
document.getElementById("btn-gaps").addEventListener("click", () => {
  styleModalOpen = false;
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

// ---- Painel de Estilo (cores, raio, rótulo — ao vivo + salvo por navegador) ----
const STYLE_LABELS = {
  essay: "Essay", concept: "Concept", entity: "Entity", insights: "Insight",
  reference: "Reference", edge: "Arestas",
};

const GRAPH_THEMES = {
  cosmico: { label: "Cósmico", glow: "alto", starfield: true, gradient: true },
  padrao: { label: "Padrão", glow: "leve", starfield: true, gradient: true },
  minimalista: { label: "Minimalista", glow: "off", starfield: false, gradient: false },
};

function renderStylePanel(seed) {
  const draft = JSON.parse(JSON.stringify(seed || styleConfig)); // rascunho — só grava de fato no "Salvar"

  const colorRow = (key) => `
    <label class="style-row">
      <span>${STYLE_LABELS[key]}</span>
      <input type="color" data-color="${key}" value="${draft.colors[key]}">
    </label>`;

  const themeBtn = (key, t) => `<button class="btn theme-btn" data-theme="${key}">${t.label}</button>`;

  modalBody.innerHTML = `
    <h2>Estilo do grafo</h2>
    <div class="style-section">
      <p class="style-hint">Temas ajustam vários controles de uma vez — os itens abaixo continuam ajustáveis um a um depois.</p>
      <div class="theme-row">${Object.entries(GRAPH_THEMES).map(([k, t]) => themeBtn(k, t)).join("")}</div>
    </div>
    <div class="style-section">${Object.keys(STYLE_LABELS).map(colorRow).join("")}</div>
    <div class="style-section">
      <label class="style-row">
        <span>Tamanho da bolinha representa</span>
        <select id="st-size-mode">
          <option value="degree" ${draft.sizeMode === "degree" ? "selected" : ""}>Nº de conexões</option>
          <option value="bytes" ${draft.sizeMode === "bytes" ? "selected" : ""}>Tamanho do essay (bytes)</option>
          <option value="lines" ${draft.sizeMode === "lines" ? "selected" : ""}>Tamanho do essay (linhas)</option>
        </select>
      </label>
      <p class="style-hint">Referências não têm arquivo — nos modos de tamanho de essay elas ficam sempre no raio base.</p>
      <label class="style-row style-slider">
        <span>Raio base da bolinha</span>
        <input type="range" id="st-radius-base" min="2" max="14" step="1" value="${draft.radiusBase}">
      </label>
      <label class="style-row style-slider">
        <span>Escala do tamanho</span>
        <input type="range" id="st-radius-scale" min="0" max="8" step="0.5" value="${draft.radiusScale}">
      </label>
    </div>
    <div class="style-section">
      <label class="style-row style-slider">
        <span>Opacidade das arestas</span>
        <input type="range" id="st-edge-opacity" min="0.1" max="1" step="0.05" value="${draft.edgeOpacity}">
      </label>
      <label class="style-row style-slider">
        <span>Tamanho do rótulo</span>
        <input type="range" id="st-label-size" min="8" max="18" step="1" value="${draft.labelSize}">
      </label>
      <label class="style-row style-slider">
        <span>Espaçamento entre bolinhas</span>
        <input type="range" id="st-spacing" min="0.6" max="2.5" step="0.1" value="${draft.spacing ?? 1}">
      </label>
      <p class="style-hint">Sobe a distância mínima entre nós, a força que os empurra pra longe e o comprimento das arestas — útil quando o grafo fica denso demais pra ler.</p>
    </div>
    <div class="style-section">
      <label class="style-row">
        <span>Nível de desempenho</span>
        <select id="st-performance">
          <option value="auto" ${(draft.performance ?? "auto") === "auto" ? "selected" : ""}>Automático (recomendado)</option>
          <option value="alta" ${draft.performance === "alta" ? "selected" : ""}>Alta</option>
          <option value="media" ${draft.performance === "media" ? "selected" : ""}>Média</option>
          <option value="baixa" ${draft.performance === "baixa" ? "selected" : ""}>Baixa</option>
        </select>
      </label>
      <p class="style-hint">
        Controla a física da simulação e quando os rótulos somem ao afastar o zoom — não mexe em cor/glow.
        No automático, este navegador/grafo está usando: <b>${resolvePerformanceTier(draft)}</b>
        (${data.nodes.length} nós${DEVICE_IS_MOBILE ? ", aparelho móvel" : ""}).
      </p>
    </div>
    <div class="style-section">
      <p class="style-hint">Extras puramente decorativos — desligue os que não quiser, principalmente em wikis grandes ou no celular.</p>
      <label class="style-row">
        <span>Brilho (glow) nos nós</span>
        <select id="st-glow">
          <option value="off" ${draft.glow === "off" ? "selected" : ""}>Desligado</option>
          <option value="leve" ${draft.glow === "leve" ? "selected" : ""}>Leve (leve no processamento)</option>
          <option value="alto" ${draft.glow === "alto" ? "selected" : ""}>Alto (mais bonito, mais pesado)</option>
        </select>
      </label>
      <label class="style-row">
        <span>Gradiente nas bolinhas</span>
        <input type="checkbox" id="st-gradient" ${draft.gradient ? "checked" : ""}>
      </label>
      <label class="style-row">
        <span>Céu estrelado no fundo</span>
        <input type="checkbox" id="st-starfield" ${draft.starfield ? "checked" : ""}>
      </label>
    </div>
    <div class="style-actions">
      <button class="btn" id="st-reset">Restaurar padrão</button>
      <button class="btn style-primary" id="st-save">Salvar</button>
    </div>`;

  const preview = () => applyStyle(draft); // aplica ao vivo no grafo por trás do modal, sem salvar ainda

  modalBody.querySelectorAll(".theme-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      Object.assign(draft, GRAPH_THEMES[btn.getAttribute("data-theme")]);
      preview();
      renderStylePanel(draft); // redesenha os controles pra refletir o tema, sem perder o resto do rascunho
    });
  });
  modalBody.querySelectorAll("input[data-color]").forEach(inp => {
    inp.addEventListener("input", () => { draft.colors[inp.getAttribute("data-color")] = inp.value; preview(); });
  });
  modalBody.querySelector("#st-size-mode").addEventListener("change", (e) => { draft.sizeMode = e.target.value; preview(); });
  modalBody.querySelector("#st-edge-opacity").addEventListener("input", (e) => { draft.edgeOpacity = +e.target.value; preview(); });
  modalBody.querySelector("#st-radius-base").addEventListener("input", (e) => { draft.radiusBase = +e.target.value; preview(); });
  modalBody.querySelector("#st-radius-scale").addEventListener("input", (e) => { draft.radiusScale = +e.target.value; preview(); });
  modalBody.querySelector("#st-label-size").addEventListener("input", (e) => { draft.labelSize = +e.target.value; preview(); });
  modalBody.querySelector("#st-spacing").addEventListener("input", (e) => { draft.spacing = +e.target.value; preview(); });
  modalBody.querySelector("#st-performance").addEventListener("change", (e) => {
    draft.performance = e.target.value;
    preview();
    renderStylePanel(draft); // atualiza o texto "está usando: X" com o novo valor
  });
  modalBody.querySelector("#st-glow").addEventListener("change", (e) => { draft.glow = e.target.value; preview(); });
  modalBody.querySelector("#st-gradient").addEventListener("change", (e) => { draft.gradient = e.target.checked; preview(); });
  modalBody.querySelector("#st-starfield").addEventListener("change", (e) => { draft.starfield = e.target.checked; preview(); });

  modalBody.querySelector("#st-save").addEventListener("click", () => {
    try { localStorage.setItem(STYLE_KEY, JSON.stringify(draft)); } catch {}
    styleModalOpen = false;
    modalOverlay.classList.remove("open");
  });
  modalBody.querySelector("#st-reset").addEventListener("click", () => {
    try { localStorage.removeItem(STYLE_KEY); } catch {}
    applyStyle(JSON.parse(JSON.stringify(defaultStyle)));
    renderStylePanel(); // redesenha o modal já com os controles no padrão
  });
}

document.getElementById("btn-style").addEventListener("click", () => {
  styleModalOpen = true;
  renderStylePanel();
  modalOverlay.classList.add("open");
});

// Fechar o modal de Estilo sem clicar "Salvar" descarta o rascunho e volta
// ao estilo realmente salvo (ou ao padrão, se nada foi salvo ainda) — sem
// isto, um preview ao vivo cancelado ficaria "grudado" no grafo por engano.
// Só se aplica quando era o modal de Estilo: fechar Índice/Gaps não deve
// reiniciar a simulação à toa.
function revertUnsavedStylePreview() {
  if (!styleModalOpen) return;
  applyStyle(mergeWithDefaults(loadSavedStyle()));
}
document.getElementById("modal-close").addEventListener("click", revertUnsavedStylePreview);
modalOverlay.addEventListener("click", (e) => { if (e.target === modalOverlay) revertUnsavedStylePreview(); });

// ---- Endurecimento para iPhone/Safari -----------------------------------
// Safari tem um gesto de pinça PRÓPRIO da página (`gesturestart` etc, não
// padrão, não existe no Chrome/Android) que compete com o pinça-zoom do
// próprio grafo (d3.zoom). `touch-action: none` no CSS já resolve a maior
// parte, mas esses eventos são a rede de segurança para versões de iOS que
// os disparam mesmo assim — sem isto, no iPhone a página inteira "pula" de
// zoom em vez de só o grafo.
["gesturestart", "gesturechange", "gestureend"].forEach(evt => {
  document.addEventListener(evt, (e) => e.preventDefault());
});

// Safari esconde/mostra a barra de endereço sem sempre disparar `resize` na
// `window` — o evento confiável para isso é o do `visualViewport`. Sem ele,
// o grafo pode ficar com o viewBox de um tamanho de tela que já não existe
// mais depois de rolar uma vez no iPhone (sintoma: grafo "cortado" ou
// deslocado, que não acontece no Android porque o Chrome sempre dispara
// `resize` de qualquer forma).
if (window.visualViewport) {
  window.visualViewport.addEventListener("resize", ajustarViewport);
}

</script>
</body>
</html>
"""


def render_html(nodes, edges, tag_gaps):
    data_json = json.dumps(
        {
            "nodes": nodes,
            "edges": edges,
            "tag_gaps": tag_gaps,
            "defaultStyle": GRAPH_STYLE,
            "defaultStyleMobileOverrides": GRAPH_STYLE_MOBILE_OVERRIDES,
        },
        ensure_ascii=False,
    )
    html = HTML_TEMPLATE.replace("__DATA_JSON__", data_json)
    return html


def main():
    nodes, edges, isolated = build_graph()
    tag_gaps = compute_tag_gaps(nodes, edges)

    layout_start = time.perf_counter()
    compute_layout(nodes, edges)
    layout_ms = (time.perf_counter() - layout_start) * 1000

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
    print(f"  layout pré-calculado em {layout_ms:.0f}ms")
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
