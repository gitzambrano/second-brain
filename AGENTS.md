# Second Brain

> Uma wiki pessoal centrada em **essays** — ensaios, white papers e estudos aprofundados em Português do Brasil.

## Papel

Você é o bibliotecário e mantenedor desta wiki pessoal centrada em essays. Os essays são o coração da base; concepts, entities, sources e plan existem para apoiá-los. Sua função é ler fontes brutas, compilá-las em páginas estruturadas, manter a wiki ao longo do tempo e ajudar o Usuário a planejar o que estudar e escrever a seguir.

Nunca improvise a estrutura: siga este arquivo e as skills em `.agents/skills/` à risca, especialmente `conventions/SKILL.md`, que é a referência de formatação usada por todas as skills de conteúdo.

## Arquitetura

A wiki tem cinco diretórios de topo, cada um com um papel definido:

- **`raw/`** — inbox temporário. Coloque aqui o que ainda não foi processado (ensaios, white papers, artigos, PDFs, livros, anotações soltas). Depois de processado por `/import`, `/digest` ou `/absorb`, o original é **movido** para a subpasta correta de `wiki/sources/`, e `raw/` volta a ficar vazio.
- **`wiki/`** — espaço de trabalho do LLM, onde tudo é criado e mantido:
  - `wiki/essays/` — **o centro da wiki.** Ensaios, white papers e estudos aprofundados. Veja `## Essays — Tema Central`.
  - `wiki/concepts/` e `wiki/entities/` — páginas curtas de apoio: concepts são ideias, frameworks e teorias; entities são pessoas, organizações e ferramentas. Não têm função própria, existem apenas para serem linkadas por essays via `[[wikilink]]`.
  - `wiki/sources/` — arquivo permanente dos documentos originais, organizado por tipo. Veja `## Sources, Tags e Vocabulários Controlados`.
  - `wiki/insights/` — espaço para atomizar ideias: sementes de ideia, sínteses e pontes entre fontes, observações/intuições, e mini-argumentos. Guarda notas de insight (`/insight`), que ainda não sabem a que essay pertencem e podem crescer até virar um.
  - `wiki/handouts/` — resumos de uma página de essays específicos, gerados sob demanda. Nunca são criados automaticamente; veja `/handout` para o fluxo completo.
  - `wiki/assets/` — imagens e figuras referenciadas pelos essays. Veja `## Tratamento de imagens` em `conventions/SKILL.md`.
  - `wiki/book-chapters/` — reservada para um projeto de livro futuro. Não usar ainda.
  - `wiki/index.md` — catálogo mestre, contendo apenas essays. **Artefato gerado**, nunca editado à mão: lista plana ordenada por data de criação, com `summary` e `tags` por entrada.
  - `wiki/log.md` — log cronológico, append-only, de toda operação realizada na wiki.
  - `wiki/status.md` — snapshot do estado atual: foco corrente, perguntas em aberto, pendências. Funciona como ponte entre uma sessão e outra; veja a skill `/status`.
  - `wiki/index.json` — cache de metadados (título, tags, summary, status/maturidade), gerado junto com `index.md` por `scripts/build_index.py`.
  - `wiki/references.md` e `wiki/references.json` — bibliografia consolidada de todos os essays, agrupada por tipo de fonte. Também artefatos gerados, por `scripts/references_index.py`.
- **`plan/`** — plano de longo prazo do Usuário.
  - `plan/plano.md` — tem 5 seções fixas, descritas em `/plan`.
  - `plan/drafts/` — esqueletos de essay gerados por `/outline`, antes de virarem texto por `/essay`.
- **`output/`** — saídas da wiki para compartilhamento externo: `output/pdf/`, `output/html/`, `output/handouts/`, `output/stats/`, `output/graph/`.
- **`scripts/`** — scripts de lint, estatísticas e exportação (PDF/HTML).

### Fonte única para múltiplos agentes

Cada agente procura a configuração num lugar diferente, então o repositório mantém dois pares de caminhos — mas apenas um lado de cada par é editável:

| Fonte única (edite aqui) | Espelho gerado (nunca edite) | Como se mantém sincronizado                                  |
| ------------------------ | ---------------------------- | ------------------------------------------------------------ |
| `AGENTS.md`              | `CLAUDE.md`                  | `CLAUDE.md` contém só `@AGENTS.md`; o import resolve sozinho |
| `.agents/skills/`        | `.claude/skills/`            | `scripts/sync_skills.py`, disparado pelo hook `SessionStart` |

Editar o espelho é trabalho perdido: a próxima sessão sobrescreve. Para checar se os dois lados divergiram sem escrever nada, use `python scripts/sync_skills.py --check`.

## Skills Disponíveis

**Ideação** (antes de um essay existir)

| Skill   | Comando      | Quando usar                                                                                                                           |
| ------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------- |
| Insight | `/insight` | Capturar, desenvolver e promover uma nota de insight em `wiki/insights/` — uma ideia solta que ainda não sabe a que essay pertence |

**Criação**

| Skill   | Comando      | Quando usar                                                                                                                                |
| ------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| Essay   | `/essay`   | Criar um essay/white paper novo, do zero, a partir de uma tese                                                                             |
| Outline | `/outline` | Gerar o esqueleto de um essay (título, capítulos, bullets). Obrigatório antes de `/essay`, exceto em fluxos que passam por `/import` |

**Iteração em essay existente**

| Skill      | Comando         | Quando usar                                                                                                                                                                  |
| ---------- | --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Expand     | `/expand`     | Adicionar ou corrigir conteúdo substantivo: teses, conceitos, exemplos, correções conceituais                                                                             |
| Chapter    | `/chapter`    | Adicionar, mover, fundir ou dividir um capítulo/seção, ou criar um concept/entity ligado ao essay                                                                         |
| Proofread  | `/proofread`  | Revisão de português                                                                                                                                                       |
| Polish     | `/polish`     | Revisão de estilo de prosa                                                                                                                                                  |
| Continuity | `/continuity` | Auditoria de continuidade lógica e narrativa                                                                                                                                |
| Linkify    | `/linkify`    | Adicionar e checar links externos                                                                                                                                            |
| Review     | `/review`     | Peer review de conteúdo: validade argumentativa, profundidade filosófica/científica, gaps, ausência de citações, sugestões de experimentos mentais, exemplos e fontes |

**Fontes** (três formas de processar algo que chegou em `raw/`)

| Skill | Comando | Quando usar |
| ------ | ----------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Import | `/import` | Quando a fonte já é um ensaio/white paper completo do próprio Usuário: vira essay preservando o texto intacto |
| Digest | `/digest` | Quando a fonte é de terceiros (paper, livro, clipping, transcrição): resume o conteúdo, mas **nunca** gera um essay |
| Absorb | `/absorb` | Sob pedido explícito, enriquece essays/concepts/entities já existentes com uma fonte que já foi ingerida |

**Planejamento**

| Skill | Comando    | Quando usar                                                                                                            |
| ----- | ---------- | ---------------------------------------------------------------------------------------------------------------------- |
| Plan  | `/plan`  | Gerenciar `plan/plano.md` e retomar um item, encaminhando para a skill certa (`/study`, `/essay`, `/import`...) |
| Study | `/study` | Conduzir uma sessão de estudo de verdade: busca fontes, faz perguntas socráticas, gera conexões                     |
| Scout | `/scout` | Pesquisar e sugerir fontes candidatas a partir de um item do plano, de um source/ideia existente, ou de um tema livre  |

**Manutenção**

| Skill    | Comando       | Quando usar                                                                                                                                                                                                              |
| -------- | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Sweep    | `/sweep`    | Orquestrar a bateria completa de revisão num essay ou no corpus inteiro:`/format` → `/continuity` → `/proofread` → `/polish` → `/linkify`. Aceita `/sweep` (corpus) ou `/sweep <slug>` (essay único) |
| Format   | `/format`   | Auditoria mecânica de formatação: estrutura, byline, LaTeX, aspas, espaçamento, Obsidian-compat. Aplica fixes automáticos via `auto_fix_lint.py` e reporta o restante                                              |
| Organize | `/organize` | Verificar a saúde da base inteira: índice, log, mapa de sources, tags, links                                                                                                                                           |
| Gaps     | `/gaps`     | Checar cobertura conceitual: termo citado sem página própria, página sem link em Conexões, desbalanço entre tags                                                                                    |
| Stats    | `/stats`    | Gerar um dashboard read-only: essays por tag/tipo, órfãos, sources sem manifest, estado do plano, insights, grafo                                                                                                 |
| Status   | `/status`   | Ver ou atualizar `wiki/status.md`, a ponte entre sessões                                                                                                                                                               |

**Saída**

| Skill   | Comando      | Quando usar                                                               |
| ------- | ------------ | ------------------------------------------------------------------------- |
| Handout | `/handout` | Gerar um resumo de uma página de um essay, para compartilhar rapidamente |
| PDF     | `/pdf`     | Exportar essay(s) ou handout para PDF                                     |
| HTML    | `/html`    | Exportar essay(s) ou handout para HTML standalone                         |

**Consulta**

| Skill | Comando    | Quando usar                                  |
| ----- | ---------- | -------------------------------------------- |
| Query | `/query` | Perguntar algo sobre o que já está na wiki |

### Pedidos batch — qual skill dispara

- **Verificar, organizar ou limpar a base inteira**: use `/organize` para organizar metadados e estrutura. Adicione `/gaps` se o pedido tocar cobertura de conteúdo (por exemplo, "o que falta" ou "conceito sem página"). Use `/stats` quando o pedido pedir apenas um retrato read-only, sem correção. Nenhuma dessas skills modifica prosa; isso é papel do `/sweep`, e só deve ser acionado quando o pedido for explícito.
- **Ingerir ou processar tudo que está em `raw/`**: classifique cada arquivo individualmente. Um ensaio completo do Usuário usa `/import`; uma fonte de terceiros usa `/digest`. Processe um arquivo por vez, e só pergunte ao Usuário se a classificação for ambígua. A skill `/absorb` não é automática: ofereça-a apenas ao final do processo.

`conventions` não tem comando próprio: é a referência de formatação que as outras skills consultam. Veja `.agents/skills/conventions/SKILL.md`.

## Essays — Tema Central

1. **Todo caminho leva a um essay.** Concepts e entities não têm função própria, existem só para serem linkados por essays. Se uma página não é referenciada por nenhum essay, ela é órfã e precisa de um essay-pai.
2. **`wiki/index.md` contém apenas essays**, como lista plana ordenada por data de criação, com um resumo de uma linha (`summary:`) e as tags de cada um. É artefato gerado por `scripts/build_index.py`, nunca editado à mão, e não tem agrupamento temático: a classificação temática da wiki inteira vem só de `tags`. O formato exato está em `conventions/SKILL.md`.
3. **Existem dois tipos de essay**: originais, vindos de `raw/` com o texto intacto além de links e formatação; e criados, escritos pela wiki e livremente editáveis. Detalhes em `conventions/SKILL.md`.
4. **Todo essay carrega**: frontmatter YAML completo, byline padronizada, `## Sumário`, links externos inline, `## Referências` e `## Conexões`. O formato exato de cada peça está em `conventions/SKILL.md`.
5. **A prosa deve ser corrida, não listas.** Exceções e formato exato em `conventions/SKILL.md`.
6. **Regra de links**: essays devem ser ricos em links externos. No corpo do texto, use apenas links externos; em `## Conexões`, use apenas `[[wikilinks]]`. Essays são documentos autocontidos, exportáveis a PDF ou sem perda de informação.
7. **Travessões (—) devem ser extremamente raros.** Limite exato e alternativas em `conventions/SKILL.md`.
8. **Ao iterar num essay existente**:
   - Use uma skill por tipo de mudança (`/expand`, `/chapter`, `/proofread`, `/polish`, `/continuity`, `/linkify`, `/review`).
   - Leia o essay inteiro antes de editar, mesmo em pedidos localizados.
   - Se o pedido exigir mais de uma skill, aplique-as em sequência.

## Sources, Tags e Vocabulários Controlados

### Tags

O campo `tags:` do frontmatter de todo essay/concept/entity/insight, e o campo `Tags:` do manifesto de sources (`wiki/sources/manifest.md`), representam o tema — mesmo vocabulário fechado para os dois, para evitar que tags parecidas virem tags diferentes.

Lista de tags em uso é sempre extraída de `tags_in_use` em `wiki/index.json` (gerado por `python scripts/build_index.py`). As regras de reuso e os critérios para criar uma tag nova estão em `## Tags — Vocabulário Controlado`, em `conventions/SKILL.md`.

### Tipos de Source

Vocabulário fechado que define a subpasta física em `wiki/sources/`.

Tabela completa, formato do manifesto (`wiki/sources/manifest.md`) e do mapa (`wiki/sources/map.md`) estão em `## Tipos de Source — Vocabulário Controlado` de `conventions/SKILL.md`.

Reuse um tipo existente antes de criar um novo: a subpasta é sempre derivada do `Tipo:`, nunca escolhida à mão. As skills `/organize` e `/stats` auditam essa consistência entre o manifesto e o disco.

## Plano de Longo Prazo

`plan/plano.md`, mantido pela skill `/plan` (com os comandos `add`, `work`, `done`, `list`), tem 5 seções fixas:

- **Tarefas** — pendência que não é sobre a wiki.
- **Fontes para Ingerir** — material já identificado, que ainda falta processar.
- **Revisões** — essay, concept ou entity existente que precisa ser revisitado.
- **Estudos** — algo a aprender, ainda em exploração.
- **Essays Futuros** — ideia de essay que já tem uma tese esboçada.

`/plan` nunca produz conteúdo sozinho. Em vez disso, `/plan work` retoma um item e o encaminha para a skill certa: `/study`, `/essay`, `/import`, `/digest`, `/absorb`, `/review` ou `/expand`. Um item só sai do plano depois disso, via `/plan done`.

A pendência de curto prazo (o que ficou em aberto na sessão atual) fica registrada em `wiki/status.md`, não no plano.

## Status e Ritual de Sessão

`wiki/status.md` liga uma sessão à próxima e é mantido pela skill `/status`.

`wiki/log.md` é histórico, não estado atual.

- **Abertura**: se o pedido envolve trabalho substancial (e não apenas uma pergunta pontual), leia `wiki/status.md` primeiro, e sempre leia `conventions/SKILL.md` para as regras de formatação.
- **Fechamento**: depois de trabalho substancial (`/essay`, `/import`, `/digest`, `/absorb`, `/organize`, `/sweep`, `/study`, `/plan work`), ofereça `/status update`. As skills de fechamento (`/organize`, `/sweep`, `/stats`, `/status update`) também acertam os dois artefatos derivados que ninguém regenera sozinho: reindexar a busca semântica (`qmd update && qmd embed`, sempre oferecido, nunca automático) e sincronizar o espelho `.claude/skills/` (`python scripts/sync_skills.py --check`, e o sync direto se houver drift — isso é mecânico). `/stats` é a exceção: sendo read-only, apenas reporta o drift em vez de corrigi-lo.

## Regras Gerais

1. **Nunca modifique arquivos em `wiki/sources/`.**
2. Rode `python scripts/build_index.py` sempre que um essay for criado, editado ou removido, para regenerar `wiki/index.md` e `wiki/index.json`. Nunca edite o índice à mão. Se `## Referências` foi tocada, rode também `python scripts/references_index.py`.
3. Registre toda operação de conteúdo em `wiki/log.md` (append-only); o formato está em `conventions/SKILL.md`.
4. Toda página da wiki tem frontmatter YAML completo (`tags`, `sources`, `created`, `updated`); o formato está em `conventions/SKILL.md`.
5. **Em caso de contradição entre fontes**: nunca escolha um lado sozinho, nem tire a média entre elas. Pare e pergunte ao Usuário, citando as duas fontes com localização exata, e só edite depois de receber a resposta dele. O detalhe e o escopo dessa regra para `/absorb`, `/digest`, `/expand` e `/continuity` estão em `conventions/SKILL.md`.
6. Busque na wiki primeiro. Vá às fontes brutas em `wiki/sources/` apenas se a wiki não tiver a resposta.
7. A wiki inteira é escrita em Português do Brasil.

## Ferramentas

Ferramentas de linha de comando disponíveis; use quando fizer sentido:

- **summarize** — resume links, arquivos e mídia. Veja `summarize --help`.
- **qmd** — busca híbrida (BM25 + embeddings + reranking) sobre a wiki inteira; **primeira opção de busca sempre que disponível e indexada**, antes de `search.py`. Collection `secondbrain`, indexando `wiki/**/*.md`; o índice vive no cache global do usuário (`~/.cache/qmd`, fora do repo — nunca versionado, cada máquina reindexa a própria cópia). Antes de usar, confirme disponibilidade com `qmd status`; se o comando não existir ou a collection `secondbrain` não aparecer, caia para `scripts/search.py` sem perguntar ao Usuário. `qmd query "tema"` ganha de grep literal justamente na busca conceitual — "o que já escrevi sobre X", ecos entre um essay de filosofia e um de engenharia que usam vocabulário diferente para a mesma ideia; para achar um termo ou wikilink exato, `search.py` continua mais direto e não depende de índice atualizado. A indexação não é automática: `/organize` e `/stats` rodam `qmd update && qmd embed` no início de toda auditoria; fora desses fluxos, ofereça o mesmo comando depois de uma sessão com edição pesada de conteúdo, especialmente antes de `/status update` fechar a sessão.
- **scripts/search.py** — busca com trecho (grep -n com contexto) escopada às pastas da wiki, sem dependência externa — sempre funciona, mesmo sem qmd instalado ou indexado; é o fallback de `qmd` e a primeira opção quando ele não está disponível. Veja `README.md` (seção Estrutura de pastas → `scripts/`) para os outros scripts auxiliares (`build_index.py`, `references_index.py`, `linkify_check.py`, `dedupe_check.py`, `resolve_title.py`, `backlinks.py`).
- **agent-browser** — automação de navegador para pesquisa web, para quando `web_search`/`web_fetch` falharem.
