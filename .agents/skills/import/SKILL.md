---
name: import
description: >
  Ingere uma fonte que já é um essay/white paper completo escrito pelo
  próprio Usuário: preserva o texto intacto, empacota como um essay
  próprio da wiki. Use quando um arquivo em raw/ (ou texto colado) for
  um texto pronto do próprio autor, não material de terceiro a
  resumir. Se houver dúvida se a fonte é de fato obra completa do
  autor, pergunte antes de prosseguir: usar /import numa fonte de
  terceiro apresentaria incorretamente a escrita de outra pessoa como
  essay do autor.
allowed-tools: Bash Read Write Edit Glob Grep WebSearch WebFetch AskUserQuestion
---

# Import

Processa uma fonte que **já é** um ensaio, white paper, ou artigo completo escrito pelo próprio Usuário. O texto vira essay preservando-se intacto — Claude aqui é arquivista, não coautor. Para qualquer fonte que não seja do próprio autor (paper de terceiro, livro, web clipping, transcrição), use `/digest`, não este skill.

Diferente de `/essay`, este skill **não passa por `/outline`**: não há tese a estruturar, porque não há autoria nova acontecendo — o texto já existe pronto, o trabalho aqui é fiel transformação em `.md`, não redação.

## Antes de começar: confirme a natureza da fonte

Se não estiver claro que o texto é do próprio Usuário e já está pronto (não um rascunho a desenvolver, não um material de terceiro), pergunte antes de prosseguir. É melhor uma pergunta rápida do que apresentar o trabalho de outra pessoa como um essay do autor.

## Passo a passo

1. Leia a fonte inteira em `raw/`.
2. Discuta com o Usuário os pontos-chave, se fizer sentido — mas o texto em si não muda.
3. Se necessário, traduza para Português do Brasil.
4. Classifique o `Tipo:` do source (normalmente `Ensaio Completo Importado`, ver `## Tipos de Source — Vocabulário Controlado` no AGENTS.md) — isso determina a subpasta de destino em `wiki/sources/`.
5. Copie o conteúdo **integralmente** para `wiki/essays/` como arquivo `.md`. **O texto original não é alterado** — apenas adicione: frontmatter YAML (incluindo `summary:`, resumo de uma linha até 120 caracteres), links externos inline, `## Sumário`, `## Referências`, `## Conexões`. Sem resumo condensado dentro do essay (use a skill `/handout` depois, se o Usuário quiser um). `status: finalizado` por padrão (texto chegou pronto); `status: draft` se ficar claro que é rascunho do próprio autor — ver `## Status de essay` em `conventions/SKILL.md`.
6. Identifique todos os conceitos e entidades mencionados. Para cada um: se já existe página, atualize com informação nova desta fonte; se não existe, crie na subpasta apropriada.
7. Verifique se todos os conceitos/entidades criados/atualizados são referenciados por pelo menos um essay. Se não, crie um novo essay que os abrace ou atualize um existente.
8. Adicione `[[wikilinks]]` entre todas as páginas relacionadas, na seção `## Conexões`.
9. Preencha `summary:` no frontmatter e rode `python scripts/build_index.py` para regenerar `wiki/index.json`/`wiki/index.md` (apenas essays entram no índice) — nunca insira a entrada à mão.
10. Como o passo 5 acrescentou `## Referências`, rode `python scripts/references_index.py` para regenerar `wiki/references.json`/`.md`.
11. Mova o arquivo original de `raw/` para `wiki/sources/<subpasta-do-tipo>/`, preservando o nome original. Registre em `wiki/sources/manifest.md` (`Tipo:`, `Tags:`, `Pasta:`, `Virou:`) e em `wiki/sources/map.md` (status: "Importado como [[Essay]]"). `Tags:` reusa o mesmo vocabulário controlado dos essays (`## Tags — Vocabulário Controlado` em `conventions/SKILL.md`) — em geral as mesmas tags do essay que a fonte virou, já que é o mesmo conteúdo.
12. Log: `## [YYYY-MM-DD] import | Título do Essay`

Uma única fonte pode tocar 10-15 páginas da wiki. Isso é normal.

## Convenções

- **O texto original não é alterado no momento da importação** — só depois, se pedido explicitamente via `/expand`, `/proofread`, etc.

## Skills relacionadas

- `/digest` — quando a fonte NÃO é um essay completo do autor
- `/absorb` — para enriquecer páginas existentes com uma fonte já processada
- `/expand`, `/proofread`, `/polish` — para iterar no essay depois de importado
