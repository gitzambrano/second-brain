---
name: sweep
description: >
  Varre todos os essays de wiki/essays/ e corrige cada um, orquestrando
  os skills focados de iteração (continuity, proofread, polish,
  linkify) um essay por vez. Use quando o Usuário disser "corrige
  todos os essays", "faz uma revisão geral", "passa o pente fino na
  wiki inteira", ou quiser uma passada completa no corpus de essays em
  vez de um essay específico. É um orquestrador: chama outros skills,
  não duplica a lógica deles.
allowed-tools: Bash Read Write Edit Glob Grep WebSearch WebFetch
---

# Sweep

Varre todos os essays de `wiki/essays/` e corrige cada um, chamando os skills focados de iteração em sequência. É um **orquestrador**: a lógica de cada correção vive no skill correspondente, `/sweep` só decide a ordem e agrega o relatório final.

## Diferença em relação a `/organize`

`/sweep` trabalha **dentro** de cada essay (prosa, continuidade, links). `/organize` trabalha na **camada de metadados** da wiki inteira (índice, log, mapa de sources, tags). Rode `/stats` primeiro para decidir qual dos dois (ou os dois) vale a pena.

## Passo a passo

1. Liste todos os essays em `wiki/essays/` (`ls wiki/essays/*.md` ou `Glob`).
2. **Passada mecânica primeiro**, por script, antes de qualquer correção de prosa: rode `scripts/lint_all.py` (formatação: linha em branco após heading, labels de capítulo soltos, símbolos residuais, resíduos HTML, blockquote mal usado, contagem de travessões, parágrafos possivelmente não traduzidos para PT-BR) e `scripts/deep_format_check.py`. Aplique os fixes automáticos via `scripts/auto_fix_lint.py` quando o achado for mecânico e inequívoco (ex: linha em branco faltando); para o resto, reporte e peça confirmação. Nessa mesma passada, confirme: frontmatter completo, byline padronizada, ausência de `## Resumo Executivo`, `## Sumário`/`## Referências`/`## Conexões` presentes, nenhum `[[wikilink]]` fora de Conexões.
3. Para cada essay, na ordem:
   1. **`/continuity`** — se encontrar problema estrutural relevante (salto lógico, conclusão que não fecha o argumento), reporte e pergunte se o Usuário quer que a correção seja aplicada agora ou revisada por ele depois, antes de prosseguir para os passos seguintes neste essay.
   2. **`/proofread`** — passada de português.
   3. **`/polish`** — passada de estilo (bullets, travessões).
   4. **`/linkify`** — checagem e adição de links externos.
4. Acumule um resumo por essay (o que foi corrigido, o que foi só reportado e aguarda decisão) em vez de expor cada correção individual durante a execução.
5. Ao final, apresente o relatório consolidado de todos os essays de uma vez.

## Volume e ritmo

Se a wiki tiver muitos essays, isso pode ser uma operação longa. Avise o Usuário da escala antes de começar (ex: "são 23 essays, vou levar um tempo") e considere processar em lotes se ele preferir acompanhar o progresso em vez de esperar o relatório final de tudo.

## Depois

Log como uma única entrada consolidada, não uma por essay:

```
## [YYYY-MM-DD] sweep | N essays revisados
Resumo agregado: X problemas de continuidade reportados, Y correções de português, Z de estilo, W links adicionados/corrigidos.
```

Atualize `updated:` no frontmatter de cada essay tocado.

## Convenções

Não pule `/continuity` mesmo que o Usuário só tenha pedido "corrige o português de tudo" — se você notar um problema estrutural sério passando por um essay durante o `/proofread`, reporte de qualquer forma ao final, mesmo que fora do escopo original pedido.

## Skills relacionadas

- `/organize` — saúde da base inteira (índice, log, mapa, tags), não prosa de essay individual
- `/continuity`, `/proofread`, `/polish`, `/linkify` — os skills que `/sweep` de fato chama
- `/stats` — rode antes para decidir se vale a pena um sweep completo
