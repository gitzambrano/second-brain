---
name: conventions
description: >
  Referência central de estilo e formatação da wiki: onde cada tipo de
  conteúdo vai (tabela canônica de pastas), tipos de source e sua
  subpasta física, frontmatter, byline, Sumário/Referências/Conexões,
  regra de links (exportabilidade PDF), estilo de prosa, nomenclatura,
  imagens, compatibilidade Obsidian, conversão de fontes e regra de
  contradição entre fontes. Não tem fluxo
  próprio — as outras skills (essay, expand, chapter, proofread, polish,
  continuity, linkify, import, digest, absorb, handout, organize, sweep,
  pdf, html) leem este arquivo para saber o formato exato a produzir e em que pasta
  salvar. Consulte também quando o Usuário perguntar "qual é a regra de
  X" ou "onde isso deveria ficar" sobre a wiki.
allowed-tools: Read
---

# Conventions

Fonte única das regras de formatação e estilo — não executa nada.

Toda skill que grava ou edita conteúdo segue o que está aqui. Mudou uma regra, muda só neste arquivo.

## Onde as coisas vão — tabela canônica

Toda skill que grava em disco decide onde salvar consultando esta tabela, não por analogia. `/organize` e `/sweep` também a usam para auditar desconexões.

| Pasta | Contém | Quem escreve | Quando |
| --- | --- | --- | --- |
| `wiki/essays/` | Ensaios/white papers completos, tese sustentada do início ao fim | `/essay`, `/import` | A ideia já é (ou virou, via `/atom promote`) um argumento completo |
| `wiki/concepts/` | Definição/explicação curta de um conceito, sem tese própria | `/essay`, `/expand`, `/absorb`, `/digest`, `/chapter` | Um termo é citado mas ainda não tem página própria |
| `wiki/entities/` | Página curta sobre pessoa/obra/instituição nomeada | mesmas skills que concepts | Uma entidade nomeada é citada mas ainda não tem página própria |
| `wiki/synthesis/` | Comparações curtas (`tipo: comparacao`) e notas atômicas (`tipo: nota-atomica`) | `/query` (comparações), `/atom` (notas atômicas) | Insight ou comparação que não é essay nem concept/entity |
| `wiki/sources/<tipo>/` | Cópia/referência do documento original, por tipo (vocabulário em `AGENTS.md`) | `/import`, `/digest`, `/absorb` (via `/scout` como triagem) | Toda fonte processada, sempre |
| `wiki/sources/resumos/` | Resumo de uma página por fonte processada | `/digest` | Toda vez que uma fonte é resumida |
| `wiki/handouts/` | Versão de uma página de um essay **já existente** | `/handout` | Sempre derivado, sob demanda |
| `wiki/assets/` | Imagens/figuras referenciadas pelos essays | `/import`, `/digest`, `/absorb` | Fonte processada tem figura embutida (ver `## Tratamento de imagens`) |
| `wiki/book-chapters/` | Reservado para projeto de livro futuro | — | Não usar ainda |
| `plan/plano.md` | Pendência de longo prazo | `/plan` | Nunca conteúdo de wiki — só intenção de trabalhar algo depois |
| `wiki/status.md` | Snapshot do estado da sessão atual | `/status` | Ponte entre sessões, não confundir com o plano |

Regra geral: tese própria sustentada → `essays/`. Definição/explicação sem tese própria → `concepts/`/`entities/`. Insight novo sem lar, ou comparação → `synthesis/`. Material bruto de terceiros → `sources/`.

O resto (handouts, book-chapters, plan) tem função única, listada acima.

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

Essays têm um campo a mais, `status: draft | maduro | finalizado` — ver `## Status de essay` abaixo.

## Tags — Vocabulário Controlado

Campo `tags:` do frontmatter, vocabulário fechado — evita tags quase-duplicadas (`Filosofia`, `filosofia`, `Filosofia da Mente`) que fragmentam a navegação.

**Tags atuais** (fonte da verdade — adicione uma nova aqui só quando um essay não se encaixa em nenhuma existente):

Vida Pessoal · Produtividade · Finanças · Saúde · Aprendizado · Projetos · Diário · Filosofia · Aerodinâmica · Dinâmica de Vôo · Engenharia · Xadrez

1. **Reuse antes de criar** — busque em `wiki/index.md` e nos frontmatters já usados.
2. **Uma tag, uma grafia** — Title Case em Português, nunca uma variante (singular/plural, acento, sinônimo) de tag existente.
3. **Tags são temas, não tipos** — o tipo do essay (`Ensaio`, `White Paper`, etc.) já vive na byline.
4. **2 a 5 tags por essay.**
5. `/organize` audita quase-duplicadas e propõe consolidação.

## Tipos de Source — Vocabulário Controlado

Campo `Tipo:` do manifesto (`wiki/sources/manifest.md`), vocabulário fechado — cada tipo define a subpasta física em `wiki/sources/`, nunca escolhida à mão.

| Tipo (manifesto)          | Subpasta                  | O que entra aqui                                                                                                                   |
| ------------------------- | ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Ensaio Completo Importado | `ensaio-importado/`     | Ensaio ou white paper pronto vindo de fora, que virou essay preservando o texto integral                                           |
| Web Clipping              | `web-clipping/`         | Recorte de página web: post, thread, matéria online                                                                              |
| Artigo Acadêmico         | `artigo-academico/`     | Paper com peer review, DOI, ou publicado em periódico/conferência                                                                |
| Livro                     | `livro/`                | Livro ou capítulo, inteiro ou em trecho relevante                                                                                 |
| Documentação Técnica   | `documentacao-tecnica/` | Manuais, specs, normas, documentação de ferramenta ou API                                                                        |
| Transcrição             | `transcricao/`          | Palestra, podcast, entrevista, aula                                                                                                |
| Ideias                    | `ideias/`               | Texto curto e não estruturado: rascunho, nota rápida, trecho de conversa, que ainda não é um ensaio, artigo ou clipping formal |
| Outro                     | `outro/`                | Use apenas quando genuinamente nenhuma categoria acima cobre o caso                                                                |

Reuse um tipo existente antes de criar um novo. `/organize` e `/stats` auditam a consistência entre `Tipo:` no manifesto e a subpasta real no disco.

## Status de essay (draft | maduro | finalizado)

Campo `status:` no frontmatter, **só em `wiki/essays/`**, nunca em `concepts/`/`entities/`. Vocabulário fechado: `draft`, `maduro`, `finalizado`.

- `/essay` (redigido do zero): nasce `draft`.
- `/import` (texto pronto do autor): nasce `finalizado` por padrão, ou `draft` se ficar claro que é rascunho do próprio autor.
- Essay antigo sem o campo: default `draft` na migração, corrigido depois via `/organize`.

**Regra para skills que editam prosa** (`/sweep`, `/expand`, `/chapter`, `/proofread`, `/polish`, `/continuity`, `/linkify`). Batch ou específico depende de o Usuário ter nomeado um essay ou não, não de quantos essays a skill acaba tocando no fim.

- **Batch** (sem nomear um essay específico — "/sweep tudo", "revisa todos"): pule `finalizado`/`maduro`, sem perguntar nem avisar durante a execução. No resumo final, informe quantos foram pulados por status.
- **Específico** (Usuário nomeia o essay): execute normalmente, mesmo se `finalizado`/`maduro`. Depois de editar um `finalizado`, avise ao final: "esse essay estava marcado como finalizado — segui porque você pediu direto." `maduro`: sem alerta. `draft`: comportamento normal.

## Byline do essay

Logo após o `# Título`, com uma linha vazia entre título e byline:

```
# Título do Essay

> Tipo · Categoria Temática
> Gustavo Zambrano · Mês de Ano
```

- **Tipo**: `Ensaio`, `White Paper`, `Brainstorm`, `Estudo` ou `Análise`.
- **Categoria**: área temática (ex: `Filosofia da Ciência & Biologia`).
- **Mês de Ano**: por extenso (ex: `Maio de 2026`).
- **Nunca** `[[wikilinks]]` (exportada a PDF como texto puro) nem dois-pontos (`:`) — Obsidian interpreta como separador de bloco.

## Estrutura obrigatória do essay

1. **Sem resumo executivo interno** — abre com a byline e vai direto ao `## Sumário`. A primeira seção `##` já é a introdução. Resumo condensado é artefato à parte (`/handout`), nunca embutido.
2. **`## Sumário` obrigatório**, logo após a byline, com links para todas as seções `##` (exceto Referências e Conexões):

   ```
   ## Sumário

   - [Título da Seção](#título-da-seção)
   - [Outra Seção](#outra-seção)

   ---
   ```

3. **Links externos** para todo conceito/entidade/termo técnico, ao menos na primeira ocorrência.
4. **`## Referências` obrigatória** — bibliografia com links externos. Heading exato (nunca H1, nunca "Referências Bibliográficas", nunca numerado).
5. **`## Conexões` obrigatória** no final — `[[wikilinks]]` bidirecionais para páginas relacionadas. Não exportada a PDF.

## Regra de links — exportabilidade para PDF

- **Corpo (inline)**: só links externos `[texto](url)`. Nunca `[[wikilinks]]` inline.
- **`## Conexões`**: só `[[wikilinks]]` — metadata interna, não exportada.
- **`## Referências`**: links externos bibliográficos, exportados.
- Motivo: essays são documentos autocontidos, compartilháveis como PDF sem perda de informação.
- Mínimo prático: ~10 links externos no corpo — abaixo disso, faltam links.

## Dois tipos de essay

- **Originais** (de `raw/`, via `/import`): texto integral preservado, traduzido se necessário. Só recebem link/formatação/`## Referências`/`## Conexões` — nunca alteração do texto original no momento da ingestão. Podem ser expandidos depois, sob pedido explícito.
- **Criados** (pela wiki, via `/essay`): livremente modificáveis, expandidos, enriquecidos.

## Estilo de prosa

Vale para todo trecho **escrito ou reescrito pela wiki** — não retroage sobre texto original de `raw/`, a menos que `/polish` ou `/proofread` seja pedido explicitamente.

1. **Evitar bullets no corpo.** Prosa argumentativa em parágrafos com transições explícitas. Bullets só em `## Sumário`, `## Referências`, e tabelas genuinamente mais claras que prosa (dados numéricos/técnicos).
2. **Travessões (—) extremamente raros**: no máximo 1 a 2 no essay inteiro, não por parágrafo. Prefira vírgula, dois-pontos, parênteses, ou reestruture a frase. Não contam o `·` da byline nem o `—` de display text em wikilinks do índice.

## Formato do índice (`wiki/index.md`)

Apenas essays, por categoria temática:

```
## Filosofia & Consciência
- [[filename|Título do Essay]] — resumo de uma linha
```

- Formato `[[filename|Display Title]]`.
- **Nunca** dois-pontos no display text (quebra o link no Obsidian) — substitua `:` por `—`. Correto: `[[filename|Título — Subtítulo]]`.
- Título do arquivo: `# Índice`.

## Formato de páginas em `wiki/synthesis/`

Dois tipos de conteúdo, mesma pasta, distinguidos pelo `tipo:` do frontmatter — nunca misture os dois formatos no mesmo arquivo:

- **`tipo: comparacao`** — comparação curta gerada por `/query`. Frontmatter simples (`tags`, `sources`, `created`, `updated`, `tipo: comparacao`), prosa curta, sem `## Sumário`/`## Referências`.
- **`tipo: nota-atomica`** — fragmento denso de uma ideia só, gerado por `/atom` (formato completo em `.agents/skills/atom/SKILL.md`): frontmatter com `maturidade: solta | germinando | madura`, corpo curto, `## Conexões` com `[[wikilinks]]`.

Ambos ficam fora de `wiki/index.md` e fora da contagem de "essays" de `/stats` — aparecem na seção "Synthesis".

## Formato do log (`wiki/log.md`)

```
## [YYYY-MM-DD] operação | Título
Descrição breve do que foi feito.
```

Append-only — nunca editar entradas existentes.

## Formato do manifesto de sources (`wiki/sources/manifest.md`)

Append-only, uma entrada por fonte ingerida:

```
## [YYYY-MM-DD] nome-do-arquivo-original.pdf
Tipo: [vocabulário controlado, ver AGENTS.md].
Pasta: wiki/sources/<subpasta-correspondente>/
Virou: [[Essay Resultante]] (essay novo) | enriqueceu [[Essay Existente]].
Verificação: [referências confirmadas | não verificado — checar antes de citar em outro essay].
```

Antes de reutilizar uma citação em outro essay, confira `Verificação:` — se estiver "não verificado", confirme antes de propagar.

Atualize o manifesto e `wiki/sources/map.md` no mesmo momento em que o arquivo é movido de `raw/` para `wiki/sources/<subpasta>/`.

## Formato do mapa de sources (`wiki/sources/map.md`)

Visão por assunto de tudo já processado ou pendente:

```
## <Categoria Temática>
- [[Nome do Source]] — Tipo · Status
  - Status: Importado como [[Essay]] | Resumido — ver wiki/sources/resumos/<slug>.md | Absorvido em [[Essay X]] | Pendente em raw/
```

Atualizado por `/import`, `/digest` e `/absorb` durante o processamento, e revisado por inteiro por `/organize`.

## Nomenclatura de páginas

- Arquivos: kebab-case + `.md`. Títulos: Title Case.
- Essays/concepts/entities: `wiki/<pasta>/nome-do-arquivo.md` → `# Nome Do Arquivo`.
- Sources: nomes originais preservados em `wiki/sources/<subpasta-do-tipo>/` — não são páginas wiki.
- `[[wikilinks]]` usam o título da página, nunca o nome do arquivo: `[[Nome Da Entidade]]`, não `[[nome-da-entidade]]`.
- Título → nome de arquivo: minúsculas, espaços viram hífens, remove caracteres especiais.

## Tratamento de imagens

1. Toda imagem/figura da wiki vive em `wiki/assets/` — nunca embutida inline em base64, nunca deixada só dentro do PDF/DOCX/HTML original.
2. Toda fonte processada por `/import`, `/digest` ou `/absorb` que contenha figura embutida (PDF, DOCX, HTML, clipping): extraia para `wiki/assets/` no mesmo momento do processamento.
3. Essays e resumos linkam a imagem por caminho relativo, `../assets/nome-da-imagem.png` (a partir de `wiki/essays/`) ou `../../assets/nome-da-imagem.png` (a partir de `wiki/sources/resumos/`) — nunca um caminho absoluto do sistema de arquivos.
4. Se uma imagem carrega informação importante (diagrama, gráfico), descreva o conteúdo em texto também — não pode existir só na imagem.

## Compatibilidade com Obsidian

Reforça regras já definidas acima:

- `[[wikilinks]]` só em `## Conexões` e em páginas de concept/entity/source, nunca inline (ver `## Regra de links`).
- Nunca dois-pontos no display text (ver `## Formato do índice`).
- Imagens em caminho relativo (ver `## Tratamento de imagens`).

Regra específica desta seção: wikilinks em `## Conexões` usam `[[Título da Página]]` — Obsidian resolve pelo caminho mais curto até a página (shortest path).

## Conversão de fontes (HTML/PDF/DOCX → Markdown)

1. **Blockquotes (`>`)**: só para conteúdo que era caixa especial no original (callout, warning-box, pullquote).
2. **Tabelas HTML** → markdown tables, nunca linhas soltas.
3. **Índices/TOC do original**: remover — substituídos pelo `## Sumário` gerado.
4. **Labels de capítulo** (`01 — Introdução`): incorporar como heading ou remover se já há um equivalente.
5. **Símbolos residuais**: remover diamantes (◆), replacement chars, zero-width spaces, `&nbsp;`, `&amp;`, etc.
6. **Verificar fidelidade**: comparar o `.md` gerado contra o original.

## Exportação para PDF (`export_essay.py`, Pandoc + LuaLaTeX)

- **LuaLaTeX, não XeLaTeX** — o dvipdfmx do MiKTeX não gera anotações de link.
- `## Conexões` é removida do PDF. `## Sumário` e `## Referências` são preservadas.
- Frontmatter YAML + byline viram título/subtítulo/autor em LaTeX.
- Nunca `--number-sections` (essays já têm numeração manual).
- Imagens com caminho relativo resolvidas para absoluto.
- Hyperlinks via variáveis Pandoc (`colorlinks`, `urlcolor`, `linkcolor`), não `\usepackage{hyperref}` manual.
- Caracteres LaTeX especiais no subtítulo (`&`, `#`, `%`, `_`) são escapados.
- Wikilinks residuais `[[Target|Display]]` viram texto puro.
- Handouts exportam pelo mesmo pipeline via `--handout`.

## Regra de contradição entre fontes

Se informação nova (fonte ingerida, ou algo que o Usuário disse) contradiz o que já está escrito na wiki: **não escolha um lado sozinho, não tire a média.** Pare, aponte a contradição citando as duas fontes com localização exata, e só edite depois que o Usuário disser qual prevalece.

Vale para `/absorb`, `/digest`, `/expand`, `/continuity` e qualquer skill que compare conteúdo novo contra o que já está na wiki.

## Decisões fechadas

Decisões de estilo já resolvidas — não reabra sem evidência nova (um caso real que a regra não cobre, não uma preferência estética isolada).

- [Nenhuma decisão fechada registrada ainda. Adicione aqui conforme surgirem — formato: `- [decisão] (YYYY-MM-DD) — [motivo/link]`.]
