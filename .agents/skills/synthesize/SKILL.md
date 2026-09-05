---
name: synthesize
description: >
  Procura padrões emergentes entre páginas já existentes sem editar nem pesquisar
  a web. Use para convergências, tensões, pontes entre domínios e hipóteses que
  surgem da combinação de múltiplas páginas.
metadata:
  second-brain-role: "knowledge-synthesis"
  second-brain-mode: "read"
  second-brain-scope: "wiki"
  second-brain-approval: "none"
  second-brain-closure: "none"
allowed-tools: Bash Read Glob Grep AskUserQuestion
---
# Synthesize

Procura conhecimento que **emerge da combinação** de páginas existentes.

`/query` responde. `/synthesize` procura padrões que ainda não foram explicitados.

Não pesquisa a web. Quando faltar evidência, encaminhe para `/study` ou `/scout`.

## Fluxo

1. Resolva tema e escopo.
2. Rode 2 a 4 `qmd query` com formulações semanticamente distintas.
3. Se qmd não estiver disponível, use `python scripts/find_text.py`.
4. Leia integralmente as páginas que realmente sustentam a síntese.
5. Procure convergências independentes, tensões, pontes entre domínios, consequências não explicitadas e lacunas reveladas pela combinação.
6. Retorne no máximo 3 a 5 sínteses candidatas.

## Formato

```markdown
### Síntese candidata — Título

**Formulação:** ...

**Base:** [[slug-a|A]], [[slug-b|B]], [[slug-c|C]].

**O que é novo:** ...

**Confiança:** alta | média | exploratória.
```

`alta` exige sustentação clara em múltiplas páginas. `exploratória` é hipótese para estudo, não conclusão.

## Fechamento

Ofereça `/insight add`, `/study`, `/outline` ou não salvar.

Nunca grave nada sem escolha explícita do Usuário.

## Limites

- Read-only.
- Não confunda tema comum com síntese.
- Não escolha lado em contradição.
- Cite as pages usadas.
