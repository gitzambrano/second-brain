# Second Brain

Uma wiki pessoal centrada em **essays** — ensaios, white papers e estudos aprofundados em Português do Brasil, mantida por agentes de IA (Claude/Codex/etc.) seguindo as regras deste repositório.

Toda a lógica operacional vive em [`AGENTS.md`](./AGENTS.md). Este README é só o mapa de superfície.

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
  synthesis/             comparações e análises cruzadas curtas
  handouts/              versões de uma página de essays, sob demanda
  index.md               catálogo mestre — apenas essays, por categoria
  log.md                 log cronológico append-only de toda operação
  status.md              snapshot do estado atual — ponte entre sessões
scripts/                 lint, stats, export (PDF/HTML)
plan/                    to-do de estudos e planos de essays futuros
  plano-estudos.md       índice por tópico do que falta estudar/escrever
output/                  tudo que sai da wiki: PDFs, HTMLs, handouts, snapshots de stats
.agents/skills/          skills (slash commands) que operam sobre a wiki
```

## Skills

| Skill      | Comando              | Uso                                                                                                       |
| ---------- | -------------------- | --------------------------------------------------------------------------------------------------------- |
| Essay      | `/essay`           | Criar um essay novo do zero, a partir de uma tese                                                         |
| Expand     | `/expand`          | Adicionar/corrigir conteúdo substantivo de um essay existente                                            |
| Chapter    | `/chapter`         | Adicionar, mover, fundir ou dividir capítulo/seção                                                     |
| Proofread  | `/proofread`       | Revisão de português                                                                                    |
| Polish     | `/polish`          | Revisão de estilo de prosa                                                                               |
| Continuity | `/continuity`      | Auditoria de continuidade lógica/narrativa                                                               |
| Linkify    | `/linkify`         | Links externos: adicionar e checar                                                                        |
| Import     | `/import`          | Fonte já é um ensaio completo do autor → vira essay                                                    |
| Digest     | `/digest`          | Fonte de terceiro → resumo, nunca essay                                                                  |
| Absorb     | `/absorb`          | Enriquece páginas existentes com fonte já ingerida                                                      |
| Sweep      | `/sweep`           | Varre e corrige todos os essays (orquestra as skills de iteração)                                       |
| Organize   | `/organize`        | Saúde da base inteira: índice, log, mapa de sources, tags, links                                        |
| Stats      | `/stats`           | Dashboard read-only de saúde da wiki                                                                     |
| Status     | `/status`          | Snapshot do estado atual — ponte entre uma sessão e outra                                               |
| Handout    | `/handout`         | Resumo de uma página de um essay                                                                         |
| PDF / HTML | `/pdf` / `/html` | Exportação                                                                                              |
| Query      | `/query`           | Pergunta sobre o que já está na wiki                                                                    |
| Study      | `/study`           | Mantém`plan/plano-estudos.md`: ingere ideias de estudo/essay futuro, marca como estudado               |
| Scout      | `/scout`           | Pesquisa e sugere fontes candidatas a partir de um item do plano, de um source/ideia, ou de um tema livre |

A `conventions` (sem slash command próprio) é a referência central de estilo/formatação usada pelas outras skills — ver `.agents/skills/conventions/SKILL.md`.

## Vocabulários controlados

- **Tags de essay**: ver `## Tags — Vocabulário Controlado` em `AGENTS.md`.
- **Tipos de source**: ver `## Tipos de Source — Vocabulário Controlado` em `AGENTS.md` — cada tipo determina a subpasta física em `wiki/sources/`.

Ambos são fechados por design: reuse antes de criar, nunca duas grafias para o mesmo tema/tipo.

## Requisitos

- Python 3 com `pyyaml`, para os scripts em `scripts/`.
- Pandoc + **LuaLaTeX** (não XeLaTeX) para exportação em PDF.

## Notas

- `wiki/sources/` guarda os documentos originais e está fora do controle de versão (`.gitignore`) — o que é versionado é a wiki em si (`.md`), não os binários/PDFs/HTMLs originais.
- Todo o conteúdo é em Português do Brasil.
