# Second Brain

Wiki pessoal centrada em **essays** — ensaios, white papers e estudos aprofundados em Português do Brasil — mantida por agentes de IA.

- [`AGENTS.md`](./AGENTS.md): regras operacionais e routing para agentes.
- [`.agents/skills/`](./.agents/skills/): fluxo de cada comando.
- [`.agents/skills/conventions/SKILL.md`](./.agents/skills/conventions/SKILL.md): formato e estilo canônicos.
- [`TESTING.md`](./TESTING.md): testes, fixtures e quality gates.

## Estrutura

Três repositórios Git independentes, aninhados por conveniência de workspace:

```text
./      second-brain-engine  PUBLIC   engine: agentes, skills, scripts, testes, frontend
data/   second-brain-data    PRIVATE  wiki, plan, raw, output, Obsidian
site/   second-brain-site    PUBLIC   projeção gerada dos essays autorizados
```

`data/` e `site/` **não** são submodules; o Git do engine os ignora integralmente.
Caminho de conteúdo abaixo é lógico: `wiki/...` significa `data/wiki/...`.

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

scripts/                    lint, busca, índice, grafo, export e quality gates
output/                     PDFs, HTML, handouts, stats e grafo gerados

.agents/skills/             fonte única das skills
.agents/agents/             fonte única dos subagents
site_src/                   templates, CSS e JS do site público
AGENTS.md                   regras operacionais
CLAUDE.md                   importa AGENTS.md para Claude Code
```

Os tipos de source, tags, frontmatter, byline, links, referências, prosa, imagens e demais formatos vivem somente em `conventions/SKILL.md`.

## Fonte única

`.agents/` é a única árvore editável de skills e subagents, compartilhada por todos os
agentes. Não existem espelhos gerados e não há passo de sincronização. `CLAUDE.md` é um
adaptador de uma linha que importa `@AGENTS.md`.

Para validar contratos de skill:

```bash
python scripts/check_skills.py
```

O subagent `update` cuida do fechamento mecânico quando uma skill o aciona: rebuild de derivados privados, quality gates e commit/push separados por repositório. Ele nunca constrói nem publica o site. O subagent `lint-report` é diagnóstico read-only sob pedido direto.

## Publicação

O site tem duas camadas. O **catálogo e o mapa** cobrem a base inteira — título,
resumo, tags, datas, status e conexões de todo essay, concept, entity, insight e
referência. O **texto** só é legível se o frontmatter do essay tiver o booleano
YAML `publish: true`; sem isso a página aparece marcada como privado e não abre.
Nenhuma skill altera esse campo automaticamente.

O mapa público usa os mesmos renderizadores da wiki (`build_graph.py` e
`build_sphere.py`), alimentados com os nós já sanitizados.

```bash
python scripts/publication.py                       # allowlist atual
python scripts/check_publication.py                 # validação read-only
python scripts/build_site.py                        # gera site/
python scripts/build_site.py --check
python scripts/check_site_privacy.py
python scripts/serve_site.py                        # inspeção local
```

O `scripts/bootstrap_repositories.py` cria os esqueletos de `data/` e `site/` —
só é necessário num clone novo, e sem argumentos ele apenas mostra o que faria.

## Skills

### Ideação e criação

| Comando | Uso |
| ------------ | ----------------------------------------------------------------------- |
| `/insight` | Capturar, desenvolver, listar ou promover uma ideia ainda sem essay-pai |
| `/outline` | Estruturar tese, capítulos e bullets antes de escrever um essay |
| `/essay` | Escrever um essay novo a partir de outline aprovado |

### Iteração em essay

| Comando         | Uso                                                            |
| --------------- | -------------------------------------------------------------- |
| `/expand`     | Adicionar ou corrigir conteúdo substantivo                    |
| `/chapter`    | Adicionar, mover, fundir ou dividir seções                   |
| `/continuity` | Auditar progressão lógica e narrativa                        |
| `/proofread`  | Corrigir português                                            |
| `/polish`     | Melhorar estilo sem alterar conteúdo                          |
| `/linkify`    | Adicionar/validar links externos e referências                |
| `/review`     | Peer review crítico de tese, rigor, profundidade e evidência |

### Fontes e estudo

| Comando | Uso |
| ----------- | --------------------------------------------------------------------- |
| `/import` | Ingerir essay completo do próprio autor preservando o texto |
| `/digest` | Resumir e arquivar fonte de terceiros; nunca gera essay |
| `/absorb` | Incorporar fonte já processada a páginas existentes |
| `/study` | Estudar um tema lendo fontes e desenvolvendo entendimento |
| `/scout` | Curar fontes candidatas sem ingerir |
| `/plan` | Gerenciar pendências de longo prazo e retomá-las pela skill correta |

### Manutenção

| Comando       | Uso                                                        |
| ------------- | ---------------------------------------------------------- |
| `/organize` | Metadados, estrutura e formatação mecânica              |
| `/sweep`    | `/organize` + continuidade + português + estilo + links |
| `/gaps`     | Identificar lacunas e conexões ausentes; read-only        |
| `/connect`  | Agir sobre candidatos de`/gaps`                          |
| `/stats`    | Dashboard read-only                                        |
| `/status`   | Mostrar ou atualizar o estado entre sessões               |
| `/merge`    | Fundir duas páginas do mesmo tipo                         |
| `/delete`   | Remover página com confirmação e reparo de links        |
| `/doctor`   | Diagnóstico read-only do repositório                     |

### Saída e consulta

| Comando      | Uso                                        |
| ------------ | ------------------------------------------ |
| `/handout` | Gerar resumo de uma página                |
| `/pdf`     | Exportar e validar PDF                     |
| `/html`    | Exportar e validar HTML standalone         |
| `/query`   | Consultar a wiki como base de conhecimento |
| `/synthesize` | Procurar padrões emergentes na combinação de páginas já existentes |

O arquivo de cada skill é a especificação completa. `conventions` não possui comando próprio.

## Requisitos

Base:

- Python 3
- PyYAML

Exports e checks completos:

- Pandoc
- LuaLaTeX
- PyMuPDF
- BeautifulSoup/html5lib
- Playwright + Chromium

`qmd` é opcional para busca semântica. Sem ele, `scripts/find_text.py` continua disponível.

## Privacidade e versionamento

Conteúdo pessoal fica fora do Git por design: `raw/`, `plan/`, `wiki/` e `output/` são ignorados, exceto estruturas necessárias com `.gitkeep` e fixtures sintéticas de teste.

O Git versiona a camada operacional: `AGENTS.md`, `CLAUDE.md`, `README.md`, `.agents/**`, scripts, testes e configuração. Espelhos gerados não são fonte de verdade.

## Qualidade

```bash
python scripts/check_repo.py
python scripts/check_repo.py --quick
python scripts/check_skills.py
python -m pytest -q
```
