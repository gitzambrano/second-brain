---
name: stats
description: >
  Mostra métricas agregadas de saúde da wiki sem corrigir conteúdo. Use para um
  retrato rápido de corpus, tags, órfãos, sources, plano e insights; só grava
  snapshot quando o Usuário pedir explicitamente.
metadata:
  second-brain-role: "diagnostic"
  second-brain-mode: "mixed"
  second-brain-scope: "corpus"
  second-brain-approval: "conditional"
  second-brain-closure: "none"
allowed-tools: Bash Read
---
# Stats

Dashboard de diagnóstico. Não corrige a wiki; a única escrita permitida é o snapshot solicitado explicitamente com `--save`.

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
