---
name: scout
description: >
  Pesquisa a web e sugere fontes candidatas a ingerir — a partir de um
  item de plan/plano.md, de um source/ideia já existente em
  wiki/sources/ideias/, ou de um tema livre passado direto no prompt.
  Nunca ingere sozinho: apenas propõe uma lista curada para o Usuário
  escolher. Use quando o Usuário disser "acha fontes sobre X", "pesquisa
  material pra esse estudo", ou "o que eu poderia ler sobre isso".
allowed-tools: WebSearch WebFetch Read Write Edit Glob
---

# Scout

Encontra candidatos a fonte e devolve uma lista curta e justificada — nunca baixa, nunca move para `raw/`, nunca ingere sozinho. Quem decide o que vale a pena ler é o Usuário; `/scout` só reduz o trabalho de busca.

**Escopo deliberadamente raso**: `/scout` lista candidatos com uma frase de justificativa cada, não lê o conteúdo inteiro nem produz resumo. Para leitura de verdade — `WebFetch` do conteúdo, resumo parafraseado de verdade, link junto do resumo — isso é `/study`, não `/scout`. Use `/scout` pra triagem ampla ("quais dessas 8 fontes valem meu tempo"); use `/study` quando já se sabe que vale ler e o objetivo é sair com compreensão, não só uma lista.

## Pontos de partida (qualquer um dos três)

1. **Um item de `plan/plano.md`**: "acha fontes pro item X do plano" — leia a Nota e o Tópico do item para orientar a busca. Faz mais sentido para itens das seções Estudos/Essays Futuros/Fontes para Ingerir; para Revisões, prefira reler a fonte original já ligada ao alvo em vez de buscar fonte nova.
2. **Um source ou ideia já existente**: "acha mais material a partir dessa ideia em `wiki/sources/ideias/`" — leia o conteúdo do arquivo e use como ponto de partida temático, não como texto a resumir.
3. **Um tema livre direto no prompt**: "acha fontes sobre X" — sem precisar de plano ou source prévio.

## Passo a passo

1. Identifique o ponto de partida e extraia 2 a 4 ângulos de busca distintos (não uma única query genérica — ver disciplina de busca: termos específicos, buscas separadas por sub-tema).
2. Pesquise (`WebSearch`/`WebFetch`). Priorize fontes primárias: papers com peer review, documentação oficial, livros, sites de instituições — evite agregadores rasos e conteúdo SEO.
3. Para cada candidato, produza:
   - Título e autor/fonte.
   - Link.
   - Uma frase sobre por que essa fonte é relevante para o tema/item específico (não uma descrição genérica do assunto).
   - Tipo provável no vocabulário de `AGENTS.md` (Artigo Acadêmico, Livro, Documentação Técnica, Web Clipping, etc.), para já indicar a subpasta de destino se for ingerida depois.
4. Apresente de 3 a 8 candidatos (não despeje dezenas) — curadoria, não uma lista bruta de resultados de busca.
5. Se o ponto de partida foi um item de `plan/plano.md`, ofereça anexar a lista a esse item, como uma linha `- Fontes candidatas:` sob o item, para não se perder entre sessões.
6. **Nunca baixe nem copie o conteúdo da fonte para `raw/` automaticamente.** Se o Usuário escolher uma, oriente-o a colocar o arquivo/link em `raw/` e rodar `/import` ou `/digest` normalmente — `/scout` termina na sugestão.

## Regras

1. Respeita as mesmas restrições de busca e copyright do resto do sistema — nunca reproduz trechos extensos das fontes encontradas, só descreve.
2. Não inventa fontes: só lista o que a busca de fato retornou.
3. Se a busca não encontrar nada relevante, diga isso claramente em vez de forçar candidatos fracos só para preencher a lista.

## Skills relacionadas

- `/plan` — origem dos itens do plano que `/scout` pode usar como ponto de partida.
- `/study` — sessão de estudo que pode chamar `/scout` no meio, quando uma busca rápida não basta.
- `/import` / `/digest` — o que processa de fato a fonte escolhida, depois que ela chega em `raw/`.
