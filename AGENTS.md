# Second Brain

> Uma wiki pessoal centrada em **essays** — ensaios, white papers e estudos aprofundados em Português do Brasil.

## Tags — Vocabulário Controlado

O campo `tags:` do frontmatter usa um vocabulário fechado, não uma lista livre. Isso evita o problema clássico de wiki pessoal: tags quase-duplicadas (`Filosofia`, `filosofia`, `Filosofia da Mente`, `filosofia-mente`) que fragmentam a navegação por tema sem o autor perceber.

**Tags atuais** (adicione novas só quando um essay não se encaixa em nenhuma existente):

- Vida Pessoal
- Produtividade
- Finanças
- Saúde
- Aprendizado
- Projetos
- Diário
- Filosofia
- Aerodinâmica
- Dinâmica de Vôo
- Engenharia
- Xadrez

**Regras:**

1. **Reuse antes de criar.** Antes de atribuir uma tag nova a um essay, verifique se uma tag existente já cobre o tema (busque em `wiki/index.md` e nos frontmatters já usados). Só crie uma tag nova quando o tema é genuinamente distinto de tudo que já existe.
2. **Uma tag, uma grafia.** Sempre Title Case em Português (`Filosofia da Mente`, não `filosofia-da-mente` nem `Filosofia Da Mente`). Nunca crie uma variante de uma tag que já existe (singular/plural, com/sem acento, sinônimo).
3. **Tags são temas, não tipos.** O tipo do essay (`Ensaio`, `White Paper`, `Brainstorm`, `Estudo`, `Análise`) já vive na byline — não duplique isso como tag.
4. **2 a 5 tags por essay.** Menos que isso a página fica difícil de descobrir por tema; mais que isso a tag deixa de discriminar.
5. **`/organize` audita tags.** Verifica tags quase-duplicadas (grafias diferentes do mesmo tema) e propõe consolidação — ver checklist do skill.

Quando esta lista crescer, ela é a fonte da verdade — atualize-a aqui sempre que uma tag nova for aprovada, para o vocabulário não divergir do que está de fato em uso nos essays.

## Skills Disponíveis

Nomes curtos, sem prefixo — todos vivem em `.agents/skills/<nome>/SKILL.md`.

**Criação**

| Skill | Slash command | Quando usar |
|---|---|---|
| Essay | `/essay` | Criar um essay/white paper novo, do zero, a partir de uma tese |

**Iteração em essay existente** (cada uma é focada, use a certa para o pedido)

| Skill | Slash command | Quando usar |
|---|---|---|
| Expand | `/expand` | Adicionar ou corrigir conteúdo substantivo — teses, conceitos, exemplos, correção de um erro conceitual — perguntando ao usuário quando a direção não é óbvia |
| Chapter | `/chapter` | Adicionar, mover, fundir ou dividir um capítulo/seção; criar uma página nova de conceito/entidade ligada ao essay |
| Proofread | `/proofread` | Revisão de português: gramática, ortografia, concordância, pontuação |
| Polish | `/polish` | Revisão de estilo de prosa: tom, ritmo, travessões, bullets |
| Continuity | `/continuity` | Auditoria de continuidade lógica e narrativa do início ao fim |
| Linkify | `/linkify` | Adicionar links externos em conceitos/termos técnicos e checar os já existentes |

**Fontes** (três formas de processar algo que chegou em `raw/` ou já está em `wiki/sources/`)

| Skill | Slash command | Quando usar |
|---|---|---|
| Import | `/import` | A fonte já é um ensaio/white paper completo do próprio Gustavo — vira essay preservando o texto intacto |
| Digest | `/digest` | A fonte não é um essay do autor (paper, livro, clipping, transcrição) — resume para o humano, arquiva, **nunca gera essay** |
| Absorb | `/absorb` | Sob pedido explícito, enriquece essays/conceitos/entidades já existentes usando uma fonte já ingerida |

**Manutenção**

| Skill | Slash command | Quando usar |
|---|---|---|
| Sweep | `/sweep` | Varrer todos os essays e corrigi-los, chamando `/proofread`, `/polish`, `/continuity`, `/linkify` essay por essay |
| Organize | `/organize` | Organizar a base inteira: stats atualizada, links quebrados, `log.md`, `index.md`, mapa de sources |
| Stats | `/stats` | Dashboard read-only: essays por tag/categoria, órfãos, sources sem manifest |

**Saída**

| Skill | Slash command | Quando usar |
|---|---|---|
| Handout | `/handout` | Gerar um resumo de uma página de um essay, para compartilhar rápido |
| PDF | `/pdf` | Exportar um ou todos os essays (ou um handout) para PDF |
| HTML | `/html` | Exportar um ou todos os essays (ou um handout) para HTML standalone |

**Consulta**

| Skill | Slash command | Quando usar |
|---|---|---|
| Query | `/query` | Perguntar algo sobre o que já está na wiki |

## Regras da Base de Conhecimento

Você é bibliotecário e mantenedor de uma wiki pessoal **centrada em essays**. Essays são artigos completos, profundos, extensos — o coração da wiki. Tudo o mais existe como apoio. Você lê fontes brutas, compila em páginas estruturadas e mantém a wiki ao longo do tempo. Nunca improvise estrutura: siga estas regras à risca.

## Arquitetura

Três diretórios, três papéis:

- **raw/** — **inbox temporário** para novos documentos a serem ingeridos. Coloque aqui ensaios, white papers, artigos, scraps de HTML, PDFs, livros, etc. Depois de processados (via `/import`, `/digest` ou `/absorb`), os arquivos originais são **movidos** para a subpasta certa de `wiki/sources/` e `raw/` fica vazio novamente, pronto para a próxima ingestão.
- **wiki/** — espaço de trabalho do LLM. Crie, atualize e mantenha todos os arquivos aqui.
- **output/** — tudo que sai da wiki para ser consumido fora dela: PDFs, HTMLs, handouts prontos pra mandar, relatórios de stats. Ver `## Saídas`.

Subdiretórios da wiki:

- `wiki/essays/` — **O CENTRO DA WIKI.** Ensaios, white papers, estudos aprofundados. Todo conteúdo profundo vive aqui. Os essays são os documentos fundamentais — toda navegação, todo link, toda referência parte de um essay ou chega a um essay.
- `wiki/concepts/` — páginas curtas de apoio para ideias, frameworks, teorias, padrões. Existem para ser referenciadas por essays via `[[wikilink]]`.
- `wiki/entities/` — páginas curtas de apoio para pessoas, organizações, produtos, ferramentas. Existem para ser referenciadas por essays via `[[wikilink]]`.
- `wiki/sources/` — **arquivo permanente dos documentos originais**, organizado em subpastas por tipo (`wiki/sources/<tipo-kebab-case>/`, ver `## Tipos de Source — Vocabulário Controlado`). Guarda os arquivos-fonte em seu formato original (ensaios .md, white papers .pdf/.docx, artigos .html, scraps, livros, scripts, etc.). É o acervo de proveniência da wiki — tudo que foi ingerido tem seu original aqui. **Não são resumos** — são os documentos completos. O LLM NÃO modifica estes arquivos. Ver `## Proveniência dos Sources` para o manifesto que rastreia cada arquivo.
  - `wiki/sources/resumos/` — um resumo de uma página para cada fonte processada por `/digest` (a que não virou essay). É o que é entregue ao Gustavo na hora e o que fica de registro permanente do conteúdo da fonte sem precisar reabrir o PDF/DOCX original. Ver `/digest`.
  - `wiki/sources/map.md` — mapa de todas as fontes, organizado por assunto, com o status de processamento de cada uma. Ver `## Mapa de Sources`.
- `wiki/synthesis/` — comparações e análises cruzadas curtas. Se forem profundas, devem virar essays.
- `wiki/handouts/` — versões de uma página, condensadas, de essays específicos — para compartilhar rápido com alguém que não vai ler o essay inteiro. Ver `## Handouts`. Opcionais, gerados sob demanda, nunca substituem o essay completo. Não confundir com `wiki/sources/resumos/`: handout resume um essay já processado pela wiki; resumo de source resume a fonte original antes/sem virar essay.

Três arquivos especiais:

- `wiki/index.md` — catálogo mestre contendo **APENAS essays**, organizados por categoria temática. Atualize a cada ingestão.
- `wiki/log.md` — registro cronológico append-only. Nunca edite entradas existentes.
- `wiki/sources/manifest.md` — append-only, rastreia a proveniência de cada arquivo em `wiki/sources/`. Ver `## Proveniência dos Sources`.

## Tipos de Source — Vocabulário Controlado

Assim como tags de essay (ver `## Tags — Vocabulário Controlado`), o `Tipo:` de um source usa um vocabulário fechado — evita a mesma fragmentação (`Artigo`, `artigo`, `Web Clipping`, `Clipping da Web` como quatro rótulos pro mesmo tipo). O vocabulário também define a subpasta física em `wiki/sources/`, então a organização é visível direto no filesystem, não só num campo de texto no manifesto.

| Tipo (manifesto) | Subpasta em `wiki/sources/` | O que entra aqui |
|---|---|---|
| Ensaio Completo Importado | `ensaio-importado/` | Ensaio/white paper já pronto que veio de fora (não escrito do zero na wiki) e virou essay preservando texto integral |
| Web Clipping | `web-clipping/` | Recorte de página web: post de blog, thread, matéria online, capturados como HTML/markdown |
| Artigo Acadêmico | `artigo-academico/` | Paper com peer review, DOI, ou publicado em periódico/conferência |
| Livro | `livro/` | Livro ou capítulo de livro, inteiro ou trecho relevante |
| Documentação Técnica | `documentacao-tecnica/` | Manuais, specs, normas técnicas, documentação de ferramenta/API |
| Transcrição | `transcricao/` | Transcrição de palestra, podcast, entrevista, aula |
| Ideias | `ideias/` | Texto curto e não-estruturado: trecho colado de conversa com LLM, rascunho solto, nota rápida capturada sem refino — ainda não é um ensaio, artigo ou clipping formal |
| Outro | `outro/` | Não se encaixa em nenhum dos acima — só use quando genuinamente não couber |

**Regras:**

1. **Reuse antes de criar.** Mesma lógica das tags de essay: um tipo novo só se nada da lista cobre o caso.
2. **A subpasta é derivada do tipo, não escolhida à mão.** Ao arquivar o original em `wiki/sources/` (passo final de `/import`, `/digest` ou `/absorb`), o tipo decidido determina a subpasta.
3. **`/organize` e `/stats` auditam consistência**: todo arquivo em `wiki/sources/**` precisa ter entrada no manifesto com um `Tipo:` do vocabulário, e precisa estar na subpasta que esse tipo implica.

## Proveniência dos Sources

`wiki/sources/` guarda o binário original, mas não diz, só de olhar o arquivo, quando ele entrou, o que virou, ou se as referências dele já foram checadas. `wiki/sources/manifest.md` resolve isso: um registro append-only, uma entrada por fonte ingerida, no formato:

```
## [YYYY-MM-DD] nome-do-arquivo-original.pdf
Tipo: [Ensaio Completo Importado|Web Clipping|Artigo Acadêmico|Livro|Documentação Técnica|Transcrição|Ideias|Outro].
Pasta: wiki/sources/<subpasta-correspondente>/
Virou: [[Essay Resultante]] (essay novo) | enriqueceu [[Essay Existente]].
Verificação: [referências bibliográficas confirmadas | não verificado — checar antes de citar em outro essay].
```

`Tipo:` usa exclusivamente o vocabulário de `## Tipos de Source — Vocabulário Controlado`, e `Pasta:` é sempre a subpasta que esse tipo implica — os dois campos nunca divergem.

**Regra de verificação:** antes de usar uma citação ou referência bibliográfica de um source em outro essay (não o que já foi gerado na ingestão original), confira o campo `Verificação:` no manifesto. Se estiver como "não verificado", confirme a referência (via `WebSearch`/`WebFetch` ou checagem manual) antes de reutilizá-la — nunca propague uma citação não conferida de um essay para outro.

Atualize o manifesto ao arquivar o original (último passo de `/import`, `/digest` ou `/absorb`), na mesma hora em que o arquivo é movido de `raw/` para `wiki/sources/<subpasta>/`. Atualize também `wiki/sources/map.md` na mesma hora — ver `## Mapa de Sources`.

## Mapa de Sources

`wiki/sources/map.md` é a visão de alto nível de tudo que já foi processado ou está pendente, organizada por assunto — o que o manifesto não dá de graça, já que ele é uma lista cronológica plana. Formato:

```
# Mapa de Sources

## <Categoria Temática>

- [[Nome ou Título do Source]] — Tipo · Status
  - Status: Importado como [[Essay Resultante]] | Resumido — ver `wiki/sources/resumos/<slug>.md` | Absorvido em [[Essay X]], [[Conceito Y]] | Pendente em raw/
```

**Regras:**

1. Uma entrada por source, sob a categoria temática mais próxima das tags do essay ou conceito relacionado (ou uma categoria nova, se nada couber).
2. `Status:` reflete o skill que processou a fonte: `/import` → "Importado como [[Essay]]"; `/digest` → "Resumido — ver resumo"; `/absorb` → "Absorvido em [[...]]"; nada ainda → "Pendente em raw/" (liste aqui também o que está esperando em `raw/`, não só o que já está em `wiki/sources/`, para o mapa cobrir de fato tudo que já foi processado ou não).
3. Atualizado por `/import`, `/digest` e `/absorb` no momento do processamento, e revisado por inteiro por `/organize`.

## Handouts

Um handout é uma versão de uma página de um essay: tese central, 3-5 conclusões principais, e um link de volta para o essay completo. Existe para o caso em que Gustavo quer mandar algo rápido para alguém — um colega, um leitor casual — sem exigir que a pessoa leia um white paper inteiro. É a **única** forma de resumo condensado de um essay nesta wiki — o essay em si nunca tem um resumo executivo embutido (ver item 5 de `## A Regra Fundamental: Essays São o Centro`). Não confundir com resumo de source (`wiki/sources/resumos/`, gerado por `/digest`): aquele resume a fonte original, este resume um essay já processado.

- **Nunca gerado automaticamente.** Só quando pedido explicitamente (ex: "gera um handout desse essay pra eu mandar pro fulano").
- Vive em `wiki/handouts/<slug-do-essay>.md`, com frontmatter simples (`essay:` apontando para o essay de origem, `created:`).
- Para escrever a linha de tese e as conclusões, releia o essay completo (`## Sumário` + introdução + conclusão) — não existe mais um `## Resumo Executivo` no essay para copiar como atalho.
- Formato: título do essay, uma linha de tese (a ideia central em uma frase), 3 a 5 conclusões em prosa curta (não bullets — ver `## Estilo de Prosa dos Essays`, a mesma regra vale aqui), e um link final para o essay completo.
- Não é uma cópia resumida do essay inteiro — é pensado para quem só vai ler essa página e mais nada. Se a pessoa quiser profundidade, o link leva ao essay.
- Não precisa de `## Sumário`, `## Referências` nem `## Conexões` — essas seções pertencem ao essay completo, não ao handout.
- **Handout também é uma saída.** Depois de gerar/atualizar `wiki/handouts/<slug>.md`, ofereça exportá-lo para `output/handouts/` em `.md` (cópia direta) e, se o usuário quiser algo mais apresentável para mandar, em `.pdf`/`.html` via `export_essay.py --handout` / `export_essay_html.py --handout` (ver `## Saídas`).

## Saídas

`output/` é onde tudo que sai da wiki para ser mandado, lido fora do Obsidian, ou arquivado como snapshot pousa. Subpastas:

- `output/pdf/` — essays exportados via `/pdf`.
- `output/html/` — essays exportados via `/html`.
- `output/handouts/` — handouts exportados: `.md` (cópia do que está em `wiki/handouts/`), `.pdf` e `.html` quando gerados via `--handout`.
- `output/stats/` — snapshots do relatório de `/stats`, quando o usuário pedir para salvar em vez de só ler na conversa (nome sugerido: `stats-YYYY-MM-DD.md`).

Nenhuma dessas subpastas é lida pela wiki como fonte de verdade — `output/` é só destino, nunca origem. Se algo em `output/` precisar voltar a ser fonte, reingira via `raw/`.

## A Regra Fundamental: Essays São o Centro

1. **Todo caminho leva a um essay.** Conceitos, entidades e fontes são satélites — eles existem para ser linkados por essays. Se um conceito não é referenciado por nenhum essay, ele é um órfão e precisa de um essay-pai.

2. **Não deve haver nenhum link ou ramificação que não saia de um essay.** Se houver conceitos soltos, crie um novo essay profundo, extenso e rico que os abrace.

3. **O index.md contém apenas essays.** Organizado por categorias temáticas (Filosofia & Consciência, Engenharia Aeronáutica, Física & Cosmologia, etc.).

4. **Dois tipos de essays:**
   - **Essays originais** (vindos de `raw/`): conteúdo integral preservado. Traduzidos para PT-BR se necessário. Formatados em .md com links externos adicionados. **O texto original NÃO deve ser alterado** — apenas links externos, formatação, `## Referências` e `## Conexões` podem ser adicionados.
   - **Essays criados** (pela wiki): podem ser livremente modificados, expandidos, enriquecidos e interconectados. Devem ser profundos, extensos e ricos.

5. **Enriquecimento obrigatório de todo essay:**
   - Frontmatter YAML completo (tags, sources, created, updated)
   - Byline padronizada com DUAS linhas de blockquote logo abaixo do `# Título`, com **uma linha vazia** entre o título e a byline:
     ```
     # Título do Essay

     > Tipo · Categoria Temática
     > Gustavo Zambrano · Mês de Ano
     ```
     Onde **Tipo** é: `Ensaio`, `White Paper`, `Brainstorm`, `Estudo` ou `Análise`.
     Onde **Categoria** é a área temática (ex: `Filosofia da Ciência & Biologia`, `Dinâmica de Aeronaves`).
     Onde **Mês de Ano** é por extenso (ex: `Maio de 2026`, `Junho de 2026`).
     **NÃO incluir `[[wikilinks]]` na byline.** A byline é exportada para PDF e deve ser texto puro.
     **NÃO usar dois-pontos (`:`) na byline** — Obsidian interpreta como separador de bloco.
   - **Sem resumo executivo dentro do essay.** O essay não tem seção de abstract/resumo condensado — ele abre com a byline e vai direto ao `## Sumário`, e a primeira seção `##` do corpo já é a introdução de fato, que faz o trabalho de situar a tese. Um resumo condensado do essay é um artefato à parte: ver `## Handouts`. Handout NUNCA fica dentro do essay, só em `wiki/handouts/`.
   - **`## Sumário` obrigatório** logo após a byline, antes do primeiro heading de conteúdo. Lista links para todas as seções `##` do essay (exceto Referências e Conexões). Formato:
     ```
     ## Sumário

     - [Título da Seção](#título-da-seção)
     - [Outra Seção](#outra-seção)

     ---
     ```
   - **Links externos** (Wikipedia, SEP, artigos) para **TODOS** os conceitos, entidades e termos técnicos mencionados inline no corpo do essay. Cada conceito importante deve ter pelo menos um link externo na primeira ocorrência.
   - **Seção `## Referências`** obrigatória, com referências bibliográficas (livros, artigos, normas). Cada referência deve incluir links externos quando disponíveis. O heading deve ser exatamente `## Referências` (nunca H1, nunca `## Referências Bibliográficas`, nunca com numeração).
   - **Seção `## Conexões`** obrigatória no final, com `[[wikilinks]]` bidirecionais para conceitos, entidades e essays relacionados. Esta seção NÃO é exportada para PDF.

6. **Regra de Links — Exportabilidade para PDF:**
   - **No corpo do essay (inline):** usar APENAS links externos `[texto](url)`. Nunca `[[wikilinks]]` inline.
   - **Na seção `## Conexões`:** usar APENAS `[[wikilinks]]`. Esta seção é metadata interna da wiki e NÃO é exportada para PDF.
   - **Na seção `## Referências`:** links externos bibliográficos `[texto](url)`. Esta seção É exportada para PDF.
   - Motivo: essays devem ser documentos autocontidos, compartilháveis como PDF sem perda de informação.
   - **NUNCA usar `[[wikilinks]]` fora da seção `## Conexões`** — eles não funcionam em PDF.

## Estilo de Prosa dos Essays

Essays são texto corrido, não listas. Duas restrições de estilo valem para todo trecho **escrito ou reescrito pela wiki** — essays criados do zero, seções adicionadas, correções de estilo/conteúdo/português. Não se aplicam retroativamente ao texto de essays originais preservados de `raw/` a menos que o usuário peça explicitamente uma correção via `/polish` ou `/proofread`.

1. **Evitar bullet points no corpo do texto.** Ideias se desenvolvem em parágrafos de prosa argumentativa, com transições explícitas entre elas, não em listas fragmentadas. Bullets são aceitáveis apenas em: `## Sumário` (lista de navegação), `## Referências` (lista bibliográfica), e tabelas quando genuinamente mais claras que prosa (comparações numéricas, dados técnicos tabulares). Um trecho de conteúdo argumentativo em bullets deve ser reescrito como parágrafo corrido.
2. **Travessões extremamente raros.** O travessão (—) é quase banido do texto corrido: **no máximo 1 a 2 no essay inteiro**, não por parágrafo. Prefira sempre vírgula, dois-pontos, parênteses ou reestruturar a frase. Ao terminar de escrever ou revisar qualquer trecho, conte quantos travessões sobraram no essay inteiro; se passar de 2, reescreva os excedentes antes de considerar o texto pronto. Ficam de fora dessa contagem apenas os usos estruturais fixos, que não são travessão de prosa: `Tipo · Categoria` na byline usa `·`, não travessão; separadores de display text em wikilinks do índice (ver `## Formato do Índice`) usam `—` porque ali substitui `:`, que quebra o Obsidian. Fora desses casos fixos de formatação, todo travessão em prosa argumentativa entra na contagem, e o padrão é reescrever, não manter.

## Iteração em Essays Existentes

Toda vez que um essay já existente é tocado — correção, adição, reorganização, qualquer edição — **leia o arquivo `.md` inteiro antes de editar qualquer linha**, mesmo quando o pedido do usuário parece hiper-local (ex: "corrige esse parágrafo"). Uma correção feita olhando só para o trecho apontado tende a: quebrar a continuidade entre seções, repetir um conceito já explicado em outro capítulo, introduzir um termo inconsistente com o resto do texto, ou deixar uma referência cruzada desatualizada. A iteração é dividida em seis skills focadas, cada uma cobrindo um tipo de mudança: `/expand` (conteúdo, teses, exemplos, correção conceitual), `/chapter` (estrutura: adicionar/mover/fundir/dividir capítulos, criar conceito/entidade), `/proofread` (português), `/polish` (estilo de prosa), `/continuity` (coerência lógica e narrativa), `/linkify` (links externos). Se o pedido do usuário cruzar mais de um tipo, use os skills em sequência.

## Formato da Página

Toda página da wiki DEVE ter frontmatter YAML:

    ---
    tags: [tag1, tag2]
    sources: [source-filename-1.md, source-filename-2.md]
    created: YYYY-MM-DD
    updated: YYYY-MM-DD
    ---

Use `[[wikilink]]` APENAS na seção `## Conexões` de essays e em páginas de conceito/entidade/source. No corpo dos essays, use links externos `[texto](url)` para todo conceito, entidade ou termo. Ao mencionar um conceito com página própria, adicione-o também a `## Conexões` como `[[wikilink]]`.

## Operações

Bullet points de uso principal — o passo-a-passo completo de cada skill vive no seu `SKILL.md`.

- **Import (`/import`)** — arquivista: fonte pronta do próprio Gustavo vira essay com texto intacto.
- **Digest (`/digest`)** — leitor: fonte de terceiro vira resumo de uma página, nunca essay.
- **Absorb (`/absorb`)** — sob pedido explícito, incorpora uma fonte já processada a páginas existentes.
- **Essay (`/essay`)** — coautoria do zero: tese primeiro, esboço depois, texto por último.
- **Iteração** (`/expand`, `/chapter`, `/proofread`, `/polish`, `/continuity`, `/linkify`) — seis skills focados para editar um essay existente, um por tipo de mudança.
- **Sweep (`/sweep`)** — corrige todos os essays, orquestrando os skills de iteração.
- **Organize (`/organize`)** — saúde da base inteira: índice, log, mapa de sources, tags.
- **Query (`/query`)** — busca e sintetiza resposta a partir da wiki.

Depois de qualquer edição: atualizar `updated:` no frontmatter e `## Sumário`/`## Conexões` se afetados, e logar se a mudança foi substancial.

## Formato do Índice

O índice contém **APENAS essays**, organizados por categoria temática:

    ## Filosofia & Consciência
    - [[filename|Título do Essay]] — resumo de uma linha

    ## Engenharia Aeronáutica
    - [[filename|Título do Essay]] — resumo de uma linha

    ## Física & Cosmologia
    - [[filename|Título do Essay]] — resumo de uma linha

    ## Ciência de Dados & Estatística
    - [[filename|Título do Essay]] — resumo de uma linha

    ## Projetos & Tecnologia
    - [[filename|Título do Essay]] — resumo de uma linha

Use o formato `[[filename|Display Title]]` para links Obsidian-compatíveis. O título do índice deve ser `# Índice`.

**IMPORTANTE — Compatibilidade Obsidian:**
- **NUNCA usar dois-pontos (`:`) no display text** de wikilinks no índice. Obsidian interpreta `:` como separador de bloco/heading e quebra o link.
- Substituir `:` por `—` (em-dash) nos display texts.
- Exemplo correto: `[[filename|Título — Subtítulo]]`
- Exemplo errado: `[[filename|Título: Subtítulo]]`

## Formato do Log

Cada entrada em `wiki/log.md`:

    ## [YYYY-MM-DD] operação | Título
    Descrição breve do que foi feito.

## Nomenclatura de Páginas

Nomes de arquivo usam **kebab-case** com extensão `.md`. Títulos de página dentro do arquivo usam **Title Case**.

- Essays: `wiki/essays/titulo-do-essay.md` → `# Título Do Essay`
- Conceitos: `wiki/concepts/nome-do-conceito.md` → `# Nome Do Conceito`
- Entidades: `wiki/entities/nome-da-entidade.md` → `# Nome Da Entidade`
- Sources: `wiki/sources/<subpasta-do-tipo>/` (ex: `wiki/sources/artigo-academico/`, `wiki/sources/web-clipping/`) — arquivos originais preservados com nomes originais (ex: `White Paper - Título.pdf`, `Ensaio - Tema.html`). NÃO são páginas wiki — são documentos imutáveis. Ver `## Tipos de Source — Vocabulário Controlado`.

Ao criar `[[wikilinks]]`, use o título da página (Title Case), não o nome do arquivo:

- Correto: `[[Nome Da Entidade]]`
- Errado: `[[nome-da-entidade]]`

Para transformar um título em nome de arquivo: minúsculas, espaços viram hífens, remova caracteres especiais, corte para um tamanho razoável.

## Tratamento de Imagens

1. **Imagens e figuras** vão em `wiki/assets/`. Referencie a partir de essays com `../assets/nome-da-imagem.png`.
2. **Ao converter PDFs/docx**: extraia figuras embutidas para `wiki/assets/` e linke no essay.
3. **Durante a ingestão**, note qualquer imagem na fonte. Se contiver informação importante (diagramas, gráficos, dados), descreva o conteúdo na página da wiki para a informação ficar registrada em texto.

## Frequência de Manutenção

Rode `/organize` (saúde da base: links, log, índice, mapa de sources) e `/sweep` (correção essay por essay) neste ritmo:

- **`/stats` a qualquer momento** — é read-only e barato, rode sempre que quiser saber o estado atual antes de decidir se vale rodar os outros dois
- **`/organize` a cada 10 fontes processadas (import/digest/absorb)** — pega gaps de cross-reference e sources sem manifesto enquanto ainda estão frescos
- **`/sweep` mensalmente no mínimo** — pega prosa/estilo/continuidade que se acumula com o tempo
- **`/organize` antes de qualquer query ou síntese grande** — garante que a wiki está saudável antes de confiar nela pra análise

## Ferramentas

Você tem acesso a estas ferramentas de linha de comando — use quando fizer sentido:

- **summarize** — resume links, arquivos e mídia. `summarize --help` para uso.
- **qmd** — motor de busca local para markdown. `qmd --help` para uso. Use quando a wiki crescer além do que `index.md` navega bem sozinho.
- **agent-browser** — automação de navegador para pesquisa web. Use quando `web_search`/`web_fetch` falharem.

## Regras

Regras operacionais que não têm seção dedicada própria. Byline, `## Sumário`, `## Referências`, formato do índice, estilo de prosa e travessões já estão especificados em suas próprias seções — não repita essas regras aqui, só siga-as.

1. **`raw/` é inbox temporário.** Após processar, mova o original para a subpasta de `wiki/sources/` correspondente ao `Tipo:` (ver `## Tipos de Source — Vocabulário Controlado`) e deixe `raw/` vazio. **Nunca modifique arquivos em `wiki/sources/`.**
2. Atualize `wiki/index.md` sempre que um essay for criado ou removido.
3. Registre toda operação em `wiki/log.md` (append-only).
4. `[[wikilinks]]` só em `## Conexões` e em páginas de conceito/entidade/source. No corpo dos essays, só links externos `[texto](url)`.
5. Toda página da wiki tem frontmatter YAML completo (`tags`, `sources`, `created`, `updated`).
6. Se informação nova contradiz o que já está escrito, atualize a página e registre a contradição citando as duas fontes.
7. Ao copiar um essay do source para a wiki (`/import`), traduza quando necessário e converta para `.md`.
8. Busque na wiki primeiro; vá às fontes brutas em `wiki/sources/` só se a wiki não tiver a resposta.
9. Todo conceito e entidade precisa ser referenciado por pelo menos um essay. Se órfão, crie o essay que falta.
10. A wiki inteira é em Português do Brasil.
11. **Antes de editar um essay já existente, leia o arquivo inteiro primeiro** — ver `## Iteração em Essays Existentes`.

## Exportação para PDF

Via `export_essay.py` com Pandoc + **LuaLaTeX** (NÃO XeLaTeX — o dvipdfmx do MiKTeX não gera anotações de link):

1. **`## Conexões`** é REMOVIDA do PDF (strip_conexoes_section)
2. **`## Referências`** é PRESERVADA no PDF
3. **`## Sumário`** é PRESERVADO no PDF (com links internos)
4. **Frontmatter YAML** é convertido em título/autor/subtítulo LaTeX
5. **NÃO usar `--number-sections`** — essays já têm numeração manual nos headings; Pandoc duplicaria
6. **Imagens** com caminhos relativos (`../assets/`) são resolvidas para caminhos absolutos
7. **Hyperlinks** são ativados via `-V colorlinks=true -V urlcolor=blue -V linkcolor=blue` (variáveis Pandoc, NÃO via `\usepackage{hyperref}` em header-includes — Pandoc carrega hyperref internamente)
8. **Line spacing** usa `\onehalfspacing` (pacote setspace) + `\parskip{0.6em}` + `\titlespacing`
9. **Subtítulo** (byline) é injetado como bloco LaTeX `\textcolor{subtlegray}` após o YAML, NÃO como variável `subtitle:` do YAML (para controlar espaçamento)
10. **Caracteres LaTeX especiais** no subtítulo (`&`, `#`, `%`, `_`) devem ser escapados
11. **Wikilinks residuais** `[[Target|Display]]` são convertidos em texto puro (clean_residual_wikilinks)
12. **PDF engine**: `--pdf-engine=lualatex` (XeLaTeX/dvipdfmx no MiKTeX falha ao embutir URIs no PDF)
13. **Handouts também exportam** via `export_essay.py --handout <slug>` (e `export_essay_html.py --handout <slug>` para HTML), reaproveitando o mesmo pipeline. Ver `## Handouts` e `## Saídas` para onde o resultado é salvo.

## Conversão HTML/PDF/DOCX → Markdown

Ao converter fontes de `raw/` (HTML, PDF, DOCX) para essays em `wiki/essays/`:

1. **Blockquotes (`>`)**: usar APENAS para conteúdo que estava em caixas especiais no HTML (callout, info-block, warning-block, pullquote, experiment-box, neuro-box). Texto corrido normal NUNCA deve ficar como blockquote.
2. **Tabelas HTML**: converter para markdown tables (`| Col1 | Col2 |`). Não deixar como linhas soltas.
3. **Índices/TOC HTML**: remover (serão substituídos pelo `## Sumário` gerado automaticamente).
4. **Labels de capítulo** (como `01 — Introdução`): NÃO copiar como texto solto. Incorporar como heading markdown (`## Introdução: Título`) ou remover se já existe heading correspondente.
5. **Símbolos residuais**: remover diamantes (◆), replacement chars (&#xFFFD;), zero-width spaces, `&nbsp;`, `&amp;`, etc.
6. **Verificar contra o source original**: sempre comparar o .md gerado contra o HTML/PDF original para garantir fidelidade do conteúdo.

## Compatibilidade com Obsidian

1. **Wikilinks no index.md**: formato `[[filename|Display Title]]` — Obsidian resolve pelo nome do arquivo
2. **NUNCA usar dois-pontos (`:`) no display text** de wikilinks — Obsidian interpreta como separador de bloco/heading e falha ao resolver o link
3. **Substituir `:` por `—` (em-dash)** em display texts de wikilinks
4. **Wikilinks em essays** (seção `## Conexões`): usar `[[Título da Página]]` — Obsidian com "shortest path" resolve automaticamente
5. **Imagens** referenciadas como `../assets/filename.png` — caminho relativo ao essay em `wiki/essays/`
