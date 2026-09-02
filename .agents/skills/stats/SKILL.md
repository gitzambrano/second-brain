---
name: stats
description: >
  Dashboard read-only de saúde da wiki: contagem de essays por tag/
  tipo, conceitos/entidades órfãos, sources sem entrada no
  manifesto ou na subpasta errada, sinais de travessão/formatação,
  contagem de handouts, itens do plano por seção, insights por
  maturidade. Pode também gerar o grafo visual de conexões. Use para
  obter um retrato rápido de saúde sem rodar o lint completo.
allowed-tools: Bash Read
---
# Stats

Dashboard **read-only**. Só relata; `/organize` e `/sweep` corrigem.

## Passo a passo

1. Se `qmd` estiver disponível, atualize o índice local. Sem qmd, pule.
2. Rode `python scripts/check_skills.py`. Se houver erro de contrato de skill, reporte; não corrija dentro de `/stats`.
3. Rode:

```bash
python scripts/stats.py
```

4. Resuma os achados relevantes.
5. Salve snapshot somente sob pedido:

```bash
python scripts/stats.py --save
```

6. Se o Usuário quiser visualizar conexões:

```bash
python scripts/build_graph.py
```

## O que o script cobre

- essays: total, tipo e tags;
- sinais rápidos de estrutura/formatação;
- órfãos e páginas sem essay-pai;
- sources, manifesto, subpastas e tags;
- handouts;
- plano por seção/status;
- insights por maturidade: `solta`, `germinando`, `madura`, `absorvida` e qualquer valor inválido que apareça no corpus.

A varredura é agregada e não substitui `check_wiki.py`, `/organize` ou julgamento editorial.

## Diferença para manutenção

| | `/stats` | `/organize` / `/sweep` |
| --- | --- | --- |
| Corrige? | Não | Sim |
| Saída | contagens e sinais | achados acionáveis |
| Uso | retrato rápido | manutenção |

## Skills relacionadas

- `/organize`, `/sweep`
- `/import`, `/digest`, `/absorb`
