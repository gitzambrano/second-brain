---
name: linkify
description: >
  Adiciona links externos a conceitos e termos técnicos ao longo do
  corpo de um essay, e checa os links existentes quanto a validade/
  relevância. Use quando o usuário disser "adiciona mais links", "essa
  seção não tem nenhum link", "checa se os links ainda funcionam", ou
  depois de escrever/editar uma seção que introduz conceitos,
  pensadores ou termos técnicos novos sem hyperlink na primeira
  menção.
allowed-tools: Bash Read Write Edit Glob Grep WebSearch WebFetch
---

# Linkify

Garante que todo conceito, termo técnico, pensador, ou obra citada no corpo de um essay tem um link externo na primeira ocorrência, e que os links existentes ainda apontam para algo relevante e correto.

## Regra de escopo

Só o **corpo do essay** (texto corrido) recebe links externos `[texto](url)`. `[[wikilinks]]` ficam exclusivamente em `## Conexões` — nunca misture os dois formatos fora dessa seção (ver item 6, "Regra de Links — Exportabilidade para PDF", de `## A Regra Fundamental: Essays São o Centro` no AGENTS.md).

## Adicionar links

1. Leia o essay inteiro e liste os conceitos, termos técnicos, pensadores, correntes filosóficas, obras, normas técnicas, ou entidades mencionados sem link.
2. Para cada um, busque a referência mais apropriada: Wikipedia para conceitos gerais, Stanford Encyclopedia of Philosophy (SEP) para filosofia, paper original ou norma técnica para conceitos de engenharia, site oficial para ferramentas/produtos.
3. Adicione o link na **primeira ocorrência** do termo no essay (não em toda repetição — isso poluiria o texto).
4. Mínimo de 10 links externos por essay (ver item 5 de `## A Regra Fundamental: Essays São o Centro` no AGENTS.md) — se o essay estiver abaixo disso, esse é o sinal de que faltam links, não que o mínimo é opcional.

## Checar links existentes

1. Para cada link externo já presente, avalie se a URL parece plausível e se o texto-âncora corresponde ao que o link deveria mostrar.
2. Se houver dúvida sobre um link estar quebrado ou desatualizado, use `WebFetch` para confirmar.
3. Links para páginas que claramente mudaram de conteúdo ou saíram do ar devem ser substituídos por uma fonte equivalente, nunca deixados apontando para o lugar errado.

## O que não fazer

Não adicione um link só para bater o mínimo de 10 — o link deve ser genuinamente relevante ao termo. Não linke a mesma entidade duas vezes no mesmo parágrafo. Não transforme isso numa desculpa para reescrever a prosa (isso é `/polish`) — a única mudança de texto aqui é a inserção do markdown do link.

## Depois

Atualize `updated:` no frontmatter se algum link foi adicionado/corrigido. Log só se for uma passada grande (essay com poucos links recebendo vários):
```
## [YYYY-MM-DD] linkify | Título do Essay
N links adicionados, M links corrigidos.
```

## Skills relacionadas

- `/expand` — se o processo de linkificar revelar que um conceito citado de passagem merece uma explicação melhor no corpo, isso é `/expand`, não `/linkify`
- `/sweep` — roda `/linkify` em todos os essays de uma vez
