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
| ------------------------- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------ |
| `wiki/essays/` | Ensaios/white papers completos, tese sustentada do início ao fim | `/essay`, `/import` | A ideia já é (ou virou, via`/insight promote`) um argumento completo |
| `wiki/concepts/` | Definição/explicação curta de um conceito, sem tese própria | `/essay`, `/expand`, `/absorb`, `/digest`, `/chapter` | Um termo é citado mas ainda não tem página própria |
| `wiki/entities/` | Página curta sobre pessoa/obra/instituição nomeada | mesmas skills que concepts | Uma entidade nomeada é citada mas ainda não tem página própria |
| `wiki/insights/` | Fragmentos densos de ideia — sementes, sínteses, observações, mini-argumentos | `/insight` (também via `/query`, que passa a ideia para `/insight add`) | Insight novo que ainda não tem lar, não é essay nem concept/entity |
| `wiki/sources/<tipo>/` | Cópia/referência do documento original, por tipo (vocabulário em `AGENTS.md`) | `/import`, `/digest`, `/absorb` (via `/scout` como triagem) | Toda fonte processada, sempre |
| `wiki/sources/resumos/` | Resumo de uma página por fonte processada | `/digest` | Toda vez que uma fonte é resumida |
| `wiki/handouts/` | Versão de uma página de um essay **já existente** | `/handout` | Sempre derivado, sob demanda |
| `wiki/assets/` | Imagens/figuras referenciadas pelos essays | `/import`, `/digest`, `/absorb` | Fonte processada tem figura embutida (ver`## Tratamento de imagens`) |
| `wiki/book-chapters/` | Reservado para projeto de livro futuro | — | Não usar ainda |
| `plan/plano.md` | Pendência de longo prazo | `/plan` | Nunca conteúdo de wiki — só intenção de trabalhar algo depois |
| `wiki/status.md` | Snapshot do estado da sessão atual | `/status` | Ponte entre sessões, não confundir com o plano |

Regra geral: tese própria sustentada → `essays/`. Definição/explicação sem tese própria → `concepts/`/`entities/`. Insight novo sem lar → `insights/`. Material bruto de terceiros → `sources/`.

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

Essays têm dois campos a mais: `status: draft | maduro | finalizado` — ver `## Status de essay` abaixo — e `summary:`, resumo de uma linha (até 120 caracteres) usado por `build_index.py` para montar a entrada em `wiki/index.md`. Escrito por quem cria o essay (`/essay`, `/import`, ou `/query` quando salva uma síntese como essay novo).

## Tags — Vocabulário Controlado

Campo `tags:` do frontmatter de essay/concept/entity/insight, e campo `Tags:` do manifesto de sources (`wiki/sources/manifest.md`) e do mapa (`wiki/sources/map.md`). **Uma única lista, um único vocabulário fechado** para a wiki inteira — consolidado em `tags_in_use` em `wiki/index.json` — evitando tags quase-duplicadas que fragmentam a navegação.

1. **Reuse antes de criar** — cheque `tags_in_use` em `wiki/index.json` (gerado por `build_index.py`) antes de escrever uma tag nova. Rode `python scripts/build_index.py` primeiro se o índice estiver desatualizado.
2. **Uma tag, uma grafia** — Title Case em Português, nunca uma variante (singular/plural, acento, sinônimo) de tag existente.
3. **Tags são temas, não tipos** — o tipo do essay (`Ensaio`, `White Paper`, etc.) ou da source (`Artigo Acadêmico`, `Livro`, etc.) já vive na byline/`Tipo:`, nunca em `tags`/`Tags:`.
4. **2 a 5 tags por essay ou source**.
5. `/organize` audita quase-duplicadas (nos dois campos, `tags:` e `Tags:`) e propõe consolidação.

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

> Tipo
> Gustavo Zambrano · Mês de Ano
```

- **Tipo**: `Ensaio`, `White Paper`, `Brainstorm`, `Estudo` ou `Análise`.
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
4. **`## Referências` obrigatória** — bibliografia com links externos, no formato AIAA (ver `## Formato de "## Referências" — padrão AIAA` abaixo). Heading exato (nunca H1, nunca "Referências Bibliográficas", nunca numerado). Todo conceito/claim de fonte externa não arquivada em `wiki/sources/` precisa de entrada aqui.
5. **`## Conexões` obrigatória** no final — `[[wikilinks]]` bidirecionais para páginas relacionadas. Não exportada a PDF.

## Regra de links — exportabilidade para PDF

- **Corpo (inline)**: só links externos `[texto](url)`. Nunca `[[wikilinks]]` inline.
- **`## Conexões`**: só `[[wikilinks]]` — metadata interna, não exportada.
- **`## Referências`**: links externos bibliográficos, exportados, no formato AIAA (ver `## Formato de "## Referências" — padrão AIAA` abaixo).
- Motivo: essays são documentos autocontidos, compartilháveis como PDF sem perda de informação.
- **Trabalho de bibliografia não toca no corpo.** Uma passada sobre `## Referências` (formato, numeração, link da obra, dedup) mexe só na seção do fim do arquivo. Os links inline do corpo ficam exatamente onde estão, com o texto-âncora que já têm. Quando um check acusa uma obra citada no corpo e ausente da bibliografia, a correção é **acrescentar a entrada em `## Referências`** — nunca mexer no link do corpo para silenciar o aviso. Alterar links inline é trabalho de `/linkify` no modo `## Adicionar links`, e só sob pedido explícito do Usuário.
- Mínimo prático: ~10 links externos no corpo — abaixo disso, faltam links.

## Dois tipos de essay

- **Originais** (de `raw/`, via `/import`): texto integral preservado, traduzido se necessário. Só recebem link/formatação/`## Referências`/`## Conexões` — nunca alteração do texto original no momento da ingestão. Podem ser expandidos depois, sob pedido explícito.
- **Criados** (pela wiki, via `/essay`): livremente modificáveis, expandidos, enriquecidos.

## Formato de `## Referências` — padrão AIAA

Um item por linha, numerado `[N]` em ordem de citação no corpo:

```
## Referências

[1] Cheeseman, I. C., e Bennett, W. E., *The Effect of the Ground on a Helicopter Rotor in Forward Flight*, Aeronautical Research Council Reports and Memoranda, No. 3021, HMSO, London, 1955. — Referência seminal: derivou a equação fechada do ganho IGE em função da altura normalizada e do ângulo de skew da esteira. [Link](https://example.org/arc-rm-3021)

[2] Glauert, H., *The Elements of Aerofoil and Airscrew Theory*, Cambridge University Press, Cambridge, 1926. — Base da Teoria do Momento em escoamento oblíquo; sem edição digital confiável, sem link.

[3] *Blade Element Momentum Theory*, Wikipedia, The Free Encyclopedia. — Verbete de apoio para a definição geral do método. [Link](https://en.wikipedia.org/wiki/Blade_element_momentum_theory)

[4] Zambrano, G., *zbemt*, GitHub repository, 2026. — Repositório do solver referenciado neste white paper. [Link](https://github.com/gustavo/zbemt)
```

Regras:

- **Título sempre em itálico**, sem exceção por tipo de fonte (artigo, livro, capítulo, verbete web, repositório).
- **O link é a palavra `Link`, clicável, como última coisa da entrada**, depois do ponto final. Nunca no título, nunca no periódico, nunca envolvendo a citação inteira: o texto da citação é texto limpo do começo ao fim, e a única coisa colorida é a palavra `Link`, sempre no mesmo lugar. Isso mantém o itálico do título legível (sublinhado de hyperlink o estragaria), evita que o PDF exportado vire um bloco azul, e deixa a coluna de links alinhada para varrer com o olho.
- Link de glossário **dentro da nota** (um verbete para um termo comentado ali) pode ficar onde está: ele não é o endereço da obra.
- Entrada sem link nenhum é entrada normal, na mesma lista das outras: ausência de edição digital não é um tipo de fonte.
- Sem autor identificável (verbete, repositório institucional, site): começa direto pelo título em itálico.
- Container troca conforme o tipo de fonte: periódico, editora + cidade, série + órgão (relatório técnico), site/wiki, plataforma + tipo (GitHub, YouTube).
- Ordem de preferência de link: (1) DOI/link permanente do editor; (2) site institucional primário (NASA/NTRS, AIAA, ARC/NACA, universidade, GitHub do projeto); (3) SEP para verbetes filosóficos; (4) Wikipedia, só para conceito geral.
- Data de acesso obrigatória só para fontes sem versão fixa (Wikipedia, GitHub README, página institucional sem data). Formato `(acesso em DD Mês. AAAA)` ao final da nota.
- Nota curta opcional depois do link.
- Exceção "sem link" só para caso genuíno (livro impresso sem edição digital) — sinalizado como aviso pelo lint, nunca erro bloqueante.
- Nunca duas entradas com a mesma URL normalizada no mesmo essay.
- **Verifique o título e o autor reais antes de escrever a entrada — nunca "de memória".** Nunca escreva "Autor (Ano). *Nome do Periódico*." como se isso bastasse, nem aceite uma entrada como `[N] Schmidt, F. L., & Hunter, J. E. (1998). *Psychological Bulletin*.` — sem título real, com o container erroneamente em itálico. Se o título do trabalho não estiver explícito na fonte que você está usando, use WebFetch/WebSearch no DOI ou URL para confirmar título, autores completos e container reais antes de criar a entrada. Dois bugs reais já aconteceram por pular esse passo: (1) itálico envolvendo "Autor (Ano)" inteiro no lugar do título, porque o título nunca foi de fato buscado; (2) autor errado atribuído a uma URL (ex.: um DOI de Sackett et al. creditado a "Griebe et al.", um link do MDPI creditado a "Bowden et al." quando os autores reais eram outros) — só o fetch do próprio link/DOI pega esse tipo de erro, releitura visual não pega. **Autor errado é pior que autor ausente**: quando o essay cita explicitamente que o link aponta para uma fonte secundária (ex.: "citado em revisão contemporânea"), preserve essa distinção na referência — não troque pela obra original sem confirmar que é isso que o essay realmente pretende citar.
- **Nome de autor nunca em negrito.** Só o título leva ênfase (itálico); autor e container são texto normal. `python scripts/check_format.py` sinaliza `REF_BOLD_AUTHOR` se isso escapar. Se encontrar `**Autor**` numa entrada existente, é desvio a corrigir, não uma variação de estilo aceitável.
- Essay com corpo rico em links externos e `## Referências` vazia é **sempre bug**, nunca estado válido — `check_format.py` sinaliza isso como `EMPTY_REFERENCIAS`.

## `wiki/references.md` e `wiki/references.json`

Mesmo padrão de `index.json`/`index.md`: artefatos na raiz de `wiki/`, **nunca editados à mão**, regenerados por `scripts/build_references.py` ao final de `/essay`, `/expand`, `/absorb`, `/digest`, `/import`, `/linkify`, `/review`, `/organize`.

```json
{
  "references": [
    {
      "url": "https://doi.org/xxxx",
      "citation_aiaa": "Sobrenome, I., *Título*, Fonte, Ano.",
      "domain_group": "doi",
      "cited_by": ["essay-slug-a", "essay-slug-b"],
      "has_link": true
    }
  ]
}
```

`domain_group` (só no JSON, para consultas): `doi`, `nasa`, `aiaa`, `sep`, `wikipedia`, `github`, `institucional`, ou nulo quando a entrada não tem link.

**Antes de escrever uma entrada nova em `## Referências`, procure a mesma fonte em `wiki/references.md`** (por URL ou pelo título em itálico) — se ela já estiver catalogada, reuse a citação exata já existente em vez de redigir uma versão nova com palavras diferentes. É esse desvio, repetido essay a essay, que produz a classe 4 de `check_dedupe.py` (mesma obra, citação divergente entre essays): evitar na criação é mais barato do que consolidar depois. Só vale a pena uma citação diferente da já catalogada se a fonte real for outra edição/tradução genuinamente distinta, não apenas uma reformulação da mesma nota.

`references.md` é **lista única em ordem alfabética**, sem agrupamento. Agrupar por domínio separaria o livro e o paper do mesmo autor, e criava um balde "Sem link" que falava de disponibilidade digital em vez de tipo de fonte. Bibliografia se lê por autor.

`concepts/` e `entities/` **não ganham** seção `## Referências` própria — essas páginas continuam sendo frontmatter simples e conteúdo denso, sem bibliografia formal, e isso não muda. `references.json`/`.md` é alimentado só pelas `## Referências` de essays, com o mesmo rigor de regeneração automática que `build_index.py` já aplica a `tags_in_use`/`index.json`.

## Estilo de prosa

Vale para todo trecho **escrito ou reescrito pela wiki** — não retroage sobre texto original de `raw/`, a menos que `/polish` ou `/proofread` seja pedido explicitamente.

1. **Evitar bullets no corpo.** Prosa argumentativa em parágrafos com transições explícitas. Bullets só em `## Sumário`, `## Referências`, e tabelas genuinamente mais claras que prosa (dados numéricos/técnicos).
2. **Travessões (—) extremamente raros**: no máximo 1 a 2 no essay inteiro, não por parágrafo. Prefira vírgula, dois-pontos, parênteses, ou reestruture a frase. Não conta o `·` da byline.

## Formato do índice (`wiki/index.md`)

Apenas essays. **Artefato gerado, nunca editado à mão** — regenerado por `python scripts/build_index.py` (que emite `index.json` e `index.md` juntos, a partir da mesma varredura de frontmatter) toda vez que um essay é criado, editado ou removido. Nenhuma skill insere linha nele diretamente.

Lista plana, ordenada por `created` decrescente, sem agrupamento por categoria — a classificação temática vem só de `tags`:

```markdown
- [Título do Essay](essays/nome-do-arquivo.md) — Resumo de uma linha.
  `consciência` · `identidade-pessoal` · `filosofia-da-mente`
```

- Cada entrada usa o campo `summary:` do frontmatter (ver `## Frontmatter`) como resumo de uma linha, e `tags` para a lista de temas.
- Continua Markdown, não HTML — sem template visual separado, gerado direto pela função de renderização de `build_index.py`.

## Formato de páginas em `wiki/insights/`

Um formato único — não existe mais distinção de `tipo:` dentro da pasta, tudo ali é insight (gerado por `/insight`, formato completo em `.agents/skills/insight/SKILL.md`): frontmatter com `tags`, `sources`, `created`, `updated`, `maturidade: solta | germinando | madura | absorvida`, corpo curto, `## Conexões` com `[[wikilinks]]`.

Fica fora de `wiki/index.md` e fora da contagem de "essays" de `/stats` — aparece na seção "Insights".

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
Tags: [tag1, tag2] (mesmo vocabulário controlado dos essays — ver ## Tags — Vocabulário Controlado logo abaixo; nunca uma lista própria de tags de source).
Pasta: wiki/sources/<subpasta-correspondente>/
Virou: [[Essay Resultante]] (essay novo) | enriqueceu [[Essay Existente]] | ainda não — ver resumo em wiki/sources/resumos/.
Verificação: [referências confirmadas | não verificado — checar antes de citar em outro essay].
```

`Tags:` é obrigatório em toda entrada nova (`/import`, `/digest`, `/absorb`) — 2 a 5 tags do mesmo tema da fonte, reusando o vocabulário controlado de `## Tags — Vocabulário Controlado`. Existe **uma única fonte de tags para toda a wiki**: essay e source nunca têm vocabulários de tag separados — uma tag nova entra no mesmo lugar (a lista canônica abaixo) e vale para os dois. `build_index.py` consolida `tags_in_use` combinando essays e manifesto num só cômputo, exatamente por isso.

Antes de reutilizar uma citação em outro essay, confira `Verificação:` — se estiver "não verificado", confirme antes de propagar.

Atualize o manifesto e `wiki/sources/map.md` no mesmo momento em que o arquivo é movido de `raw/` para `wiki/sources/<subpasta>/`.

## Formato do mapa de sources (`wiki/sources/map.md`)

Lista plana de tudo já processado ou pendente, sem agrupamento por categoria — a classificação temática vem só de `Tags:`:

```
- [[Nome do Source]] — Tipo · Tags: tag1, tag2 · Status
  - Status: Importado como [[Essay]] | Resumido — ver wiki/sources/resumos/<slug>.md | Absorvido em [[Essay X]] | Pendente em raw/
```

`Tags:` aqui espelha o que já está em `manifest.md` para a mesma fonte (nunca uma lista divergente) — repetido no mapa só como referência rápida ao ler a lista.

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
- Imagens em caminho relativo (ver `## Tratamento de imagens`).

Regra específica desta seção: wikilinks em `## Conexões` usam `[[Título da Página]]` — Obsidian resolve pelo caminho mais curto até a página (shortest path).

## Conversão de fontes (HTML/PDF/DOCX → Markdown)

1. **Blockquotes (`>`)**: só para conteúdo que era caixa especial no original (callout, warning-box, pullquote).
2. **Tabelas HTML** → markdown tables, nunca linhas soltas.
3. **Índices/TOC do original**: remover — substituídos pelo `## Sumário` gerado.
4. **Labels de capítulo** (`01 — Introdução`): incorporar como heading ou remover se já há um equivalente.
5. **Símbolos residuais**: remover diamantes (◆), replacement chars, zero-width spaces, `&nbsp;`, `&amp;`, etc.
6. **Verificar fidelidade**: comparar o `.md` gerado contra o original.

## Exportação para PDF (`export_essay_pdf.py`, Pandoc + LuaLaTeX)

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
