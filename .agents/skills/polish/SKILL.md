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

1. **Bullets no corpo argumentativo.** Ideias em lista devem virar prosa corrida com transições explícitas entre elas. Bullets ficam só em `## Sumário`, `## Referências`, e tabelas genuinamente mais claras que prosa (comparações numéricas).
2. **Travessões.** Conte quantos `—` existem no essay inteiro, excluindo a byline (`Tipo`) e os separadores de display text de wikilinks no index. **Máximo 2 no essay inteiro.** Se passar, reescreva os excedentes com vírgula, dois-pontos, parênteses ou reestruturação da frase — nunca troque um travessão por outro em outro ponto do texto.
3. **Ritmo e variação de frase.** Frases muito uniformes em tamanho/estrutura cansam — varie, mas sem sacrificar clareza.
4. **Divida frases unidas por ponto e vírgula** em duas frases. Ponto e vírgula deve ser evitado ao máximo.

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
