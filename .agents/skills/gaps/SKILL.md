---
name: gaps
description: >
  Audita a cobertura conceitual da wiki — não a saúde estrutural (isso é
  /organize) nem os links externos de um essay (isso é /linkify), mas o
  que está faltando na camada de conteúdo: conceitos/entidades citados
  repetidamente na prosa dos essays que nunca viraram página própria em
  concepts/ ou entities/; páginas que já existem mas são citadas num
  essay sem virar [[wikilink]] em Conexões; e áreas temáticas com
  cobertura desproporcionalmente rasa. Use quando o Usuário disser
  "verifica gaps", "o que falta cobrir", "esse conceito devia ter
  página?", "os essays estão bem conectados entre si?", ou pedir uma
  auditoria de completude em vez de uma auditoria de estrutura/link
  quebrado.
allowed-tools: Bash Read Write Edit Glob Grep
---

# Gaps

Audita **cobertura**: o que devia existir na wiki e não existe, ou o que já existe e não está conectado. Três lacunas que nada mais cobre:

1. **Termo sem página**: um conceito/pensador/entidade citado repetidamente na prosa (link externo, negrito, ou nome próprio) em vários essays, claramente relevante, mas nunca promovido a `[[wikilink]]` — porque a convenção do corpo do essay é só link externo (ver `## Regra de links` em `conventions/SKILL.md`), então isso nunca aparece como "wikilink morto" em `lint_all.py`.
2. **Página sem link**: o inverso — já existe `concepts/X.md` ou `entities/X.md`, um essay cita X na prosa, mas não linka em `## Conexões`. Diferente do "órfão" que `/organize` passo 2 já cobre (página sem *nenhum* essay que a referencie); aqui a página tem essay relevante, só falta o link.
3. **Desbalanço temático**: uma categoria em `wiki/index.md` com um essay só, comparado a outras com dez — sinal de área subexplorada, não um bug de formatação.

`/gaps` é **prospectivo e opt-in por candidato** — nunca cria página, nunca insere wikilink sozinho. O trabalho é levantar candidatos ranqueados e devolver a decisão pro Usuário, exatamente como `/organize` faz com órfãos reversos.

## Passo a passo

1. Rode `python scripts/gap_candidates.py`. O script é heurístico (regex sobre nomes próprios capitalizados, texto em negrito, e âncoras de link externo) — trata falso positivo como esperado, não como bug. Não existe extração perfeita de "conceito relevante" sem NLP de verdade; o valor está em levantar candidatos plausíveis pro seu julgamento, não em acertar 100%.
2. **Parte 1 do output (termo sem página)**: para cada candidato acima do threshold, decida com o Usuário:
   - Vira página nova em `concepts/` ou `entities/` → delega para `/chapter` (seção "Criar página de conceito/entidade").
   - Já é coberto o suficiente inline, não merece página própria → descarte, sem ação.
   - É ruído do heurístico (nome comum, falso positivo de capitalização) → descarte, e se for um padrão recorrente, considere adicionar à lista `NOISE_TERMS` do script.
3. **Parte 2 do output (página sem link)**: para cada par (essay, página existente), confirme que a menção no essay de fato se refere à página (não homônimo nem falso positivo) e, se sim, adicione o `[[wikilink]]` em `## Conexões` do essay — mecânico, pode aplicar direto depois de confirmar que não é falso positivo. `python scripts/backlinks.py "Título Da Página"` mostra rápido quem já linka essa página, útil para decidir se o wikilink novo é redundante com algo que já existe por outro caminho.
4. **Parte 3 do output (balanço por categoria)**: não é uma correção — é um sinal para `/plan` ou `/scout`. Se uma categoria estiver muito rasa e o Usuário quiser agir, ofereça `/plan add` (item de tipo Essay futuro) ou `/scout` (buscar fontes candidatas pro tema).
5. Para candidatos ambíguos das Partes 1 e 2 que o Usuário não quer decidir agora, ofereça registrar como item `Revisão` em `plan/plano.md` via `/plan add` — mesmo padrão que `/organize` usa para contradição não resolvida na hora.
6. **Comunique priorizado, nunca cole o output bruto do script**: agrupe por "vira página", "só falta linkar", "ruído/descartado", "desbalanço de categoria" — não uma lista plana na ordem que o script imprimiu.

## O que não fazer

Não crie página nem insira wikilink sem confirmação — mesmo um candidato com frequência alta pode ser um heurístico capturando ruído (nome comum, título de seção, sigla).

Não rode isso como parte automática de `/organize` ou `/sweep` — é uma auditoria pesada e específica, chamada sob demanda.

Não tente ajustar o threshold do script para "pegar tudo" — mais ruído satura o Usuário mais do que ajuda; se o threshold atual (`MIN_ESSAY_HITS`, `MIN_TOTAL_HITS` no topo do script) estiver claramente errado pro tamanho atual da wiki, ajuste com o Usuário, não sozinho.

## Depois

Log só se algo foi de fato criado ou linkado como resultado:
```
## [YYYY-MM-DD] gaps | Resumo do que foi criado/linkado a partir da auditoria
```

## Skills relacionadas

- `/organize` — saúde estrutural/metadados da base inteira; órfão *reverso* (página sem essay) é passo 2 de lá, não daqui
- `/linkify` — links *externos* dentro do corpo de um essay; `/gaps` opera na camada de `[[wikilink]]`/página, não em URL
- `/chapter` — quem de fato cria a página de concept/entity que `/gaps` só propôs
- `/plan` — recebe candidatos que o Usuário quer decidir depois, não agora
- `/scout` — quando o desbalanço de categoria (Parte 3) vira "preciso de mais fonte sobre esse tema"
