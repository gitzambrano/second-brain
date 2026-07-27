---
name: sweep
description: >
  Varre todos os essays de wiki/essays/ e corrige cada um, orquestrando
  os skills focados de iteração (continuity, proofread, polish,
  linkify) um essay por vez. Use quando o Usuário disser "corrige
  todos os essays", "faz uma revisão geral", "passa o pente fino na
  wiki inteira", ou quiser uma passada completa no corpus de essays.
  Também aceita escopo único ("passa o pente fino nesse essay", "roda
  o sweep só no essay X") para rodar a mesma bateria de correções e
  gerar o mesmo tipo de relatório consolidado num essay específico,
  em vez de invocar continuity/proofread/polish/linkify manualmente
  um por um. É um orquestrador: chama outros skills, não duplica a
  lógica deles.
allowed-tools: Bash Read Write Edit Glob Grep WebSearch WebFetch
---
# Sweep

Varre todos os essays de `wiki/essays/` e corrige cada um, chamando os skills focados de iteração em sequência. É um **orquestrador**: a lógica de cada correção vive no skill correspondente, `/sweep` só decide a ordem e agrega o relatório final.

## Diferença em relação a `/organize`

`/sweep` trabalha **dentro** de cada essay (prosa, continuidade, links). `/organize` trabalha na **camada de metadados** da wiki inteira (índice, log, mapa de sources, tags). Rode `/stats` primeiro para decidir qual dos dois (ou os dois) vale a pena.

## Passo a passo

1. Liste todos os essays em `wiki/essays/` (`ls wiki/essays/*.md` ou `Glob`). Em modo escopado (veja `## Modo essay único`), pule direto pra esse essay.
2. **Passada mecânica primeiro**, por script, antes de qualquer correção de prosa:
   - Rode `scripts/lint_all.py` (formatação: linha em branco após heading, labels de capítulo soltos, símbolos residuais, resíduos HTML, blockquote mal usado, contagem de travessões, parágrafos possivelmente não traduzidos para PT-BR) e `scripts/deep_format_check.py`.
   - Aplique os fixes automáticos via `scripts/auto_fix_lint.py` quando o achado for mecânico e inequívoco (ex: linha em branco faltando); para o resto, reporte e peça confirmação.
   - Nessa mesma passada, confirme: frontmatter completo, byline padronizada, `## Sumário`/`## Referências`/`## Conexões` presentes, nenhum `[[wikilink]]` fora de Conexões.
   - Essay sem `status:` (essay antigo, pré-campo): proponha `draft` como default e confirme com o Usuário, não aplique em silêncio.
3. **Pule essays com `status: finalizado` ou `maduro`** — sem perguntar, sem avisar durante a execução (regra completa em `## Status de essay`, `conventions/SKILL.md`). No resumo final, informe quantos foram pulados por status.
4. Para os demais, na ordem:
   1. **`/continuity`** — se encontrar um problema grave (contradição direta com a tese, conclusão que não fecha o argumento), reporte e pergunte se a correção deve ser aplicada agora ou revisada depois, mas só pause os passos seguintes deste essay — nunca o sweep inteiro; continue processando os demais essays do batch normalmente enquanto aguarda essa decisão. Para achados estruturais menores (transição fraca, termo levemente antecipado), apenas registre no relatório final sem interromper.
   2. **`/proofread`** — passada de português.
   3. **`/polish`** — passada de estilo (bullets, travessões).
   4. **`/linkify`** — checagem e adição de links externos.
5. Acumule um resumo por essay (o que foi corrigido, o que foi só reportado e aguarda decisão) em vez de expor cada correção individual durante a execução.
6. Ao final, apresente o relatório consolidado de todos os essays de uma vez, incluindo a contagem de pulados por status.

## Volume e ritmo

Se a wiki tiver muitos essays, isso pode ser uma operação longa. Avise o Usuário da escala antes de começar (ex: "são 23 essays, vou levar um tempo") e considere processar em lotes se ele preferir acompanhar o progresso em vez de esperar o relatório final de tudo. Não se aplica ao modo essay único.

## Modo essay único

`/sweep <slug ou título>` roda a mesma bateria (`/continuity` → `/proofread` → `/polish` → `/linkify`) e o mesmo relatório consolidado, só que num único essay pedido pelo Usuário — sem precisar invocar os quatro skills um por um manualmente.

Ao final das modificações, se o `status: finalizado`alerte o usuário que esse essay estava com status finalizado.

## Depois

Log como uma única entrada consolidada, não uma por essay (modo corpus inteiro):

```
## [YYYY-MM-DD] sweep | N essays revisados
Resumo agregado: X problemas de continuidade reportados, Y correções de português, Z de estilo, W links adicionados/corrigidos. K essays pulados por status (finalizado/maduro).
```

Em modo essay único:

```
## [YYYY-MM-DD] sweep | <Título do Essay>
Resumo: X problemas de continuidade reportados, Y correções de português, Z de estilo, W links adicionados/corrigidos.
```

Atualize `updated:` no frontmatter de cada essay tocado.

## Convenções

Todo texto adicionado ou corrigido segue o `## Estilo de prosa` de `conventions/SKILL.md`.

## Skills relacionadas

- `/organize` — saúde da base inteira (índice, log, mapa, tags), não prosa de essay individual
- `/continuity`, `/proofread`, `/polish`, `/linkify` — os skills que `/sweep` de fato chama
- `/stats` — rode antes para decidir se vale a pena um sweep completo
