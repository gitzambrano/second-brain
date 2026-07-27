---
name: chapter
description: >
  Adiciona, move, funde ou divide um capítulo/seção dentro de um essay
  já existente, ou cria uma página nova de conceito/entidade ligada a
  ele. Use quando o Usuário disser "adiciona um capítulo sobre X",
  "junta essas duas seções", "divide esse capítulo em dois", "move
  essa seção pra depois da 3", "cria uma página de conceito pra Y", ou
  quiser mudanças estruturais no essay em vez de mudança de conteúdo
  dentro de seções já existentes.
allowed-tools: Bash Read Write Edit Glob Grep
---

# Chapter

Trabalha a **estrutura** de um essay: capítulos/seções que entram, saem, se movem, se fundem, se dividem, ou uma página nova de conceito/entidade que passa a ser referenciada por ele. Diferente de `/expand`, que lida com o conteúdo dentro de uma seção já existente.

## Regra de abertura

Leia o essay inteiro antes de mover uma única linha. Reorganização é cara de desfazer se sair errada — mais um motivo para não trabalhar só a partir do trecho apontado.

## Adicionar um capítulo/seção nova

1. Depois de ler o essay inteiro, decida a posição: onde a seção nova prepara o terreno para a seguinte e continua o que veio antes.
2. Crie a seção com heading `##`, escreva o conteúdo seguindo o `## Estilo de prosa` de `conventions/SKILL.md`.
3. Adicione a nova seção ao `## Sumário` com o link correspondente.
4. Se a seção nova introduz um conceito/entidade que merece página própria, crie em `wiki/concepts/` ou `wiki/entities/` e linke em `## Conexões`.

## Criar página de conceito/entidade

1. Verifique primeiro se já não existe uma página equivalente (busque em `wiki/concepts/`, `wiki/entities/`, e nos títulos do `wiki/index.md`) — não duplique.
2. Crie o arquivo na subpasta certa, com frontmatter simples e conteúdo denso o bastante para justificar a página própria.
3. Linke a partir do essay em `## Conexões`, e a partir da página nova de volta para o essay.

## Mover, fundir, ou dividir seções

Dois modos, dependendo de quem decide a estrutura final:

- **Pontual**: o Usuário já sabe o que quer mover/fundir/dividir. Execute exatamente o pedido, depois releia o essay inteiro para checar que as transições na nova ordem ainda fazem sentido — uma seção que antes abria referenciando a anterior pode precisar de ajuste na frase de abertura.
- **Geral**: o Usuário pede para você decidir a melhor estrutura. Proponha um esboço novo de seções, em ordem, e espere aprovação antes de mover texto de fato.

Depois de qualquer reorganização, atualize `## Sumário` para refletir a nova ordem e os novos títulos.

## Depois

Atualize `updated:` no frontmatter. Se a mudança foi de peso (nova seção, reorganização geral, página nova criada), log:
```
## [YYYY-MM-DD] chapter | Título do Essay
Resumo da mudança estrutural.
```
Se existir handout para este essay e a reorganização mudou a tese ou o caminho argumentativo, avise o Usuário e ofereça regenerá-lo (`/handout`).

## Convenções

Texto novo segue o `## Estilo de prosa` de `conventions/SKILL.md`. Não invente conteúdo para preencher uma seção nova sem ter material — se o pedido for só "cria um capítulo sobre X" sem mais direção, trate como um pedido de `/expand` primeiro (perguntar o que deve entrar), e só então estruture aqui.

## Skills relacionadas

- `/expand` — conteúdo dentro de uma seção, não a estrutura
- `/continuity` — depois de mover/fundir seções, vale checar que a nova ordem não quebrou a progressão lógica
- `/linkify` — toda página de conceito/entidade nova precisa de link externo na primeira ocorrência dela no essay
