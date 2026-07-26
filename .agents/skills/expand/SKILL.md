---
name: expand
description: >
  Adiciona ou corrige conteúdo substantivo num essay já existente:
  teses novas, conceitos, exemplos, ou correção de um erro conceitual/
  factual, perguntando ao usuário quando a direção não é óbvia. Use
  quando o usuário disser "adiciona uma ideia sobre X", "corrige esse
  conceito", "acho que falta um exemplo aqui", "quero incluir a
  perspectiva de Y", ou apontar uma lacuna/erro factual ou conceitual
  num essay existente.
allowed-tools: Bash Read Write Edit Glob Grep WebSearch WebFetch AskUserQuestion
---

# Expand

Adiciona ou corrige conteúdo substantivo — ideias, teses, exemplos, conceitos — num essay que já existe. Diferente de `/chapter` (que lida com a estrutura: onde um capítulo entra, sai, se funde), `/expand` lida com o conteúdo em si: o que está sendo dito, não a organização de onde é dito.

## Regra de abertura

Leia o essay inteiro antes de qualquer edição, mesmo que o pedido pareça hiper-local. Ver `## Iteração em Essays Existentes` no AGENTS.md.

## Quando o pedido é vago, pergunte

Se o usuário disser "adiciona algo sobre determinismo" sem mais detalhe, não invente uma direção sozinho — pergunte o que ele quer que o essay defenda ou explore ali, que exemplo ou pensador ele tem em mente, ou se é uma expansão de um parágrafo existente ou um ponto novo. Uma pergunta direta, não um questionário. Se o pedido já vem específico ("adiciona um parágrafo citando o experimento mental do quarto chinês do Searle aqui"), não precisa perguntar, só execute.

## Dois modos

### 1. Adição

O usuário quer incluir uma ideia, tese, conceito ou exemplo novo, sem tirar o que já está escrito.

1. Depois de ler o essay inteiro, decida o melhor ponto de inserção — o lugar certo é onde o conteúdo novo se conecta ao que vem antes e prepara o que vem depois, não necessariamente o fim do documento.
2. Se for grande o bastante para virar seção própria, isso é trabalho de `/chapter`, não deste skill — avise o usuário e sugira.
3. Se for uma expansão de um parágrafo ou ponto já existente, integre à prosa corrida, não como um adendo colado ao final.
4. Se o conteúdo se apoia em fonte externa nova, adicione a `## Referências` e ao campo `sources:` do frontmatter, com link externo inline na primeira ocorrência do conceito.
5. Se o novo conceito merece página própria (`wiki/concepts/` ou `wiki/entities/`), crie-a e linke em `## Conexões`.

### 2. Correção conceitual/factual

O usuário aponta um erro. Depois de ler o essay inteiro:

1. Verifique se o mesmo erro se repete em outro trecho e corrija todas as ocorrências, não só a apontada.
2. Se envolve um dado, cifra, ou claim que merece verificação externa, use `WebSearch`/`WebFetch` antes de reescrever — nunca corrija um fato por palpite.
3. Se o conceito tem página própria em `wiki/concepts/`, atualize-a também, para as duas fontes não ficarem contraditórias entre si.
4. Preserve o resto do texto intacto — a correção é cirúrgica.

## Depois

Atualize `updated:` no frontmatter. Se a mudança foi substancial, log:
```
## [YYYY-MM-DD] expand | Título do Essay
Resumo do que foi adicionado/corrigido.
```
Se `## Sumário` ou `## Conexões` ficaram desatualizados, atualize-os. Se existir handout em `wiki/handouts/<slug>.md` e a tese central mudou, avise o usuário e ofereça regenerá-lo (`/handout`).

## Convenções

Todo texto adicionado segue `## Estilo de Prosa dos Essays` do AGENTS.md (sem bullets no corpo, travessões extremamente raros) e está em Português do Brasil. Essays originais preservados de `raw/` também podem receber expansão — a regra de "texto intacto" vale para o momento da ingestão, não impede uma expansão pedida explicitamente depois.

## Skills relacionadas

- `/chapter` — quando a adição é estrutural (capítulo/seção nova, reorganização)
- `/continuity` — se a adição for grande, vale rodar depois para checar que a nova peça se encaixa
- `/linkify` — garantir que todo conceito novo tem link externo
