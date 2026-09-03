"""Ocultar um essay leva junto o que só existia por causa dele.

`visibility: hidden` tira o essay de tudo. Se as páginas de apoio que só ele
citava ficassem para trás, o mapa mostraria um concept sem nada que o sustente
— um órfão que denuncia por omissão que existe algo ali. O que outro essay
também alcança tem de permanecer, ou esconder um essay apagaria meia wiki.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from build_graph import prune_hidden  # noqa: E402


def montar():
    ids = [
        "essay:visivel", "essay:oculto",
        "concept:exclusivo", "concept:compartilhado", "reference:0",
        "concept:sem-aresta", "concept:ilha-a", "concept:ilha-b",
    ]
    nodes = {i: {"id": i, "type": i.split(":")[0], "degree": 0} for i in ids}
    edges = [
        {"source": "essay:oculto", "target": "concept:exclusivo"},
        {"source": "essay:oculto", "target": "concept:compartilhado"},
        {"source": "essay:visivel", "target": "concept:compartilhado"},
        # a referência só é alcançada através do concept exclusivo
        {"source": "concept:exclusivo", "target": "reference:0"},
        # componente que nunca teve essay: condição pré-existente
        {"source": "concept:ilha-a", "target": "concept:ilha-b"},
    ]
    return nodes, edges


def test_conexao_exclusiva_do_oculto_some():
    nodes, edges = montar()
    restantes, _ = prune_hidden(nodes, edges, {"essay:oculto"})
    assert "essay:oculto" not in restantes
    assert "concept:exclusivo" not in restantes


def test_cascata_alcanca_a_referencia_pendurada():
    # A referência tinha grau 1 depois da poda do essay; só o critério de
    # ALCANCE até um essay visível a remove. Grau sozinho a deixaria de pé.
    nodes, edges = montar()
    restantes, _ = prune_hidden(nodes, edges, {"essay:oculto"})
    assert "reference:0" not in restantes


def test_conexao_compartilhada_permanece():
    nodes, edges = montar()
    restantes, _ = prune_hidden(nodes, edges, {"essay:oculto"})
    assert "concept:compartilhado" in restantes


def test_condicao_preexistente_nao_e_varrida_junto():
    nodes, edges = montar()
    restantes, _ = prune_hidden(nodes, edges, {"essay:oculto"})
    # Nunca foram sustentados por essay nenhum: são buraco real da wiki, que
    # `isolated` precisa continuar denunciando em vez de esconder.
    assert "concept:sem-aresta" in restantes
    assert "concept:ilha-a" in restantes
    assert "concept:ilha-b" in restantes


def test_arestas_orfas_nao_sobrevivem():
    nodes, edges = montar()
    restantes, arestas = prune_hidden(nodes, edges, {"essay:oculto"})
    for e in arestas:
        assert e["source"] in restantes and e["target"] in restantes


def test_sem_ocultos_nada_muda():
    nodes, edges = montar()
    restantes, arestas = prune_hidden(nodes, edges, set())
    assert len(restantes) == len(nodes)
    assert len(arestas) == len(edges)


def test_grau_reflete_o_grafo_podado():
    nodes, edges = montar()
    restantes, arestas = prune_hidden(nodes, edges, {"essay:oculto"})
    esperado = dict.fromkeys(restantes, 0)
    for e in arestas:
        esperado[e["source"]] += 1
        esperado[e["target"]] += 1
    assert {i: n["degree"] for i, n in restantes.items()} == esperado
