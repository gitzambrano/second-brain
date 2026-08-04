---
name: organize
description: >
  Organiza a base de conhecimento na camada de metadados/grafo E na
  formatação mecânica de essay: roda e
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

**[ambos]** Organiza metadados e formatação mecânica: índice, log, mapa de sources, tags, plano, insights, estrutura de pastas, formatação de essay (Markdown, byline, Sumário/Referências/Conexões, Obsidian-compat, espaçamento, aspas, LaTeX, travessões, bullets, residuais, idioma PT-BR).

A maior parte roda por script e aplica fix mecânico. Decisões de fusão/renomeação/contradição exigem leitura e pergunta ao Usuário (marcadas abaixo).

**Não reescreve prosa nem argumento** — isso é `/sweep` (estilo, continuidade, português, links) e `/review` (validade argumentativa).

## Dois modos

```
/organize              → corpus inteiro: formatação de TODOS os essays + índice, órfãos,
                          manifesto/sources, tags, plano, insights, grafo.
/organize <slug>       → escopo único: só formatação mecânica, referências e wikilinks
                          DAQUELE essay. Pula o que exige corpus (órfãos, index, manifesto,
                          tags quase-duplicadas, grafo) — avisando que pulou.
```

Use `/organize <slug>` só quando o Usuário pedir explicitamente a auditoria completa de um essay. Para "acabei de mexer nesse essay, confere o formato", prefira o fechamento embutido nas skills de conteúdo (`/essay`, `/expand`, `/chapter`, `/proofread`, `/polish`, `/continuity`, `/linkify`, `/import`, `/absorb`), que já chamam `check_wiki.py <slug>` e `fix_lint.py <slug>` — mais barato que este skill inteiro.

Nunca cole o relatório bruto de `check_wiki.py` — é genérico de propósito. Resuma priorizado (ver Passo 18).

## Modo corpus inteiro

1. **[script]** `python scripts/build_index.py && python scripts/build_references.py` — direto, sem o subagent.
2. **[script]** Formatação mecânica de todos os essays:

   ```bash
   python scripts/check_wiki.py --json
   python scripts/check_references.py --json
   python scripts/fix_lint.py
   ```

   `check_wiki.py` cobre essay e corpus (índice, órfãos, manifesto, plano, insights, wikilinks mortos). `check_references.py` valida formatação AIAA. `fix_lint.py` aplica fixes mecânicos sem perguntar, incluindo reformatação de `## Referências` ao padrão AIAA.

   Pule fixes automáticos em essays `finalizado`/`maduro` (não altera a prosa deles), mas inclua no relatório.
3. **[script]** Órfãos: `python scripts/find_backlinks.py --orphans`. **[leitura]** Para cada concept/entity sem essay que o referencie, decida com o Usuário: essay novo, anexar a existente, ou remover.
4. **[leitura]** Contradições e claims desatualizados: ao ler os essays (achados do stats ou amostragem), sinalize contradições entre páginas e claims superados, seguindo `## Regra de contradição entre fontes` de `conventions/SKILL.md` — nunca escolha um lado sozinho. Se a correção não for imediata, ofereça registrar `Revisão` em `plan/plano.md` via `/plan add`.
5. **[script]** Confirme `wiki/index.md`/`index.json` regenerados (passo 1). Se essay novo/editado/removido não refletir, rode `build_index.py` de novo.

   **Cobertura do índice**, no JSON do passo 2:

   - `FM_NO_SUMMARY`: essay sem `summary:` — liste nominalmente em "Crítico".
   - `FM_LONG_SUMMARY`: resumo passou de 120 caracteres.

   Não escreva os resumos aqui — resumo é conteúdo editorial. Reporte e ofereça passada dedicada.

   **Cobertura de bibliografia**: cruze `wiki/references.json` com os essays — sem nenhuma entrada em `## Referências`, ou bibliografia rasa para a extensão do texto, entra em "Atenção". `check_wiki.py` emite `NO_REFERENCIAS` para a seção ausente; o julgamento de suficiência é seu.
6. **[leitura]** Tags quase-duplicadas: cheque `tags_in_use` em `wiki/index.json` (essay/concept/entity/insight + manifesto de sources, mesma fonte de vocabulário). Proponha consolidação e liste os afetados antes de renomear em massa.
7. **[script]** Balanço de cobertura por tag: `python scripts/check_gaps.py --tags-only`. Uma tag com um essay só, comparada a outras com dez, é sinal de área subexplorada. **Não corrija nada aqui** — se o Usuário quiser agir sobre uma tag rasa, ofereça `/plan add` (item Essay futuro) ou `/scout` (fontes candidatas pro tema).
8. **[script + leitura]** `python scripts/check_dedupe.py` (se o corpus cresceu desde a última passada, rode também com `--threshold 0.75`). Reporta quatro classes: títulos de essay, títulos de concept/entity, tags, e mesma referência com citação divergente entre essays.

   **Nunca funde nem deleta** — para cada candidato, mostre os dois lados com caminho e **pergunte ao Usuário**. Fuzzy matching erra: par com similaridade alta pode ser conceitos irmãos legítimos.
9. **[script + leitura]** Manifesto, tipos de source, estrutura canônica:

   - Verifique se todo arquivo em `wiki/sources/**` tem entrada no manifesto e vice-versa, se `Tipo:` usa vocabulário controlado, se `Tipo: Ensaio Completo Importado` tem `Virou: [[slug|Essay]]` existente.
   - `Tags:` faltando numa entrada antiga: preencha agora usando o conteúdo da fonte, sem perguntar. Tag fora do vocabulário: sinalize junto ao passo 6.
   - Arquivo fora da subpasta correta: mova agora sem perguntar, atualize `Pasta:`.
   - Exceção que pede pergunta: arquivo sem entrada e sem `Tipo:` inferível — reporte, não adivinhe.
10. **[script]** Estrutura canônica de pastas: `check_wiki.py` verifica as 8 subpastas de `wiki/sources/` e `wiki/handouts/`. Faltando: crie com `.gitkeep` direto.
11. **[leitura]** `wiki/sources/map.md`: revise por inteiro — toda fonte em `wiki/sources/` e todo item pendente em `raw/` aparece, com status correto.
12. **[script]** `wiki/log.md`: confirme append-only (nenhuma entrada antiga editada) — só verifique.
13. **[leitura]** `plan/plano.md`: as 5 seções existem (mesmo vazias)? `Status:` fora do vocabulário (Pendente | Em Andamento)? Tópico fragmentado em quase-duplicatas? Corrija estrutura faltando direto; para tópicos quase-duplicados, proponha consolidação.
14. **[leitura]** `wiki/insights/`: toda página tem `maturidade:` válida? Sinalize insights sem link em `## Conexões` (candidatos a órfãos) e `madura` há tempo sem promoção (sugira `/insight promote`).
15. **[script + leitura]** Wikilinks mortos (já cobertos no passo 2): erro de digitação óbvio de página existente → corrija agora. Alvo sem correspondência óbvia → não invente nem apague, reporte e pergunte. Links externos quebrados são `/linkify`, não `/organize`.
16. **[script]** Formato das `## Referências`: `REFERENCIA_SEM_LINK` e `LINK_NOT_IN_REFERENCIAS` que sobrarem após `fix_lint.py` entram em "Atenção" — pedem busca de fonte (`/linkify`), não correção mecânica.
17. **[script]** Chame o subagent `update` (`.agents/agents/update.md`). Leia o relato: `stats:` e `grafo:` trazem os caminhos — abra `output/graph/graph.html` de lá e use `stats:` no resumo do passo 19. Clusters isolados ou muitos wikilinks mortos sem alvo óbvio: ofereça `/connect`.
18. **[script]** Exportação (opcional, só sob pedido): `python scripts/export_essay_pdf.py --all` e `export_essay_html.py --all`; confirme hyperlinks clicáveis, imagens resolvendo, seção`## Conexões` ausente do PDF, seção`## Referências`/`## Sumário` presentes.
19. **[leitura]** Resumo priorizado — nunca cole o relatório bruto:

    - **Corrigido automaticamente** (mecânico, já aplicado).
    - **Crítico — precisa de decisão** (sources sem essay, wikilinks mortos sem alvo, contradições, seções do plano fora do vocabulário).
    - **Atenção — vale revisar** (notas órfãs, tags quase-duplicadas, tags com cobertura rasa, quase-duplicatas de título/referência, `## Referências` sem link ou fora do padrão, estrutura de pastas faltando).
    - **Informativo** (contagens do stats, link do grafo).
    - **Liste nominalmente os essays com `FM_NO_SUMMARY`.**
    - **[leitura]** `EMPTY_REFERENCIAS`, `REF_BOLD_AUTHOR`, `REF_TITLE_IS_AUTHOR`, `REF_MISSING_TITLE` nunca são auto-corrigíveis — exigem descobrir o título/autor real de fonte externa, o que `fix_lint.py` não navega a web para fazer.

      Use WebFetch na URL (ou WebSearch por autor+ano+container se falhar) antes de reescrever — nunca "de memória". Já revelaram autor completamente errado, não só formatação.

## Modo essay único (`/organize <slug>`)

1. **[leitura]** Resolva o slug (nome do arquivo, título parcial, caminho completo); ambíguo → pergunte.
2. **[script]**

   ```bash
   python scripts/check_wiki.py <slug> --json
   python scripts/check_references.py --file <slug> --json
   python scripts/fix_lint.py <slug>
   ```

   `check_wiki.py <slug>` já pula sozinho, com aviso, o que exige corpus (órfãos, index, manifesto, plano, insights) — só reporta formatação e wikilinks mortos originados nele.
3. **[script]** Aplique fixes automáticos sem perguntar. Reporte o restante por categoria (Estrutura obrigatória, Qualidade de referência, Resumo do índice, Byline, Links, LaTeX/aspas, Espaçamento, Estilo, Residuais, Idioma, Referências).
4. **Não rode** `build_graph.py`, `stats.py`, nem auditorias de manifesto/plano/insights/órfãos — avise que foram puladas por serem checagens de corpus inteiro.
5. **[script]** `## Referências` mudou → `build_references.py`. `summary`/`tags` mudou → `build_index.py`.
6. Apresente: issues corrigidos, issues restantes por categoria, aviso do que foi pulado.

## Depois

Log:

```
## [YYYY-MM-DD] organize | Resumo do que foi corrigido
```

(Essay único: `## [YYYY-MM-DD] organize | Título do Essay`.)

## Convenções

Wikilink e formato de link de seção: `## Regra de links` em `conventions/SKILL.md`. Prosa: `## Estilo de prosa` em `conventions/SKILL.md`.

Não corrija silenciosamente algo que depende de julgamento editorial (qual claim prevalece numa contradição, se um órfão vira essay ou é removido, se duas categorias viram uma só).

Correções mecânicas e inequívocas (índice desatualizado, entrada de manifesto faltando, pasta canônica ausente, espaçamento, tags, formatação) aplicam direto via `fix_lint.py`.

## Skills relacionadas

- `/sweep` — corrige prosa/continuidade/estilo, não metadados
- `/gaps` — cobertura conceitual (termo sem página, página sem link); balanço de tag migrou pra cá
- `/connect` — repara/expande a malha usando a checagem mecânica daqui
- `/stats`, `/import`, `/digest`, `/absorb`, `/plan`, `/insight`, `/status`
