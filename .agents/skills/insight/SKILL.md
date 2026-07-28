---
name: insight
description: >
  Captura, desenvolve e promove insights — fragmentos densos de uma
  ideia, síntese, observação ou mini-argumento só, em wiki/insights/,
  que ainda não sabem a que essay pertencem. Comandos: add (registrar
  um insight novo imediatamente, sem precisar de conversa — depois
  oferece, sem insistir, expandir/conectar/polir), develop (retomar
  um insight existente numa sessão futura, conversando e iterando com
  o Usuário para polir ou expandir a nota), list (mostrar insights por
  maturidade), promote (levar um insight maduro para virar essay novo
  ou capítulo de um essay existente). Use quando o Usuário disser
  "tive uma ideia sobre X mas não é um essay ainda", "anota esse
  insight solto", "esse insight já está maduro o bastante para virar
  essay?", ou trouxer uma semente de ideia, uma ponte entre duas
  fontes, uma observação/intuição, ou um mini-argumento que não se
  encaixa em nenhum essay hoje.
allowed-tools: Bash Read Write Edit Glob Grep AskUserQuestion
---
# Insight

Segura o espaço entre "uma ideia solta" e "um essay completo": o insight. Um insight trata de **uma ideia só**, densa o bastante para ser útil, mas sem o aparato de um essay (sem `## Sumário`, sem mínimo de 10 links, sem tese sustentada do início ao fim).

Existe para não forçar toda ideia nova a nascer como capítulo ou como página de concept. Muita ideia boa leva meses até encontrar seu essay; sem um lugar para isso, ela se perde entre sessões ou é forçada cedo demais numa estrutura que ainda não cabe.

Vive em `wiki/insights/` (ver `## Formato de páginas em wiki/insights/` em `conventions/SKILL.md`). Não existe distinção de `tipo:` dentro da pasta — tudo ali é insight.

## O que conta como insight

`wiki/insights/` é a pasta atomizadora de ideias — não só "ideias soltas" no sentido estreito, mas qualquer uma destas quatro formas:

1. **Sementes de ideia** — aquele estalo que surge do nada no banho, numa caminhada ou no meio do dia. Pode ser uma frase só, sem desenvolvimento nenhum ainda.
2. **Sínteses e pontes** — o cruzamento entre duas fontes diferentes (ex: ligar um conceito de teoria de sistemas a um modelo de escrita). Inclui a síntese que uma pergunta ao `/query` pode provocar — não existe mais uma pasta/tipo separado para isso, é insight igual ao resto.
3. **Observações e intuições** — reflexões pessoais sobre padrões que o Usuário começa a notar.
4. **Mini-argumentos** — teses curtas e opiniões já bem fundamentadas, no ponto para compor um essay no futuro.

As quatro entram pelo mesmo fluxo (`/insight add`) e seguem a mesma escala de maturidade — o que muda é só o ponto de partida: uma semente normalmente nasce `solta`, um mini-argumento já pode nascer `germinando` ou até perto de `madura`.

## Maturidade — vocabulário fechado

Todo insight carrega `maturidade:` no frontmatter, um de três estados:

1. **`solta`** — acabou de ser capturada. Pode ser uma frase, uma pergunta, uma intuição ainda não articulada por inteiro. Pode não ter nenhum link ainda.
2. **`germinando`** — já foi revisitada ao menos uma vez (via `/insight develop`), ganhou corpo, e está ligada a pelo menos um essay/concept/entity/outro insight via `## Conexões`. Ainda não é densa o bastante para virar essay sozinha, mas está a caminho.
3. **`madura`** — densa, bem conectada, com uma tese ou insight central articulado com clareza. Pronta para `/insight promote`. `/stats` sinaliza todo insight `madura` como candidato a promoção, mas a promoção em si nunca é automática.

Não pule estados retroativamente sem justificativa (um insight não vira `madura` só porque cresceu em tamanho — precisa ter uma ideia central clara, não um parágrafo grande e difuso).

## `/insight add`

Registre primeiro, converse depois — o Usuário pode só querer soltar a ideia e seguir em frente, sem interagir.

1. Capture a ideia como o Usuário a trouxe e **grave imediatamente**, sem inflar artificialmente e sem exigir uma rodada de conversa antes de salvar. Um insight de 3 linhas é normal e não é um problema a corrigir.
2. Busque na wiki (`python scripts/search.py "termo" --ignore-case`, cobre `wiki/index.md`-relevant essays, `concepts/`, `entities/`, e outros insights em `wiki/insights/` de uma vez) por algo relacionado — se a ideia já ecoa um essay ou concept existente, linke desde o início em `## Conexões`. Isso não deve atrasar o registro: é uma busca rápida, não uma pesquisa aprofundada.
3. Título curto — antes de decidir o nome do arquivo, rode `python scripts/resolve_title.py "Título Da Ideia"` para não nascer um quase-duplicado de algo que já existe com outra grafia.
4. `tags:` reusa o mesmo vocabulário controlado dos essays. Cheque `tags_in_use` em `wiki/index.json` (gerado por `python scripts/build_index.py`; rode-o primeiro se estiver desatualizado) e só crie tag nova se nenhuma existente cobrir o tema.

   Arquivo `wiki/insights/<slug>.md`:

   ```markdown
   ---
   tags: [tag1]
   sources: []
   created: YYYY-MM-DD
   updated: YYYY-MM-DD
   maturidade: solta
   ---

   # Título Da Ideia

   Um ou dois parágrafos curtos, prosa corrida, a ideia central sem enchimento.

   ## Conexões
   - [[Essay ou Concept Relacionado]]
   ```

   `## Conexões` pode ficar vazia (`- (nenhuma ainda)`) se a ideia é genuinamente nova e solta — não force um link fraco só para preencher.
5. Não gera entrada em `wiki/log.md` — captura de insight é leve demais para o log cronológico, ao contrário de `/essay`/`/import`/`/digest`.
6. **Depois** de salvar, ofereça — sem insistir — desenvolver mais: perguntar se quer expandir a ideia, adicionar conexões, ou deixar exatamente como está. Uma frase curta basta ("Registrado. Quer desenvolver mais agora ou fica assim por enquanto?"). Se o Usuário não responder ou disser que só queria registrar, encerre por aí — não force `/insight develop` na mesma mensagem.

## `/insight develop <nota>`

Retoma um insight existente numa sessão futura, quando o Usuário quer desenvolvê-lo mais. Isso é sempre uma conversa, não uma edição silenciosa: o objetivo é polir e expandir a nota iterando com o Usuário, não apenas acrescentar texto por conta própria.

1. Leia a nota inteira, e leia também o que ela já linka em `## Conexões` para ter o contexto que ela já acumulou.
2. Converse com o Usuário sobre a direção — o que mudou desde a última vez, o que ele quer aprofundar, se surgiu alguma conexão nova — antes de reescrever qualquer parágrafo.
3. Incorpore o novo conteúdo à prosa existente — não apenas anexe um parágrafo solto ao final sem integrar.
4. Reavalie `## Conexões`: a nota provavelmente ganhou relação com algo novo.
5. Reavalie `maturidade:` — se a nota tinha `solta` e agora tem corpo e pelo menos um link, suba para `germinando`; se já está densa e com tese clara, `madura`. Não suba maturidade automaticamente sem que o conteúdo de fato sustente o novo estado — se tiver dúvida, pergunte ao Usuário como ele avalia.
6. Atualize `updated:` no frontmatter.

## `/insight list`

Leia todos os insights em `wiki/insights/` e mostre agrupados por maturidade — destaque os `madura` primeiro, como candidatos a promoção. Read-only.

## `/insight promote <nota>`

Leva um insight `madura` para o conteúdo de fato da wiki. Nunca promove um insight `solta` ou `germinando` sem antes perguntar se o Usuário tem certeza — a maturidade existe para evitar promoção prematura.

1. Pergunte (se não estiver óbvio pela nota) se ela vira:
   - **Essay novo**: quando a ideia sustenta um argumento inteiro por si só. Rode o fluxo completo de `/essay` — o insight serve de ponto de partida (a tese já pode estar praticamente pronta), não de rascunho a copiar sem desenvolver.
   - **Capítulo/seção de um essay existente**: quando a ideia se encaixa como parte de um argumento maior já em andamento. Rode `/expand` (se cabe dentro de uma seção) ou `/chapter` (se merece seção própria).
2. Depois que o essay/capítulo existe, **não delete o insight** — atualize seu frontmatter: `maturidade: absorvida`, e adicione uma linha no corpo indicando o destino: `> Absorvida em [[Essay Resultante]] em YYYY-MM-DD.` Isso preserva a genealogia da ideia, do mesmo jeito que `wiki/sources/manifest.md` preserva proveniência de fontes.
3. Log: `## [YYYY-MM-DD] insight-promote | Título da nota → [[Essay Resultante]]`

## O que não fazer

Não crie um insight para algo que já é claramente um essay completo na cabeça do Usuário — isso é `/essay` direto, o insight existiria só como um passo morto no meio.

Não force conversa em `/insight add` — o registro imediato vem primeiro, a oferta de desenvolver vem depois e nunca é obrigatória.

Não deixe insights `solta` acumularem por muito tempo sem nunca virarem `germinando` — se `/stats`/`/organize` sinalizarem vários soltos antigos, isso é sinal de que vale uma sessão de `/insight develop` em lote, ou de que alguns devem ser arquivados por não terem vingado (pergunte ao Usuário, não decida sozinho).

## Skills relacionadas

- `/query` — se a resposta revelar uma ideia nova em vez de só organizar o que já existe na wiki, `/query` pode oferecer capturá-la via `/insight add`
- `/essay`, `/expand`, `/chapter` — para onde um insight `madura` é promovido
- `/stats` — sinaliza insights `madura` como candidatos a promoção, e insights `solta` antigos
- `/organize` — audita insights órfãos (sem nenhuma `## Conexões` preenchida há muito tempo) como parte da saúde geral da base
- `/study` — origem mais comum de insight: uma ideia que emergiu de uma sessão de estudo, sem tese completa ainda
- `/absorb`, `/digest` — outra origem comum: uma ideia tangencial que uma fonte revelou, mas que não cabe no essay/resumo em edição
- `/plan` — se o insight revelar que vale a pena estudar mais antes de promover, isso vira um item na seção Estudos do plano, não trava a nota em `/insight`
