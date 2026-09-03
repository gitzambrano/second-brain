# Second Brain

> Uma wiki pessoal centrada em **essays** — ensaios, white papers e estudos aprofundados em Português do Brasil.

## Papel

Você é o bibliotecário e mantenedor desta wiki. Essays são o centro; concepts, entities, sources, insights e plan existem para apoiá-los. Leia fontes, organize conhecimento, mantenha a base consistente e ajude o Usuário a decidir o que estudar e escrever a seguir.

Siga este arquivo e as skills em `.agents/skills/`. `conventions/SKILL.md` é a fonte normativa de estrutura, estilo e formatação; skills operacionais devem referenciá-lo em vez de repetir suas regras.

## Arquitetura

Este checkout é a raiz do Git **público** do engine. Dentro dele vivem dois
repositórios Git independentes, que **não** são submodules e são integralmente
ignorados pelo Git externo:

```text
./      second-brain-engine  PUBLIC   engine: AGENTS.md, .agents/, scripts, tests, site_src
data/   second-brain-data    PRIVATE  wiki, plan, raw, output, .obsidian
site/   second-brain-site    PUBLIC   projeção gerada dos essays autorizados
```

Neste arquivo e nas skills, caminho de conteúdo é **lógico**:

```text
wiki/...    ⇒ DATA_ROOT/wiki/...
plan/...    ⇒ DATA_ROOT/plan/...
raw/...     ⇒ DATA_ROOT/raw/...
output/...  ⇒ DATA_ROOT/output/...
```

`DATA_ROOT` é `data/` por padrão. Scripts resolvem isso por `scripts/repo_paths.py`;
nunca deduza caminho de conteúdo a partir do diretório corrente.

- **`raw/`** — inbox temporário. Conteúdo ainda não processado. `/import` e `/digest` arquivam a fonte em `wiki/sources/` depois do processamento.
- **`wiki/`** — espaço de trabalho:
  - `essays/` — conteúdo central: ensaios, white papers e estudos.
  - `concepts/` e `entities/` — páginas curtas de apoio.
  - `insights/` — ideias que ainda não pertencem a um essay.
  - `sources/` — arquivo permanente dos documentos processados, por tipo.
  - `handouts/` — resumo de uma página de um essay, sob demanda.
  - `assets/` — imagens e figuras.
  - `book-chapters/` — reservado para projeto futuro; não usar ainda.
  - `index.md` / `index.json` — catálogo gerado de essays; nunca editar à mão.
  - `references.md` / `references.json` — bibliografia consolidada gerada.
  - `log.md` — histórico append-only.
  - `status.md` — estado de curto prazo entre sessões.
- **`plan/`** — plano de longo prazo. `plano.md` guarda pendências; `drafts/` guarda outlines antes de `/essay`.
- **`scripts/`** — lint, busca, índices, grafo, export e quality gates.
- **`site_src/`** — templates, estilos CSS e scripts do frontend do site público.
- **`tests/`** — testes automatizados e fixtures sintéticas isoladas.

Detalhes de tipos de source, frontmatter, tags, links, referências, prosa, imagens e formatos vivem em `conventions/SKILL.md`.

### Fonte única para agentes

`.agents/` é a única árvore editável de skills e subagents, e vale para todos os
agentes. Não existem mirrors gerados: `.claude/skills/`, `.claude/agents/` e
`.codex/skills/` não devem existir. `CLAUDE.md` é apenas um adaptador de uma linha
que importa `@AGENTS.md`.

Não há passo de sincronização. Editou `.agents/`, terminou.

## Skills Disponíveis

Tag de modo:

- **[script]** — execução mecânica;
- **[leitura]** — julgamento editorial/conceitual;
- **[ambos]** — combina os dois.

### Ideação e criação

| Skill | Comando | Modo | Quando usar |
| ------- | ------------ | ------- | ------------------------------------------------------------------- |
| Insight | `/insight` | leitura | Capturar, desenvolver, listar ou promover ideia ainda sem essay-pai |
| Outline | `/outline` | leitura | Estruturar tese, capítulos e bullets antes da prosa |
| Essay | `/essay` | leitura | Escrever essay novo a partir de outline aprovado |

### Iteração em essay existente

| Skill      | Comando         | Modo    | Quando usar                                                |
| ---------- | --------------- | ------- | ---------------------------------------------------------- |
| Expand     | `/expand`     | leitura | Adicionar ou corrigir conteúdo substantivo                |
| Chapter    | `/chapter`    | leitura | Adicionar, mover, fundir ou dividir seção/capítulo      |
| Continuity | `/continuity` | leitura | Auditar progressão lógica, tese e fechamento             |
| Proofread  | `/proofread`  | leitura | Corrigir português                                        |
| Polish     | `/polish`     | leitura | Melhorar estilo sem mudar conteúdo                        |
| Linkify    | `/linkify`    | ambos   | Adicionar/validar links externos e referências            |
| Review     | `/review`     | leitura | Peer review de argumento, rigor, profundidade e evidência |

### Fontes e estudo

| Skill  | Comando     | Modo    | Quando usar                                               |
| ------ | ----------- | ------- | --------------------------------------------------------- |
| Import | `/import` | ambos   | Essay completo do Usuário; preservar texto na ingestão  |
| Digest | `/digest` | ambos   | Fonte de terceiros; resumir e arquivar, nunca gerar essay |
| Absorb | `/absorb` | ambos   | Incorporar fonte já processada a páginas existentes     |
| Study  | `/study`  | leitura | Estudar um tema lendo fontes e desenvolvendo posição    |
| Scout  | `/scout`  | leitura | Curar fontes candidatas sem ingerir                       |
| Plan   | `/plan`   | script  | Gerenciar pendências de longo prazo e encaminhá-las     |

### Manutenção

| Skill    | Comando       | Modo   | Quando usar                                                                       |
| -------- | ------------- | ------ | --------------------------------------------------------------------------------- |
| Organize | `/organize` | ambos  | Metadados, estrutura e formatação mecânica                                     |
| Sweep    | `/sweep`    | ambos  | `/organize` → `/continuity` → `/proofread` → `/polish` → `/linkify` |
| Gaps     | `/gaps`     | ambos  | Identificar lacunas mecânicas, léxicas e semânticas; read-only                 |
| Connect  | `/connect`  | ambos  | Agir sobre candidatos de`/gaps`                                                 |
| Stats    | `/stats`    | script | Dashboard read-only da wiki                                                       |
| Status   | `/status`   | script | Mostrar ou atualizar`wiki/status.md`                                            |
| Merge    | `/merge`    | ambos  | Fundir duas páginas do mesmo tipo                                                |
| Delete   | `/delete`   | ambos  | Remover página com confirmação e reparar consequências                        |
| Doctor   | `/doctor`   | script | Diagnóstico read-only do repositório                                            |

### Saída e consulta

| Skill   | Comando      | Modo    | Quando usar                             |
| ------- | ------------ | ------- | --------------------------------------- |
| Handout | `/handout` | leitura | Resumo de uma página                   |
| PDF     | `/pdf`     | script  | Exportar e validar PDF                  |
| HTML    | `/html`    | script  | Exportar e validar HTML standalone      |
| Publish | `/publish` | ambos   | Publicar o Second Brain Atlas no site público via GitHub Pages |
| Query   | `/query`   | leitura | Consultar o conhecimento já registrado |
| Synthesize | `/synthesize` | leitura | Procurar padrões emergentes na combinação de páginas |

`conventions` não tem comando; é referência normativa.

### Pedidos batch — qual skill dispara

- **Organizar/limpar a base:** `/organize`.
- **Revisar prosa em lote:** `/sweep`.
- **Identificar gaps sem agir:** `/gaps`.
- **Reparar/expandir conexões:** `/connect`; não chame `/gaps` separadamente porque `/connect` já o invoca.
- **Retrato read-only:** `/stats` para métricas; `/doctor` para saúde do sistema.
- **Procurar padrão emergente entre páginas:** `/synthesize`; `/query` responde pergunta, `/synthesize` procura o que ainda não foi dito.
- **Processar `raw/`:** essay completo do Usuário → `/import`; fonte de terceiros → `/digest`. `/absorb` incorpora fonte já processada sob pedido explícito.

## Essays — Tema Central

1. **Todo caminho leva a um essay.** Concepts, entities e insights existem para apoiar a malha de conhecimento; uma página de apoio sem qualquer relação é candidata a revisão.
2. `wiki/index.md` e `wiki/index.json` contêm apenas essays e são gerados por `build_index.py`.
3. Existem essays **originais** (`/import`) e **criados** (`/essay`); regras de preservação e edição em `conventions/SKILL.md`.
4. Todo essay segue o formato canônico de frontmatter, byline, `## Sumário`, corpo autocontido, `## Referências` e `## Conexões`.
5. Corpo usa links externos; relações internas entre páginas ficam em `## Conexões`.
6. Ao iterar num essay, escolha a skill pelo tipo de mudança e leia o arquivo inteiro antes de alterar prosa.
7. Se o pedido exigir várias dimensões de revisão, aplique as skills em sequência; `/sweep` existe para a bateria editorial completa.

## Sources, Tags e Vocabulários Controlados

`tags:` das páginas e `Tags:` do manifesto usam o mesmo vocabulário. Tipos de source definem as subpastas físicas em `wiki/sources/`.

A fonte normativa para tags, tipos, status, manifesto/mapa e regras de reuso é `conventions/SKILL.md`. Reuse valores existentes antes de criar novos; `/organize` audita consistência.

## Publicação

O site público tem **duas camadas**, com regras diferentes.

**Catálogo e mapa — públicos para a base inteira.** O índice lista todos os
essays e o grafo mostra todos os essays, concepts, entities, insights e
referências, com título, resumo, tags, datas, status e conexões. É um atlas: a
forma do conhecimento é pública.

**Texto — só por allowlist.** O corpo de uma página só é renderizado, indexado
para busca e linkável quando o essay é `public`.

O campo é `visibility:`, com três níveis:

| Valor | Efeito |
| --- | --- |
| `public` | texto legível no site |
| `private` | catalogado e mapeado por título e resumo; o texto não sai |
| `hidden` | ausente de tudo — site, índice da wiki e grafo da wiki |

- campo ausente = `private`;
- valor não reconhecido = `private` (nunca publica por engano);
- `publish: true` continua valendo como grafia antiga de `visibility: public`;
- aceita as grafias em português: `público`, `privado`, `oculto`;
- só se aplica a essays — nunca a source, concept, entity, insight, handout, status, log ou plano.

`scripts/set_visibility.py` escreve o campo (`allow`, `deny`, `hide`, `set-exclusive`)
e sem argumentos lista o corpus por nível.

O que **nunca** sai do repo privado: o corpo de qualquer página, qualquer caminho
para dentro de `data/`, e qualquer link que abra uma página não autorizada. Um
essay não publicado aparece no catálogo e no mapa marcado como **privado**, e não
abre.

Um site estático não esconde o que serve: título e resumo no catálogo são
legíveis por qualquer pessoa. Essa é a troca deliberada.

Nenhuma skill define ou altera `visibility:` automaticamente. Nem `/review`, nem
`/import`, nem `/organize`, nem o subagent `update`. É decisão explícita do Usuário,
aplicada por `scripts/set_visibility.py` ou pela skill `/publish`.

`scripts/build_site.py` roda **apenas** sob pedido explícito de publicação (via skill `/publish`), e o
resultado precisa passar em `scripts/check_site_privacy.py`.

Regras completas em `conventions/SKILL.md`.

## Plano de Longo Prazo

`plan/plano.md`, mantido por `/plan`, possui cinco seções fixas:

1. Tarefas
2. Fontes para Ingerir
3. Revisões
4. Estudos
5. Essays Futuros

`/plan work` retoma um item e executa o routing para a skill adequada. O item só sai pelo fluxo `/plan done`.

Pendência de curto prazo fica em `wiki/status.md`, não no plano.

## Status e Ritual de Sessão

`wiki/status.md` liga uma sessão à próxima. `wiki/log.md` é histórico, não estado atual.

- **Abertura:** se o pedido envolve trabalho substancial, leia `wiki/status.md` e as convenções relevantes antes de editar.
- **Fechamento:** após trabalho substancial (`/essay`, `/import`, `/digest`, `/absorb`, `/organize`, `/sweep`, `/study`, `/plan work`), ofereça `/status update`.
- Skills que precisam regenerar derivados usam o subagent `update` **depois** das edições.
- `/stats` é read-only e não chama `update`.

## Regras Gerais

1. **Não modifique documentos originais em `wiki/sources/`.** `manifest.md` e `map.md` são catálogos vivos e podem ser atualizados pelas skills responsáveis.
2. Derivados (`index.*`, `references.*`, grafo, stats) são gerados por script; nunca editar à mão.
3. Registre operações de conteúdo em `wiki/log.md` quando a skill exigir; o log é append-only.
4. Toda página segue frontmatter, nomenclatura e estrutura de `conventions/SKILL.md`.
5. **Contradição entre fontes:** não escolha um lado nem faça média. Mostre as versões com localização e aguarde a decisão do Usuário.
6. Busque na wiki primeiro. Vá às fontes arquivadas quando a wiki não bastar ou quando for necessário verificar a evidência.
7. Toda a wiki é escrita em Português do Brasil.
8. **Git é sempre explícito por repositório.** Nunca use um único `git add`/`commit`
   para representar o workspace inteiro:

   ```bash
   git -C . status
   git -C data status
   git -C site status
   ```

   O engine ignora `/data/` e `/site/` integralmente; nunca force `git add -f data`.

## Subagents

`.agents/agents/` guarda subagents mecânicos.

### `update`

Executa fechamento transacional: pre-flight, fixer, rebuild, post-flight e, somente com gates sem erro bloqueante, commit/push.

Pode reconstruir índice, referências, grafo, sphere, stats, qmd e espelhos. Não decide conteúdo, não resolve contradições, não funde/deleta páginas e não escreve prosa.

Chame apenas quando a skill de fechamento pedir ou sob pedido direto de sincronização/atualização.

### `lint-report`

Agrega diagnósticos de `check_wiki.py`, `check_references.py`, `check_dedupe.py` e `check_gaps.py`, prioriza em Crítico/Atenção/Informativo e não corrige nada.

Só sob pedido direto; nenhuma skill precisa chamá-lo automaticamente.

### Escrever e modificar skills e agentes

Vale para `.agents/skills/` e `.agents/agents/`.

- Escreva para execução: o que fazer, em que ordem e com que comando.
- Frase direta e legível; prosa curta, não telegrama.
- Justifique uma regra somente quando a justificativa muda a decisão.
- Não descreva o que outra skill faz; cite o comando ou arquivo canônico.
- Não registre histórico de mudança; o arquivo descreve o comportamento atual.
- Reserve “nunca” e “sempre” para invariantes realmente bloqueantes.
- Mudou o comportamento, atualize `description:` do frontmatter.
- Editou `.agents/`, terminou: não há mirror para sincronizar. Valide com `python scripts/check_skills.py`.

## Ferramentas

- **qmd** — primeira opção de busca conceitual quando disponível. Collection `secondbrain`, indexando `DATA_ROOT/wiki/**/*.md` (por padrão `data/wiki`), nunca a raiz do engine. Confirme com `qmd status`; se indisponível, use `scripts/find_text.py`.
- **scripts/find_text.py** — busca textual com contexto na wiki; também serve para termos/wikilinks exatos.
- **summarize** — resume links, arquivos e mídia quando disponível.
- **agent-browser** — fallback de navegador quando busca/fetch não resolverem.

## Repository Quality Gates

O repositório público versionado é um **engine de código e agentes**, não uma wiki. Ele não
contém corpus pessoal: `wiki/`, `plan/`, `raw/`, `output/` e `.obsidian/` vivem no repo
privado `data/` e são ignorados aqui. O único corpus versionado é sintético, em
`tests/fixtures/mini-brain/`, e os testes o instalam sob `tmp_path` — nunca na `data/` real.
CI roda sem `data/` e sem `site/`, e nunca clona nem recebe credencial do repo privado.

```bash
python scripts/check_repo.py
python scripts/check_repo.py --quick
python scripts/check_script_defaults.py
python -m pytest -q
```

- `check_repo.py` sem argumentos executa o diagnóstico completo; `--wiki` e `--exports` restringem o escopo.
- Todo script executável deve ter um default útil sem argumentos.
- `/doctor` é diagnóstico read-only e nunca corrige/commita.
- Clone sem essays, HTML ou PDF produz `SKIP` nos grupos aplicáveis.
- Correção mecânica determinística deve ganhar teste de regressão quando viável. Ver `TESTING.md`.
