---
name: conventions
description: >
  Referência normativa de estrutura, estilo e formatação da wiki:
  localização de conteúdo, frontmatter, tags, tipos de source, status,
  byline, Sumário/Referências/Conexões, links, prosa, imagens, nomes,
  Obsidian, conversão de fontes e contradições. Não executa fluxo próprio;
  as skills que escrevem ou editam conteúdo consultam este arquivo.
allowed-tools: Read WebFetch WebSearch
---
# Conventions

**[leitura]** Fonte única das regras de conteúdo e formatação. Não replique estas regras em outras skills; cite esta seção e siga.

## Onde as coisas vão — tabela canônica

| Pasta | Conteúdo | Regra |
| --- | --- | --- |
| `wiki/essays/` | Ensaio, white paper ou estudo com tese sustentada | `/essay`, `/import` |
| `wiki/concepts/` | Conceito, framework ou teoria sem tese própria | Página curta de apoio |
| `wiki/entities/` | Pessoa, obra, organização ou ferramenta | Página curta de apoio |
| `wiki/insights/` | Uma ideia ainda sem essay-pai | `/insight` |
| `wiki/sources/<tipo>/` | Documento original processado | Tipo define a subpasta |
| `wiki/sources/resumos/` | Resumo de uma fonte de terceiros | `/digest` |
| `wiki/handouts/` | Resumo de uma página de um essay | `/handout` |
| `wiki/assets/` | Figuras e imagens | Sempre arquivo separado |
| `wiki/book-chapters/` | Projeto futuro | Não usar ainda |
| `plan/plano.md` | Trabalho futuro | `/plan` |
| `wiki/status.md` | Estado da sessão | `/status` |

Regra de decisão: tese própria → essay; definição sem tese → concept/entity; ideia sem lar → insight; material bruto → source.

## Frontmatter

Páginas da wiki:

```yaml
---
tags: [Tag 1, Tag 2]
sources: [source-filename.md]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

Essays acrescentam:

```yaml
summary: "Resumo de uma linha, até 120 caracteres."
status: draft | maduro | finalizado
publish: true          # opcional; ver ## Publicação
```

`summary:` sempre entre aspas duplas. `publish:` é opcional e sua ausência é o
estado seguro.

## Tags — Vocabulário Controlado

`tags:` das páginas e `Tags:` de `wiki/sources/manifest.md` usam o mesmo vocabulário, consolidado em `tags_in_use` de `wiki/index.json`.

- Reuse uma tag existente antes de criar outra.
- Use uma única grafia em Title Case, sem variantes por plural, acento ou sinônimo.
- Tags representam temas, não tipo de essay/source.
- Use 2 a 5 tags por essay ou source.
- `/organize` audita quase-duplicatas; renomeação em massa exige aprovação.

## Reuso de vocabulário controlado (`tags_in_use`)

Antes de criar tag nova, confira `tags_in_use`. Se o índice estiver desatualizado, rode `python scripts/build_index.py`. Crie uma tag apenas quando nenhuma existente cobrir o tema.

## Tipos de Source — Vocabulário Controlado

`Tipo:` no manifesto define a subpasta física.

| Tipo | Subpasta |
| --- | --- |
| Ensaio Completo Importado | `ensaio-importado/` |
| Web Clipping | `web-clipping/` |
| Artigo Acadêmico | `artigo-academico/` |
| Livro | `livro/` |
| Documentação Técnica | `documentacao-tecnica/` |
| Transcrição | `transcricao/` |
| Ideias | `ideias/` |
| Outro | `outro/` |

Reuse um tipo existente. `Outro` só quando nenhum tipo específico servir.

`manifest.md` e `map.md` são catálogos editáveis; a regra de não modificar `wiki/sources/` protege os documentos originais.

## Status de essay (draft | maduro | finalizado)

`status:` existe apenas em essays.

- `/essay` cria `draft`.
- `/import` cria `finalizado` por padrão; use `draft` se o original for rascunho.
- Essay antigo sem status é tratado como `draft` até `/organize` corrigir.

Status protege a prosa, não a formatação mecânica. `/organize` e `fix_lint.py` podem corrigir estrutura/formatação em qualquer status.

Para skills que editam prosa:
- **Batch:** pule `maduro` e `finalizado`; informe a contagem no fim.
- **Essay nomeado pelo Usuário:** edite normalmente. Se era `finalizado`, avise ao final.

## Publicação

`publish:` controla **leitura**, não visibilidade no catálogo. Nunca use `tags:`
para controlar exposição: `tags:` descreve assunto, `publish:` decide quem pode
ler o texto.

O site tem duas camadas:

| Camada | Alcance | Conteúdo |
| --- | --- | --- |
| Catálogo e mapa | base inteira | título, resumo, tags, datas, status, conexões |
| Texto | só `publish: true` | corpo renderizado, busca full-text, link que abre |

| Valor no frontmatter | Resultado |
| --- | --- |
| campo ausente | catalogado como privado; não abre |
| `publish: false` | catalogado como privado; não abre |
| `publish: "true"` (string) | inválido; tratado como não publicado |
| `publish: true` (booleano YAML) | texto legível no site |

Regras:

- `publish:` só se aplica a **essays**; nenhuma outra página tem o campo;
- nenhuma skill de escrita, revisão ou organização define ou altera `publish:` automaticamente — é decisão explícita do Usuário;
- o corpo de uma página não autorizada nunca é renderizado, indexado ou linkado;
- nenhum caminho para dentro de `data/` pode aparecer na saída pública;
- imagem só é copiada para o site se for referenciada por um essay publicado **e** estiver dentro de `DATA_ROOT/wiki/assets`;
- um essay não publicado aparece no catálogo e no mapa com o selo **privado**, e em rascunho com **draft**.

Um site estático não esconde o que serve: título e resumo publicados no catálogo
são legíveis por qualquer pessoa. A troca é deliberada — o mapa é público, o
texto não.

Aplicação e verificação ficam em `scripts/publication.py`, `scripts/check_publication.py`
e `scripts/check_site_privacy.py`. Detalhes de implementação do site não pertencem aqui.

## Byline do essay

Logo após o H1:

```markdown
# Título do Essay

> Tipo
> Gustavo Zambrano · Mês de Ano
```

`Tipo`: `Ensaio`, `White Paper`, `Brainstorm`, `Estudo` ou `Análise`.

Não use `[[wikilinks]]` nem `:` na byline.

## Estrutura obrigatória do essay

1. H1 + byline.
2. `## Sumário` logo após a byline, com links para todos os H2 de conteúdo.
3. Introdução como primeira seção de conteúdo. Não crie `## Resumo Executivo` em essays novos.
4. Corpo autocontido com links externos na primeira ocorrência dos termos relevantes.
5. `## Referências` com heading exato e bibliografia no padrão abaixo.
6. `## Conexões` como última seção, contendo apenas relações internas.

`Referências` e `Conexões` não entram no Sumário.

## Regra de links — Obsidian é o leitor primário

| Uso | Forma |
| --- | --- |
| Outra página | `[[slug-do-arquivo\|Título Visível]]` |
| Seção do mesmo arquivo | `[[#Texto Exato Do Heading]]` ou `[[#Texto\|Display]]` |
| Corpo do essay | links externos `[texto](url)`; sem wikilinks para outras páginas |
| `## Conexões` | apenas `[[slug\|Título]]` |
| `## Referências` | links externos bibliográficos |

Regras:
- O alvo de wikilink é o nome do arquivo, não o H1.
- Não coloque link Markdown dentro de heading.
- Não remeta a outro essay no corpo; mantenha o documento autocontido e registre a relação em `## Conexões`.
- Trabalho bibliográfico modifica `## Referências`, não links do corpo.
- Como referência prática, essays completos devem ter cerca de 10 links externos ou mais quando o tema oferecer material relevante.

Exportadores convertem links de seção, removem `## Conexões` e limpam wikilinks residuais.

## Compatibilidade com Obsidian

Use os formatos canônicos de `## Regra de links — Obsidian é o leitor primário`, caminhos relativos para imagens e Markdown puro nos artefatos gerados. Valide mudanças de sintaxe de navegação no Obsidian quando elas alterarem comportamento de clique.

## Dois tipos de essay

- **Originais (`/import`)**: texto do autor preservado na ingestão; só recebem estrutura, links e metadados necessários. Edição substantiva posterior exige pedido explícito.
- **Criados (`/essay`)**: texto novo, livremente iterável pelas skills editoriais.

## Formato de `## Referências` — padrão AIAA

Uma entrada por parágrafo, numerada `[N]` na ordem de citação.

```markdown
## Referências

[1] Cheeseman, I. C., e Bennett, W. E., *The Effect of the Ground on a Helicopter Rotor in Forward Flight*, Aeronautical Research Council Reports and Memoranda, No. 3021, HMSO, London, 1955. — Nota contextual opcional. [Link](https://example.org/arc-rm-3021)

[2] *Blade Element Momentum Theory*, Wikipedia, The Free Encyclopedia. [Link](https://en.wikipedia.org/wiki/Blade_element_momentum_theory)
```

Regras:
- Título sempre em itálico.
- Até 3 autores: liste todos. Acima disso: primeiro autor + `et al.`.
- Preserve subtítulo quando existir.
- Use container completo; inclua `Vol.`, `No.` e `pp.` quando aplicável.
- Sem autor identificado: comece pelo título.
- O link externo é `[Link](url)` e fica no final.
- Nota contextual, quando houver, vem antes de `[Link]`.
- Entrada sem link é válida quando não existe versão digital confiável.
- Para fonte mutável (Wikipedia, README, página sem versão fixa), inclua data de acesso.
- Prefira DOI/editor; depois fonte institucional; SEP para filosofia; Wikipedia apenas para conceitos gerais.
- Não repita a mesma URL normalizada no mesmo essay.
- Nunca use negrito no nome do autor.
- `## Referências` vazia em essay com claims externos é erro.

Antes de criar ou corrigir uma referência, confirme título, autores e container na fonte. Não complete dados bibliográficos de memória.

## `wiki/references.md` e `wiki/references.json`

São gerados por `python scripts/build_references.py` e nunca editados manualmente.

Antes de escrever uma citação nova, procure a fonte em `wiki/references.md` por URL ou título. Se já existir, reutilize a citação canônica. Edição/tradução diferente conta como fonte distinta.

`concepts/` e `entities/` não recebem `## Referências` própria.

## Estilo de prosa

Vale para texto novo ou reescrito pela wiki. Texto original importado só muda sob pedido editorial explícito.

### Regras gerais

1. Uma proposição principal por frase.
2. Use conectores apenas quando a transição lógica precisar deles.
3. Corpo argumentativo em prosa; bullets apenas quando a estrutura exigir lista real.
4. Use o mesmo termo para o mesmo conceito.
5. Abra cada parágrafo com o tema; um tema por parágrafo.
6. Use travessões raramente: no máximo 1 a 2 na prosa do essay.
7. Não use ponto e vírgula; prefira frases autônomas.
8. Parênteses apenas para informação curta.
9. Evite atalhos tipográficos: `/`, `~`, `--`, intervalos `5-30`, `Cap.`/`Sec.`, `e.g.`/`i.e.`.
10. Prefira frase direta, completa e sem enchimento.

`check_wiki.py` cobre as regras mecânicas; `/polish` e `/proofread` cobrem as editoriais.

### Regras adicionais para essays técnicos

1. Português claro, conciso, formal e assertivo.
2. Não antropomorfize código, modelos ou teorias.
3. Prefira voz ativa quando o agente for conhecido.
4. Prefira verbo direto a nominalização.
5. Evite gerúndio de consequência ambígua.
6. Evite `isso/isto` quando o referente não for inequívoco.
7. Simplifique cadeias longas de `de/da/do`.
8. Mantenha grafia única para termos, siglas, unidades e variáveis.
9. Elimine marketing, superlativo e hedge vazio.
10. Concisão preserva sujeito, verbo e precisão técnica.

## Formato do índice (`wiki/index.md`)

Gerado por `python scripts/build_index.py`; nunca editar à mão.

```markdown
- [Título do Essay](essays/nome-do-arquivo.md) — Resumo de uma linha.
  `tag-1` · `tag-2`
```

Contém apenas essays, em ordem decrescente de `created`, usando `summary` e `tags` do frontmatter.

## Formato de páginas em `wiki/insights/`

Frontmatter: `tags`, `sources`, `created`, `updated`, `maturidade: solta | germinando | madura | absorvida`. Corpo curto em prosa e `## Conexões`. Detalhes de fluxo em `/insight`.

Insights ficam fora de `wiki/index.md`.

## Formato do log (`wiki/log.md`)

```markdown
## [YYYY-MM-DD] operação | Título
Descrição breve do que foi feito.
```

Append-only. Não altere entradas antigas.

## Formato do manifesto de sources (`wiki/sources/manifest.md`)

Uma entrada por fonte processada:

```markdown
## [YYYY-MM-DD] nome-do-arquivo-original.pdf
Tipo: <tipo controlado>
Tags: [tag1, tag2]
Pasta: wiki/sources/<subpasta>/
Virou: [[slug-do-essay|Essay]] | enriqueceu [[slug|Essay]] | ainda não — ver resumo
Verificação: referências confirmadas | não verificado — checar antes de citar
```

`Tags:` é obrigatório e usa o mesmo vocabulário das páginas. Atualize manifesto e mapa quando a fonte sair de `raw/` para `wiki/sources/`.

## Formato do mapa de sources (`wiki/sources/map.md`)

Lista plana de fontes já processadas:

```markdown
- [[slug-do-source|Nome do Source]] — Tipo · Tags: tag1, tag2 · Status
  - Status: Importado como [[Essay]] | Resumido — ver resumo | Absorvido em [[Essay]]
```

`raw/` não entra no mapa.

## Nomenclatura de páginas

- Arquivo de página: kebab-case + `.md`.
- Título: Title Case.
- Wikilink: `[[nome-do-arquivo|Título Visível]]`.
- Sources preservam o nome original na subpasta do tipo.

## Tratamento de imagens

1. Salve imagens em `wiki/assets/`; nunca use base64 inline.
2. Extraia figuras relevantes de fontes durante a ingestão.
3. Use caminho relativo: `../assets/...` em essays e `../../assets/...` em resumos de sources.
4. Descreva em texto a informação essencial de gráficos e diagramas.

## Conversão de fontes (HTML/PDF/DOCX → Markdown)

- Preserve blockquote apenas quando o original tiver bloco semântico equivalente.
- Converta tabelas para Markdown.
- Remova TOC do original; use `## Sumário`.
- Normalize labels de capítulo e símbolos residuais.
- Extraia imagens relevantes.
- Compare o Markdown final com a fonte para verificar fidelidade.

## Regra de contradição entre fontes

Se uma fonte nova ou uma afirmação do Usuário contradizer conteúdo existente, não escolha um lado nem faça média. Mostre as duas versões com localização exata e espere a decisão do Usuário antes de editar.

## Fechamento padrão de essay único

Skills que editam um essay específico fecham com:

```bash
python scripts/check_wiki.py <slug>
python scripts/fix_lint.py <slug>
```

Aplique correções mecânicas inequívocas e reporte o restante. Use `/organize <slug>` apenas quando o Usuário pedir auditoria completa daquele essay.
