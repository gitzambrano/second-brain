---
name: organize
description: >
  Organiza a base de conhecimento inteira na camada de metadados/
  grafo: roda e comunica o lint completo (manifesto, sources sem
  essay, estrutura canônica de pastas, plano, insights, categorias
  quase-duplicadas), corrige links quebrados ou órfãos, atualiza
  wiki/index.md, wiki/sources/map.md, tags, e gera o grafo de
  conexões via scripts/graph.py. Use quando o Usuário disser "organiza
  a wiki inteira", "vê se tá tudo certo", "o que está faltando",
  "confere a estrutura", ou quiser manutenção da base inteira em vez
  de corrigir a prosa de um essay específico (isso é /sweep).
allowed-tools: Bash Read Write Edit Glob Grep AskUserQuestion
---

# Organize

Organiza a base inteira na camada de metadados: índice, log, mapa de sources, tags, plano, insights, e a estrutura de pastas como um todo. **Não reescreve prosa de essay** — isso é `/sweep`. Pense em `/organize` como a manutenção do grafo e do catálogo; `/sweep` como a manutenção do texto.

`/organize` é a skill mais importante para comunicar com clareza — ela existe para pegar **tudo** que está faltando ou desconectado, não só o óbvio. Nunca cole o relatório bruto de `lint_all.py` sem tratamento; ele é genérico de propósito (pega tudo), mas o Usuário precisa de um resumo priorizado, não de um texto bruto e extenso.

## Passo a passo

1. Rode `python scripts/stats.py` para ver o estado atual — números de essays/tags/órfãos/sources sem manifesto/plano/insights.
2. **Órfãos**: para cada concept/entity sem essay que o referencie, decida com o Usuário se cria um essay novo, se anexa a um existente, ou se a página órfã deve ser removida por não servir a nada.
3. **Contradições e claims desatualizados**: ao ler os essays (via os achados do stats ou amostragem), sinalize contradições entre páginas e claims que fontes mais novas já superaram. Se a correção não for imediata, ofereça registrar como item `Revisão` em `plan/plano.md` (via `/plan add`) em vez de deixar a inconsistência solta.
4. **`wiki/index.md`**: confirme que contém apenas essays, no formato `[[filename|Display Title]]`, sem dois-pontos no display text, organizados por categoria temática (ver `## Formato do índice` em `conventions/SKILL.md`). Adicione essays que faltarem, remova entradas de essays deletados.
5. **Tags quase-duplicadas**: verifique se alguma tag em uso é variante de grafia de outra (acento, plural, sinônimo). Proponha consolidação e liste os essays afetados antes de renomear em massa.
6. **Categorias temáticas quase-duplicadas**: `lint_all.py` já sinaliza isso (heurística de normalização), mas categorias são vocabulário aberto por design — não force um vocabulário fechado, só avise e pergunte se o Usuário quer unificar a grafia daqui para frente.
7. **`wiki/sources/manifest.md`, tipos de source e estrutura canônica — audite E corrija**: verifique se todo arquivo em `wiki/sources/**` tem entrada no manifesto e vice-versa (`lint_all.py` cobre as duas direções), se todo `Tipo:` usa o vocabulário controlado, e se toda fonte `Tipo: Ensaio Completo Importado` tem um `Virou: [[Essay]]` que de fato existe. Para todo arquivo fora da subpasta que seu `Tipo:` implica: mova para a subpasta correta agora, sem perguntar (correção mecânica e inequívoca), e atualize `Pasta:` na entrada correspondente. Única exceção que exige pergunta: arquivo sem entrada no manifesto e sem `Tipo:` inferível com confiança — reporte e peça para classificar, não adivinhe.
8. **Estrutura canônica de pastas**: `lint_all.py` verifica se todas as 8 subpastas de `wiki/sources/` (uma por tipo, incluindo `artigo-academico/`) e `wiki/handouts/` existem. Se alguma faltar, crie com `.gitkeep` diretamente — é mecânico.
9. **`wiki/sources/map.md`**: revise por inteiro (não só incremente) — toda fonte em `wiki/sources/` e todo item ainda pendente em `raw/` deve aparecer, com status correto e organizado por assunto.
10. **`wiki/log.md`**: confirme que é append-only (nenhuma entrada antiga foi editada) — só verifique, nunca reescreva o histórico.
11. **`plan/plano.md`**: as 5 seções fixas existem (mesmo vazias)? Algum item usa um `Status:` fora do vocabulário (Pendente | Em Andamento)? Algum tópico fragmentou em quase-duplicatas? Corrija estrutura (seções faltando) direto; para tópicos quase-duplicados, proponha consolidação como faria com tags.
12. **`wiki/insights/`**: toda página tem `maturidade:` válida? Sinalize insights sem nenhum link em `## Conexões` — candidatos a órfãos — e insights `madura` havia tempo sem promoção (sugira `/insight promote`).
13. **Links de toda a wiki — rode e corrija**: rode `python scripts/lint_all.py` (cobre wikilinks mortos, órfãos, consistência de `index.md`, formatação mecânica, sources/manifesto nos dois sentidos, plano, insights, categorias — tudo dos passos acima, em um único relatório). Aplique `python scripts/auto_fix_lint.py` para os achados mecânicos e inequívocos (espaçamento de heading, dois-pontos em display text de wikilink) — sem perguntar. Para cada **wikilink morto** reportado:
    - Se o alvo for claramente um erro de digitação de uma página que existe, corrija agora, sem perguntar.
    - Se o alvo não corresponder a nada existente nem a um erro de digitação óbvio, **não invente ou apague o link silenciosamente** — reporte a lista completa e pergunte o que fazer.
      Links **externos** (URLs que saíram do ar) não são responsabilidade do `/organize` — isso é `/linkify`, chamado por essay via `/sweep`.
14. **Grafo**: rode `python scripts/graph.py` para gerar `output/graph/graph.html` (visualização interativa) e `output/graph/graph.md` (versão Mermaid). Ofereça abrir o HTML — é a forma mais rápida de ver clusters isolados, hubs, e partes da wiki que nunca se conectam entre si (ex: ensaios de filosofia que nunca linkam com os de engenharia).
15. **Exportação** (opcional, só se o Usuário quiser uma checagem completa): rode `python scripts/export_essay.py --all` e `python scripts/export_essay_html.py --all`, confirme que PDFs têm hyperlinks clicáveis, imagens resolvem, `## Conexões` não aparece no PDF e `## Referências`/`## Sumário` aparecem.
16. **Comunique um resumo priorizado** — nunca cole o relatório bruto. Estruture assim:
    - **Corrigido automaticamente** (lista curta do que foi mecânico e já foi aplicado).
    - **Crítico — precisa de decisão sua** (sources sem essay, wikilinks mortos sem alvo óbvio, contradições entre essays, seções do plano fora do vocabulário).
    - **Atenção — vale revisar quando puder** (notas atômicas órfãs, categorias possivelmente duplicadas, tags quase-duplicadas, estrutura de pastas faltando).
    - **Informativo** (contagens do `/stats`, link pro grafo gerado).

## Depois

Log:

```
## [YYYY-MM-DD] organize | Resumo do que foi corrigido
```

Se quiser um snapshot salvo da stats pós-organização, rode `python scripts/stats.py --save`.

## Convenções

Prosa segue `## Estilo de prosa` em `conventions/SKILL.md`.

Não corrija silenciosamente algo que depende de julgamento editorial (qual claim prevalece numa contradição, se um órfão vira essay ou é removido, se duas categorias devem de fato virar uma só).

Correções mecânicas e inequívocas (índice desatualizado, entrada de manifesto faltando, pasta canônica ausente, espaçamento) podem ser aplicadas direto.

## Skills relacionadas

- `/sweep` — corrige prosa dentro de cada essay, não a camada de metadados
- `/stats` — o primeiro passo daqui, e também útil sozinho sem rodar o resto
- `/import`, `/digest`, `/absorb` — quem alimenta `manifest.md` e `map.md` no dia a dia; `/organize` é a auditoria periódica
- `/plan` — recebe itens `Revisão` quando `/organize` encontra algo que precisa de atenção mas não pode ser corrigido na hora
- `/insight` — recebe notas atômicas maduras sinalizadas aqui, para promoção
- `/status` — depois de um `/organize` substancial, ofereça `/status update` para refletir as pendências corrigidas
- `/gaps` — cobertura conceitual (direção oposta ao órfão *reverso* do passo 2)
