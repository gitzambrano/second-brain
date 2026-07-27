---
name: digest
description: >
  Lê uma fonte que NÃO é um essay completo do autor (paper acadêmico,
  livro, web clipping, documentação técnica, transcrição), resume para
  o Usuário, arquiva corretamente — e nunca gera um essay a partir
  dela. Use quando o Usuário colocar uma fonte de terceiro em raw/ e
  quiser um resumo rápido e o arquivamento correto, não um essay novo.
  Se o Usuário quiser o conteúdo da fonte incorporado a essays/
  conceitos já existentes, isso é /absorb, executado depois deste.
allowed-tools: Bash Read Write Edit Glob Grep WebSearch WebFetch AskUserQuestion
---

# Digest

Lê uma fonte que não é um ensaio completo do próprio Usuário, escreve um resumo para ele e arquiva a fonte organizadamente. **Nunca gera essay.** Se o material for denso o bastante para merecer um essay próprio, avise o Usuário e sugira `/essay` ou `/import` em vez de fazer isso aqui.

## Quando usar (e quando não)

Use para: papers acadêmicos, capítulos de livro, web clippings, documentação técnica, transcrições — qualquer coisa que Usuário não escreveu e não quer necessariamente virar um essay agora.

Não use para: um ensaio/white paper do próprio Usuário (isso é `/import`) ou quando o Usuário já quer o conteúdo incorporado a um essay/conceito existente agora mesmo (isso é `/absorb`, rodado depois do digest ou direto se a fonte já estiver em `wiki/sources/`).

## Passo a passo

1. Leia a fonte inteira em `raw/`.
2. Classifique o `Tipo:` (vocabulário controlado: Web Clipping, Artigo Acadêmico, Livro, Documentação Técnica, Transcrição, Ideias, Outro — ver AGENTS.md).
3. Se a fonte tiver figura embutida (PDF, DOCX, HTML), extraia para `wiki/assets/` e linke no resumo — ver `## Tratamento de imagens` em `conventions/SKILL.md`.
4. Escreva um resumo de uma página em `wiki/sources/resumos/<slug>.md`: claim(s) principal(is), metodologia se aplicável, limitações, 2-3 citações-chave (parafraseadas, nunca copiadas verbatim além de trechos curtíssimos). Frontmatter simples: `fonte:` (nome do arquivo original), `tipo:`, `created:`.
5. **Entregue o resumo ao Usuário na própria conversa** — não é suficiente só salvar o arquivo, ele quer ler agora.
6. Arquive o original em `wiki/sources/<subpasta-do-tipo>/`, preservando o nome. Registre em `wiki/sources/manifest.md` e em `wiki/sources/map.md` (status: "Resumido — ver resumo", com link pro arquivo em `resumos/`).
7. Log: `## [YYYY-MM-DD] digest | Título da Fonte`

## Depois

Pergunte se o Usuário quer usar essa fonte para enriquecer algum essay/conceito existente agora — se sim, é `/absorb`. Se ele quiser que ela vire um essay novo, é `/essay` (com a fonte como referência) ou, se ele reescrever o conteúdo como próprio, eventualmente `/import`.

## Convenções

Resumo é sempre parafraseado nas próprias palavras — nunca reproduza parágrafos inteiros da fonte, mesmo internamente em `wiki/sources/resumos/`.

Isso não é um essay: sem `## Sumário`, `## Referências` formal, ou `## Conexões` — é um resumo de uma página, direto ao ponto.

Prosa segue `## Estilo de prosa` em `conventions/SKILL.md`.

## Skills relacionadas

- `/import` — quando a fonte é um essay completo do próprio autor
- `/absorb` — para de fato incorporar o conteúdo da fonte a páginas existentes
- `/essay` — se o Usuário decidir que o tema merece um essay novo, depois de ver o resumo
- `/atom` — se o resumo provocar uma ideia nova, solta, que não é sobre a fonte em si
