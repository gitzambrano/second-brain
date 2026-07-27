---
name: conventions
description: >
  Referência central de estilo e formatação da wiki: onde cada tipo de
  conteúdo vai (tabela canônica de pastas), frontmatter, byline,
  Sumário/Referências/Conexões, regra de links (exportabilidade PDF),
  estilo de prosa, nomenclatura, imagens, compatibilidade Obsidian,
  conversão de fontes e regra de contradição entre fontes. Não tem fluxo
  próprio — as outras skills (essay, expand, chapter, proofread, polish,
  continuity, linkify, import, digest, absorb, organize, sweep, pdf, html)
  leem este arquivo para saber o formato exato a produzir e em que pasta
  salvar. Consulte também quando o usuário perguntar "qual é a regra de
  X" ou "onde isso deveria ficar" sobre a wiki.
allowed-tools: Read
---

# Conventions

Este skill não executa nada — é a fonte única das regras de formatação e estilo. Toda outra skill que grava ou edita conteúdo (essay, expand, chapter, proofread, polish, continuity, linkify, import, digest, absorb, handout, organize, sweep, pdf, html) segue o que está aqui. Se uma regra de formatação mudar, muda só neste arquivo.

## Onde as coisas vão — tabela canônica

Toda skill que grava em disco decide onde salvar consultando esta tabela, não por analogia ou hábito. `/organize` e `/sweep` também a usam para auditar desconexões (arquivo na pasta errada, pasta canônica faltando, etc.).

| Pasta | Contém | Quem escreve | Quando |
| --- | --- | --- | --- |
| `wiki/essays/` | Ensaios/white papers completos, com tese sustentada do início ao fim | `/essay`, `/import` | A ideia já é (ou virou, via `/atom promote`) um argumento completo |
| `wiki/concepts/` | Definição/explicação curta de um conceito, sem tese própria | `/essay`, `/expand`, `/absorb`, `/digest`, `/chapter` | Um termo é citado mas ainda não tem página própria |
| `wiki/entities/` | Página curta sobre uma pessoa, obra, instituição específica e nomeada | mesmas skills que concepts | Uma entidade nomeada é citada mas ainda não tem página própria |
| `wiki/synthesis/` | Comparações curtas (`tipo: comparacao`) e notas atômicas (`tipo: nota-atomica`) | `/query` (comparações), `/atom` (notas atômicas) | Insight ou comparação que não é essay nem concept/entity |
| `wiki/sources/<tipo>/` | Cópia/referência do documento original, por tipo (ver vocabulário controlado em `AGENTS.md`) | `/import`, `/digest`, `/absorb` (via `/scout` como triagem anterior) | Toda fonte processada, sempre — mesmo se só embasou um claim pontual |
| `wiki/sources/resumos/` | Resumo de uma página por fonte processada | `/digest` | Toda vez que uma fonte é resumida (não é um source-type, é derivado) |
| `wiki/handouts/` | Versão de uma página de um essay **já existente** | `/handout` | Nunca conteúdo primário — sempre derivado, sob demanda |
| `wiki/book-chapters/` | Reservado para um projeto de livro futuro | — | Não usar ainda |
| `plan/plano.md` | Pendência de longo prazo (tarefa, fonte a ingerir, revisão, estudo, essay futuro) | `/plan` | Nunca conteúdo de wiki — só a intenção de trabalhar algo depois |
| `wiki/status.md` | Snapshot do estado da sessão atual | `/status` | Ponte entre sessões, não confundir com o plano de longo prazo |

Regra geral: se o conteúdo tem tese própria sustentada → `essays/`. Se é definição/explicação de um termo ou entidade sem tese própria → `concepts/`/`entities/`. Se é insight novo sem lar ainda, ou comparação do que já existe → `synthesis/`. Se é material bruto de terceiros → `sources/`. Tudo o mais específico (handouts, book-chapters, plan) tem função única, listada acima — não miscelânea.

## Frontmatter

Toda página da wiki (essay, concept, entity) tem frontmatter YAML completo:

```yaml
---
tags: [tag1, tag2]
sources: [source-filename-1.md, source-filename-2.md]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

## Byline do essay

Logo após o `# Título`, com uma linha vazia entre o título e a byline:

```
# Título do Essay

> Tipo · Categoria Temática
> Gustavo Zambrano · Mês de Ano
```

- **Tipo**: `Ensaio`, `White Paper`, `Brainstorm`, `Estudo` ou `Análise`.
- **Categoria**: área temática (ex: `Filosofia da Ciência & Biologia`, `Dinâmica de Aeronaves`).
- **Mês de Ano**: por extenso (ex: `Maio de 2026`).
- **Nunca** `[[wikilinks]]` na byline — ela é exportada para PDF como texto puro.
- **Nunca** dois-pontos (`:`) na byline — Obsidian interpreta como separador de bloco.

## Estrutura obrigatória do essay

1. **Sem resumo executivo interno.** O essay abre com a byline e vai direto ao `## Sumário`; a primeira seção `##` do corpo já é a introdução, situando a tese. Um resumo condensado é um artefato à parte — ver skill `/handout`, nunca embutido no essay.
2. **`## Sumário` obrigatório**, logo após a byline, com links para todas as seções `##` (exceto Referências e Conexões):

   ```
   ## Sumário

   - [Título da Seção](#título-da-seção)
   - [Outra Seção](#outra-seção)

   ---
   ```

3. **Links externos** para todo conceito, entidade ou termo técnico mencionado inline, ao menos na primeira ocorrência.
4. **`## Referências` obrigatória**: bibliografia com links externos quando disponíveis. Heading exatamente `## Referências` (nunca H1, nunca "Referências Bibliográficas", nunca numerado).
5. **`## Conexões` obrigatória** no final: `[[wikilinks]]` bidirecionais para conceitos, entidades e essays relacionados. Não é exportada para PDF.

## Regra de links — exportabilidade para PDF

- **Corpo do essay (inline)**: apenas links externos `[texto](url)`. Nunca `[[wikilinks]]` inline.
- **`## Conexões`**: apenas `[[wikilinks]]`. Metadata interna, não exportada.
- **`## Referências`**: links externos bibliográficos, exportados.
- Motivo: essays são documentos autocontidos, compartilháveis como PDF sem perda de informação.
- Mínimo de referência prática: um essay bem linkado tem pelo menos ~10 links externos no corpo — abaixo disso é sinal de que faltam links, não que o mínimo é opcional.

## Dois tipos de essay

- **Originais** (de `raw/`, via `/import`): texto integral preservado, traduzido para PT-BR se necessário. Só podem receber adição de links externos, formatação, `## Referências` e `## Conexões` — nunca alteração do texto original. Podem ser expandidos depois, sob pedido explícito (a regra de "texto intacto" vale para o momento da ingestão, não bloqueia expansão futura).
- **Criados** (pela wiki, via `/essay`): livremente modificáveis, expandidos, enriquecidos.

## Estilo de prosa

Vale para todo trecho **escrito ou reescrito pela wiki**. Não se aplica retroativamente a texto original preservado de `raw/`, a menos que o usuário peça `/polish` ou `/proofread` explicitamente.

1. **Evitar bullets no corpo do texto.** Prosa argumentativa em parágrafos com transições explícitas. Bullets só em `## Sumário`, `## Referências`, e tabelas quando genuinamente mais claras que prosa (dados numéricos/técnicos). Conteúdo argumentativo em bullets deve virar parágrafo corrido.
2. **Travessões (—) extremamente raros**: no máximo 1 a 2 no essay inteiro, não por parágrafo. Prefira vírgula, dois-pontos, parênteses, ou reestruture a frase. Ao terminar um trecho, conte os travessões do essay inteiro; acima de 2, reescreva os excedentes. Não contam: o `·` da byline, e o `—` usado como separador de display text em wikilinks do índice (ver abaixo).

## Formato do índice (`wiki/index.md`)

Apenas essays, por categoria temática:

```
## Filosofia & Consciência
- [[filename|Título do Essay]] — resumo de uma linha
```

- Formato `[[filename|Display Title]]`.
- **Nunca** dois-pontos no display text — Obsidian quebra o link. Substitua `:` por `—`.
- Correto: `[[filename|Título — Subtítulo]]`. Errado: `[[filename|Título: Subtítulo]]`.
- Título do arquivo: `# Índice`.

## Formato de páginas em `wiki/synthesis/`

Dois tipos de conteúdo, na mesma pasta, distinguidos pelo campo `tipo:` do frontmatter — nunca misture os dois formatos no mesmo arquivo:

**`tipo: comparacao`** — comparação ou análise cruzada curta, gerada por `/query` quando uma resposta vale a pena guardar. Frontmatter simples (`tags`, `sources`, `created`, `updated`, `tipo: comparacao`), corpo em prosa curta, sem `## Sumário`/`## Referências` formais.

**`tipo: nota-atomica`** — fragmento denso de uma ideia só, gerado por `/atom`. Formato completo em `.agents/skills/atom/SKILL.md`; resumo: frontmatter com `tipo: nota-atomica` e `maturidade: solta | germinando | madura`, corpo curto (uma ideia, não um esboço de capítulo), `## Conexões` com `[[wikilinks]]` para o que a ancora na wiki.

Ambos ficam fora de `wiki/index.md` (que é só essays) e não entram na contagem de "essays" de `/stats` — aparecem na seção própria "Synthesis".

## Formato do log (`wiki/log.md`)

```
## [YYYY-MM-DD] operação | Título
Descrição breve do que foi feito.
```

Append-only — nunca editar entradas existentes.

## Nomenclatura de páginas

- Arquivos: kebab-case + `.md`. Títulos dentro do arquivo: Title Case.
- Essays: `wiki/essays/titulo-do-essay.md` → `# Título Do Essay`.
- Concepts: `wiki/concepts/nome-do-conceito.md` → `# Nome Do Conceito`.
- Entities: `wiki/entities/nome-da-entidade.md` → `# Nome Da Entidade`.
- Sources: nomes originais preservados, arquivados em `wiki/sources/<subpasta-do-tipo>/` — não são páginas wiki.
- `[[wikilinks]]` usam o título da página (Title Case), nunca o nome do arquivo: `[[Nome Da Entidade]]`, não `[[nome-da-entidade]]`.
- Para transformar título em nome de arquivo: minúsculas, espaços viram hífens, remova caracteres especiais.

## Tratamento de imagens

1. Imagens e figuras vão em `wiki/assets/`, referenciadas como `../assets/nome-da-imagem.png`.
2. Ao converter PDF/DOCX, extraia figuras embutidas para `wiki/assets/` e linke no essay.
3. Se uma imagem da fonte carrega informação importante (diagrama, gráfico, dado), descreva o conteúdo em texto na página — a informação não pode existir só na imagem.

## Compatibilidade com Obsidian

1. `[[wikilinks]]` só em `## Conexões` e em páginas de concept/entity/source — nunca inline no corpo.
2. Nunca dois-pontos no display text de wikilinks (quebra o link); use `—`.
3. Wikilinks em `## Conexões`: `[[Título da Página]]` — Obsidian resolve por "shortest path".
4. Imagens: caminho relativo `../assets/filename.png`.

## Conversão de fontes (HTML/PDF/DOCX → Markdown)

1. **Blockquotes (`>`)**: só para conteúdo que era caixa especial no original (callout, warning-box, pullquote). Texto corrido normal nunca vira blockquote.
2. **Tabelas HTML** → markdown tables (`| Col1 | Col2 |`), nunca linhas soltas.
3. **Índices/TOC do HTML original**: remover — serão substituídos pelo `## Sumário` gerado.
4. **Labels de capítulo** (`01 — Introdução`): incorporar como heading markdown ou remover se já há heading equivalente.
5. **Símbolos residuais**: remover diamantes (◆), replacement chars, zero-width spaces, `&nbsp;`, `&amp;`, etc.
6. **Verificar fidelidade**: sempre comparar o `.md` gerado contra o original.

## Exportação para PDF (`export_essay.py`, Pandoc + LuaLaTeX)

- **LuaLaTeX, não XeLaTeX** — o dvipdfmx do MiKTeX não gera anotações de link.
- `## Conexões` é removida do PDF; `## Sumário` e `## Referências` são preservadas.
- Frontmatter YAML + byline viram bloco de título/subtítulo/autor em LaTeX.
- Nunca usar `--number-sections` (essays já têm numeração manual nos headings).
- Imagens com caminho relativo são resolvidas para absoluto.
- Hyperlinks via variáveis Pandoc (`colorlinks`, `urlcolor`, `linkcolor`) — não via `\usepackage{hyperref}` manual.
- Caracteres LaTeX especiais no subtítulo (`&`, `#`, `%`, `_`) são escapados.
- Wikilinks residuais `[[Target|Display]]` viram texto puro.
- Handouts exportam pelo mesmo pipeline via `--handout`.

## Regra de contradição entre fontes

Se uma informação nova (de uma fonte ingerida, ou de algo que o usuário disse) contradiz o que já está escrito numa página da wiki: **não escolha um lado sozinho e não tire a média das duas.** Pare, aponte a contradição ao Usuário citando as duas fontes (a existente e a nova, com localização exata), e só edite a página depois que ele disser qual prevalece ou como as duas coexistem. Isso vale para `/absorb`, `/digest`, `/expand`, `/continuity` e qualquer skill que compare conteúdo novo contra o que já está na wiki.

## Decisões fechadas

Decisões de estilo já resolvidas — não reabra sem evidência nova (um caso real que a regra não cobre, não uma preferência estética isolada).

- [Nenhuma decisão fechada registrada ainda. Adicione aqui conforme surgirem — formato: `- [decisão] (YYYY-MM-DD) — [motivo/link]`.]
