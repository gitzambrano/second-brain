---
name: polish
description: >
  Passada de estilo de prosa num essay: tom, ritmo, elegância, adesão
  às regras de prosa da wiki (sem bullets no corpo argumentativo,
  travessões extremamente raros). Use quando o Usuário disser "melhora
  o estilo", "deixa a prosa mais elegante", "tira os bullets daqui",
  "conta os travessões", ou quiser que o texto leia melhor sem mudar o
  que ele argumenta.
allowed-tools: Bash Read Write Edit Glob Grep
---
# Polish

Ajuste de tom, ritmo e elegância de prosa, sem alterar conteúdo. Aplica o `## Estilo de prosa` de `conventions/SKILL.md`.

## Regra de abertura

Leia o essay inteiro antes de reescrever qualquer trecho — estilo é sobre coerência de voz do início ao fim, não sobre polir um parágrafo isolado.

## O que corrigir

1. **Uma proposição por frase.** Divida períodos longos e orações subordinadas encadeadas em frases curtas com ponto final.
2. **Sobriedade de conectores.** Remova conectores empilhados ou desnecessários.
3. **Bullets no corpo argumentativo.** Converta listas de ideias em prosa contínua. Bullets ficam só em `## Sumário`, `## Referências` e tabelas comparativas.
4. **Travessões.** Máximo 2 no essay inteiro. Reescreva excedentes com ponto final, vírgula, dois-pontos ou reestruturação.
5. **Sem ponto e vírgula.** Divida frases unidas por ponto e vírgula em frases autônomas.
6. **Tipografia e símbolos.** Elimine barras (`/`), til (`~`), remissões abreviadas e intervalos numéricos com hífen na prosa.
7. **Essays técnicos.** Elimine antropomorfização (*"o código vê"*), gerúndios soltos de consequência, locuções verbais pesadas e superlativos vazios.

## O que preservar

Mantenha a voz do autor e o nível técnico esperado pelo público do essay — um white paper de engenharia e um ensaio filosófico têm registros diferentes, e a correção de estilo deve preservar essa diferença, não uniformizar tudo para o mesmo tom. Não adicione nem remova ideias, só a forma como estão expressas.

## Relatório

Resuma o que foi ajustado (ex: "3 travessões reescritos, 2 blocos de bullets convertidos em prosa no capítulo 4") em vez de mostrar cada frase antes/depois, a menos que o Usuário peça o diff.

## Depois

Feche com o `## Fechamento padrão de essay único` de `conventions/SKILL.md`.

Atualize `updated:` no frontmatter. Log se o ajuste foi extenso:

```
## [YYYY-MM-DD] polish | Título do Essay
Resumo do ajuste de estilo.
```

## Convenções

Segue a regra de status (batch vs específico) de `## Status de essay` em `conventions/SKILL.md`.

## Skills relacionadas

- `/proofread` — gramática e ortografia, não tom
- `/sweep` — roda `/polish` em todos os essays de uma vez
