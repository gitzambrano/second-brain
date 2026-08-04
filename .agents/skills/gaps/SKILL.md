---
name: gaps
description: >
  Identifica lacunas na wiki nas três camadas — mecânica (wikilink
  quebrado ou mal formatado), léxica (termo citado que nunca virou
  página, página existente citada sem link) e semântica (páginas
  tematicamente próximas que nunca se mencionam) — tratando essays,
  concepts, entities e insights como peers. Aceita corpus inteiro, uma
  pasta, um tema/tag, ou um subconjunto de páginas. Só identifica e
  ranqueia candidatos — nunca cria página, nunca insere link, nunca
  corrige nada; é a metade "olhar" do par gaps/connect, e o primeiro
  passo interno de /connect. Use quando o Usuário disser "verifica
  gaps", "o que falta cobrir", "esse conceito devia ter página?", "os
  essays estão bem conectados entre si?", "tem link quebrado?", ou
  pedir uma auditoria de completude/conexão em vez de já aplicar a
  correção. Não precisa ser chamado à parte quando o Usuário já pediu
  /connect — /connect já invoca isto por baixo dos panos.
allowed-tools: Bash Read Glob Grep
---

# Gaps

**[ambos]** Identifica **lacunas**: o que devia existir e não existe, ou o que já existe e não está conectado. Read-only nas três camadas — mecânica, léxica, semântica. Nunca cria página, nunca insere wikilink, nunca corrige nada; essa é a camada de **identificação**, que `/connect` (a camada de **ação**) consome como primeiro passo.

## Escopo

```
/gaps                    → corpus inteiro
/gaps <slug ou lista>     → só as páginas nomeadas (qualquer mistura dos 4 tipos)
/gaps concepts/           → só uma pasta (concepts/, entities/, insights/, essays/)
/gaps <tema ou tag>        → só páginas com aquela tag em tags_in_use
```

Mesma sintaxe de escopo que `/connect` — os dois precisam aceitar o mesmo argumento pra `/connect` poder repassar o escopo recebido direto pra `/gaps` sem tradução. Se o argumento for ambíguo, pergunte antes de prosseguir.

## As três camadas

1. **Mecânica** — wikilink quebrado (aponta pra nada) ou mal formatado (fora de `[[slug|Título]]`, ou `WIKILINK_DISPLAY_COLON`). Detecção: `check_wiki.py`.
2. **Léxica** — mesmo heurístico (regex sobre nome próprio, negrito, âncora de link externo), nos quatro tipos como peers:
   - *Termo sem página*: conceito/entidade citado repetidamente na prosa de qualquer essay/concept/entity/insight, nunca virou wikilink nem tem página.
   - *Página sem link*: já existe página (qualquer um dos 4 tipos), outra página a cita na prosa, mas não linka.
   Detecção: `check_gaps.py --skip-tags` (o script cobre os quatro tipos como fonte e como alvo; a Parte 3 dele — balanço de tag — foi pra `/organize`, por isso a flag).
3. **Semântica** — páginas tematicamente próximas que nunca se mencionam literalmente, comum entre concept↔concept e entity↔entity (vocabulário diferente pra mesma ideia, onde o heurístico léxico erra mais). Detecção: `qmd query` por página, ou `find_text.py` sem qmd.

## Passo a passo

1. Determine o escopo (corpus inteiro, subconjunto, pasta, tema) a partir do argumento recebido — se ambíguo, pergunte antes de prosseguir. Corpus inteiro em wiki grande: avise a escala antes de começar.
2. **Camada mecânica**: rode `python scripts/check_wiki.py --json` (ou `check_wiki.py <slug> --json` por página, se o escopo for um subconjunto). Filtre `DEAD_WIKILINKS` e achados de formatação fora do padrão (`WIKILINK_DISPLAY_COLON`, sintaxe fora de `[[slug|Título]]`). Não corrija — só liste, sinalizando quando o alvo for um typo óbvio de página existente (candidato a correção de alta confiança).
3. **Camada léxica**: rode `python scripts/check_gaps.py --skip-tags`. O script roda sobre o corpus inteiro; se o escopo pedido for um subconjunto, filtre o output pelas páginas do escopo depois de rodar (o script não aceita escopo parcial como argumento). É heurístico — falso positivo é esperado, não é bug. Parte 1 do output → candidatos a página nova (só `concepts/` ou `entities/`, nunca essay/insight). Parte 2 do output → candidatos a wikilink faltando entre páginas que já existem, nos dois sentidos entre os quatro tipos.
4. **Camada semântica**: para cada página no escopo (ou amostra representativa em corpus grande — avise antes de amostrar), rode `qmd query "<título/tags da página>"` se `qmd status` disponível, senão `find_text.py` com os termos centrais. Procure páginas tematicamente próximas que não se mencionam literalmente. Foque em concept↔concept e entity↔entity primeiro — é onde o heurístico léxico da camada 2 tende a errar mais.
5. Combine as três camadas e classifique por confiança:
   - **Alta**: nome exato da página-alvo já aparece no texto, só falta o wikilink (léxico Parte 2); ou wikilink morto com typo óbvio de alvo existente (mecânico).
   - **Média**: relação temática forte via busca semântica sem menção literal; ou termo léxico Parte 1 acima do threshold, mas sem consenso claro de que merece página própria.
   - **Baixa**: descarte sem listar. Ruído satura mais do que ajuda.
6. **Comunique priorizado, nunca cole o output bruto dos scripts**: agrupe por "link quebrado/mal formatado", "vira página nova", "só falta linkar", "conexão temática sem menção literal", "ruído/descartado" — não uma lista plana na ordem que os scripts imprimiram.
7. Nunca aplique nada. Ao final, ofereça `/connect` para agir sobre os candidatos levantados — **exceto** quando `/gaps` foi chamado de dentro de `/connect` (ver `## Relação com /connect` abaixo), caso em que quem oferece o próximo passo é o `/connect`, não o `/gaps`.

## O que não fazer

Não crie página, não insira wikilink, não corrija link quebrado nem formatação — mesmo um candidato óbvio de alta confiança. `/gaps` só identifica; `/connect` age.

Não rode como parte automática de `/organize` ou `/sweep` — é uma auditoria pesada e específica, chamada sob demanda pelo Usuário ou como passo interno de `/connect`.

Não tente ajustar os thresholds de `check_gaps.py` (`MIN_PAGE_HITS`, `MIN_TOTAL_HITS`) para "pegar tudo" — mais ruído satura mais do que ajuda; se o threshold atual estiver claramente errado pro tamanho atual da wiki, ajuste com o Usuário, não sozinho.

## Relação com /connect

`/connect` sempre invoca `/gaps` como primeiro passo, escopado ao mesmo argumento recebido por `/connect`, e reusa a lista de candidatos das três camadas em vez de gerar a própria. Quando o Usuário chama `/connect` diretamente, não é preciso (nem correto) rodar `/gaps` antes manualmente — seria redundante, `/connect` já inclui.

Quando `/gaps` é chamado direto (fora de `/connect`), ele só identifica e comunica — ofereça `/connect` no fim para quem quiser agir sobre os candidatos.

## Depois

Read-only — nada para logar quando chamado direto. (Se chamado de dentro de `/connect` e algo foi de fato criado/linkado como resultado, o log é responsabilidade de `/connect`, não de `/gaps`.)

## Skills relacionadas

- `/connect` — age sobre a lista que `/gaps` identifica
- `/linkify` — links externos, não `[[wikilink]]`/página
- `/organize`, `/chapter`, `/plan`, `/scout`
