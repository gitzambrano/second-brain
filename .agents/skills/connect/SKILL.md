---
name: connect
description: >
  Expande e repara a malha de conexões (wikilinks em ## Conexões) entre
  essays, concepts, entities e insights — os quatro tipos ao mesmo tempo,
  como peers. Checa conexão que devia existir e não existe, conexão
  quebrada ou mal formatada, e cria conexão nova tanto com página já
  existente quanto com página que ainda não existe (criando a página
  mínima junto). Aceita corpus inteiro (/connect) ou um subconjunto
  (/connect <slugs, pasta, ou tema>). Use quando o Usuário disser "expande
  as conexões", "essa página está bem conectada?", "cria os links que
  faltam", "esse conceito devia linkar com aquele outro", "essas duas
  entidades deviam estar ligadas", "conecta esse insight a algo", ou pedir
  para checar/reparar links quebrados na wiki inteira ou num subconjunto.
allowed-tools: Bash Read Write Edit Glob Grep AskUserQuestion
---
# Connect

Expande e repara **o grafo de conexões** — `## Conexões` de essays, concepts, entities e insights — como unidade própria de trabalho. Trata os quatro tipos de página como peers: concept pode linkar concept, entity pode linkar entity, insight pode linkar essay ou concept. Parte do grafo inteiro e pergunta o que falta nele, em vez de só tocar `## Conexões` de passagem durante a edição de um essay específico.

## Escopo

```
/connect                    → corpus inteiro: todo essay, concept, entity, insight
/connect <slug ou lista>     → só as páginas nomeadas (qualquer mistura dos 4 tipos)
/connect concepts/           → só uma pasta (concepts/, entities/, insights/, essays/)
/connect <tema ou tag>        → só páginas com aquela tag em tags_in_use
```

Se o argumento for ambíguo (casa com mais de uma página/tema), pergunte antes de prosseguir. Corpus inteiro em wiki grande: avise a escala antes de começar ("são N páginas, vou levar um tempo") e ofereça processar em lotes.

## O que este skill reusa (não reimplementa)

- **Wikilink quebrado ou fora do padrão**: detecção via `check_wiki.py` (`DEAD_WIKILINK`, `NON_SLUG_WIKILINK`, `WIKILINK_DISPLAY_COLON`).
- **Termo citado repetidamente sem virar página**, ou **página existente sem link num essay que a cita**: candidatos vêm de `python scripts/check_gaps.py`, que já cobre isso na direção essay→página; reusa a mesma lista como ponto de partida da Parte B e **estende** a lógica para concept↔concept, entity↔entity, e qualquer par envolvendo insight.
- **Órfão reverso** (página sem nenhum essay que a referencie): `find_backlinks.py --orphans`.
- **Quase-duplicata** (duas páginas que parecem a mesma coisa): `check_dedupe.py`, antes de criar qualquer página nova.
- **Nome de página novo**: `check_title.py "Título Proposto"` sempre antes de nomear um arquivo, evita nascer quase-duplicata por grafia diferente.

## Passo a passo

### 1. Preparar

Rode `python scripts/build_index.py` se `wiki/index.json` estiver desatualizado. Rode `python scripts/find_backlinks.py --orphans` para o grafo atual de quem linka quem. Se `qmd status` disponível, prefira `qmd query` para achar páginas tematicamente próximas; sem qmd, `scripts/find_text.py --ignore-case` cobre os quatro tipos numa passada só.

### 2. Parte A — conexões quebradas ou mal formatadas

1. Rode `python scripts/check_wiki.py --json` (ou `check_wiki.py <slug> --json` por página, se o escopo for um subconjunto) e filtre os achados de `DEAD_WIKILINKS`.
2. **Typo óbvio de página existente** (ex: `[[entropi-termodinamica]]` quando a página é `entropia-termodinamica`): corrija direto, mecânico.
3. **Alvo que não corresponde a nada nem a typo óbvio**: não invente nem apague — liste e pergunte o que fazer.
4. **Mal formatado mas não morto** (`WIKILINK_DISPLAY_COLON`, ou sintaxe fora de `[[slug|Título]]`): corrija a forma, mantendo o mesmo alvo e texto visível.
5. **Errado no sentido semântico** (o link existe, aponta para uma página real, mas é a errada): `check_wiki.py` não detecta isso. Ao ler cada página, preste atenção ao contexto ao redor de cada wikilink — se a frase descreve algo que não bate com o título/resumo da página alvo, sinalize como candidato a link errado e pergunte, nunca troque sozinho.

### 3. Parte B — conexões ausentes entre páginas já existentes

Para cada página no escopo, gere candidatos de duas formas e combine:

- **Léxica**: título de outra página do wiki aparece no corpo (nome próprio, negrito, ou já linkado como link externo) sem estar em `## Conexões`.
- **Semântica**: `qmd query "<título/tags da página>"` (ou `find_text.py` com os termos centrais, sem qmd) para achar páginas tematicamente próximas que nunca se mencionam literalmente — comum entre concept↔concept e entity↔entity, onde duas páginas tratam da mesma ideia com vocabulário diferente.

Classifique por confiança:

- **Alta confiança** (nome exato da página-alvo já aparece no texto, só falta o `[[wikilink]]`): aplique direto. Adicione nos dois lados (ver `## Bidirecionalidade`).
- **Média confiança** (relação temática forte via busca semântica, termo não aparece literalmente): agrupe e apresente em lote curto para o Usuário confirmar ou descartar — não aplique sem essa confirmação.
- **Baixa confiança**: descarte sem listar. Ruído satura mais do que ajuda.

### 4. Parte C — conexões com página que ainda não existe

Quando o candidato da Parte B não tem página nenhuma no wiki (nem em `concepts/`, `entities/`, `insights/`, nem como essay) mas aparece com força o bastante para justificar uma:

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

Nunca cole a lista bruta de candidatos. Agrupe:

- **Corrigido automaticamente** (typos, formatação, alta confiança aplicada).
- **Conexões novas — pendente confirmação** (média confiança, lote curto).
- **Páginas novas propostas** (Parte C, com a página mínima que seria criada).
- **Links suspeitos — possível alvo errado** (Parte A, item 5).
- **Descartado como ruído**, só se relevante para calibrar expectativa.

## O que não fazer

Não crie essay nem insight — só `concepts/` e `entities/`, e só como stub mínimo.

Não enriqueça o conteúdo de uma página existente além do necessário para justificar uma conexão nova.

Não aplique conexão de baixa confiança nem página nova sem confirmação do Usuário, mesmo que pareça óbvio.

## Skills relacionadas

- `/gaps` — auditoria só-leitura, essay-cêntrica, nunca aplica; `/connect` cobre o mesmo heurístico de origem mas em todos os tipos de página e aplica direto os casos de alta confiança. Se o Usuário só quer saber o que falta cobrir, a resposta é `/gaps`; se quer a malha de fato expandida e reparada, é `/connect`. Rodar os dois na mesma sessão é redundante para o caso essay→página — prefira `/connect`, que já inclui esse heurístico
- `/chapter` — cria concept/entity a partir de um essay em edição, com conteúdo completo; `/connect` cria a mesma pasta mas como stub mínimo, disparado pela lacuna do grafo
- `/organize` — dono da checagem mecânica de wikilink quebrado (`check_wiki.py`) que `/connect` reusa; órfão reverso (passo 3 de lá) é outra face do mesmo grafo, mas `/organize` só reporta, não conecta. Ofereça `/connect` ao final de um `/organize` de corpus inteiro
- `/expand`, `/absorb` — para aprofundar o conteúdo de uma página depois que `/connect` criou o stub ou a conexão
- `/insight` — `/connect` pode dar a um insight `solta` sua primeira conexão, mas não muda `maturidade:` sozinho — isso continua decisão de `/insight develop`
- `/sweep` — não inclui `/connect` na bateria automática, mas ofereça como próximo passo ao final
