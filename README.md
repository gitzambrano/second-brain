# Second Brain

Uma wiki pessoal centrada em **essays** — ensaios, white papers e estudos aprofundados em Português do Brasil, mantida por agentes de IA (Claude Code, Codex, Antigravity, etc.) seguindo as regras deste repositório.

Toda a lógica operacional (papel do agente, regras gerais, formato de cada peça da wiki) vive em [`AGENTS.md`](./AGENTS.md). Este README é a porta de entrada para humanos: estrutura de pastas, o que cada skill faz, e os vocabulários controlados usados em toda a base.

## Estrutura de pastas

```
raw/                        inbox temporário — coloque aqui o que ainda não foi processado
                             (ensaios, PDFs, livros, artigos, anotações soltas)

wiki/                        espaço de trabalho do LLM — tudo que é conteúdo de fato

  essays/                    o centro da wiki: ensaios, white papers, estudos aprofundados
  concepts/                  páginas curtas de apoio — ideias, frameworks, teorias
  entities/                  páginas curtas de apoio — pessoas, organizações, ferramentas
  insights/                  pasta atomizadora de ideias 
  handouts/                  resumo de uma página de um essay específico, sob demanda (/handout)
  assets/                    imagens e figuras referenciadas pelos essays/resumos
  book-chapters/             reservada para um projeto de livro futuro — não usar ainda
  sources/                   arquivo permanente dos documentos originais, por tipo
    ensaio-importado/        ensaio/white paper completo do autor, importado via /import
    web-clipping/            recorte de página web: post, thread, matéria online
    artigo-academico/        paper com peer review, DOI, ou de periódico/conferência
    livro/                   livro ou capítulo, inteiro ou em trecho relevante
    documentacao-tecnica/    manuais, specs, normas, documentação de ferramenta/API
    transcricao/             palestra, podcast, entrevista, aula
    ideias/                  texto curto e não estruturado, ainda sem forma de ensaio/artigo
    outro/                   só quando nenhuma categoria acima cobre o caso
    resumos/                 resumo de uma página por fonte processada via /digest
    manifest.md              proveniência: uma entrada por fonte ingerida (append-only)
    map.md                   mapa de todas as fontes por assunto
  index.md                   catálogo mestre gerado — apenas essays, lista plana com summary e tags
  index.json                 cache de metadados (título, tags, summary, status/maturidade) 
  references.md              bibliografia consolidada gerada, agrupada por tipo de fonte
  references.json            mesma bibliografia em JSON (url, citação AIAA, quem cita) 
  log.md                     log cronológico, append-only, de toda operação realizada na wiki
  status.md                  snapshot do estado atual — ponte entre uma sessão e a próxima

plan/                        plano de longo prazo do Usuário (não confundir com wiki/status.md)
  plano.md                   tarefas, fontes para ingerir, revisões, estudos, essays futuros
  drafts/                    esqueletos de essay 

scripts/                     lint, stats, grafo de conexões, export (PDF/HTML), busca e índice
  check_wiki.py              lint unificado: formatação de essay (byline, Sumário/Referências/
                              Conexões, LaTeX, aspas, símbolos residuais...) + estrutura de corpus
                              (wikilinks mortos, órfãos, índice, manifesto, plano, insights).
                              Usado por /organize. Escopo: --all (padrão) ou <slug>/--file <slug>
  fix_lint.py                único fixer mecânico: aplica tudo que for inequívoco sem perguntar,
                              inclusive a migração de ## Referências para o padrão AIAA. Mesma
                              CLI de check_wiki.py (--all / <slug> / --file <slug>)
  stats.py                   dashboard read-only (usado por /stats)
  check_gaps.py              heurística de cobertura conceitual (usado por /gaps e /connect)
  build_graph.py             gera output/graph/graph.html (interativo) e graph.md (Mermaid)
  find_text.py               busca com trecho (grep -n com contexto) escopada à wiki
  build_index.py             gera wiki/index.md e wiki/index.json a partir do frontmatter
  build_references.py        gera wiki/references.md e .json das ## Referências dos essays
  check_references.py        valida ## Referências no padrão AIAA, somente-leitura (usado por /linkify e /organize)
  check_dedupe.py            candidatos a quase-duplicata: títulos, tags, referências
  check_title.py             checagem exata/fuzzy de títulos
  sync_qmd.bat               reindexa a wiki no qmd (collection "secondbrain") — dois cliques, ou rode no terminal
  find_backlinks.py          lookup reverso de [[wikilinks]] e detecção de órfãos 
  export_essay_pdf.py        export para PDF via Pandoc + LuaLaTeX (usado por /pdf)
  export_essay_html.py       export para HTML standalone via Pandoc (usado por /html)
  essay_template.html        template do HTML exportado
  sync_skills.py             espelha .agents/skills/ em .claude/skills/ (hook SessionStart)
  console_encoding.py        força UTF-8 na saída dos scripts (console Windows é cp1252)

output/                      tudo que sai da wiki para compartilhamento externo
  pdf/                       essays/handouts exportados em PDF (/pdf)
  html/                      essays/handouts exportados em HTML standalone (/html)
  handouts/                  cópia do handout (.md, e opcionalmente .pdf/.html) pronta pra enviar
  stats/                     snapshots salvos de /stats --save (stats-YYYY-MM-DD.md)
  graph/                     gerado sob demanda por /organize ou /stats — graph.html, graph.md

.agents/skills/               skills (slash commands) que operam sobre a wiki — ver seção abaixo
.claude/skills/               espelho gerado do anterior, para o Claude Code — nunca editar
.claude/settings.json         hook SessionStart que mantém o espelho sincronizado
AGENTS.md                     regras operacionais — fonte única para todos os agentes
CLAUDE.md                     só um `@AGENTS.md`; existe porque o Claude Code procura por ele
```

### Um conteúdo, dois caminhos

Cada agente procura a configuração num lugar diferente, então há dois pares de caminhos — e, em cada par, só um lado se edita:

| Fonte única (edite aqui) | Espelho gerado (nunca edite) | Mecanismo |
| ------------------------- | ---------------------------- | ------------------------------------------------------------------ |
| `AGENTS.md` | `CLAUDE.md` | `CLAUDE.md` contém só `@AGENTS.md`; o import resolve sozinho |
| `.agents/skills/` | `.claude/skills/` | `scripts/sync_skills.py`, via hook `SessionStart` |

O espelho de skills é regenerado no início de cada sessão do Claude Code, então qualquer edição feita direto em `.claude/skills/` é perdida. Para ver se os dois lados divergiram, sem escrever nada:

```bash
python scripts/sync_skills.py --check
```

### Ritual de fechamento

Dois artefatos da wiki são derivados e não se regeneram sozinhos: o índice do `qmd` (busca semântica) e o espelho `.claude/skills/`. As skills de fechamento — `/organize`, `/sweep`, `/stats` e `/status update` — cuidam dos dois no fim do trabalho:

| Artefato            | Comando                           | Comportamento                                                       |
| ------------------- | --------------------------------- | ------------------------------------------------------------------- |
| Índice do qmd      | `qmd update && qmd embed`       | Sempre**oferecido**, nunca rodado sozinho (pode ser demorado) |
| `.claude/skills/` | `python scripts/sync_skills.py` | Checado com`--check`; o sync é mecânico e aplicado direto       |

`/stats` é a exceção: sendo read-only por definição, ele só reporta o drift do espelho, sem corrigir.

## Skills

As skills estão agrupadas pela mesma lógica de `AGENTS.md`: da ideação de uma ideia solta até a exportação de um essay pronto. Cada uma é um arquivo `.agents/skills/<nome>/SKILL.md` — a fonte de verdade é sempre o arquivo, isto aqui é um resumo para orientação humana.

### Ideação (antes de um essay existir)

- **Insight** · `/insight` — captura, desenvolve e promove insights em `wiki/insights/`: sementes de ideia, sínteses/pontes entre fontes, observações/intuições e mini-argumentos, fragmentos densos de uma ideia só que ainda não sabem a que essay pertencem. `add` registra na hora, sem exigir conversa, e só depois oferece (sem insistir) expandir/conectar. `develop` já é conversa e iteração com o Usuário para polir ou expandir a nota. Tem três estados de maturidade (`solta` → `germinando` → `madura`) e comandos `add`, `develop`, `list`, `promote`. Existe para não forçar toda ideia nova a nascer já como capítulo ou concept.

### Criação

- **Outline** · `/outline` — gera o esqueleto de um essay futuro (título, tipo, capítulos com papel argumentativo e bullets), salvo em `plan/drafts/<slug>.md`. **Passo obrigatório antes de `/essay`** para todo essay novo, exceto quando a fonte já é `/import`. Permite quantas rodadas de revisão o Usuário quiser antes de qualquer prosa ser escrita.
- **Essay** · `/essay` — escreve um essay/white paper novo do zero a partir de um esboço já aprovado por `/outline`. Claude atua como coautor: pesquisa, estrutura e escreve seguindo as convenções de prosa, links e formatação da wiki. Nunca escreve sem esboço aprovado (única exceção: `/import`).

### Iteração em essay existente

- **Expand** · `/expand` — adiciona ou corrige conteúdo substantivo: teses, conceitos, exemplos, correções factuais/conceituais. Pergunta ao Usuário quando o pedido é vago demais para decidir a direção sozinho.
- **Chapter** · `/chapter` — trabalha a estrutura do essay: adicionar, mover, fundir ou dividir capítulo/seção, ou criar página de concept/entity ligada a ele. Diferente de `/expand`, que lida com o conteúdo dentro de uma seção já existente.
- **Proofread** · `/proofread` — revisão de português: gramática, ortografia, concordância, pontuação, consistência terminológica. Não toca em conteúdo, argumento ou tom.
- **Polish** · `/polish` — revisão de estilo de prosa: ritmo, elegância, remoção de bullets do corpo argumentativo, contagem de travessões (máximo 2 por essay). Não altera o que é dito, só como é dito.
- **Continuity** · `/continuity` — auditoria de continuidade lógica e narrativa do início ao fim: conceitos usados antes de definidos, saltos abruptos entre seções, tese sustentada, conclusão que fecha o argumento. Só diagnostica e reporta — nunca corrige silenciosamente.
- **Linkify** · `/linkify` — garante que todo conceito/termo técnico/pensador citado no corpo tem link externo na primeira ocorrência (mínimo 10 por essay), e audita se os links já existentes ainda apontam para algo válido.
- **Review** · `/review` — peer review no estilo acadêmico: validade argumentativa e lógica, rigor físico/matemático quando aplicável, profundidade, ausência de citações, gaps conceituais, e sugestões ativas de enriquecimento (experimentos mentais, exemplos, fontes candidatas, conexões internas). Gera um plano de modificação e só edita após aprovação explícita.

### Fontes (três formas de processar algo em `raw/`)

- **Import** · `/import` — quando a fonte já é um ensaio/white paper completo do próprio Usuário: vira essay preservando o texto intacto. Claude é arquivista aqui, não coautor — não passa por `/outline`.
- **Digest** · `/digest` — quando a fonte é de terceiros (paper, livro, clipping, transcrição): lê, resume numa página em `wiki/sources/resumos/`, extrai figuras embutidas para `wiki/assets/` se houver, e arquiva o original. **Nunca gera um essay.**
- **Absorb** · `/absorb` — sob pedido explícito, incorpora o conteúdo de uma fonte já processada (importada ou resumida) às páginas existentes da wiki — essays, concepts, entities. Uma única fonte pode tocar 10-15 páginas.

### Planejamento

- **Plan** · `/plan` — gerencia `plan/plano.md`, o plano de longo prazo (5 seções fixas: Tarefas, Fontes para Ingerir, Revisões, Estudos, Essays Futuros). Comandos `add`, `work`, `done`, `list`. `/plan work` retoma um item e encaminha para a skill certa — nunca produz conteúdo sozinho.
- **Study** · `/study` — conduz uma sessão de estudo de verdade: busca e lê fontes de verdade (não só lista), faz perguntas socráticas para o Usuário desenvolver a própria posição, e gera conexões ativas com o que já existe na wiki. Fecha perguntando o que fazer com o material estudado (`/insight`, `/digest`, `/essay`, ou deixar no plano).
- **Scout** · `/scout` — pesquisa a web e devolve uma lista curta e curada de fontes candidatas (3 a 8, com justificativa), a partir de um item do plano, de um source/ideia existente, ou de um tema livre. Nunca baixa nem ingere sozinho — só propõe.

### Manutenção

- **Sweep** · `/sweep` — orquestra a bateria completa de revisão num essay ou no corpus inteiro: `/organize` (passada mecânica, no escopo correspondente) → `/continuity` → `/proofread` → `/polish` → `/linkify`, com relatório consolidado. Aceita `/sweep` (corpus) ou `/sweep <slug>` (essay único). Fecha regenerando índice e bibliografia, passando pelo ritual de fechamento acima, e oferecendo `/connect` como próximo passo.
- **Organize** · `/organize` — organiza a base na camada de metadados e formatação mecânica de essay: índice, log, manifesto de sources, tags, plano, insights, estrutura de pastas, formatação (estrutura obrigatória, byline, LaTeX, aspas, espaçamento, compatibilidade Obsidian — fixes automáticos via `fix_lint.py`), e gera o grafo de conexões. Aceita `/organize` (corpus inteiro) ou `/organize <slug>` (só formatação/referências/wikilinks daquele essay, pulando órfãos/índice/manifesto/plano/grafo com aviso). A skill mais importante para comunicar com clareza — nunca cola o relatório bruto do lint. Não toca em prosa nem argumento. No modo corpus inteiro, se o grafo mostrar clusters isolados, ofereça `/connect`.
- **Gaps** · `/gaps` — audita cobertura conceitual: termo citado repetidamente na prosa mas sem página própria, página existente sem link em `## Conexões`, e desbalanço entre tags. Prospectivo e opt-in — nunca cria página nem insere link sozinho. Ao final, ofereça `/connect` para o que fica fora do escopo (concept↔concept, entity↔entity, insight, links quebrados).
- **Connect** · `/connect` — expande e repara `## Conexões` entre essays, concepts, entities e insights, tratando os quatro tipos como peers. Corrige link quebrado/mal formatado, aplica direto conexão de alta confiança, e propõe (com aprovação) conexão de média confiança e página nova. Aceita `/connect` (corpus) ou `/connect <slug/pasta/tema>`. Não roda automaticamente dentro de `/organize`/`/sweep`/`/gaps`, mas é o próximo passo natural depois deles.
- **Stats** · `/stats` — dashboard read-only de saúde da wiki: essays por tag/tipo, órfãos, sources sem manifesto, itens do plano, notas atômicas por maturidade. Não corrige nada, só relata; rápido o bastante para rodar com frequência.
- **Status** · `/status` — mantém `wiki/status.md`, o snapshot que liga uma sessão à próxima: foco atual, perguntas em aberto, decisões recentes, pendências (raw/, plano, sources não verificados). `/status` mostra; `/status update` recalcula e reescreve.

### Saída

- **Handout** · `/handout` — gera `wiki/handouts/<slug>.md`: uma versão de uma página do essay (linha de tese + 3 a 5 conclusões em prosa), para o Usuário mandar rápido a alguém que não vai ler o white paper inteiro. Nunca automático — só sob pedido explícito.
- **PDF** · `/pdf` — exporta um ou todos os essays (ou um handout, via `--handout`) para PDF, usando `scripts/export_essay_pdf.py` (Pandoc + **LuaLaTeX**).
- **HTML** · `/html` — exporta um ou todos os essays (ou um handout) para um `.html` standalone, responsivo, com CSS/imagens embutidos, usando `scripts/export_essay_html.py`.

### Consulta

- **Query** · `/query` — responde perguntas usando a wiki como base de conhecimento: começa pelo índice, aprofunda via `[[wikilinks]]` de `## Conexões`, cita sempre o essay de origem. Se a resposta gerar uma síntese nova, oferece salvá-la como essay (`/essay`) ou nota curta (`/insight` ou `wiki/insights/`).

### Referência de formatação (sem comando próprio)

- **Conventions** — não é uma skill acionável, é a referência central de estilo e formatação que todas as outras leem: tabela canônica de pastas, tipos de source, frontmatter, byline, regra de links, estilo de prosa, tratamento de imagens, compatibilidade Obsidian, conversão de fontes, regra de contradição entre fontes. Ver `.agents/skills/conventions/SKILL.md`.

## Vocabulários controlados

Todos vivem em `conventions/SKILL.md` — a fonte única de verdade, para nunca haver duas grafias do mesmo tema/tipo. Reuso sempre antes de criar um item novo.

### Tags

Campo `tags:` do frontmatter de essay/concept/entity/insight, e campo `Tags:` do manifesto de sources (`wiki/sources/manifest.md`) — **uma única fonte de tags para a wiki inteira**, não duas listas separadas.

Uma tag nova só entra quando um essay ou source genuinamente não se encaixa em nenhuma existente — `/organize` audita quase-duplicadas (acento, plural, sinônimo) nos dois campos e propõe consolidação.

A lista de tags em uso é sempre extraída de `tags_in_use` em `wiki/index.json` (gerado por `python scripts/build_index.py`), a fonte da verdade.

### Status de essay

Campo `status:` do frontmatter, só em `wiki/essays/` (nunca em concepts/entities): `draft` (recém-escrito por `/essay`) → `maduro` (revisado, mas ainda pode evoluir) → `finalizado` (fechado; skills de edição em lote pulam por padrão, mas rodam se o Usuário nomear o essay diretamente).

### Tipos de source

Campo `Tipo:` do manifesto (`wiki/sources/manifest.md`) — cada tipo determina a subpasta física em `wiki/sources/`:

| Tipo (manifesto)          | Subpasta                  | O que entra aqui                                                                      |
| ------------------------- | ------------------------- | ------------------------------------------------------------------------------------- |
| Ensaio Completo Importado | `ensaio-importado/`     | Ensaio/white paper pronto vindo de fora, que virou essay preservando o texto integral |
| Web Clipping              | `web-clipping/`         | Recorte de página web: post, thread, matéria online                                 |
| Artigo Acadêmico         | `artigo-academico/`     | Paper com peer review, DOI, ou publicado em periódico/conferência                   |
| Livro                     | `livro/`                | Livro ou capítulo, inteiro ou em trecho relevante                                    |
| Documentação Técnica   | `documentacao-tecnica/` | Manuais, specs, normas, documentação de ferramenta ou API                           |
| Transcrição             | `transcricao/`          | Palestra, podcast, entrevista, aula                                                   |
| Ideias                    | `ideias/`               | Texto curto e não estruturado, ainda não é ensaio, artigo ou clipping formal       |
| Outro                     | `outro/`                | Só quando genuinamente nenhuma categoria acima cobre o caso                          |

Toda fonte processada também gera uma entrada em `wiki/sources/manifest.md` (proveniência, append-only, incluindo `Tags:` — mesmo vocabulário controlado da seção acima) e uma linha em `wiki/sources/map.md` (mapa por assunto); ambos são auditados por `/organize`.

### Insights

`wiki/insights/` guarda um único formato (ver skill `/insight`): fragmentos densos de uma ideia só — sementes, sínteses/pontes, observações/intuições, mini-argumentos — com `maturidade:` no frontmatter (`solta` → `germinando` → `madura`). Fica fora de `wiki/index.md`.

## Requisitos

- Python 3 com `pyyaml`, para os scripts em `scripts/`.
- Pandoc + **LuaLaTeX** (não XeLaTeX — o `dvipdfmx` do MiKTeX não gera anotações de link) para exportação em PDF.
- `qmd` (opcional, mas recomendado) para busca semântica sobre a wiki — ver `## Ferramentas` em `AGENTS.md`. Sem ele, tudo continua funcionando via `scripts/find_text.py` (sem dependência externa). `scripts/sync_qmd.bat` reindexa com um clique.

## Notas

- **Tudo o que é pessoal fica fora do controle de versão, por design.** `raw/`, `plan/` e a `wiki/` inteira (essays, concepts, entities, insights, handouts, assets, sources, `manifest.md`, `map.md`, `index.md`, `references.md`, `log.md`, `status.md`) estão no `.gitignore` — só a estrutura de pastas é versionada (via `.gitkeep`), nunca o conteúdo. `output/` também fica fora, é sempre derivado. O que de fato é versionado no Git é a camada operacional: `AGENTS.md`, `CLAUDE.md`, `README.md`, `.agents/skills/**`, `scripts/**` e `.claude/settings.json`. O espelho `.claude/skills/**` fica de fora, por ser derivado.
- Todo o conteúdo é em Português do Brasil.
