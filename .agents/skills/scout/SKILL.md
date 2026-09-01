---
name: scout
description: >
  Pesquisa a web e sugere fontes candidatas a ingerir — a partir de um
  item de plan/plano.md, de uma ideia/source existente ou de um tema
  livre. Nunca ingere sozinho: apenas propõe uma lista curada para o
  Usuário escolher.
allowed-tools: WebSearch WebFetch Read Write Edit Glob
---
# Scout

Encontra candidatos a fonte e devolve uma lista curta e justificada. Não baixa, não move para `raw/` e não ingere sozinho.

Use `/study` quando o objetivo for ler e compreender as fontes; `/scout` é triagem.

## Pontos de partida

1. item de `plan/plano.md`;
2. source/ideia existente;
3. tema livre.

## Passo a passo

1. Extraia 2 a 4 ângulos de busca.
2. Pesquise com `WebSearch`/`WebFetch`. Priorize fontes primárias, documentação oficial, livros e instituições.
3. Confira `wiki/references.md` para sinalizar obra já catalogada.
4. Para cada candidato, informe:
   - título e autor/fonte;
   - link;
   - por que é relevante;
   - tipo provável segundo `## Tipos de Source — Vocabulário Controlado` em `conventions/SKILL.md`.
5. Entregue 3 a 8 candidatos.
6. Se veio do plano, ofereça anexar a shortlist ao item.
7. Não ingira automaticamente. Se o Usuário escolher uma fonte, encaminhe para `/digest`; use `/import` apenas se o material for texto completo do próprio Usuário.

## Regras

- Não reproduza trechos extensos.
- Não invente fonte.
- Não force candidato fraco para completar quantidade.

## Skills relacionadas

- `/plan`, `/study`, `/import`, `/digest`
