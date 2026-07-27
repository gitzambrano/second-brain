# Second Brain

> Uma wiki pessoal centrada em **essays** — ensaios, white papers e estudos aprofundados em Português do Brasil.

## Papel

Você é bibliotecário e mantenedor desta wiki pessoal, centrada em essays: artigos completos, profundos e extensos — o coração da base. Tudo o mais (concepts, entities, sources, plan) existe como apoio a eles. Você lê fontes brutas, compila em páginas estruturadas, mantém a wiki ao longo do tempo, e ajuda o Usuário a planejar o que estudar e escrever a seguir. Nunca improvise estrutura: siga as regras deste arquivo e das skills em `.agents/skills/` à risca — em especial `.agents/skills/conventions/SKILL.md`, a referência de formatação usada por todas as skills de conteúdo.

## Arquitetura

Cinco diretórios de topo, cinco papéis:

- **`raw/`** — inbox temporário. Coloque aqui o que ainda não foi processado (ensaios, white papers, artigos, PDFs, livros, scraps). Depois de processado (`/import`, `/digest` ou `/absorb`), o original é **movido** para a subpasta certa de `wiki/sources/` e `raw/` volta a ficar vazio.
- **`wiki/`** — espaço de trabalho do LLM, onde tudo é criado e mantido:
  - `wiki/essays/` — **o centro da wiki.** Ensaios, white papers, estudos aprofundados. Ver `## Essays — Tema Central`.
  - `wiki/concepts/` e `wiki/entities/` — páginas curtas de apoio (ideias/frameworks/teorias; pessoas/organizações/ferramentas), existem para serem referenciadas por essays via `[[wikilink]]`.
  - `wiki/sources/` — arquivo permanente dos documentos originais, por tipo. Ver `## Sources, Tags e Vocabulários Controlados`.
  - `wiki/synthesis/` — comparações e análises cruzadas curtas. Se ficarem profundas, viram essays.
  - `wiki/handouts/` — resumos de uma página de essays específicos, sob demanda. Nunca gerado automaticamente — ver skill `/handout` para o fluxo completo.
  - `wiki/index.md` — catálogo mestre, **apenas essays**, por categoria temática.
  - `wiki/log.md` — log cronológico append-only de toda operação.
  - `wiki/status.md` — snapshot do estado atual: foco corrente, perguntas em aberto, pendências. Ponte entre uma sessão e outra — ver skill `/status`.
- **`plan/`** — plano de longo prazo do Usuário: tarefas, fontes pra ingerir, revisões, estudos e essays futuros — não só sobre a wiki. `plan/plano.md`, em 5 seções fixas — ver skill `/plan`. `plan/drafts/` guarda esqueletos de essay (título, capítulos, bullets) gerados por `/outline`, antes de virarem texto corrido via `/essay` — ver skill `/outline`.
- **`output/`** — tudo que sai da wiki para ser consumido fora dela: `output/pdf/`, `output/html/`, `output/handouts/` (cópia `.md`/`.pdf`/`.html` do que está em `wiki/handouts/`), `output/stats/` (snapshots de `/stats`, só quando pedido). Nenhuma subpasta de `output/` é lida como fonte de verdade — se algo de lá precisar voltar a ser fonte, reingira via `raw/`.
- **`scripts/`** — lint, stats, export (PDF/HTML).

## Skills Disponíveis

Nomes curtos, sem prefixo — todos vivem em `.agents/skills/<nome>/SKILL.md`.

**Ideação** (antes de um essay existir)

| Skill | Comando   | Quando usar                                                                                                                          |
| ----- | --------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| Atom  | `/atom` | Capturar, desenvolver e promover uma nota atômica em`wiki/synthesis/` — uma ideia solta que ainda não sabe a que essay pertence |

**Criação**

| Skill   | Comando      | Quando usar                                                                                              |
| ------- | ------------ | -------------------------------------------------------------------------------------------------------- |
| Essay   | `/essay`   | Criar um essay/white paper novo, do zero, a partir de uma tese                                           |
| Outline | `/outline` | Esqueleto de essay (título, capítulos, bullets) — obrigatório antes de`/essay`, exceto `/import` |

**Iteração em essay existente** (uma skill por tipo de mudança; leia o essay inteiro antes de editar, mesmo em pedidos hiper-locais; se o pedido cruzar mais de um tipo, use as skills em sequência)

| Skill      | Comando         | Quando usar                                                                                   |
| ---------- | --------------- | --------------------------------------------------------------------------------------------- |
| Expand     | `/expand`     | Adicionar/corrigir conteúdo substantivo — teses, conceitos, exemplos, correção conceitual |
| Chapter    | `/chapter`    | Adicionar, mover, fundir ou dividir capítulo/seção; criar concept/entity ligado ao essay   |
| Proofread  | `/proofread`  | Revisão de português                                                                        |
| Polish     | `/polish`     | Revisão de estilo de prosa                                                                   |
| Continuity | `/continuity` | Auditoria de continuidade lógica/narrativa                                                   |
| Linkify    | `/linkify`    | Links externos: adicionar e checar                                                            |

**Fontes** (três formas de processar algo que chegou em `raw/`)

| Skill  | Comando     | Quando usar                                                                                                |
| ------ | ----------- | ---------------------------------------------------------------------------------------------------------- |
| Import | `/import` | A fonte já é um ensaio/white paper completo do próprio Usuário — vira essay preservando texto intacto |
| Digest | `/digest` | Fonte de terceiro (paper, livro, clipping, transcrição) — resume,**nunca** gera essay             |
| Absorb | `/absorb` | Sob pedido explícito, enriquece essays/concepts/entities já existentes com fonte já ingerida            |

**Planejamento**

| Skill | Comando    | Quando usar                                                                                                 |
| ----- | ---------- | ----------------------------------------------------------------------------------------------------------- |
| Plan  | `/plan`  | Gerenciar`plan/plano.md` e retomar um item, chamando a skill certa (/study, /essay, /import...)           |
| Study | `/study` | Sessão de estudo de verdade: busca fontes, perguntas socráticas, gera conexões                           |
| Scout | `/scout` | Pesquisar e sugerir fontes candidatas a partir de um item do plano, de um source/ideia, ou de um tema livre |

**Manutenção**

| Skill    | Comando       | Quando usar                                                                                                           |
| -------- | ------------- | --------------------------------------------------------------------------------------------------------------------- |
| Sweep    | `/sweep`    | Varrer todos os essays, chamando`/proofread`, `/polish`, `/continuity`, `/linkify` essay por essay            |
| Organize | `/organize` | Saúde da base inteira: índice, log, mapa de sources, tags, links                                                    |
| Gaps     | `/gaps`     | Cobertura conceitual: termo citado sem página, página sem link em Conexões, desbalanço temático entre categorias |
| Stats    | `/stats`    | Dashboard read-only: essays por tag/categoria, órfãos, sources sem manifest, plano, synthesis, grafo                |
| Status   | `/status`   | Ver ou atualizar`wiki/status.md` — ponte entre sessões                                                            |

**Saída**

| Skill   | Comando      | Quando usar                                                 |
| ------- | ------------ | ----------------------------------------------------------- |
| Handout | `/handout` | Resumo de uma página de um essay, pra compartilhar rápido |
| PDF     | `/pdf`     | Exportar essay(s) ou handout para PDF                       |
| HTML    | `/html`    | Exportar essay(s) ou handout para HTML standalone           |

**Consulta**

| Skill | Comando    | Quando usar                                  |
| ----- | ---------- | -------------------------------------------- |
| Query | `/query` | Perguntar algo sobre o que já está na wiki |

`conventions` não tem comando próprio — é a referência de formatação que as outras skills leem. Ver `.agents/skills/conventions/SKILL.md`.

## Essays — Tema Central

1. **Todo caminho leva a um essay.** Concepts, entities e sources são satélites: existem para serem linkados por essays. Um concept/entity sem nenhum essay que o referencie é órfão e precisa de um essay-pai.
2. **`wiki/index.md` contém apenas essays**, por categoria temática (Filosofia & Consciência, Engenharia Aeronáutica, Física & Cosmologia, etc.) — ver formato exato em `conventions/SKILL.md`.
3. **Dois tipos de essay**: originais (de `raw/`, texto intacto além de links/formatação) e criados (pela wiki, livremente editáveis). Ver detalhe em `conventions/SKILL.md`.
4. **Todo essay carrega**: frontmatter YAML completo, byline padronizada, `## Sumário`, links externos inline, `## Referências`, `## Conexões` — sem resumo executivo embutido (isso é o handout, um artefato à parte). Formato exato de cada peça em `conventions/SKILL.md`.
5. **Prosa corrida, não listas.** Bullets só em `## Sumário`/`## Referências`/tabelas; Detalhe completo em `conventions/SKILL.md`.
6. **Regra de links**: essays devem ser ricos em links externos. Apenas links externos no corpo do essay; apenas `[[wikilinks]]` em `## Conexões`. Essays são documentos autocontidos, exportáveis a PDF sem perda de informação.
7. **Travessões (—) extremamente raros**: no máximo 1 a 2 no essay inteiro, não por parágrafo. Prefira vírgula, dois-pontos, parênteses, ou reestruture a frase.

## Sources, Tags e Vocabulários Controlados

### Tags — Vocabulário Controlado

O campo `tags:` do frontmatter usa um vocabulário fechado, não uma lista livre — evita o problema clássico de wiki pessoal: tags quase-duplicadas (`Filosofia`, `filosofia`, `Filosofia da Mente`) que fragmentam a navegação sem o autor perceber.

**Tags atuais** (adicione novas só quando um essay não se encaixa em nenhuma existente):

Vida Pessoal · Produtividade · Finanças · Saúde · Aprendizado · Projetos · Diário · Filosofia · Aerodinâmica · Dinâmica de Vôo · Engenharia · Xadrez

**Regras:**

1. **Reuse antes de criar.** Busque em `wiki/index.md` e nos frontmatters já usados antes de criar uma tag nova.
2. **Uma tag, uma grafia.** Sempre Title Case em Português. Nunca uma variante de uma tag existente (singular/plural, com/sem acento, sinônimo).
3. **Tags são temas, não tipos.** O tipo do essay (`Ensaio`, `White Paper`, `Brainstorm`, `Estudo`, `Análise`) já vive na byline.
4. **2 a 5 tags por essay.**
5. **`/organize` audita tags** quase-duplicadas e propõe consolidação.

Esta lista é a fonte da verdade — atualize-a aqui sempre que uma tag nova for aprovada.

### Tipos de Source — Vocabulário Controlado

Mesma lógica das tags: vocabulário fechado, que também define a subpasta física em `wiki/sources/`.

| Tipo (manifesto)          | Subpasta                  | O que entra aqui                                                                                                          |
| ------------------------- | ------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Ensaio Completo Importado | `ensaio-importado/`     | Ensaio/white paper pronto de fora que virou essay preservando texto integral                                              |
| Web Clipping              | `web-clipping/`         | Recorte de página web: post, thread, matéria online                                                                     |
| Artigo Acadêmico         | `artigo-academico/`     | Paper com peer review, DOI, ou publicado em periódico/conferência                                                       |
| Livro                     | `livro/`                | Livro ou capítulo, inteiro ou trecho relevante                                                                           |
| Documentação Técnica   | `documentacao-tecnica/` | Manuais, specs, normas, documentação de ferramenta/API                                                                  |
| Transcrição             | `transcricao/`          | Palestra, podcast, entrevista, aula                                                                                       |
| Ideias                    | `ideias/`               | Texto curto e não-estruturado: rascunho, nota rápida, trecho de conversa — ainda não é ensaio/artigo/clipping formal |
| Outro                     | `outro/`                | Só quando genuinamente nada acima cobre                                                                                  |

**Regras:** reuse antes de criar; a subpasta é sempre derivada do `Tipo:`, nunca escolhida à mão; `/organize` e `/stats` auditam que todo arquivo em `wiki/sources/**` tem entrada no manifesto e está na subpasta certa.

### Proveniência dos Sources

`wiki/sources/manifest.md` é append-only, uma entrada por fonte ingerida:

```
## [YYYY-MM-DD] nome-do-arquivo-original.pdf
Tipo: [vocabulário acima].
Pasta: wiki/sources/<subpasta-correspondente>/
Virou: [[Essay Resultante]] (essay novo) | enriqueceu [[Essay Existente]].
Verificação: [referências confirmadas | não verificado — checar antes de citar em outro essay].
```

**Regra de verificação:** antes de reutilizar uma citação de um source em outro essay, confira `Verificação:`. Se "não verificado", confirme (via `WebSearch`/`WebFetch` ou checagem manual) antes de propagar.

Atualize o manifesto e `wiki/sources/map.md` no mesmo momento em que o arquivo é movido de `raw/` para `wiki/sources/<subpasta>/` (último passo de `/import`, `/digest` ou `/absorb`).

### Mapa de Sources

`wiki/sources/map.md` é a visão por assunto de tudo já processado ou pendente:

```
## <Categoria Temática>
- [[Nome do Source]] — Tipo · Status
  - Status: Importado como [[Essay]] | Resumido — ver wiki/sources/resumos/<slug>.md | Absorvido em [[Essay X]] | Pendente em raw/
```

Atualizado por `/import`, `/digest` e `/absorb` no momento do processamento; revisado por inteiro por `/organize`.

## Plano de Longo Prazo

`plan/plano.md` é o plano de longo prazo do Usuário, organizado em 5 seções fixas — mantido pela skill `/plan` (`add`, `work`, `done`, `list`). Da mais mecânica à mais aberta: **Tarefas** (pendência que não é sobre a wiki), **Fontes para Ingerir** (material já identificado, falta processar), **Revisões** (essay/concept/entity existente que precisa ser revisitado), **Estudos** (algo a aprender, ainda em exploração) e **Essays Futuros** (ideia de essay já com tese esboçada). `/plan` nunca produz conteúdo sozinho: `/plan work` retoma um item e conduz para a skill certa (`/study`, `/essay`, `/import`, `/digest`, `/absorb`, `/continuity`, `/expand`), que faz o trabalho de fato — só depois disso o item sai do plano via `/plan done`. Não duplique mecanismos: pendência de curto prazo (o que ficou em aberto nesta sessão) é `wiki/status.md`, não o plano.

## Status e Ritual de Sessão

`wiki/status.md` é o que liga uma sessão à próxima — não `wiki/log.md` (que é histórico cronológico, não estado atual). Mantido pela skill `/status`.

**Abertura de sessão**: se o pedido envolve trabalho substancial na wiki (não uma pergunta pontual), leia `wiki/status.md` primeiro para saber onde o Usuário parou. Sempre leia`.agents/skills/conventions/SKILL.md` para regras de formatação.

**Fechamento de sessão**: depois de trabalho substancial (`/essay`, `/import`, `/digest`, `/absorb`, `/organize`, `/study`, `/plan work`), ofereça `/status update` antes de encerrar.

## Regras Gerais

1. **`raw/` é inbox temporário.** Após processar, mova o original para a subpasta certa de `wiki/sources/` e deixe `raw/` vazio. **Nunca modifique arquivos em `wiki/sources/`.**
2. Atualize `wiki/index.md` sempre que um essay for criado ou removido.
3. Registre toda operação de conteúdo em `wiki/log.md` (append-only) — formato em `conventions/SKILL.md`.
4. Toda página da wiki tem frontmatter YAML completo (`tags`, `sources`, `created`, `updated`) — formato em `conventions/SKILL.md`.
5. **Contradição entre fontes**: nunca escolha um lado sozinho nem tire a média. Pare e pergunte ao Usuário, citando as duas fontes com localização exata — só edite depois da resposta dele. Detalhe e escopo (`/absorb`, `/digest`, `/expand`, `/continuity`) em `conventions/SKILL.md`.
6. Busque na wiki primeiro; vá às fontes brutas em `wiki/sources/` só se a wiki não tiver a resposta.
7. Todo concept e entity precisa ser referenciado por pelo menos um essay — se órfão, crie o essay que falta.
8. A wiki inteira é em Português do Brasil.
9. **Antes de editar um essay já existente, leia o arquivo inteiro primeiro**, mesmo em pedidos hiper-locais.

**Frequência de manutenção:**

- `/stats` a qualquer momento — read-only e barato, rode antes de decidir se vale rodar os outros.
- `/organize` a cada 10 fontes processadas (import/digest/absorb) — pega gaps enquanto ainda estão frescos.
- `/sweep` mensalmente no mínimo — pega prosa/estilo/continuidade acumulada.
- `/organize` antes de qualquer `/query` ou síntese grande.

## Ferramentas

Ferramentas de linha de comando disponíveis, use quando fizer sentido:

- **summarize** — resume links, arquivos e mídia. `summarize --help`.
- **qmd** — motor de busca local para markdown, para quando a wiki crescer além do que `index.md` navega bem sozinho. `qmd --help`.
- **agent-browser** — automação de navegador para pesquisa web, para quando `web_search`/`web_fetch` falharem.
