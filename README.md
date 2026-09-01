# Second Brain

Wiki pessoal centrada em **essays** — ensaios, white papers e estudos aprofundados em Português do Brasil — mantida por agentes de IA.

- [`AGENTS.md`](./AGENTS.md): regras operacionais e routing para agentes.
- [`.agents/skills/`](./.agents/skills/): fluxo de cada comando.
- [`.agents/skills/conventions/SKILL.md`](./.agents/skills/conventions/SKILL.md): formato e estilo canônicos.
- [`TESTING.md`](./TESTING.md): testes, fixtures e quality gates.

## Estrutura

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

.agents/skills/             fonte das skills
.agents/agents/             fonte dos subagents
.claude/skills/             espelho gerado — não editar
.claude/agents/             espelho gerado — não editar
.codex/skills/              espelho gerado — não editar
AGENTS.md                   regras operacionais
CLAUDE.md                   importa AGENTS.md para Claude Code
```

Os tipos de source, tags, frontmatter, byline, links, referências, prosa, imagens e demais formatos vivem somente em `conventions/SKILL.md`.

## Fonte única e espelhos

| Fonte editável | Derivado | Como sincroniza |
| ---------------------------------------- | ------------------------------------------------------------ | ------------------------------------ |
| `AGENTS.md` | `CLAUDE.md` | `CLAUDE.md` importa `@AGENTS.md` |
| `.agents/skills/`, `.agents/agents/` | `.claude/skills/`, `.claude/agents/`, `.codex/skills/` | `python scripts/sync_skills.py` |

Nunca edite os espelhos. Para verificar drift:

```bash
python scripts/sync_skills.py --check
```

O subagent `update` cuida do fechamento mecânico quando uma skill o aciona: rebuild de derivados, quality gates, sync e commit/push. O subagent `lint-report` é diagnóstico read-only sob pedido direto.

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
