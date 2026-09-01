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

Lê uma fonte que não é um essay completo do próprio Usuário, escreve um resumo e arquiva a fonte. **Nunca gera essay.**

Se o material for denso o bastante para sustentar um essay original, sugira `/outline` → `/essay`. `/import` é reservado a texto completo do próprio Usuário.

## Quando usar

Use para papers, capítulos de livro, web clippings, documentação técnica, transcrições e outras fontes de terceiros.

Não use para:
- essay/white paper completo do próprio Usuário → `/import`;
- fonte já processada que o Usuário quer incorporar à wiki → `/absorb`.

## Passo a passo

1. Leia a fonte inteira em `raw/`.
2. Classifique o `Tipo:` conforme `## Tipos de Source — Vocabulário Controlado` em `conventions/SKILL.md`.
3. Se houver figura relevante, extraia para `wiki/assets/` e referencie no resumo conforme `## Tratamento de imagens`.
4. Escreva um resumo de uma página em `wiki/sources/resumos/<slug>.md`: claims principais, metodologia quando aplicável, limitações e síntese parafraseada. Frontmatter: `fonte:`, `tipo:`, `created:`.
5. Entregue também o resumo ao Usuário na conversa.
6. Arquive o original em `wiki/sources/<subpasta-do-tipo>/`, preservando o nome.
7. Registre em `wiki/sources/manifest.md` e `wiki/sources/map.md`, com `Tags:` usando o vocabulário controlado de `conventions/SKILL.md`.
8. Se um `/absorb` encadeado alterou `## Referências` de algum essay, rode `python scripts/build_references.py`.
9. Log: `## [YYYY-MM-DD] digest | Título da Fonte`.

## Depois

Pergunte se o Usuário quer:
- incorporar a fonte a páginas existentes → `/absorb`;
- desenvolver uma tese própria a partir dela → `/outline` → `/essay`;
- guardar uma síntese curta → `/insight add`.

## Convenções

O resumo é parafraseado. Não reproduza parágrafos inteiros da fonte.

Resumo de source não é essay: não recebe `## Sumário`, `## Referências` formal nem `## Conexões`.

Prosa segue `## Estilo de prosa` em `conventions/SKILL.md`.

## Skills relacionadas

- `/import` — texto completo do próprio autor
- `/absorb`, `/essay`, `/insight`
