# Second Brain

Uma wiki pessoal centrada em **essays** — ensaios, white papers e estudos aprofundados em Português do Brasil, mantida por agentes de IA (Claude/Codex/etc.) seguindo as regras deste repositório.

Toda a lógica operacional vive em [`AGENTS.md`](./AGENTS.md).

## Estrutura

```
raw/                    inbox temporário — coloque aqui o que ainda não foi processado
wiki/
  essays/                centro da wiki: ensaios, white papers, estudos
  concepts/              páginas curtas de apoio (ideias, frameworks, teorias)
  entities/              páginas curtas de apoio (pessoas, organizações, ferramentas)
  sources/               arquivo permanente dos documentos originais, por tipo
    resumos/             resumo de uma página por fonte processada via /digest
    manifest.md          proveniência: uma entrada por fonte ingerida (append-only)
    map.md               mapa de todas as fontes por assunto
  synthesis/             comparações curtas (/query) e notas atômicas (/atom)
  handouts/              versões de uma página de essays, sob demanda
  book-chapters/         reservado para um projeto de livro futuro 
  index.md               catálogo mestre — apenas essays, por categoria
  log.md                 log cronológico append-only de toda operação
  status.md              snapshot do estado atual — ponte entre sessões
scripts/                 lint, stats, grafo de conexões, export (PDF/HTML)
plan/                    plano de longo prazo: estudo, essay futuro, revisão, tarefa
  plano.md               índice por tópico
output/                  tudo que sai da wiki: PDFs, HTMLs, handouts, snapshots de stats
.agents/skills/          skills (slash commands) que operam sobre a wiki
```

## Skills

| Skill      | Comando              | Uso                                                                                                       |
| ---------- | -------------------- | --------------------------------------------------------------------------------------------------------- |
| Essay      | `/essay`           | Criar um essay novo do zero, a partir de uma tese                                                         |
| Outline    | `/outline`         | Esqueleto do essay (título, capítulos, bullets) — obrigatório antes de`/essay`                      |
| Atom       | `/atom`            | Capturar/desenvolver uma nota atômica ou ideia em`wiki/synthesis/`; promover pra essay quando madura   |
| Expand     | `/expand`          | Adicionar/corrigir conteúdo substantivo de um essay existente                                            |
| Chapter    | `/chapter`         | Adicionar, mover, fundir ou dividir capítulo/seção                                                     |
| Proofread  | `/proofread`       | Revisão de português                                                                                    |
| Polish     | `/polish`          | Revisão de estilo de prosa                                                                               |
| Continuity | `/continuity`      | Auditoria de continuidade lógico-narrativa                                                               |
| Linkify    | `/linkify`         | Links externos: adicionar e checar                                                                        |
| Import     | `/import`          | Quando fonte já é um ensaio completo do autor, vira essay                                               |
| Digest     | `/digest`          | Fonte de terceiro . Torna-se resumo para posteriormente se tornar essay                                  |
| Absorb     | `/absorb`          | Enriquece páginas ou essays existentes com fonte já ingerida                                            |
| Sweep      | `/sweep`           | Varre e corrige essay específico ou todos os essays (orquestra as skills de iteração)                  |
| Organize   | `/organize`        | Saúde da base inteira: índice, log, mapa de sources, tags, links                                        |
| Gaps       | `/gaps`            | Cobertura conceitual: termos citados sem página, páginas citadas sem link, desbalanço temático        |
| Stats      | `/stats`           | Dashboard read-only de saúde da wiki                                                                     |
| Status     | `/status`          | Snapshot do estado atual — ponte entre uma sessão e outra                                               |
| Handout    | `/handout`         | Resumo de uma página de um essay                                                                         |
| PDF / HTML | `/pdf` / `/html` | Exportação                                                                                              |
| Query      | `/query`           | Pergunta sobre o que já está na wiki                                                                    |
| Plan       | `/plan`            | Orquestra`plan/plano.md` (5 seções), plano de longo prazo                                             |
| Study      | `/study`           | Sessão de estudo: busca fontes, faz perguntas socráticas, gera conexões                                |
| Scout      | `/scout`           | Pesquisa e sugere fontes candidatas a partir de um item do plano, de um source/ideia, ou de um tema livre |

A skill`conventions` é a referência central de estilo/formatação usada pelas outras skills. Vide`.agents/skills/conventions/SKILL.md`.

## Vocabulários controlados

- **Tags de essay**: ver `## Tags — Vocabulário Controlado` em `conventions`.
- **Tipos de source**: ver `## Tipos de Source — Vocabulário Controlado` em `AGENTS.md` — cada tipo determina a subpasta física em `wiki/sources/`.

Reuso antes de criar, nunca duas grafias para o mesmo tema/tipo.

## Requisitos

- Python 3 com `pyyaml`, para os scripts em `scripts/`.
- Pandoc + **LuaLaTeX** (não XeLaTeX) para exportação em PDF.

## Notas

- **Tudo o que é pessoal fica fora do controle de versão, por design.** `raw/`, `plan/`, `output/` e a `wiki/` inteira (essays, concepts, entities, sources, `manifest.md`, `map.md`, `index.md`, `log.md`, `status.md`) estão no `.gitignore` — só a estrutura de pastas é versionada (via `.gitkeep`), nunca o conteúdo. O que de fato é versionado no Git é a camada operacional: `AGENTS.md`, `README.md`, `.agents/skills/**` e `scripts/**`.
- Todo o conteúdo é em Português do Brasil.
