---
name: conventions
description: >
  Referência central de estilo e formatação da wiki: onde cada tipo de
  conteúdo vai (tabela canônica de pastas), tipos de source e sua
  subpasta física, frontmatter, byline, Sumário/Referências/Conexões,
  regra de links (exportabilidade PDF), estilo de prosa, nomenclatura,
  imagens, compatibilidade Obsidian, conversão de fontes e regra de
  contradição entre fontes. Não tem fluxo próprio — outras skills
  (essay, expand, chapter, proofread, polish, continuity, linkify,
  import, digest, absorb, handout, organize, sweep, pdf, html) leem
  este arquivo para saber o formato exato a produzir e em que pasta
  salvar. Consulte também quando o Usuário perguntar "qual é a regra
  de X" ou "onde isso deveria ficar" sobre a wiki.
allowed-tools: Read
---
# Conventions

**[leitura]** Fonte única das regras de formatação e estilo — não executa nada. Toda skill que grava ou edita conteúdo segue o que está aqui. Mudou uma regra, muda só neste arquivo.

## Onde as coisas vão — tabela canônica

| Pasta | Contém | Quem escreve | Quando |
| ------------------------- | --------------------------------------------------------------------------- | ------------------------------------------------------------------------------ | ------------------------------------------------------------------- |
| `wiki/essays/` | Ensaio/white paper completo, tese sustentada do início ao fim | `/essay`, `/import` | Ideia já é (ou virou, via`/insight promote`) argumento completo |
| `wiki/concepts/` | Definição/explicação curta de um conceito, sem tese própria | `/essay`, `/expand`, `/absorb`, `/digest`, `/chapter` | Termo citado sem página própria |
| `wiki/entities/` | Página curta sobre pessoa/obra/instituição nomeada | mesmas skills que concepts | Entidade nomeada sem página própria |
| `wiki/insights/` | Fragmento denso de ideia — semente, síntese, observação, mini-argumento | `/insight` (também via `/query`, que passa a ideia para `/insight add`) | Ideia nova sem lar, não é essay nem concept/entity |
| `wiki/sources/<tipo>/` | Cópia/referência do documento original, por tipo | `/import`, `/digest`, `/absorb` (triagem via `/scout`) | Toda fonte processada, sempre |
| `wiki/sources/resumos/` | Resumo de uma página por fonte processada | `/digest` | Toda vez que uma fonte é resumida |
| `wiki/handouts/` | Versão de uma página de um essay já existente | `/handout` | Sempre derivado, sob demanda |
| `wiki/assets/` | Imagens/figuras referenciadas por essays | `/import`, `/digest`, `/absorb` | Fonte processada tem figura embutida |
| `wiki/book-chapters/` | Reservado para projeto de livro futuro | — | Não usar ainda |
| `plan/plano.md` | Pendência de longo prazo | `/plan` | Intenção de trabalhar algo depois, nunca conteúdo de wiki |
| `wiki/status.md` | Snapshot da sessão atual | `/status` | Ponte entre sessões |

Regra geral: tese própria → `essays/`. Definição sem tese → `concepts/`/`entities/`. Insight sem lar → `insights/`. Material bruto de terceiros → `sources/`.

## Frontmatter

```yaml
---
tags: [tag1, tag2]
sources: [source-filename-1.md, source-filename-2.md]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

Essays têm dois campos a mais: `status: draft | maduro | finalizado` (ver `## Status de essay`) e `summary:` (resumo usado por `build_index.py` e `build_graph.py`). O valor de `summary:` deve estar SEMPRE entre aspas duplas (`summary: "..."`), para evitar quebras no parser YAML quando houver dois-pontos (`:`) ou caracteres especiais. O valor de `summary:` deve estar SEMPRE entre aspas duplas (`summary: "..."`), para evitar quebras no parser YAML quando houver dois-pontos (`:`) ou caracteres especiais.

## Tags — Vocabulário Controlado

Campo `tags:` (essay/concept/entity/insight) e `Tags:` (`wiki/sources/manifest.md`, `wiki/sources/map.md`): um único vocabulário fechado, consolidado em `tags_in_use` de `wiki/index.json`.

1. **Reuse antes de criar** — cheque `tags_in_use` (rode `build_index.py` primeiro se desatualizado).
2. **Uma tag, uma grafia** — Title Case em Português, nunca variante (singular/plural, acento, sinônimo) de tag existente.
3. **Tags são temas, não tipos** — tipo do essay/source já vive na byline/`Tipo:`, nunca em `tags`/`Tags:`.
4. **2 a 5 tags** por essay ou source.
5. `/organize` audita quase-duplicadas nos dois campos e propõe consolidação.

## Tipos de Source — Vocabulário Controlado

Campo `Tipo:` do manifesto — cada tipo define a subpasta física, nunca escolhida à mão.

| Tipo (manifesto)          | Subpasta                  | O que entra                                                                       |
| ------------------------- | ------------------------- | --------------------------------------------------------------------------------- |
| Ensaio Completo Importado | `ensaio-importado/`     | Ensaio/white paper pronto vindo de fora, virou essay preservando o texto integral |
| Web Clipping              | `web-clipping/`         | Recorte de página web: post, thread, matéria online                             |
| Artigo Acadêmico         | `artigo-academico/`     | Paper com peer review, DOI, ou publicado em periódico/conferência               |
| Livro                     | `livro/`                | Livro ou capítulo, inteiro ou em trecho relevante                                |
| Documentação Técnica   | `documentacao-tecnica/` | Manuais, specs, normas, documentação de ferramenta/API                          |
| Transcrição             | `transcricao/`          | Palestra, podcast, entrevista, aula                                               |
| Ideias                    | `ideias/`               | Texto curto e não estruturado, ainda não formal                                 |
| Outro                     | `outro/`                | Só quando nenhuma categoria acima cobre o caso                                   |

Reuse um tipo existente antes de criar novo. `/organize` e `/stats` auditam consistência entre `Tipo:` e subpasta real.

`manifest.md` e `map.md` são catálogos vivos (mantidos por `/import`, `/digest`, `/organize`) — a regra "nunca modifique `wiki/sources/`" protege só os documentos originais, não esses dois arquivos. Wikilinks seguem a forma canônica `[[slug-do-arquivo|Título Visível]]` (ver `## Regra de links`).

## Status de essay (draft | maduro | finalizado)

Campo `status:`, só em `wiki/essays/`, nunca em `concepts/`/`entities/`.

- `/essay` (do zero): nasce `draft`.
- `/import` (texto pronto do autor): nasce `finalizado` por padrão, ou `draft` se ficar claro que é rascunho do autor.
- Essay antigo sem o campo: default `draft`, corrigido depois via `/organize`.

O status protege a **prosa**, não a formatação. `/organize` e `fix_lint.py` aplicam correção mecânica (aspas, espaçamento, headings, wikilinks) em todo essay, inclusive `finalizado`/`maduro` — nada disso altera o que o texto diz. Só as skills abaixo respeitam o status.

**Regra para skills que editam prosa** (`/sweep`, `/expand`, `/chapter`, `/proofread`, `/polish`, `/continuity`, `/linkify`). Depende de o Usuário ter nomeado um essay, não de quantos a skill acaba tocando.

- **Batch** ("/sweep tudo", "revisa todos"): pule `finalizado`/`maduro`, sem perguntar nem avisar durante a execução. No resumo final, informe quantos foram pulados.
- **Específico** (Usuário nomeia o essay): execute normalmente, mesmo se `finalizado`/`maduro`. Ao editar um `finalizado`, avise ao final: "esse essay estava marcado como finalizado — segui porque você pediu direto." `maduro`: sem alerta. `draft`: normal.

## Byline do essay

Logo após `# Título`, com linha vazia entre título e byline:

```
# Título do Essay

> Tipo
> Gustavo Zambrano · Mês de Ano
```

- **Tipo**: `Ensaio`, `White Paper`, `Brainstorm`, `Estudo` ou `Análise`.
- **Mês de Ano**: por extenso (ex: `Maio de 2026`).
- **Nunca** `[[wikilinks]]` (exportada a PDF como texto puro) nem dois-pontos (`:`) — Obsidian interpreta como separador de bloco.

## Estrutura obrigatória do essay

1. **Evite resumo executivo interno** — prefira uma introdução. Abra com a byline, vá direto ao `## Sumário`, e faça da primeira seção `##` a introdução. Resumo condensado sob demanda é `/handout`. Essay antigo com `## Resumo Executivo` não é erro a corrigir de ofício: converta em introdução só ao editar aquele essay por outro motivo.
2. **`## Sumário` obrigatório**, logo após a byline, com links para todas as seções `##` (exceto Referências e Conexões):

   ```
   ## Sumário

   - [Título da Seção](#título-da-seção)
   - [Outra Seção](#outra-seção)

   ---
   ```

3. **Links externos** para todo conceito/entidade/termo técnico, ao menos na primeira ocorrência.
4. **`## Referências` obrigatória** — bibliografia em formato AIAA (ver seção abaixo). Heading exato (nunca H1, nunca "Referências Bibliográficas", nunca numerado). Todo claim de fonte externa não arquivada em `wiki/sources/` precisa de entrada aqui.
5. **`## Conexões` obrigatória** no final — `[[wikilinks]]` bidirecionais para páginas relacionadas. Não exportada a PDF.

## Regra de links — Obsidian é o leitor primário

O `.md` é lido no Obsidian antes de virar PDF/HTML — a sintaxe gravada é a que esse leitor entende; exportadores traduzem na hora de gerar.

| O que                   | Forma correta                                             | Por quê                                                                     |
| ----------------------- | --------------------------------------------------------- | ---------------------------------------------------------------------------- |
| Link para outra página | `[[slug-do-arquivo\|Título Visível]]`                  | Obsidian resolve por**nome de arquivo**, não por H1 nem `aliases:`. |
| Link para seção       | `[[#Texto Exato Do Heading]]` ou `[[#Texto\|Display]]` | `[texto](#slug-github)` não navega no Obsidian, só no PDF/HTML.          |
| Heading                 | Nunca com link markdown dentro                            | Heading com`[texto](url)` fica inalcançável por qualquer link.           |
| Artefato gerado         | Markdown puro, nunca HTML solto                           | `<span>` sem fechamento engole o resto da entrada no Obsidian.             |

Exportadores convertem `[[#Heading]]` em `[Display](#slug)` (`convert_heading_wikilinks`), removem `## Conexões` e limpam wikilinks residuais — nada disso precisa estar na fonte.

**Ao mexer em link, verifique nos dois lados.** `check_wiki.py` valida a forma da fonte e o export valida o destino, mas nenhum dos dois abre o Obsidian. Uma mudança de sintaxe de link só está confirmada depois de clicada lá.

- **Corpo (inline)**: só links externos `[texto](url)`. Nunca `[[wikilink]]` para outra página. `[[#Heading]]` é permitido (aponta para seção do próprio arquivo).
- **`## Conexões`**: só `[[slug|Título]]` — metadata interna, não exportada.
- **`## Referências`**: links bibliográficos externos, formato AIAA.
- Motivo: essay é documento autocontido, compartilhável como PDF sem perda de informação.
- **Nunca remeta a outro essay no corpo.** Nada de "como argumentei no ensaio *X*" ou "o essay *Y* detalha isso": quem lê o PDF não tem o *Y* em mãos, e a frase vira uma promessa que o documento não cumpre. Atribua a ideia ao seu próprio assunto ("a epistemologia alcança a mesma lição pelo lado empírico") ou corte a frase, se ela existia só para apontar. A relação entre páginas vive em `## Conexões`, e é lá que ela sobrevive à exportação. `check_wiki.py` sinaliza o caso como `CROSS_ESSAY_REFERENCE`.
- **Trabalho de bibliografia não toca no corpo.** Passada sobre `## Referências` mexe só nessa seção. Se um check acusar obra citada no corpo e ausente da bibliografia, corrija **acrescentando a entrada em `## Referências`** — nunca mexendo no link do corpo. Alterar link inline é `/linkify` (modo Adicionar links), só sob pedido explícito.
- Mínimo prático: ~10 links externos no corpo.

## Dois tipos de essay

- **Originais** (de `raw/`, via `/import`): texto integral preservado, traduzido se necessário. Só recebem link/formatação/`## Referências`/`## Conexões` — nunca alteração do texto original na ingestão. Expansíveis depois, sob pedido explícito.
- **Criados** (via `/essay`): livremente modificáveis, expandidos, enriquecidos.

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

- **Título sempre em itálico**, sem exceção por tipo de fonte.
- **O link é a palavra `Link`, clicável, como última coisa da entrada**, depois do ponto final — nunca no título, nunca envolvendo a citação inteira. Mantém o itálico legível, evita bloco azul no PDF, alinha a coluna de links para varrer com o olho.
- Link de glossário dentro da nota (verbete comentado ali) pode ficar onde está.
- Entrada sem link é entrada normal, na mesma lista das outras.
- Sem autor identificável: começa direto pelo título em itálico.
- Container troca conforme o tipo: periódico, editora + cidade, série + órgão, site/wiki, plataforma + tipo.
- Ordem de preferência de link: (1) DOI/link permanente do editor; (2) site institucional primário (NASA/NTRS, AIAA, ARC/NACA, universidade, GitHub do projeto); (3) SEP para verbetes filosóficos; (4) Wikipedia, só para conceito geral.
- Data de acesso obrigatória só para fontes sem versão fixa (Wikipedia, GitHub README, página institucional sem data): `(acesso em DD Mês. AAAA)` ao final da nota.
- Nota curta opcional depois do link.
- Exceção "sem link" só para caso genuíno (livro impresso sem edição digital) — aviso do lint, nunca erro bloqueante.
- Nunca duas entradas com a mesma URL normalizada no mesmo essay.
- **Verifique título e autor reais antes de escrever a entrada — nunca "de memória".** Se o título não estiver explícito na fonte em mãos, use WebFetch/WebSearch no DOI ou URL para confirmar título, autores completos e container antes de criar a entrada. Erros já ocorridos por pular esse passo: itálico envolvendo "Autor (Ano)" no lugar do título; autor errado atribuído a uma URL (o fetch do link/DOI pega esse erro, releitura visual não pega). **Autor errado é pior que autor ausente**: se o essay cita explicitamente que o link aponta para uma fonte secundária, preserve essa distinção — não troque pela obra original sem confirmar que é isso que o essay pretende citar.
- **Nome de autor nunca em negrito** — só o título leva ênfase. `check_wiki.py` sinaliza `REF_BOLD_AUTHOR`.
- Essay com corpo rico em links e `## Referências` vazia é sempre bug (`EMPTY_REFERENCIAS`), nunca estado válido.

## `wiki/references.md` e `wiki/references.json`

Artefatos gerados por `scripts/build_references.py` ao final de `/essay`, `/expand`, `/absorb`, `/digest`, `/import`, `/linkify`, `/review`, `/organize` — nunca editados à mão.

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

`domain_group` (só no JSON): `doi`, `nasa`, `aiaa`, `sep`, `wikipedia`, `github`, `institucional`, ou nulo sem link.

**Antes de escrever uma entrada nova, procure a mesma fonte em `wiki/references.md`** (por URL ou título em itálico) — se já catalogada, reuse a citação exata em vez de redigir versão nova. É esse desvio, repetido essay a essay, que produz a classe 4 de `check_dedupe.py` (mesma obra, citação divergente entre essays) — evitar na criação é mais barato que consolidar depois. Só vale citação diferente se a fonte real for outra edição/tradução, não reformulação da mesma nota.

`references.md` é lista única em ordem alfabética, sem agrupamento — bibliografia se lê por autor.

`concepts/` e `entities/` **não ganham** `## Referências` própria.

## Estilo de prosa

Vale para todo trecho escrito/reescrito pela wiki — não retroage sobre texto original de `raw/`, a menos que `/polish` ou `/proofread` seja pedido explicitamente.

### Regras gerais (todo essay)

1. **Uma proposição por frase.** Um único fato, asserção ou instrução por período. Divida com ponto final em vez de encadear orações subordinadas e explicativas com vírgulas.
2. **Sobriedade de conectores.** Não empilhe conectores (*portanto*, *visto que*, *assim sendo*). Confie na ordem lógica direta das frases; use conectores apenas quando a transição lógica não for óbvia.
3. **Evitar bullets no corpo.** Prosa argumentativa em parágrafos contínuos. Bullets apenas em `## Sumário`, `## Referências` e tabelas comparativas.
4. **Termo consistente para o mesmo conceito.** Nunca alterne sinônimos para o mesmo conceito dentro do essay.
5. **Abertura direta do parágrafo.** Situe o tema logo na primeira frase (tópico frasal). Um tema por parágrafo, até 6 frases.
6. **Travessões (—) extremamente raros.** Máximo de 1 a 2 na prosa do essay inteiro. Use ponto final, vírgula, dois-pontos ou reestruture.
7. **Sem ponto e vírgula.** Divida orações unidas por ponto e vírgula em frases autônomas.
8. **Parênteses curtos.** Parênteses apenas para siglas ou notas mínimas. Se a informação sustenta a tese, transforme-a em frase independente.
9. **Tipografia e símbolos limpos na prosa:**
   - **Sem barras oblíquas (`/`)**: escreva "e" ou "ou" por extenso (*"estabilidade e controle"*, não *"estabilidade/controle"*).
   - **Sem símbolos de atalho (`~`, `--`)**: escreva *"aproximadamente"*, *"cerca de"*.
   - **Intervalos numéricos por extenso**: *"5 a 30 iterações"*, *"de 10 a 20 mm"* (não *"5-30"*).
   - **Remissões completas**: *"Capítulo 3"*, *"Seção 2"* (não *"Cap. 3"*, *"Sec. 2"*).

### Regras adicionais para essays técnicos

0. **Português claro, conciso e formal.** Tom técnico e assertivo, nunca coloquial.
1. **Sem antropomorfização de código ou teorias.** Descreva a computação ou o modelo factual (*"o solver calcula"*, *"a teoria modela"* — nunca *"o código vê/sabe"*, *"a teoria tenta"*).
2. **Voz ativa quando o agente é conhecido.** *"O solver calcula a velocidade induzida"*, não *"A velocidade induzida é calculada pelo solver"*.
3. **Verbo direto em vez de nominalização ou locução pesada.** *"Verifique o resíduo"* (não *"faça uma verificação"*); *"o modelo divergiu"* (não *"veio a apresentar divergência"*).
4. **Corte de gerúndios soltos e gerundismos.** Evite orações reduzidas de consequência ambíguas. Transforme em frase coordenada com ponto final.
5. **Substantivo no lugar de pronome ou "isso/isto" ambíguo.**
6. **Sem empilhamento excessivo de preposições ("de/da/do").** Simplifique sintagmas nominais longos.
7. **Termo técnico com grafia única.** Mantenha a mesma tradução/grafia (unidades, siglas, variáveis).
8. **"Por exemplo", "ou seja" por extenso.** Sem abreviações latinas soltas (*e.g.*, *i.e.*).
9. **Sem exagero, marketing ou hedge vazio.** Elimine superlativos (*"robusto"*, *"revolucionário"*) e hedges desnecessários (*"pode potencialmente ajudar"*). Declare o fato.
10. **Concisão não é telegrama.** Frase curta preserva artigo, verbo e sujeito.

## Formato do índice (`wiki/index.md`)

Apenas essays. **Gerado por `python scripts/build_index.py`** (emite `index.json` e `index.md` juntos) toda vez que um essay é criado, editado ou removido. Nenhuma skill insere linha nele diretamente.

Lista plana, ordenada por `created` decrescente, sem agrupamento por categoria:

```markdown
- [Título do Essay](essays/nome-do-arquivo.md) — Resumo de uma linha.
  `consciência` · `identidade-pessoal` · `filosofia-da-mente`
```

Cada entrada usa `summary:` do frontmatter e `tags` para a lista de temas. Markdown puro, gerado direto pela função de renderização de `build_index.py`.

## Formato de páginas em `wiki/insights/`

Formato único (gerado por `/insight`, detalhes em `.agents/skills/insight/SKILL.md`): frontmatter com `tags`, `sources`, `created`, `updated`, `maturidade: solta | germinando | madura | absorvida`, corpo curto, `## Conexões` com `[[wikilinks]]`.

Fica fora de `wiki/index.md` e da contagem de "essays" de `/stats` — aparece na seção "Insights".

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
Tags: [tag1, tag2] (mesmo vocabulário controlado dos essays).
Pasta: wiki/sources/<subpasta-correspondente>/
Virou: [[slug-do-essay|Essay Resultante]] (essay novo) | enriqueceu [[slug-do-essay|Essay Existente]] | ainda não — ver resumo em wiki/sources/resumos/.
Verificação: [referências confirmadas | não verificado — checar antes de citar em outro essay].
```

`Tags:` é obrigatório em toda entrada nova. Existe **uma única fonte de tags para toda a wiki** — essay e source não têm vocabulários separados; `build_index.py` consolida `tags_in_use` combinando os dois num só cômputo.

Antes de reutilizar uma citação em outro essay, confira `Verificação:` — se "não verificado", confirme antes de propagar.

Atualize manifesto e `map.md` no mesmo momento em que o arquivo é movido de `raw/` para `wiki/sources/<subpasta>/`.

## Formato do mapa de sources (`wiki/sources/map.md`)

Lista plana de tudo já processado ou pendente, sem agrupamento — classificação temática vem só de `Tags:`:

```
- [[slug-do-source|Nome do Source]] — Tipo · Tags: tag1, tag2 · Status
  - Status: Importado como [[Essay]] | Resumido — ver wiki/sources/resumos/<slug>.md | Absorvido em [[Essay X]]
```

`Tags:` espelha o que já está em `manifest.md` para a mesma fonte. Atualizado por `/import`, `/digest`, `/absorb`; revisado por inteiro por `/organize`. Só entra no mapa depois de já estar em `wiki/sources/` — `raw/` não aparece aqui.

## Nomenclatura de páginas

- Arquivos: kebab-case + `.md`. Títulos: Title Case.
- Essays/concepts/entities: `wiki/<pasta>/nome-do-arquivo.md` → `# Nome Do Arquivo`.
- Sources: nomes originais preservados em `wiki/sources/<subpasta-do-tipo>/` — não são páginas wiki.
- `[[wikilinks]]` usam o **nome do arquivo** como alvo e o título como texto visível: `[[nome-da-entidade|Nome Da Entidade]]`. Única forma que o Obsidian resolve — alvo pelo H1 ou `aliases:` não funciona.
- Título → nome de arquivo: minúsculas, espaços viram hífens, remove caracteres especiais.

## Tratamento de imagens

1. Toda imagem vive em `wiki/assets/` — nunca embutida inline em base64, nunca só dentro do PDF/DOCX/HTML original.
2. Fonte processada com figura embutida: extraia para `wiki/assets/` no mesmo momento do processamento.
3. Link por caminho relativo: `../assets/nome-da-imagem.png` (de `wiki/essays/`) ou `../../assets/nome-da-imagem.png` (de `wiki/sources/resumos/`) — nunca caminho absoluto.
4. Imagem com informação importante (diagrama, gráfico): descreva o conteúdo em texto também.

## Compatibilidade com Obsidian

- `[[wikilinks]]` só em `## Conexões` e páginas de concept/entity/source, nunca inline.
- Imagens em caminho relativo.
- Wikilinks em `## Conexões` usam `[[nome-do-arquivo|Título da Página]]` — alvo é o nome do arquivo sem extensão, texto depois da barra é o que o leitor vê. Alvo pelo H1 ou `aliases:` não resolve.

## Conversão de fontes (HTML/PDF/DOCX → Markdown)

1. **Blockquotes (`>`)**: só para conteúdo que era caixa especial no original (callout, warning-box, pullquote).
2. **Tabelas HTML** → markdown tables, nunca linhas soltas.
3. **Índices/TOC do original**: remover — substituídos pelo `## Sumário` gerado.
4. **Labels de capítulo** (`01 — Introdução`): incorporar como heading ou remover se já há equivalente.
5. **Símbolos residuais**: remover diamantes (◆), replacement chars, zero-width spaces, `&nbsp;`, `&amp;`, etc.
6. **Verificar fidelidade**: comparar o `.md` gerado contra o original.

## Regra de contradição entre fontes

Se informação nova (fonte ingerida, ou o que o Usuário disse) contradiz o que já está escrito: **não escolha um lado sozinho, não tire a média.** Pare, aponte a contradição citando as duas fontes com localização exata, e só edite depois que o Usuário disser qual prevalece.

Vale para `/absorb`, `/digest`, `/expand`, `/continuity` e qualquer skill que compare conteúdo novo contra o que já está na wiki.

## Fechamento padrão de essay único

Toda skill que edita um essay específico (`/expand`, `/chapter`, `/proofread`, `/polish`, `/linkify`, `/absorb`, `/import`, `/essay`) fecha com:

```bash
python scripts/check_wiki.py <slug>
python scripts/fix_lint.py <slug>
```

Aplique os achados automáticos e reporte o restante. Reserve `/organize <slug>` para quando o Usuário pedir a auditoria completa daquele essay — mais caro e desproporcional para um arquivo só.

## Reuso de vocabulário controlado (`tags_in_use`)

Antes de criar uma tag nova (essay, concept, entity, insight, ou `Tags:` de source), cheque `tags_in_use` em `wiki/index.json` — rode `python scripts/build_index.py` primeiro se estiver desatualizado. Só crie tag nova se nenhuma existente cobrir o tema.

## Decisões fechadas

Decisões de estilo já resolvidas — não reabra sem evidência nova (um caso real que a regra não cobre, não uma preferência estética isolada).

- [Forma canônica de citação em `## Referências`] (2026-08-24) — autores completos até 3, `et al.` acima disso; subtítulo sempre; container completo com cidade; granularidade `Vol./No./pp.`. A nota contextual após o em-dash é livre por essay — dedupe pode listá-la como candidato informativo sem ação.

## Decisões fechadas — exports HTML e PDF (2026-08-26)

Design premium: "restrição, não adição" — reduzir frequência de sinais (cores, preenchimentos, pesos) para valorizar a tipografia.

### HTML (`scripts/essay_template.html`)

| Decisão | Regra |
| --------- | ----- |
| Medida de linha | `--max-width:75vw` no desktop (~75% da largura da tela) e `700px` no mobile/base; `.masthead-inner` acompanha `var(--max-width)` |
| Fontes | Playfair Display vale para todos os temas (claro/escuro/desktop/mobile). O override `--font-display:Georgia` no desktop-claro foi removido — produzia dois produtos no mesmo arquivo |
| Hifenização | `hyphens:auto` + `-webkit-hyphens:auto` em `.content > p` no desktop. `hyphenate-limit-chars:6 3 3` |
| Paleta | Dessaturada: `--gold:#B08B4F` (escuro) / `#8A6B33` (claro), `--rust:#8E4636`. Links usam a cor do texto (`var(--text)`) com sublinhado dourado a 38% de opacidade; dourado sólido reservado a kicker, numeração e hover |
| Pull-quote | Sem aspas gigantes (`::before` com `"` a 5rem removido); a pull-quote distingue-se por itálico, filete lateral e respiro |
| Badge de caixa | Versalete espaçado na cor do tipo (`--boxc`), sem fundo preenchido e sem texto branco. A caixa usa filete lateral de 2 px em `--boxc` sobre superfície neutra. `.box.generico` usa filete cinza (`--border`) — 64% das caixas do corpus são genéricas por opção editorial |
| Sumário | Filetes hairline (topo e base) sem caixa preenchida; rótulo ÍNDICE alinhado à esquerda em versalete mono |
| Referências | Recuo pendente via CSS (`padding-left:2.4em; text-indent:-2.4em`). A seta ↗ vai só no **último** link da entrada (`a[href^="http"]:last-of-type::after`) — o "Link" final. A palavra "Link" permanece. Aplicar a todo link externo dava duas ou três setas por referência |
| `@media print` | Apenas 1 regra: ocultar chrome fixo. PDF vem do LaTeX — o `@media print` serve só ao Ctrl+P do browser |
| h3 | Playfair Display (`var(--font-display)`) a 1.24rem, cor mais fraca que o `##`. Distingue por **peso, corpo e cor**, não por família: o mono anterior punha um subtítulo com cara de rótulo de código no meio de prosa serifada. O mono continua sendo a voz dos rótulos (`.sb-kicker`, `.box-badge`, `.label-solo`, `th`) — que é o que h3 não é |
| box.generico | Aceito como caso padrão (não é heurística fraca): 87 de 136 caixas no corpus. Filete cinza discreto |
| Listas | Ambos os exports usam `+lists_without_preceding_blankline`. 28 listas em 10 essays são escritas coladas ao parágrafo que as introduz; sem a extensão saíam como prosa corrida com hífens literais |

### PDF (`scripts/export_essay_pdf.py` + `pdf_boxes.lua`)

| Decisão | Regra |
| --------- | ----- |
| Tamanho de fonte | `12pt` base (`classoption: - 12pt`) para leitura confortável |
| Margens | `top=22mm, bottom=22mm, left=26mm, right=26mm` — proporção equilibrada sem desperdício de mancha |
| Capa | Página própria com título, autor, tipo e meta-row (cap. + tempo de leitura). Não é parte numerada |
| Sumário | Na segunda página, encabeçado só pelo kicker (`\sbkicker{Sumário}`). Os títulos passam ao LaTeX como **inlines do Pandoc**, nunca via `stringify` — achatar em texto cuspia `\dot{eta}` e `C_{n_eta}` crus na página. Goteira com o numeral; o prefixo é removido do título |
| Hiperlinks | Sublinhado sutil e nítido via `\usepackage[normalem]{ulem}` + `\uline` na cor do link (`\color{sburl}`) |
| Cabeçalho corrente | Removido (`pagestyle{fancy}`, `headrulewidth=0pt`, rodapé com número de página discreto) |
| Tipografia e Contraste | Libertinus Serif + Libertinus Sans via `fontspec`. Títulos de caixas e badges com alto contraste (`sblink` `#171310` e `boxline` `#4B5563`) |
| Caixas | `tcolorbox` com filete lateral colorido, fundo neutro. Badge em versalete na cor temática |
| Babel | `portuguese` explícito para hifenização correta |
| Numeração de capítulo | O kicker respeita a grafia do autor: `## 3. Título` → "3", `## VI. Título` → "VI". Sem numeração no fonte, contador sequencial **arábico** — as subseções são sempre `3.1`, e um kicker "III" acima de um "3.1" punha dois sistemas na mesma página. O prefixo sai do título sempre que existe (árabe **e** romano) |
| `###` | Libertinus Sans 13pt grafite (`sbgraphite`), com `
eedspace`. Distingue de `##` por família e cor: 15,5pt bold serif preto contra 18pt bold serif preto era o mesmo título |
| Referências | `sbrefitem` com `\leftskip` + `\parindent` negativo, não `\hangindent` — este último vale para um parágrafo e o Pandoc emite a referência como bloco próprio, perdendo o recuo. "Link" mantido, com uma seta ↗ ao lado |
| Contagem de capítulos da capa | Exclui só `Sumário`/`Referências` **casando o título inteiro**. Com casamento por prefixo, o capítulo "Índice de Experimentos Mentais…" era lido como sumário e sumia da conta |
| Cor das caixas | `BADGE_COLOR_RULES` casa o vocabulário real do corpus (`IDEIA`, `EXPERIMENTO MENTAL`, `EVIDÊNCIA EMPÍRICA`, `MAPA CONCEITUAL`), com as regras específicas antes das genéricas. Comparação via `pandoc.text.lower` — `string.lower` do Lua só mapeia ASCII e "EVIDÊNCIA" nunca casava |

### Grafo (`scripts/build_graph.py`)

| Decisão | Regra |
| --------- | ----- |
| Esmaecimento na busca | A busca vence a política `edgeVisibility`. Com o default `"sempre"`, buscar escurecia os nós e deixava as ~2900 arestas em opacidade cheia: a tela virava uma teia branca mais forte que antes da busca. Sobrevivem as arestas que **tocam** um resultado — mostram com quem o nó encontrado se conecta |

### Grafo — modos de build e marca de rascunho (2026-08-27)

| Decisão | Regra |
| --------- | ----- |
| `--reader` | Arquivo **standalone** (~6,9 MB): fontes, MathJax e imagens embutidos. Para compartilhar solto. As imagens já passam por `_compress_image` (1200 px, JPEG q80) — não são as originais de `wiki/assets/` e não devem ser reduzidas mais: a coluna do leitor tem ~1080 px CSS, então 1200 px já está abaixo de retina |
| sem `--reader` (default) | Arquivo **leve** (~0,63 MB). O ícone 📖 abre `output/html/<slug>.html`. A existência do HTML é resolvida no BUILD (campo `htmlFile` do nó), não no navegador — quem nunca rodou `/html` cai no `.md` em vez de ganhar link quebrado |
| Ordem de abertura de um essay | leitor embutido → `htmlFile` → `.md`. Vale para `openNode`, cartão de detalhe e painel Índice |
| Botão 📖 | `<button>` quando há leitor embutido (abre o overlay), `<a>` quando é o HTML exportado (abre aba). Mesma classe e mesmo desenho. Os handlers usam `button.idx-read` / `button.read-btn`: um seletor solto pegaria a âncora e chamaria `openReader(null)` |
| MathJax | Tag comprimida própria (`sb-mathjax-data`), inflada só ao abrir um essay que tenha `class="math"` no fragmento. Não muda o tamanho do arquivo — 22 dos 45 essays nunca descomprimem os 2,3 MB do bundle |
| Marca de rascunho | Só `status: draft` é marcado; `finalizado` não recebe nada — a marca serve para dizer "ainda em obra", e 45 selos repetidos não diriam nada. Aparece como `draft` ao lado do título no painel Índice, e como **`Rascunho` no lugar da meta-row** da capa (tempo de leitura + capítulos) no HTML, no leitor do grafo e no PDF: num rascunho a duração ainda não significa nada |
| `status` no template HTML | Chega via `-V status=` (export_essay_html.py) e vira `data-status` no `<html>`. O leitor do grafo lê do próprio payload (`status` por essay) |
| `file` no `graph.json` | Sempre POSIX (`as_posix()`). No Windows o `relative_to` devolvia caminho com barra invertida e o link montava `../../wiki\essays\x.md` |
| `build_sphere.py` | Tem cópia própria do mesmo JS. Toda mudança de navegação/índice precisa ser espelhada nos dois |
