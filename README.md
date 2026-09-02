# Second Brain

Wiki pessoal centrada em **essays** — ensaios, white papers e estudos aprofundados em Português do Brasil — mantida por agentes de IA.

- [`AGENTS.md`](./AGENTS.md): regras operacionais e routing para agentes.
- [`.agents/skills/`](./.agents/skills/): fluxo de cada comando.
- [`.agents/skills/conventions/SKILL.md`](./.agents/skills/conventions/SKILL.md): formato e estilo canônicos.
- [`TESTING.md`](./TESTING.md): testes, fixtures e quality gates.

## Estrutura de repositórios

Este checkout é o **second-brain-engine** — o repositório **principal** e o único
obrigatório. Ele contém apenas a camada operacional: agentes, skills, scripts,
testes e o frontend do site. Não contém corpus pessoal.

Ele pode conviver, aninhados por conveniência de workspace, com dois outros
repositórios Git independentes. Os dois são **opcionais** — você pode trabalhar
só com o engine:

```text
./      second-brain-engine  PUBLIC   engine: agentes, skills, scripts, testes, frontend
data/   second-brain-data    PRIVATE  wiki, plan, raw, output, Obsidian
site/   second-brain-site    PUBLIC   projeção gerada dos essays autorizados
```

- **`data/`** — o repositório **privado**. Guarda todo o conteúdo pessoal da
  wiki (`wiki/`, `plan/`, `raw/`, `output/`) e a instalação Obsidian. É opcional
  porque o engine funciona sozinho (CI roda sem `data/`); sem ele, você só não
  tem corpus próprio, apenas o fixture sintético de teste. Cada um dos três
  repositórios tem o seu próprio `README.md` — veja o do `data/` para as regras
  do conteúdo privado.
- **`site/`** — o repositório **público**. Recebe a projeção gerada dos essays
  autorizados, gerada por `build_site.py`. Também é opcional: só existe se e
  quando você publicar. Veja o `README.md` do `site/` para as regras do que é
  seguro publicar.

`data/` e `site/` **não** são submodules; o Git do engine os ignora
integralmente, e nunca se usa `git add -f` neles. Os três repositórios são
versionados e commitados separadamente — Git é sempre explícito por repositório.

### Conteúdo do engine (`./`)

Apenas a camada operacional, versionada no Git público:

```text
.agents/
  skills/                  fonte única das skills (fluxo de cada comando)
  agents/                  fonte única dos subagents (update, lint-report)
scripts/                   lint, busca, índice, grafo, export e quality gates
site_src/                  templates, CSS e JS do site público
tests/                     testes e fixtures sintéticas
AGENTS.md                  regras operacionais e routing
CLAUDE.md                  importa AGENTS.md para Claude Code
pyproject.toml             configuração de pytest e ruff
TESTING.md                 testes, fixtures e quality gates
```

### Conteúdo do repositório privado (`data/`)

Caminhos **lógicos** — `wiki/...` significa `data/wiki/...`:

```text
raw/                       inbox temporário de material não processado

wiki/
  essays/                  essays, white papers e estudos
  concepts/                conceitos e frameworks de apoio
  entities/                pessoas, obras, organizações e ferramentas
  insights/                ideias ainda sem essay-pai
  handouts/                resumos de uma página
  assets/                  imagens e figuras
  sources/                 arquivo permanente das fontes processadas
    resumos/               resumos produzidos por /digest
    manifest.md            proveniência das fontes
    map.md                 mapa das fontes
  index.md / index.json    catálogo gerado de essays
  references.md / .json    bibliografia consolidada gerada
  log.md                   histórico append-only
  status.md                estado da sessão

plan/
  plano.md                 pendências de longo prazo
  drafts/                  outlines aprováveis antes de /essay

output/                    PDFs, HTML, handouts, stats e grafo gerados
.obsidian/                 configuração do vault Obsidian
```

Os tipos de source, tags, frontmatter, byline, links, referências, prosa, imagens e demais formatos vivem somente em `conventions/SKILL.md`.

## Instalação

O engine exige apenas Python 3 e PyYAML para o núcleo. Clonando-o sozinho você
já tem o `check_repo.py`, os testes e a infraestrutura funcionando — os exports
(HTML/PDF) e a busca semântica exigem dependências adicionais, descritas em
[Requisitos](#requisitos).

### 1. Clonar o engine

```bash
git clone <url-do-engine> second-brain
cd second-brain
```

Como `data/` e `site/` são opcionais, um clone novo já é suficiente para
desenvolver o engine e rodar a suíte de testes contra o corpus sintético.

### 2. Dependências Python

```bash
python -m pip install pyyaml
python -m pip install -r requirements-dev.txt   # se o arquivo existir
```

Para a suíte completa (HTML/PDF/exports), instale também as dependências
opcionais listadas em [Requisitos](#requisitos).

### 3. Criar os repositórios opcionais (data/ e site/)

Num clone novo não existem `data/` e `site/`. O `bootstrap_repositories.py`
cria os esqueletos de ambos — sem argumentos ele só mostra o que faria:

```bash
python scripts/bootstrap_repositories.py          # mostra o plano (dry-run)
python scripts/bootstrap_repositories.py --create # cria data/ e site/
python scripts/bootstrap_repositories.py --init-git # e inicializa os Gits aninhados
```

Você pode ignorar esse passo: `data/` e `site/` são opcionais e o engine não os
exige para funcionar.

### 4. Verificar a instalação

```bash
python scripts/check_env.py        # ambiente e dependências
python scripts/check_repo.py       # diagnóstico completo
python scripts/check_skills.py     # valida contratos de skill
python -m pytest -q                # suíte de testes
```

## Fonte única

`.agents/` é a única árvore editável de skills e subagents, compartilhada por todos os
agentes. Não existem espelhos gerados e não há passo de sincronização. `CLAUDE.md` é um
adaptador de uma linha que importa `@AGENTS.md`.

Para validar contratos de skill:

```bash
python scripts/check_skills.py
```

## Subagents

Dois subagents mecânicos vivem em `.agents/agents/`.

- **`update`** — o subagent de **fechamento transacional**. É quem encerra uma
  sessão de trabalho substancial. Executa, nesta ordem: **pre-flight** (valida o
  workspace e a disciplina de caminho), **fixer** de lint mecânico, **rebuild**
  dos derivados privados (índice, referências, grafo, sphere, stats e coleção
  `qmd`), **post-flight** (re-verifica o repositório) e, só com gates sem erro
  bloqueante, faz commit/push — sempre um comando Git por repositório, atuando
  em `./` e `data/`. Ele **nunca** constrói nem publica o site, nunca resolve
  contradição nem reescreve prosa, e nunca commita com erro bloqueante.
- **`lint-report`** — o subagent de **diagnóstico**. Roda `check_wiki.py`,
  `check_references.py`, `check_dedupe.py`, `check_freshness.py` e
  `check_gaps.py`, e devolve um resumo já agrupado por prioridade
  (Crítico / Atenção / Informativo). Não corrige nada e não interpreta além de
  agrupar. É chamado só sob pedido direto do Usuário.

## Publicação

O site tem duas camadas. O **catálogo e o mapa** cobrem a base inteira — título,
resumo, tags, datas, status e conexões de todo essay, concept, entity, insight e
referência. O **texto** só é legível se o frontmatter do essay tiver o campo
`visibility: public` (ou a grafia antiga `publish: true`); caso contrário a
página aparece marcada como privada e não abre. Há também o nível `hidden`, que
ausenta o essay de tudo — site, índice da wiki e grafo da wiki. Campo ausente ou
não reconhecido = `private`. Nenhuma skill altera esse campo automaticamente.

O fluxo de publicação é **explícito e manual**: você decide com
`scripts/publication.py` quais essays são públicos, roda o `build_site.py` e
valida com o `check_site_privacy.py` antes de considerar o site pronto.

```bash
python scripts/publication.py                       # allowlist atual
python scripts/publication.py allow <título>        # publica um essay
python scripts/check_publication.py                 # validação read-only
python scripts/build_site.py                        # gera site/
python scripts/build_site.py --check
python scripts/check_site_privacy.py                # sentinela de privacidade
python scripts/serve_site.py                        # inspeção local
```

O mapa público usa os mesmos renderizadores da wiki (`build_graph.py` e
`build_sphere.py`), alimentados com os nós já sanitizados.

O `scripts/bootstrap_repositories.py` cria os esqueletos de `data/` e `site/` —
só é necessário num clone novo, e sem argumentos ele apenas mostra o que faria.

## Skills

O arquivo de cada skill é a especificação completa. `conventions` não possui comando próprio.

### Ideação e criação

- **`/insight`** — Captura uma ideia solta ainda sem essay-pai em
  `wiki/insights/`, e a desenvolve em sessões, lista por maturidade ou promove
  para virar essay novo ou capítulo.
- **`/outline`** — Monta o esqueleto de um essay futuro — título, tipo e cada
  capítulo com sua frase de papel argumentativo e bullets do conteúdo — salvo em
  `plan/drafts/` para o Usuário aprovar e iterar antes de qualquer prosa.
- **`/essay`** — Escreve o essay completo a partir de um outline aprovado,
  seguindo o formato canônico de `conventions`. Sempre exige outline; a única
  exceção é `/import`.

### Iteração em essay

- **`/expand`** — Adiciona ou corrige conteúdo substantivo num essay existente:
  tese nova, conceito, exemplo, ou erro factual/conceitual, perguntando ao
  Usuário quando a direção não é óbvia.
- **`/chapter`** — Mudanças estruturais: adiciona, move, funde ou divide uma
  seção/capítulo, ou cria uma página de concept/entity ligada ao essay.
- **`/continuity`** — Audita a coerência estrutural do início ao fim: conceito
  usado antes de ser explicado, saltos abruptos, tese sustentada entre capítulos
  e conclusão que fecha o argumento aberto na introdução.
- **`/proofread`** — Passada só de língua: gramática, ortografia, concordância,
  pontuação e consistência terminológica, sem mudar conteúdo ou argumento.
- **`/polish`** — Melhora o estilo sem mudar o que o texto argumenta: tom,
  ritmo, elegância e adesão às regras de prosa da wiki.
- **`/linkify`** — Adiciona links externos a conceitos e termos técnicos ao
  longo do corpo, e valida os links existentes quanto a validade e relevância.
- **`/review`** — Peer review crítico no estilo acadêmico: ataca a força dos
  argumentos, aponta falácias, premissas não sustentadas, erros de física e
  citações ausentes; sugere fontes, exemplos e conexões, e cria um plano de
  modificação para o Usuário aprovar.

### Fontes e estudo

- **`/import`** — Ingere um essay/white paper completo escrito pelo próprio
  Usuário, preservando o texto intacto e o empacotando como essay próprio.
- **`/digest`** — Lê e resume uma fonte de terceiros (paper, livro, web
  clipping) e a arquiva em `wiki/sources/`; nunca gera essay a partir dela.
- **`/absorb`** — Incorpora uma fonte já processada a essays, conceitos ou
  entidades existentes, sob pedido explícito do Usuário.
- **`/study`** — Conduz uma sessão de estudo de verdade sobre um tema: busca
  fontes, lê e sintetiza, faz perguntas socráticas e gera conexões com o que já
  existe na wiki.
- **`/scout`** — Pesquisa a web e propõe uma lista curada de fontes candidatas a
  ingerir, sem ingerir nada sozinho.
- **`/plan`** — Gerencia as pendências de longo prazo em `plan/plano.md`
  (tarefas, fontes, revisões, estudos, essays futuros) e retoma um item pela
  skill adequada.

### Manutenção

- **`/organize`** — Organiza a base na camada de metadados/grafo e de
  formatação mecânica: roda o lint completo, corrige links quebrados, atualiza
  índice, manifesto, tags e o grafo de conexões.
- **`/sweep`** — Orquestra a bateria completa de revisão num essay ou no corpus
  inteiro: `/organize` → `/continuity` → `/proofread` → `/polish` → `/linkify`.
- **`/gaps`** — Identifica lacunas nas camadas mecânica, léxica e semântica,
  tratando essays, concepts, entities e insights como peers. Só identifica e
  ranqueia; nunca corrige.
- **`/connect`** — Age sobre os candidatos de `/gaps`: corrige link quebrado,
  aplica conexão nova de alta confiança e cria página mínima quando o candidato
  não tem nenhuma.
- **`/stats`** — Dashboard read-only de saúde da wiki: contagens, órfãos,
  fontes sem manifesto, sinais de formatação e itens do plano.
- **`/status`** — Mostra ou atualiza `wiki/status.md`, o snapshot que liga uma
  sessão à próxima.
- **`/merge`** — Funde duas páginas do mesmo tipo numa só, redirecionando todos
  os wikilinks para a sobrevivente.
- **`/delete`** — Remove uma página com confirmação e repara o que a remoção
  quebrou (links órfãos, índice, manifesto).
- **`/doctor`** — Diagnóstico read-only do repositório; nunca corrige nem
  commita.

### Saída e consulta

- **`/handout`** — Gera um resumo de uma página de um essay em `wiki/handouts/`,
  com linha de tese e conclusões em prosa.
- **`/pdf`** — Exporta e valida um ou todos os essays para PDF via Pandoc +
  LuaLaTeX.
- **`/html`** — Exporta e valida um ou todos os essays para HTML standalone e
  responsivo via Pandoc.
- **`/query`** — Responde perguntas usando a wiki como base de conhecimento
  centrada em essays.
- **`/synthesize`** — Procura padrões emergentes na combinação de páginas — o
  que ainda não foi dito, em vez de apenas responder a uma pergunta.

## Testes

Os testes vivem em `tests/` e instalam o corpus sintético `tests/fixtures/mini-brain/`
sempre sob um `tmp_path` — nunca sob a `data/` real. `conftest.py` fornece as
fixtures `mini_brain`/`installed_mini_brain` (cópia do fixture com as pastas de
saída criadas) e o helper `run_script`, que roda um script de `scripts/`
apontando `DATA_ROOT`/`SITE_ROOT` para o corpus de teste.

- **`test_repo_layout.py`** — Garante que, por padrão, `repo_paths.py` resolve
  `DATA_ROOT` e `SITE_ROOT` para os diretórios aninhados `data/` e `site/`.
- **`test_no_agent_mirrors.py`** — Garante a fonte única: `.agents/` é a única
  árvore de skills/agents e não existem espelhos em `.claude/` ou `.codex/`.
- **`test_script_defaults.py`** — Verifica que todo script executável tem um
  default útil sem argumentos (`check_script_defaults.py`) e que as ferramentas
  com parâmetro não abortam por falta de argumento.
- **`test_repo_sanity.py`** — Quality gate do repositório: `check_repo.py
  --quick` sem erros, e `check_repo.py` sem argumentos válido num skeleton vazio.
- **`test_skills.py`** — Valida os contratos de skill (`check_skills.py` sem
  erros e sem regressões conhecidas), e que `update` valida o workspace antes do
  quality gate e nunca publica o site.
- **`test_wiki_checks.py`** — (lento) Instala o mini-brain e roda `build_index` +
  `check_wiki`, garantindo zero issues bloqueantes; inclui regressão de
  `DEAD_WIKILINK`.
- **`test_freshness.py`** — Verifica que `check_freshness.py` sinaliza um claim
  temporal antigo (`STALE_CANDIDATE`) e não sinaliza um essay recente.
- **`test_visibility.py`** — Cobre os três níveis de visibilidade
  (public/private/hidden e grafias em português), publicação exclusiva, essay
  `hidden` ausente do catálogo, e a garantia de que escrever visibilidade nunca
  altera o corpo do arquivo (idempotente).
- **`test_site_privacy.py`** — Teste sentinela de privacidade do site público: o
  corpo de um essay privado nunca chega ao site, essay não publicado não tem
  página nem link, o catálogo nomeia mas não abre, e o checker aceita o site
  válido e rejeita um link de leitura forjado.
- **`test_export_parity.py`** — Verifica a paridade semântica
  markdown/HTML/PDF do essay fixture via `check_export_parity.py`, incluindo
  regressões de títulos com matemática inline e headings com espaçamento
  estendido no PDF.
- **`test_html_export.py`** — Exporta o fixture para HTML e valida a estrutura
  (`check_html_export.py`) e a renderização (`check_html_render.py`).
- **`test_pdf_export.py`** — Exporta o fixture para PDF e valida o conteúdo
  (`check_pdf_content.py`) e o layout (`check_pdf_layout.py`).
- **`test_checker_selftests.py`** — Testa os próprios checkers
  (`check_html_render`, `check_pdf_content/layout`, `check_export_parity`):
  aceitam artefatos válidos e rejeitam os quebrados.
- **`test_legacy_feature_regressions.py`** — Regressões das ferramentas legadas:
  `find_text`, `retag`, `check_title`, `mermaid_to_png` e `check_html_export`.

## Requisitos

O núcleo (lint, checks, testes, índices, grafo) exige apenas:

- Python 3
- PyYAML

Para exports e checks completos (HTML/PDF/renderização no navegador), são
necessárias dependências adicionais:

- Pandoc
- LuaLaTeX
- PyMuPDF
- BeautifulSoup/html5lib
- Playwright + Chromium

```bash
python -m playwright install chromium
```

`qmd` é opcional para busca semântica. Sem ele, `scripts/find_text.py` continua disponível.

## Privacidade e versionamento

Conteúdo pessoal fica fora do Git do engine por design: `raw/`, `plan/`, `wiki/`
e `output/` são ignorados, exceto estruturas necessárias com `.gitkeep` e
fixtures sintéticas de teste. Esse conteúdo vive no repositório privado `data/`,
que o Git do engine ignora integralmente (`.gitignore` tem `/data/` e `/site/`).

O Git do engine versiona a camada operacional: `AGENTS.md`, `CLAUDE.md`,
`README.md`, `.agents/**`, scripts, testes e configuração. Espelhos gerados não
são fonte de verdade.

## Qualidade

```bash
python scripts/check_env.py
python scripts/check_repo.py
python scripts/check_repo.py --quick
python scripts/check_skills.py
python scripts/check_script_defaults.py
python -m pytest -q
```

Detalhes de cada gate e da suíte estão em [`TESTING.md`](./TESTING.md).