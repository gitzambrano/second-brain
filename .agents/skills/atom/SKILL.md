---
name: atom
description: >
  Captura, desenvolve e promove notas atômicas — fragmentos densos de
  uma ideia só, em wiki/synthesis/, que ainda não sabem a que essay
  pertencem. Comandos: add (capturar uma ideia nova), develop
  (adicionar a uma nota atômica existente numa sessão futura), list
  (mostrar notas por maturidade), promote (levar uma nota madura para
  virar essay novo ou capítulo de um essay existente). Use quando o
  Usuário disser "tive uma ideia sobre X mas não é um essay ainda",
  "anota esse insight solto", "essa nota já está madura o bastante
  pra virar essay?", ou trouxer um fragmento de pensamento que não se
  encaixa em nenhum essay hoje.
allowed-tools: Bash Read Write Edit Glob Grep
---

# Atom

Segura o espaço entre "um insight solto" e "um essay completo": a nota atômica. Uma nota atômica trata de **uma ideia só**, densa o bastante para ser útil, mas sem o aparato de um essay (sem `## Sumário`, sem mínimo de 10 links, sem tese sustentada do início ao fim). Existe para não forçar toda ideia nova a nascer como capítulo de algo ou como página de concept — muita ideia boa fica meses "rondando" antes de encontrar seu essay, e sem um lugar pra isso ela se perde entre sessões ou é forçada cedo demais numa estrutura que ainda não cabe nela.

Vive em `wiki/synthesis/`, ao lado das comparações curtas que `/query` gera — mas com `tipo: nota-atomica` no frontmatter para não confundir os dois (ver `## Formato de páginas em wiki/synthesis/` em `conventions/SKILL.md`).

## Maturidade — vocabulário fechado

Toda nota atômica carrega `maturidade:` no frontmatter, um de três estados:

1. **`solta`** — acabou de ser capturada. Pode ser uma frase, uma pergunta, uma intuição ainda não articulada por inteiro. Pode não ter nenhum link ainda.
2. **`germinando`** — já foi revisitada ao menos uma vez (via `/atom develop`), ganhou corpo, e está ligada a pelo menos um essay/concept/entity/outra nota via `## Conexões`. Ainda não é densa o bastante pra virar essay sozinha, mas está a caminho.
3. **`madura`** — densa, bem conectada, com uma tese ou insight central articulado com clareza. Pronta para `/atom promote`. `/stats` sinaliza toda nota `madura` como candidata a promoção, mas a promoção em si nunca é automática.

Não pule estados retroativamente sem justificativa (uma nota não vira `madura` só porque cresceu em tamanho — precisa ter uma ideia central clara, não um parágrafo grande e difuso).

## `/atom add`

1. Capture a ideia como o Usuário a trouxe, sem inflar artificialmente. Uma nota atômica de 3 linhas é normal e não é um problema a corrigir.
2. Busque na wiki (`wiki/index.md`, `wiki/concepts/`, `wiki/entities/`, e outras notas em `wiki/synthesis/`) por algo relacionado — se a ideia já ecoa um essay ou concept existente, linke desde o início em `## Conexões`.
3. Título curto, arquivo `wiki/synthesis/<slug>.md`:

   ```markdown
   ---
   tags: [tag1]
   sources: []
   created: YYYY-MM-DD
   updated: YYYY-MM-DD
   tipo: nota-atomica
   maturidade: solta
   ---

   # Título Da Ideia

   Um ou dois parágrafos curtos, prosa corrida, a ideia central sem enchimento.

   ## Conexões
   - [[Essay ou Concept Relacionado]]
   ```

   `## Conexões` pode ficar vazia (`- (nenhuma ainda)`) se a ideia é genuinamente nova e solta — não force um link fraco só para preencher.
4. Não gera entrada em `wiki/log.md` — captura de nota atômica é leve demais para o log cronológico, ao contrário de `/essay`/`/import`/`/digest`.

## `/atom develop <nota>`

Retoma uma nota atômica existente numa sessão futura, quando o Usuário quer desenvolvê-la mais.

1. Leia a nota inteira, e leia também o que ela já linka em `## Conexões` para ter o contexto que ela já acumulou.
2. Incorpore o novo conteúdo à prosa existente — não apenas anexe um parágrafo solto ao final sem integrar.
3. Reavalie `## Conexões`: a nota provavelmente ganhou relação com algo novo.
4. Reavalie `maturidade:` — se a nota tinha `solta` e agora tem corpo e pelo menos um link, suba para `germinando`; se já está densa e com tese clara, `madura`. Não suba maturidade automaticamente sem que o conteúdo de fato sustente o novo estado — se tiver dúvida, pergunte ao Usuário como ele avalia.
5. Atualize `updated:` no frontmatter.

## `/atom list`

Leia todas as notas em `wiki/synthesis/` com `tipo: nota-atomica` e mostre agrupadas por maturidade — destaque as `madura` primeiro, como candidatas a promoção. Read-only.

## `/atom promote <nota>`

Leva uma nota `madura` para o conteúdo de fato da wiki. Nunca promove uma nota `solta` ou `germinando` sem antes perguntar se o Usuário tem certeza — a maturidade existe pra evitar promoção prematura.

1. Pergunte (se não estiver óbvio pela nota) se ela vira:
   - **Essay novo**: quando a ideia sustenta um argumento inteiro por si só. Rode o fluxo completo de `/essay` — a nota atômica serve de ponto de partida (a tese já pode estar praticamente pronta), não de rascunho a copiar sem desenvolver.
   - **Capítulo/seção de um essay existente**: quando a ideia se encaixa como parte de um argumento maior já em andamento. Rode `/expand` (se cabe dentro de uma seção) ou `/chapter` (se merece seção própria).
2. Depois que o essay/capítulo existe, **não delete a nota atômica** — atualize seu frontmatter: `maturidade: absorvida`, e adicione uma linha no corpo indicando o destino: `> Absorvida em [[Essay Resultante]] em YYYY-MM-DD.` Isso preserva a genealogia da ideia, do mesmo jeito que `wiki/sources/manifest.md` preserva proveniência de fontes.
3. Log: `## [YYYY-MM-DD] atom-promote | Título da nota → [[Essay Resultante]]`

## O que não fazer

Não crie uma nota atômica para algo que já é claramente um essay completo na cabeça do Usuário — isso é `/essay` direto, a nota atômica existiria só como um passo morto no meio. Não crie uma nota atômica para uma comparação/síntese que `/query` já cobre (isso é `tipo: comparacao`, não `nota-atomica`). Não deixe notas `solta` acumularem por muito tempo sem nunca virarem `germinando` — se `/stats`/`/organize` sinalizarem várias soltas antigas, isso é sinal de que vale uma sessão de `/atom develop` em lote, ou de que algumas devem ser arquivadas por não terem vingado (pergunte ao Usuário, não decida sozinho).

## Skills relacionadas

- `/query` — quando o resultado é uma comparação/síntese entre coisas já existentes na wiki, não uma ideia nova (`tipo: comparacao`, não `nota-atomica`)
- `/essay`, `/expand`, `/chapter` — para onde uma nota `madura` é promovida
- `/stats` — sinaliza notas `madura` como candidatas a promoção, e notas `solta` antigas
- `/organize` — audita notas órfãs (sem nenhuma `## Conexões` preenchida há muito tempo) como parte da saúde geral da base
- `/study` — origem mais comum de notas atômicas: um insight que emergiu de uma sessão de estudo, sem tese completa ainda
- `/absorb`, `/digest` — outra origem comum: uma ideia tangencial que uma fonte revelou, mas que não cabe no essay/resumo em edição
- `/plan` — se a nota revelar que vale a pena estudar mais antes de promover, isso vira um item na seção Estudos do plano, não trava a nota em `/atom`
