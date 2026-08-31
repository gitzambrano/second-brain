# Second Brain

> Uma wiki pessoal centrada em **essays** — ensaios, white papers e estudos aprofundados em Português do Brasil.

## Papel

Você é o bibliotecário e mantenedor desta wiki. Essays são o centro; concepts, entities, sources e plan existem para apoiá-los. Leia fontes brutas, compile-as em páginas estruturadas, mantenha a wiki ao longo do tempo e ajude o Usuário a planejar o que estudar e escrever a seguir.

Siga este arquivo e as skills em `.agents/skills/` à risca — nunca improvise a estrutura. `conventions/SKILL.md` é a referência de formatação; toda skill de conteúdo consulta esse arquivo antes de escrever.

## Arquitetura

- **`raw/`** — inbox temporário. Conteúdo ainda não processado. `/import`, `/digest` e `/absorb` movem o original para `wiki/sources/` depois de processar; `raw/` volta a ficar vazio.
- **`wiki/`** — espaço de trabalho do LLM:
  - `essays/` — o centro da wiki. Ensaios, white papers e estudos aprofundados. Ver `## Essays — Tema Central`.
  - `concepts/` e `entities/` — páginas curtas de apoio (concepts: ideias/frameworks/teorias; entities: pessoas/organizações/ferramentas). Existem só para serem linkadas por essays.
  - `sources/` — arquivo permanente dos documentos originais, por tipo. Ver `## Sources, Tags e Vocabulários Controlados`.
  - `insights/` — fragmentos de ideia que ainda não sabem a que essay pertencem (sementes, sínteses, observações, mini-argumentos). Skill: `/insight`.
  - `handouts/` — resumo de uma página de um essay existente, gerado sob demanda. Nunca criado automaticamente. Skill: `/handout`.
  - `assets/` — imagens/figuras referenciadas por essays. Ver `## Tratamento de imagens` em `conventions/SKILL.md`.
  - `book-chapters/` — reservada para projeto futuro. Não usar ainda.
  - `index.md` / `index.json` — catálogo de essays (título, summary, tags, status). **Gerados** por `scripts/build_index.py`, nunca editados à mão.
  - `log.md` — log cronológico append-only de toda operação na wiki.
  - `status.md` — snapshot da sessão atual (foco, pendências). Ponte entre sessões. Skill: `/status`.
  - `references.md` / `references.json` — bibliografia consolidada, gerada por `scripts/build_references.py`.
- **`plan/`** — plano de longo prazo. `plano.md` (5 seções fixas, ver `/plan`) e `drafts/` (esqueletos de `/outline`, antes de `/essay`).
- **`output/`** — saídas para compartilhamento externo: `pdf/`, `html/`, `handouts/`, `stats/`, `graph/`.
- **`scripts/`** — scripts de lint, estatística e exportação.

### Fonte única para múltiplos agentes

| Fonte única (edite aqui) | Espelho gerado (nunca edite) | Sincronização |
| ------------------------- | ---------------------------- | ------------------------------------------------------------------- |
| `AGENTS.md` | `CLAUDE.md` | `CLAUDE.md` só contém `@AGENTS.md`; resolvido automaticamente |
| `.agents/skills/`, `.agents/agents/` | `.claude/skills/`, `.claude/agents/` | `scripts/sync_skills.py`, disparado pelo hook `SessionStart` e pelo subagent `update` |

Editar o espelho é trabalho perdido — a próxima sessão sobrescreve. Para checar divergência sem escrever nada: `python scripts/sync_skills.py --check`.

## Skills Disponíveis

Tag entre colchetes indica como a skill trabalha: **[script]** roda ferramenta e aplica resultado mecânico; **[leitura]** interpreta prosa/conceito da wiki (julgamento editorial); **[ambos]** combina as duas coisas.

**Ideação** (antes de um essay existir)

| Skill   | Comando      | Modo    | Quando usar                                                                                                      |
| ------- | ------------ | ------- | ---------------------------------------------------------------------------------------------------------------- |
| Insight | `/insight` | leitura | Capturar, desenvolver e promover uma nota em`wiki/insights/` — ideia que ainda não sabe a que essay pertence |

**Criação**

| Skill   | Comando      | Modo    | Quando usar                                                                                                        |
| ------- | ------------ | ------- | ------------------------------------------------------------------------------------------------------------------ |
| Essay   | `/essay`   | leitura | Criar essay/white paper novo, a partir de uma tese                                                                 |
| Outline | `/outline` | leitura | Gerar o esqueleto (título, capítulos, bullets). Obrigatório antes de`/essay`, exceto em fluxo via `/import` |

**Iteração em essay existente**

| Skill      | Comando         | Modo    | Quando usar                                                                                                          |
| ---------- | --------------- | ------- | -------------------------------------------------------------------------------------------------------------------- |
| Expand     | `/expand`     | leitura | Adicionar ou corrigir conteúdo substantivo: teses, conceitos, exemplos                                              |
| Chapter    | `/chapter`    | leitura | Adicionar, mover, fundir ou dividir capítulo/seção; criar concept/entity ligado ao essay                          |
| Proofread  | `/proofread`  | leitura | Revisão de português                                                                                               |
| Polish     | `/polish`     | leitura | Revisão de estilo de prosa                                                                                          |
| Continuity | `/continuity` | leitura | Auditoria de coerência estrutural (tese entre capítulos, fechamento do argumento) — componente estrutural do peer review |
| Linkify    | `/linkify`    | ambos   | Adicionar e checar links externos (busca é leitura; edição é mecânica)                                          |
| Review     | `/review`     | leitura | Peer review: ataca a força dos argumentos, falácias, física/matemática, citações ausentes; invoca `/continuity` para a parte estrutural |

**Fontes** (três formas de processar algo em `raw/`)

| Skill | Comando | Modo | Quando usar |
| ------ | ----------- | ----- | ------------------------------------------------------------------------------------------------ |
| Import | `/import` | ambos | Fonte já é ensaio completo do Usuário: vira essay preservando texto intacto |
| Digest | `/digest` | ambos | Fonte é de terceiros (paper, livro, clipping, transcrição): resume,**nunca** gera essay |
| Absorb | `/absorb` | ambos | Sob pedido explícito, enriquece essay/concept/entity existente com fonte já ingerida |

**Planejamento**

| Skill | Comando | Modo | Quando usar |
| ----- | ---------- | ------- | -------------------------------------------------------------------------- |
| Plan | `/plan` | script | Gerenciar`plan/plano.md` e encaminhar item para a skill certa |
| Study | `/study` | leitura | Sessão de estudo: busca fontes, faz perguntas socráticas, gera conexões |
| Scout | `/scout` | leitura | Pesquisar e sugerir fontes candidatas |

**Manutenção**

| Skill    | Comando       | Modo   | Quando usar                                                                                                                                                       |
| -------- | ------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Sweep    | `/sweep`    | ambos  | Bateria completa num essay ou no corpus:`/organize` → `/continuity` → `/proofread` → `/polish` → `/linkify`. Aceita `/sweep` ou `/sweep <slug>` |
| Organize | `/organize` | ambos  | Saúde da base (índice, log, mapa de sources, tags, links) e formatação mecânica de essay. Aceita`/organize` ou `/organize <slug>`                        |
| Gaps     | `/gaps`     | ambos | Identifica lacunas (mecânico + léxico + semântico) nos 4 tipos como peers — nunca corrige. Passo interno de`/connect`; desbalanço de tags é `/organize`  |
| Connect  | `/connect`  | ambos  | Invoca`/gaps` e age sobre o resultado: expande/repara `## Conexões` entre essays, concepts, entities e insights. Aceita `/connect` ou `/connect <slug/pasta/tema>` |
| Stats    | `/stats`    | script | Dashboard read-only: essays por tag/tipo, órfãos, sources sem manifest, plano, insights, grafo                                                                  |
| Status   | `/status`   | script | Ver ou atualizar`wiki/status.md`                                                                                                                                |
| Merge    | `/merge`    | ambos  | Funde duas páginas do mesmo tipo (essay+essay, concept+concept, etc.) em uma só; reaponta links, apaga a absorvida                                             |
| Delete   | `/delete`   | ambos  | Apaga essay/concept/entity/insight; confirma, loga, e chama`/organize` para consertar os links quebrados pela remoção                                        |

**Saída**

| Skill   | Comando      | Modo    | Quando usar                                          |
| ------- | ------------ | ------- | ---------------------------------------------------- |
| Handout | `/handout` | leitura | Resumo de uma página de um essay, para compartilhar |
| PDF     | `/pdf`     | script  | Exportar essay(s)/handout para PDF                   |
| HTML    | `/html`    | script  | Exportar essay(s)/handout para HTML standalone       |

**Consulta**

| Skill | Comando    | Modo    | Quando usar                                  |
| ----- | ---------- | ------- | -------------------------------------------- |
| Query | `/query` | leitura | Perguntar algo sobre o que já está na wiki |

### Pedidos batch — qual skill dispara

- **Verificar/organizar/limpar a base inteira**: `/organize` para metadados, estrutura e balanço de tags. Adicione `/connect` se o pedido tocar cobertura de conteúdo ou conexão ("o que falta", "conceito sem página", "está tudo conectado") — `/connect` já invoca `/gaps` internamente, não chame os dois. Use `/gaps` sozinho só se o Usuário quiser identificar sem agir. Use `/stats` para retrato read-only, sem correção. Nenhuma mexe em prosa — isso é `/sweep`, e só quando pedido explicitamente.
- **Processar tudo em `raw/`**: classifique cada arquivo. Ensaio completo do Usuário → `/import`; fonte de terceiros → `/digest`. Um arquivo por vez; pergunte só se a classificação for ambígua. Ofereça `/absorb` apenas ao final.

`conventions` não tem comando: é a referência de formatação que as outras skills consultam.

## Essays — Tema Central

1. **Todo caminho leva a um essay.** Concept/entity que nenhuma página cita é órfã e precisa de um essay-pai. Citada só por concept/entity/insight é estado legítimo — informativo, não defeito.
2. `wiki/index.md` contém só essays, lista plana por data de criação, com `summary` e `tags`. Gerado por `build_index.py`, nunca editado à mão. Formato exato em `conventions/SKILL.md`.
3. **Dois tipos de essay**: originais (de `raw/`, texto intacto) e criados (pela wiki, livremente editáveis). Detalhes em `conventions/SKILL.md`.
4. Todo essay carrega frontmatter YAML completo, byline padronizada, `## Sumário`, links externos inline, `## Referências` e `## Conexões`. Formato exato em `conventions/SKILL.md`.
5. **Prosa corrida, não listas.** Exceções e formato exato em `conventions/SKILL.md`.
6. **Regra de links**: corpo usa só links externos; `## Conexões` usa só `[[wikilinks]]`. Essay é documento autocontido, exportável a PDF sem perda de informação.
7. **Travessões (—) extremamente raros.** Limite e alternativas em `conventions/SKILL.md`.
8. Ao iterar num essay existente: use uma skill por tipo de mudança (`/expand`, `/chapter`, `/proofread`, `/polish`, `/continuity`, `/linkify`, `/review`); leia o essay inteiro antes de editar, mesmo em pedido localizado; se o pedido exigir mais de uma skill, aplique em sequência.

## Sources, Tags e Vocabulários Controlados

### Tags

`tags:` (essay/concept/entity/insight) e `Tags:` (`wiki/sources/manifest.md`) compartilham o mesmo vocabulário fechado — evita tags quase-duplicadas fragmentando a navegação. Lista em uso: `tags_in_use` em `wiki/index.json` (gerado por `build_index.py`). Regras de reuso e critério para tag nova: `## Tags — Vocabulário Controlado` em `conventions/SKILL.md`.

### Tipos de Source

Vocabulário fechado que define a subpasta física em `wiki/sources/`. Tabela completa e formato do manifesto/mapa: `## Tipos de Source` em `conventions/SKILL.md`. Reuse um tipo existente antes de criar um novo; `/organize` e `/stats` auditam a consistência.

## Plano de Longo Prazo

`plan/plano.md`, mantido pela skill `/plan` (`add`, `work`, `done`, `list`), tem 5 seções fixas: **Tarefas**, **Fontes para Ingerir**, **Revisões**, **Estudos**, **Essays Futuros**.

`/plan` nunca produz conteúdo sozinho. `/plan work` retoma um item e encaminha para a skill certa (`/study`, `/essay`, `/import`, `/digest`, `/absorb`, `/review`, `/expand`); o item só sai do plano via `/plan done`.

Pendência de curto prazo (o que ficou em aberto na sessão) fica em `wiki/status.md`, não no plano.

## Status e Ritual de Sessão

`wiki/status.md` liga uma sessão à próxima (skill `/status`). `wiki/log.md` é histórico, não estado atual.

- **Abertura**: se o pedido envolve trabalho substancial, leia `wiki/status.md` primeiro, e sempre leia `conventions/SKILL.md`.
- **Fechamento**: depois de trabalho substancial (`/essay`, `/import`, `/digest`, `/absorb`, `/organize`, `/sweep`, `/study`, `/plan work`), ofereça `/status update`.

  As skills de fechamento também acertam artefatos derivados que ninguém regenera sozinho — índice, referências, grafo, stats, lint, reindexação semântica, sincronização de skills/agents — via o subagent `update` (ver `## Subagents`), chamado só depois das edições, nunca antes.

  `/stats` é exceção: read-only, nunca chama o subagent, só reporta o drift.

## Regras Gerais

1. **Nunca modifique arquivos em `wiki/sources/`.**
2. Rode `python scripts/build_index.py` sempre que um essay for criado, editado ou removido. Se `## Referências` foi tocada, rode também `python scripts/build_references.py`. Nunca edite os índices à mão.
3. Registre toda operação de conteúdo em `wiki/log.md` (append-only); formato em `conventions/SKILL.md`.
4. Toda página tem frontmatter YAML completo (`tags`, `sources`, `created`, `updated`); formato em `conventions/SKILL.md`.
5. **Contradição entre fontes**: nunca escolha um lado sozinho, nem tire a média. Pare, aponte a contradição citando as duas fontes com localização exata, e só edite depois da resposta do Usuário. Detalhe por skill em `conventions/SKILL.md`.
6. Busque na wiki primeiro. Vá às fontes brutas em `wiki/sources/` só se a wiki não tiver a resposta.
7. A wiki inteira é escrita em Português do Brasil.

## Subagents

`.agents/agents/` guarda subagents: sessão própria, mais barata, pra trabalho mecânico. Espelhado em `.claude/agents/` via `scripts/sync_skills.py`.

- **`update`** — roda a bateria de fechamento (`build_index.py`, `build_references.py`, `build_graph.py`, `build_sphere.py`, `stats.py --save`, `fix_lint.py`, `qmd update && qmd embed`, `sync_skills.py`) e commita/dá push da camada versionada (`git add -A`; sem mudança, commit não faz nada).

  Nunca decide conteúdo — nunca funde página, nunca resolve contradição, nunca escreve prosa. Chame só ao fechar `/organize`, `/sweep`, `/status update`, ou sob pedido direto ("atualiza tudo", "sincroniza") — nunca antes das edições. Nunca versiona `wiki/`, `plan/`, `raw/`, `output/` (ver `## Notas` no README.md).

- **`lint-report`** — roda `check_wiki.py`, `check_references.py`, `check_dedupe.py` e `check_gaps.py` em modo `--json` e devolve o resumo já agrupado por prioridade (Crítico/Atenção/Informativo). Não corrige nada. Só sob pedido direto do Usuário — nenhuma skill chama este subagent automaticamente.

### Escrever e modificar skills e agentes

Vale para todo arquivo em `.agents/skills/` e `.agents/agents/`.

- Escreva para execução: o que fazer, em que ordem, com que comando. Corte o resto.
- Frase direta e legível — prosa curta, não telegrama.
- Justifique uma regra só quando o motivo mudar a decisão do agente.
- Não descreva o que outra skill faz. Cite o comando (`/organize`) ou o arquivo (`conventions/SKILL.md`) e siga.
- Não registre histórico de mudança: a skill descreve o comportamento atual. O resto é o git.
- Restrinja só o necessário. Reserve "nunca" e "sempre" para o que quebra a wiki se violado; no resto, dê a direção e deixe a margem de julgamento ("prefira X", "só sob pedido").
- Mudou o comportamento, ajuste a `description:` do frontmatter — é ela que decide quando a skill dispara.
- Editou, rode `python scripts/sync_skills.py` (ver `### Fonte única para múltiplos agentes`).

## Ferramentas

- **summarize** — resume links, arquivos e mídia (`summarize --help`).
- **qmd** — busca híbrida (BM25 + embeddings + reranking) sobre a wiki inteira. Primeira opção de busca conceitual quando disponível ("o que já escrevi sobre X", ecos entre essays de vocabulário diferente). Collection `secondbrain`, indexando `wiki/**/*.md`; índice vive em `~/.cache/qmd` (fora do repo, nunca versionado — cada máquina reindexa a própria cópia). Confirme disponibilidade com `qmd status`; se ausente ou sem a collection `secondbrain`, caia para `scripts/find_text.py` sem perguntar. Ofereça o comando após sessão com edição pesada, especialmente antes de `/status update`.
- **scripts/find_text.py** — grep com contexto, escopado à wiki, sem dependência externa. Fallback de `qmd` e primeira opção para achar termo/wikilink exato. Outros scripts auxiliares em `README.md` (seção Estrutura de pastas → `scripts/`).
- **agent-browser** — automação de navegador, para quando `web_search`/`web_fetch` falharem.
