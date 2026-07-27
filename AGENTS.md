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
  - `wiki/synthesis/` — espaço para atomizar ideias. Guarda notas atômicas (`/atom`), que ainda não sabem a que essay pertencem e podem crescer até virar um, e comparações curtas (`/query`), que não chegam a virar essay.
  - `wiki/handouts/` — resumos de uma página de essays específicos, gerados sob demanda. Nunca são criados automaticamente; veja `/handout` para o fluxo completo.
  - `wiki/index.md` — catálogo mestre, contendo apenas essays, organizado por categoria temática.
  - `wiki/log.md` — log cronológico, append-only, de toda operação realizada na wiki.
  - `wiki/status.md` — snapshot do estado atual: foco corrente, perguntas em aberto, pendências. Funciona como ponte entre uma sessão e outra; veja a skill `/status`.
- **`plan/`** — plano de longo prazo do Usuário.
  - `plan/plano.md`: tem 5 seções fixas, descritas em`/plan`.
  - `plan/drafts/`: esqueletos de essay gerados por `/outline`, antes de virarem texto por `/essay`.
- **`output/`** — saídas da wiki para compartilhamento externo: `output/pdf/`, `output/html/`, `output/handouts/`, `output/stats/`.
- **`scripts/`** — scripts de lint, estatísticas e exportação (PDF/HTML).

## Skills Disponíveis

**Ideação** (antes de um essay existir)

| Skill | Comando   | Quando usar                                                                                                                          |
| ----- | --------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| Atom  | `/atom` | Capturar, desenvolver e promover uma nota atômica em`wiki/synthesis/` — uma ideia solta que ainda não sabe a que essay pertence |

**Criação**

| Skill   | Comando      | Quando usar                                                                                                                                |
| ------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| Essay   | `/essay`   | Criar um essay/white paper novo, do zero, a partir de uma tese                                                                             |
| Outline | `/outline` | Gerar o esqueleto de um essay (título, capítulos, bullets). Obrigatório antes de`/essay`, exceto em fluxos que passam por `/import` |

**Iteração em essay existente**

| Skill      | Comando         | Quando usar                                                                                          |
| ---------- | --------------- | ---------------------------------------------------------------------------------------------------- |
| Expand     | `/expand`     | Adicionar ou corrigir conteúdo substantivo: teses, conceitos, exemplos, correções conceituais     |
| Chapter    | `/chapter`    | Adicionar, mover, fundir ou dividir um capítulo/seção, ou criar um concept/entity ligado ao essay |
| Proofread  | `/proofread`  | Revisão de português                                                                               |
| Polish     | `/polish`     | Revisão de estilo de prosa                                                                          |
| Continuity | `/continuity` | Auditoria de continuidade lógica e narrativa                                                        |
| Linkify    | `/linkify`    | Adicionar e checar links externos                                                                    |

**Fontes** (três formas de processar algo que chegou em `raw/`)

| Skill | Comando | Quando usar |
| ------ | ----------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Import | `/import` | Quando a fonte já é um ensaio/white paper completo do próprio Usuário: vira essay preservando o texto intacto |
| Digest | `/digest` | Quando a fonte é de terceiros (paper, livro, clipping, transcrição): resume o conteúdo, mas**nunca** gera um essay |
| Absorb | `/absorb` | Sob pedido explícito, enriquece essays/concepts/entities já existentes com uma fonte que já foi ingerida |

**Planejamento**

| Skill | Comando    | Quando usar                                                                                                            |
| ----- | ---------- | ---------------------------------------------------------------------------------------------------------------------- |
| Plan  | `/plan`  | Gerenciar`plan/plano.md` e retomar um item, encaminhando para a skill certa (`/study`, `/essay`, `/import`...) |
| Study | `/study` | Conduzir uma sessão de estudo de verdade: busca fontes, faz perguntas socráticas, gera conexões                     |
| Scout | `/scout` | Pesquisar e sugerir fontes candidatas a partir de um item do plano, de um source/ideia existente, ou de um tema livre  |

**Manutenção**

| Skill    | Comando       | Quando usar                                                                                                                                |
| -------- | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| Sweep    | `/sweep`    | Varrer todos os essays ou aplicar várias correções num mesmo essay, chamando`/proofread`, `/polish`, `/continuity` e `/linkify` |
| Organize | `/organize` | Verificar a saúde da base inteira: índice, log, mapa de sources, tags, links                                                             |
| Gaps     | `/gaps`     | Checar cobertura conceitual: termo citado sem página própria, página sem link em Conexões, desbalanço temático entre categorias      |
| Stats    | `/stats`    | Gerar um dashboard read-only: essays por tag/categoria, órfãos, sources sem manifest, estado do plano, synthesis, grafo                  |
| Status   | `/status`   | Ver ou atualizar`wiki/status.md`, a ponte entre sessões                                                                                 |

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
2. **`wiki/index.md` contém apenas essays**, organizados por categoria temática (Filosofia & Consciência, Engenharia Aeronáutica, Física & Cosmologia, etc.). O formato exato está em `conventions/SKILL.md`.
3. **Existem dois tipos de essay**: originais, vindos de `raw/` com o texto intacto além de links e formatação; e criados, escritos pela wiki e livremente editáveis. Detalhes em `conventions/SKILL.md`.
4. **Todo essay carrega**: frontmatter YAML completo, byline padronizada, `## Sumário`, links externos inline, `## Referências` e `## Conexões`. O formato exato de cada peça está em `conventions/SKILL.md`.
5. **A prosa deve ser corrida, não listas.** Não use bullets, exceto em `## Sumário`, `## Referências` e tabelas. Detalhe completo em `conventions/SKILL.md`.
6. **Regra de links**: essays devem ser ricos em links externos. No corpo do texto, use apenas links externos; em `## Conexões`, use apenas `[[wikilinks]]`. Essays são documentos autocontidos, exportáveis a PDF sem perda de informação.
7. **Travessões (—) devem ser extremamente raros**: no máximo 1 ou 2 no essay inteiro, nunca mais de um por parágrafo. Prefira vírgula, dois-pontos, parênteses, ou reestruture a frase.
8. **Ao iterar num essay existente**:
   - Use uma skill por tipo de mudança (`/expand`, `/chapter`, `/proofread`, `/polish`, `/continuity`, `/linkify`).
   - Leia o essay inteiro antes de editar, mesmo em pedidos localizados.
   - Se o pedido exigir mais de uma skill, aplique-as em sequência.

## Sources, Tags e Vocabulários Controlados

### Tags

O campo `tags:` do frontmatter de todo essay representa o tema do essay, com vocabulário fechado, para evitar que `Filosofia`, `filosofia` e `Filosofia da Mente` virem três tags diferentes.

Lista atual, as regras de reuso e os critérios para criar uma tag nova estão em `## Tags — Vocabulário Controlado`, em `conventions/SKILL.md`.

### Tipos de Source

Vocabulário fechado, que também define a subpasta física em `wiki/sources/`.

| Tipo (manifesto)          | Subpasta                  | O que entra aqui                                                                                                                   |
| ------------------------- | ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Ensaio Completo Importado | `ensaio-importado/`     | Ensaio ou white paper pronto vindo de fora, que virou essay preservando o texto integral                                           |
| Web Clipping              | `web-clipping/`         | Recorte de página web: post, thread, matéria online                                                                              |
| Artigo Acadêmico         | `artigo-academico/`     | Paper com peer review, DOI, ou publicado em periódico/conferência                                                                |
| Livro                     | `livro/`                | Livro ou capítulo, inteiro ou em trecho relevante                                                                                 |
| Documentação Técnica   | `documentacao-tecnica/` | Manuais, specs, normas, documentação de ferramenta ou API                                                                        |
| Transcrição             | `transcricao/`          | Palestra, podcast, entrevista, aula                                                                                                |
| Ideias                    | `ideias/`               | Texto curto e não estruturado: rascunho, nota rápida, trecho de conversa, que ainda não é um ensaio, artigo ou clipping formal |
| Outro                     | `outro/`                | Use apenas quando genuinamente nenhuma categoria acima cobre o caso                                                                |

Reuse um tipo existente antes de criar um novo: a subpasta é sempre derivada do `Tipo:`, nunca escolhida à mão. As skills `/organize` e `/stats` auditam essa consistência entre o manifesto e o disco.

O formato do manifesto (`wiki/sources/manifest.md`) e do mapa (`wiki/sources/map.md`) está descrito em `conventions/SKILL.md`.

## Plano de Longo Prazo

`plan/plano.md`, mantido pela skill `/plan` (com os comandos `add`, `work`, `done`, `list`), tem 5 seções fixas:

- **Tarefas** — pendência que não é sobre a wiki.
- **Fontes para Ingerir** — material já identificado, que ainda falta processar.
- **Revisões** — essay, concept ou entity existente que precisa ser revisitado.
- **Estudos** — algo a aprender, ainda em exploração.
- **Essays Futuros** — ideia de essay que já tem uma tese esboçada.

`/plan` nunca produz conteúdo sozinho. Em vez disso, `/plan work` retoma um item e o encaminha para a skill certa: `/study`, `/essay`, `/import`, `/digest`, `/absorb` ou `/expand`. Um item só sai do plano depois disso, via `/plan done`.

A pendência de curto prazo (o que ficou em aberto na sessão atual) fica registrada em `wiki/status.md`, não no plano.

## Status e Ritual de Sessão

`wiki/status.md` liga uma sessão à próxima e é mantido pela skill `/status`.

`wiki/log.md` é histórico, não estado atual.

- **Abertura**: se o pedido envolve trabalho substancial (e não apenas uma pergunta pontual), leia `wiki/status.md` primeiro, e sempre leia `conventions/SKILL.md` para as regras de formatação.
- **Fechamento**: depois de trabalho substancial (`/essay`, `/import`, `/digest`, `/absorb`, `/organize`, `/study`, `/plan work`), ofereça `/status update`.

## Regras Gerais

1. **`raw/` é um inbox temporário.** Depois de processar um arquivo, mova o original para a subpasta correta de `wiki/sources/` e deixe `raw/` vazio. **Nunca modifique arquivos em `wiki/sources/`.**
2. Atualize `wiki/index.md` sempre que um essay for criado ou removido.
3. Registre toda operação de conteúdo em `wiki/log.md` (append-only); o formato está em `conventions/SKILL.md`.
4. Toda página da wiki tem frontmatter YAML completo (`tags`, `sources`, `created`, `updated`); o formato está em `conventions/SKILL.md`.
5. **Em caso de contradição entre fontes**: nunca escolha um lado sozinho, nem tire a média entre elas. Pare e pergunte ao Usuário, citando as duas fontes com localização exata, e só edite depois de receber a resposta dele. O detalhe e o escopo dessa regra para `/absorb`, `/digest`, `/expand` e `/continuity` estão em `conventions/SKILL.md`.
6. Busque na wiki primeiro. Vá às fontes brutas em `wiki/sources/` apenas se a wiki não tiver a resposta.
7. A wiki inteira é escrita em Português do Brasil.

## Ferramentas

Ferramentas de linha de comando disponíveis; use quando fizer sentido:

- **summarize** — resume links, arquivos e mídia. Veja `summarize --help`.
- **qmd** — motor de busca local para markdown, útil quando a wiki crescer além do que `index.md` consegue navegar bem sozinho. Veja `qmd --help`.
- **agent-browser** — automação de navegador para pesquisa web, para quando `web_search`/`web_fetch` falharem.
