---
name: organize
description: >
  Organiza a base de conhecimento na camada de metadados/grafo E na
  formatação mecânica de essay (absorveu o antigo /format): roda e
  comunica o lint completo (formatação, manifesto, sources sem essay,
  estrutura canônica de pastas, plano, insights, quase-duplicatas),
  corrige links quebrados ou órfãos, atualiza wiki/index.md,
  wiki/sources/map.md, tags, e gera o grafo de conexões via
  scripts/build_graph.py. Aceita escopo corpus inteiro (/organize) ou
  essay único (/organize <slug>) — nesse modo só formatação mecânica,
  referências e wikilinks daquele essay, pulando tudo que exige o
  corpus. Use quando o Usuário disser "organiza a wiki inteira", "vê
  se tá tudo certo", "confere a formatação desse essay", "o que está
  faltando", "confere a estrutura", ou quiser manutenção de metadados
  em vez de corrigir a prosa/argumento de um essay (isso é /sweep).
allowed-tools: Bash Read Write Edit Glob Grep AskUserQuestion
---
# Organize

Organiza a base na camada de metadados e formatação mecânica: índice, log, mapa de sources, tags, plano, insights, estrutura de pastas, e a formatação de essay (estrutura Markdown, byline, Sumário/Referências/Conexões, Obsidian-compat, espaçamento, aspas, LaTeX, travessões, bullets, HTML/símbolos residuais, idioma PT-BR — o que antes era `/format`). **Não reescreve prosa nem argumento** — isso é `/sweep` (estilo, continuidade, português, links) e `/review` (validade argumentativa).

## Dois modos — use o que couber

```
/organize              → corpus inteiro: formatação de TODOS os essays + índice, órfãos,
                          manifesto/sources, tags, plano, insights, grafo.
/organize <slug>       → escopo único: só formatação mecânica, referências e wikilinks
                          DAQUELE essay. Pula explicitamente tudo que exige o corpus
                          (órfãos, consistência do index, auditoria de manifesto, tags
                          quase-duplicatas, grafo) — avisando que pulou.
```

Use `/organize` (sem argumento) quando o pedido for sobre a saúde da base inteira. Use `/organize <slug>` quando o Usuário pedir explicitamente a auditoria completa de UM essay — para o caso comum de "acabei de mexer nesse essay, confere o formato dele", prefira o fechamento embutido nas skills de conteúdo (`/essay`, `/expand`, `/chapter`, `/proofread`, `/polish`, `/continuity`, `/linkify`, `/import`, `/absorb`), que já chamam `check_wiki.py <slug>` e `fix_lint.py <slug>` diretamente — é mais barato que acionar este skill inteiro.

`/organize` é a skill mais importante para comunicar com clareza — ela existe para pegar **tudo** que está faltando ou desconectado, não só o óbvio. Nunca cole o relatório bruto de `check_wiki.py` sem tratamento; ele é genérico de propósito (pega tudo), mas o Usuário precisa de um resumo priorizado, não de um texto bruto e extenso.

## Modo corpus inteiro — passo a passo

1. Se `qmd` estiver disponível (`qmd status`), rode `qmd update && qmd embed` primeiro — mantém a busca semântica sincronizada com o que este `/organize` está prestes a mudar; sem qmd, pule sem avisar. Rode também `python scripts/sync_skills.py --check`; se divergente, rode `python scripts/sync_skills.py` para sincronizar `.claude/skills/` — mecânico, aplique direto. Depois, rode `python scripts/stats.py` para ver o estado atual — números de essays/tags/órfãos/sources sem manifesto/plano/insights. Rode também `python scripts/build_index.py` para regenerar `wiki/index.json` — cache que `/query`, `/gaps`, `/insight add` e os passos seguintes deste skill reusam, evita reparsear frontmatter de tudo de novo em cada um. Rode `python scripts/build_references.py` para regenerar `wiki/references.json`/`.md` a partir das `## Referências` de todos os essays.
2. **Formatação mecânica de todos os essays** (herdado de `/format`): rode

   ```bash
   python scripts/check_wiki.py --json
   python scripts/check_references.py --json
   python scripts/fix_lint.py
   ```

   `check_wiki.py` cobre num relatório único formatação de essay (frontmatter, byline, Sumário/Referências/Conexões, espaçamento, aspas, LaTeX, travessões, bullets, símbolos/HTML residuais, idioma) **e** estrutura de corpus (índice, órfãos, manifesto, plano, insights, wikilinks mortos) — ver docstring do script para a lista completa de códigos. `check_references.py` valida o conteúdo AIAA de `## Referências` (`REFERENCIA_FORMATO_INVALIDO`, `DUPLICATE_REFERENCIA`, `LINK_NOT_IN_REFERENCIAS`, `REFERENCIA_SEM_LINK`, `REFERENCIA_NAO_USADA`). `fix_lint.py` é o único fixer mecânico da wiki e aplica tudo que for inequívoco sem perguntar — inclui a reformatação de `## Referências` para o padrão AIAA (antes `check_references.py --fix-format`).

   Pule os fixes automáticos de formatação em essays com `status: finalizado` ou `maduro` (não altera a prosa deles), mas ainda os inclui no relatório de problemas encontrados.
3. **Órfãos**: rode `python scripts/find_backlinks.py --orphans` em vez de recalcular do zero lendo todo `wiki/essays/*.md` manualmente. Para cada concept/entity sem essay que o referencie, decida com o Usuário se cria um essay novo, se anexa a um existente, ou se a página órfã deve ser removida por não servir a nada.
4. **Contradições e claims desatualizados**: ao ler os essays (via os achados do stats ou amostragem), sinalize contradições entre páginas e claims que fontes mais novas já superaram. Se a correção não for imediata, ofereça registrar como item `Revisão` em `plan/plano.md` (via `/plan add`) em vez de deixar a inconsistência solta.
5. **`wiki/index.md`/`wiki/index.json`**: confirme que foram regenerados via `python scripts/build_index.py` (passo 1) — artefatos gerados, nunca editados à mão (ver `## Formato do índice` em `conventions/SKILL.md`). Se algum essay novo/editado/removido não estiver refletido, rode `build_index.py` de novo.

   **Cobertura do índice — o que falta em cada entrada.** No JSON do passo 2, separe os códigos de resumo:

   - `FM_NO_SUMMARY`: o essay não tem `summary:`, então aparece no índice sem resumo. Liste todos nominalmente no bucket "Crítico" — um índice sem resumo é o catálogo mestre da wiki funcionando pela metade.
   - `FM_LONG_SUMMARY`: resumo passou de 120 caracteres e vai quebrar o layout da entrada.

   Não escreva os resumos aqui: resumo é conteúdo. Reporte a lista e ofereça uma passada dedicada.

   **Cobertura de bibliografia.** Cruze `wiki/references.json` (regenerado no passo 1) com os essays: essay sem nenhuma entrada em `## Referências`, ou com bibliografia visivelmente rasa para a extensão do texto, entra no bucket "Atenção" com o nome. `check_wiki.py` já emite `NO_REFERENCIAS` para a seção ausente; o que você acrescenta aqui é o julgamento de suficiência, que nenhum script faz.
6. **Tags quase-duplicadas**: verifique se alguma tag em uso — em `tags:` de essay/concept/entity/insight **ou** em `Tags:` do manifesto de sources, é a mesma fonte de vocabulário para as duas (ver `## Tags — Vocabulário Controlado` em `conventions/SKILL.md`). Utilize o `wiki/index.json` (gerado no passo 1) que traz `tags_in_use` consolidado. Proponha consolidação e liste os essays/sources afetados antes de renomear em massa.
7. **Quase-duplicatas em geral**: rode `python scripts/check_dedupe.py`. Se o corpus cresceu desde a última passada, rode também com `--threshold` mais baixo (ex. 0.75) para essa checagem específica — o padrão (0.85) deixa passar variação de grafia maior, especialmente em referências sem URL. Ele reporta quatro classes num relatório só — títulos de essays, títulos de concepts/entities, tags, e a mesma referência catalogada em essays diferentes com citação divergente. **Ele nunca funde nem deleta**, e você também não: para cada candidato, mostre os dois lados com o caminho de cada arquivo e **pergunte ao Usuário** se funde, se renomeia um dos dois, ou se são genuinamente páginas distintas que só se parecem — mesmo padrão do passo 6 para tags. Fuzzy matching erra: um par com similaridade alta pode ser dois conceitos irmãos legítimos, e essa decisão é editorial, nunca sua.
8. **`wiki/sources/manifest.md`, tipos de source e estrutura canônica — audite E corrija**: verifique se todo arquivo em `wiki/sources/**` tem entrada no manifesto e vice-versa (`check_wiki.py` cobre as duas direções), se todo `Tipo:` usa o vocabulário controlado, e se toda fonte `Tipo: Ensaio Completo Importado` tem um `Virou: [[Essay]]` que de fato existe. **Toda entrada precisa de `Tags:`** (mesmo vocabulário controlado dos essays) — se faltar numa entrada existente (fonte antiga, de antes desse campo existir), preencha agora usando o conteúdo da fonte/resumo para decidir, sem perguntar; se a tag usada não pertence ao vocabulário controlado, sinalize junto com as tags quase-duplicadas do passo 6. Para todo arquivo fora da subpasta que seu `Tipo:` implica: mova para a subpasta correta agora, sem perguntar (correção mecânica e inequívoca), e atualize `Pasta:` na entrada correspondente. Única exceção que exige pergunta: arquivo sem entrada no manifesto e sem `Tipo:` inferível com confiança — reporte e peça para classificar, não adivinhe.
9. **Estrutura canônica de pastas**: `check_wiki.py` verifica se todas as 8 subpastas de `wiki/sources/` (uma por tipo, incluindo `artigo-academico/`) e `wiki/handouts/` existem. Se alguma faltar, crie com `.gitkeep` diretamente — é mecânico.
10. **`wiki/sources/map.md`**: revise por inteiro (não só incremente) — toda fonte em `wiki/sources/` e todo item ainda pendente em `raw/` deve aparecer, com status correto e organizado por assunto.
11. **`wiki/log.md`**: confirme que é append-only (nenhuma entrada antiga foi editada) — só verifique, nunca reescreva o histórico.
12. **`plan/plano.md`**: as 5 seções fixas existem (mesmo vazias)? Algum item usa um `Status:` fora do vocabulário (Pendente | Em Andamento)? Algum tópico fragmentou em quase-duplicatas? Corrija estrutura (seções faltando) direto; para tópicos quase-duplicados, proponha consolidação como faria com tags.
13. **`wiki/insights/`**: toda página tem `maturidade:` válida? Sinalize insights sem nenhum link em `## Conexões` — candidatos a órfãos — e insights `madura` havia tempo sem promoção (sugira `/insight promote`).
14. **Wikilinks mortos e formatação** já cobertos no passo 2. Para cada **wikilink morto** reportado:
    - Se o alvo for claramente um erro de digitação de uma página que existe, corrija agora, sem perguntar.
    - Se o alvo não corresponder a nada existente nem a um erro de digitação óbvio, **não invente ou apague o link silenciosamente** — reporte a lista completa e pergunte o que fazer.
      Links **externos** (URLs que saíram do ar) não são responsabilidade do `/organize` — isso é `/linkify`, chamado por essay via `/sweep`.
15. **Formato das `## Referências`**: os achados `REFERENCIA_SEM_LINK` e `LINK_NOT_IN_REFERENCIAS` que sobrarem depois do `fix_lint.py` do passo 2 entram no bucket "Atenção" do resumo final, porque pedem busca de fonte, não correção mecânica — isso é `/linkify`, não `/organize`.
16. **Grafo**: rode `python scripts/build_graph.py` para gerar `output/graph/graph.html` (visualização interativa) e `output/graph/graph.md` (versão Mermaid). Ofereça abrir o HTML — é a forma mais rápida de ver clusters isolados, hubs, e partes da wiki que nunca se conectam entre si (ex: ensaios de filosofia que nunca linkam com os de engenharia).
17. **Exportação** (opcional, só se o Usuário quiser uma checagem completa): rode `python scripts/export_essay_pdf.py --all` e `python scripts/export_essay_html.py --all`, confirme que PDFs têm hyperlinks clicáveis, imagens resolvem, `## Conexões` não aparece no PDF e `## Referências`/`## Sumário` aparecem.
18. **Comunique um resumo priorizado** — nunca cole o relatório bruto. Estruture assim:
    - **Corrigido automaticamente** (lista curta do que foi mecânico e já foi aplicado — formatação + estrutura).
    - **Crítico — precisa de decisão sua** (sources sem essay, wikilinks mortos sem alvo óbvio, contradições entre essays, seções do plano fora do vocabulário).
    - **Atenção — vale revisar quando puder** (notas atômicas órfãs, tags quase-duplicadas, quase-duplicatas de título de essay/concept/entity e de referência entre essays, entradas de `## Referências` sem link ou fora do padrão AIAA, estrutura de pastas faltando).
    - **Informativo** (contagens do `/stats`, link pro grafo gerado).
    - **Liste nominalmente os essays com `FM_NO_SUMMARY`.**
    - **`EMPTY_REFERENCIAS`, `REF_BOLD_AUTHOR`, `REF_TITLE_IS_AUTHOR` e `REF_MISSING_TITLE` nunca são auto-corrigíveis** — exigem descobrir o título/autor real de uma fonte externa, o que `fix_lint.py` não pode fazer (script não navega a web). Para cada ocorrência, use `WebFetch` na URL da entrada (ou `WebSearch` por autor+ano+container quando o fetch falhar) para confirmar o título e autor reais antes de reescrever a entrada — nunca reescreva "de memória". Trate como oportunidade de auditoria: essas quatro categorias já revelaram, na prática, entradas com autor completamente errado (a fonte real, quando resolvida, era de outro autor), não só formatação.

## Modo essay único (`/organize <slug>`) — passo a passo

1. Resolva o slug (nome do arquivo, título parcial, ou caminho completo); se ambíguo, pergunte antes de prosseguir.
2. Rode:

   ```bash
   python scripts/check_wiki.py <slug> --json
   python scripts/check_references.py --file <slug> --json
   python scripts/fix_lint.py <slug>
   ```

   `check_wiki.py <slug>` já pula sozinho, com aviso explícito no relatório, as seções que exigem o corpus inteiro (órfãos, consistência do index, manifesto, plano, insights) — só reporta formatação do essay e wikilinks mortos originados nele.
3. Aplique os fixes automáticos do `fix_lint.py` (mecânicos, sem perguntar). Reporte o restante por categoria, mesmas tabelas do modo corpus (Estrutura obrigatória, Qualidade de referência, Resumo do índice, Byline, Links, LaTeX/aspas, Espaçamento, Estilo, Residuais, Idioma, Referências).
4. **Não rode** `build_graph.py`, `stats.py`, nem as auditorias de manifesto/plano/insights/órfãos neste modo — avise explicitamente que foram puladas por serem checagens de corpus inteiro, fora de escopo para um essay só.
5. Se `## Referências` mudou, rode `python scripts/build_references.py`. Se `summary`/`tags` mudou, rode `python scripts/build_index.py`.
6. Apresente o relatório: issues corrigidos automaticamente, issues restantes por categoria, e o aviso de quais seções de corpus foram puladas.

## Depois

Log:

```
## [YYYY-MM-DD] organize | Resumo do que foi corrigido
```

(Essay único: `## [YYYY-MM-DD] organize | Título do Essay`.)

Se quiser um snapshot salvo da stats pós-organização (só no modo corpus inteiro), rode `python scripts/stats.py --save`.

## Convenções

Prosa segue `## Estilo de prosa` em `conventions/SKILL.md`.

Não corrija silenciosamente algo que depende de julgamento editorial (qual claim prevalece numa contradição, se um órfão vira essay ou é removido, se duas categorias devem de fato virar uma só).

Correções mecânicas e inequívocas (índice desatualizado, entrada de manifesto faltando, pasta canônica ausente, espaçamento, tags, formatação de essay) podem ser aplicadas direto via `fix_lint.py`.

## Skills relacionadas

- `/sweep` — corrige prosa, continuidade, português e estilo dentro de cada essay; não é a camada de metadados/formatação mecânica
- `/stats` — o primeiro passo do modo corpus inteiro, e também útil sozinho sem rodar o resto
- `/import`, `/digest`, `/absorb` — quem alimenta `manifest.md` e `map.md` no dia a dia; `/organize` é a auditoria periódica
- `/plan` — recebe itens `Revisão` quando `/organize` encontra algo que precisa de atenção mas não pode ser corrigido na hora
- `/insight` — recebe notas atômicas maduras sinalizadas aqui, para promoção
- `/status` — depois de um `/organize` substancial (modo corpus inteiro), ofereça `/status update`
- `/gaps` — cobertura conceitual (direção oposta ao órfão *reverso* do passo 3)
