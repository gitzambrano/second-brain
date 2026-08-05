---
name: connect
description: >
  Expande e repara a malha de conexões (wikilinks em ## Conexões) entre
  essays, concepts, entities e insights — os quatro tipos ao mesmo tempo,
  como peers. Invoca /gaps internamente como primeiro passo para
  identificar candidatos (mecânico, léxico, semântico) e age sobre eles:
  corrige link quebrado ou mal formatado, aplica conexão nova de alta
  confiança, propõe o resto, e cria página mínima quando o candidato não
  tem nenhuma ainda. Aceita corpus inteiro (/connect) ou um subconjunto
  (/connect <slugs, pasta, ou tema>). Use quando o Usuário disser "expande
  as conexões", "essa página está bem conectada?", "cria os links que
  faltam", "esse conceito devia linkar com aquele outro", "essas duas
  entidades deviam estar ligadas", "conecta esse insight a algo", ou pedir
  para checar/reparar links quebrados na wiki inteira ou num subconjunto.
allowed-tools: Bash Read Write Edit Glob Grep AskUserQuestion
---
# Connect

Expande e repara **o grafo de conexões** — `## Conexões` de essays, concepts, entities e insights — como unidade própria de trabalho. Trata os quatro tipos de página como peers: concept pode linkar concept, entity pode linkar entity, insight pode linkar essay ou concept. `/connect` é a camada de **ação**: a identificação (as três camadas — mecânica, léxica, semântica) é trabalho de `/gaps`, que este skill invoca como passo 1, nunca reimplementa por conta própria.

## Escopo

```
/connect                    → corpus inteiro: todo essay, concept, entity, insight
/connect <slug ou lista>     → só as páginas nomeadas (qualquer mistura dos 4 tipos)
/connect concepts/           → só uma pasta (concepts/, entities/, insights/, essays/)
/connect <tema ou tag>        → só páginas com aquela tag em tags_in_use
```

Se o argumento for ambíguo (casa com mais de uma página/tema), pergunte antes de prosseguir. Corpus inteiro em wiki grande: avise a escala antes de começar ("são N páginas, vou levar um tempo") e ofereça processar em lotes.

## O que este skill reusa (não reimplementa)

- **Toda a identificação de candidatos** — mecânica, léxica, semântica — é `/gaps`, invocado no passo 1 com o mesmo argumento de escopo recebido aqui. `/connect` nunca roda `check_gaps.py` nem `qmd query` de forma independente; consome a lista que `/gaps` já produziu.
- **Órfão reverso** (página sem nenhum essay que a referencie): `find_backlinks.py --orphans`.
- **Quase-duplicata** (duas páginas que parecem a mesma coisa): `check_dedupe.py`, antes de criar qualquer página nova.
- **Nome de página novo**: `check_title.py "Título Proposto"` sempre antes de nomear um arquivo, evita nascer quase-duplicata por grafia diferente.

## Passo a passo

### 1. Invocar /gaps

Chame `/gaps` com o mesmo argumento de escopo recebido por `/connect` (corpus inteiro, slug, pasta ou tema). Isso devolve a lista das três camadas: mecânico (links quebrados/mal formatados), léxico (termo sem página, página sem link), semântico (pares tematicamente próximos sem menção literal), já classificados por confiança. As seções 2-4 abaixo agem sobre essa lista — não gere candidato novo aqui.

Se `wiki/index.json` estiver desatualizado, rode `python scripts/build_index.py` antes (necessário pra `check_title.py` e pro vocabulário de tags na Parte C).

### 2. Parte A — conexões quebradas ou mal formatadas

Age sobre o achado mecânico de `/gaps`:

1. **Typo óbvio de página existente** (ex: `[[entropi-termodinamica]]` quando a página é `entropia-termodinamica`) — mesmo candidato que `/gaps` já sinalizou como alta confiança: corrija direto, mecânico. (`/organize` passo 15 cobre o mesmo caso; rodar os dois em sequência é redundante, não incorreto.)
2. **Alvo que não corresponde a nada nem a typo óbvio**: não invente nem apague — liste e pergunte o que fazer.
3. **Mal formatado mas não morto** (`WIKILINK_DISPLAY_COLON`, ou sintaxe fora de `[[slug|Título]]`): corrija a forma, mantendo o mesmo alvo e texto visível.
4. **Errado no sentido semântico** (o link existe, aponta para uma página real, mas é a errada): isso `/gaps` não cobre — exige ler o contexto ao redor de cada wikilink válido durante esta passada, não uma auditoria em lote separada. Se a frase descreve algo que não bate com o título/resumo da página alvo, sinalize como candidato a link errado e pergunte, nunca troque sozinho.

### 3. Parte B — conexões ausentes entre páginas já existentes

Age sobre os achados léxico (Parte 2) e semântico de `/gaps`, já classificados por confiança:

- **Alta confiança** (nome exato da página-alvo já aparece no texto, só falta o `[[wikilink]]`): aplique direto. Adicione nos dois lados (ver `## Bidirecionalidade`).
- **Média confiança** (relação temática forte via busca semântica, termo não aparece literalmente): agrupe e apresente em lote curto para o Usuário confirmar ou descartar — não aplique sem essa confirmação.
- **Baixa confiança**: `/gaps` já descartou isso antes de te devolver a lista — nada a fazer aqui.

### 4. Parte C — conexões com página que ainda não existe

Age sobre o achado léxico Parte 1 de `/gaps` (termo sem página, candidato a `concepts/` ou `entities/`):

1. Rode `python scripts/check_title.py "Título Proposto"` antes de decidir o nome do arquivo.
2. Decida a pasta certa pela tabela `## Onde as coisas vão` de `conventions/SKILL.md`: ideia/framework sem tese própria → `concepts/`; pessoa/obra/instituição nomeada → `entities/`. Nunca crie essay novo nem insight novo — se o candidato é grande o bastante para isso, pare e sugira a rota certa em vez de criar você mesmo.
3. Crie a página **mínima**: frontmatter completo (`tags` do vocabulário controlado, `sources: []`, `created`/`updated`), um parágrafo curto e denso que justifique a página (não um verbete enciclopédico completo), e `## Conexões` já linkando de volta a(s) página(ns) de origem.
4. Isso sempre é apresentado como lote para aprovação antes de escrever — nunca crie página nova sem o Usuário confirmar, mesmo em alta confiança léxica.

### 5. Bidirecionalidade

Toda conexão nova é nos dois sentidos por padrão: se A ganha `[[B]]`, B ganha `[[A]]` de volta. Exceção: entidades-hub citadas por muitas páginas (ex: uma entity de pessoa referenciada por 15 essays) — adicionar todos de volta lotaria `## Conexões` da entity. Nesse caso, adicione o link em A normalmente, mas **avise** em vez de aplicar o lado de volta automaticamente, e pergunte se o Usuário quer mesmo listar todos (`find_backlinks.py "Título"` mostra rápido quantos já apontam pra lá antes de decidir).

### 6. Fechar

Para cada página tocada (link corrigido, conexão nova, ou página nova criada):

```bash
python scripts/check_wiki.py <slug>
python scripts/fix_lint.py <slug>
```

Se alguma página nova foi criada (Parte C): `python scripts/build_index.py`. Se o escopo foi corpus inteiro, rode `python scripts/build_graph.py` ao final para refletir as conexões novas no grafo, e ofereça abrir `output/graph/graph.html`.

Log:

```
## [YYYY-MM-DD] connect | Resumo do escopo processado
N links corrigidos, M conexões novas aplicadas, K páginas novas criadas.
```

(Escopo único: `## [YYYY-MM-DD] connect | Título da Página`.)

## Comunicar

Nunca cole a lista bruta de candidatos de `/gaps`. Agrupe:

- **Corrigido automaticamente** (typos, formatação, alta confiança aplicada).
- **Conexões novas — pendente confirmação** (média confiança, lote curto).
- **Páginas novas propostas** (Parte C, com a página mínima que seria criada).
- **Links suspeitos — possível alvo errado** (Parte A, item 4).
- **Descartado como ruído**, só se relevante para calibrar expectativa.

## O que não fazer

Não crie essay nem insight — só `concepts/` e `entities/`, e só como stub mínimo.

Não enriqueça o conteúdo de uma página existente além do necessário para justificar uma conexão nova.

Não aplique conexão de baixa confiança nem página nova sem confirmação do Usuário, mesmo que pareça óbvio.

Não rode a identificação por conta própria — isso é sempre `/gaps` (passo 1). Se o passo 1 falhar ou vier vazio, diga isso ao Usuário em vez de gerar candidatos por fora do fluxo.

## Skills relacionadas

- `/gaps` — identificação (sempre invocado como passo 1); `/connect` age sobre a lista
- `/chapter` — cria concept/entity com conteúdo completo; `/connect` cria stub mínimo
- `/organize`, `/expand`, `/absorb`, `/insight`, `/sweep`
