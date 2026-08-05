---
name: proofread
description: >
  Passada de revisão de português num essay: gramática, ortografia,
  concordância, pontuação, consistência terminológica. Use quando o
  Usuário disser "corrige o português", "dá uma geral na gramática",
  "revisa a ortografia", ou quiser uma passada só de língua, sem mudar
  conteúdo ou argumento.
allowed-tools: Bash Read Write Edit Glob Grep AskUserQuestion
---

# Proofread

Passada geral de português: gramática, ortografia, concordância, pontuação. Não toca em conteúdo ou argumento — só na língua.

## Regra de abertura

Prosa segue `## Estilo de prosa` em `conventions/SKILL.md`.

Leia o essay inteiro nessa passada, não seção por seção isoladamente. É comum um termo técnico aparecer traduzido de duas formas diferentes em capítulos escritos em momentos distintos, e só a leitura completa pega isso.

## O que corrigir

- Concordância verbal e nominal
- Ortografia e acentuação
- Pontuação: vírgulas ausentes ou sobrando, ponto e vírgula em excesso onde uma frase mais curta comunica melhor
- Parágrafos longos demais, quando dividir ajuda a leitura
- Grafia inconsistente de um mesmo termo técnico entre seções diferentes — escolha uma grafia e uniformize em todo o essay

## O que não fazer

- Não altere conteúdo, argumento, ou a ordem das ideias
- Não mude o tom ou registro (isso é `/polish`)
- Não corrija um termo técnico que está certo só porque parece estranho — se tiver dúvida sobre se é erro de português ou termo técnico legítimo da área (aerodinâmica, xadrez computacional, filosofia da mente), pergunte antes de mudar

## Relatório

Ao reportar, resuma o que foi corrigido em vez de listar cada troca individual — por exemplo: "concordância verbal em dois pontos, vírgulas ausentes em três frases longas, e 'inflow' vs 'influxo' padronizado para 'influxo' em todo o texto".

## Depois

Feche com o `## Fechamento padrão de essay único` de `conventions/SKILL.md`.

Correções pequenas e locais não precisam de entrada no log. Se a passada foi extensa (essay inteiro, muitos pontos corrigidos), log:

```
## [YYYY-MM-DD] proofread | Título do Essay
Resumo do que foi corrigido.
```

Atualize `updated:` no frontmatter.

## Convenções

Segue a regra de status (batch vs específico) de `## Status de essay` em `conventions/SKILL.md`.

## Skills relacionadas

- `/polish` — tom e ritmo de prosa, não gramática
- `/sweep` — roda `/proofread` em todos os essays de uma vez
