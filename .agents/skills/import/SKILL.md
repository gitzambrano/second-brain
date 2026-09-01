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
4. Classifique o `Tipo:` do source, normalmente `Ensaio Completo Importado`, conforme `## Tipos de Source — Vocabulário Controlado` em `conventions/SKILL.md`; isso determina a subpasta de destino em `wiki/sources/`.
5. Copie o conteúdo **integralmente** para `wiki/essays/` como arquivo `.md`. **O texto original não é alterado** — apenas adicione frontmatter YAML, links externos inline, `## Sumário`, `## Referências` e `## Conexões`. Sem resumo condensado dentro do essay. `status: finalizado` por padrão; use `draft` se ficar claro que é rascunho do próprio autor, conforme `## Status de essay` em `conventions/SKILL.md`.
6. Identifique conceitos e entidades mencionados. Para cada um: se já existe página, atualize com informação nova desta fonte; se não existe e a página tiver valor próprio, crie na subpasta apropriada.
7. Verifique se os concepts/entities criados ou atualizados têm relação com pelo menos um essay. Registre as relações em `## Conexões`; não crie um novo essay apenas para evitar órfão.
8. Adicione wikilinks entre páginas relacionadas na seção `## Conexões`, conforme `## Regra de links — Obsidian é o leitor primário` em `conventions/SKILL.md`.
9. Preencha `summary:` e rode `python scripts/build_index.py` para regenerar `wiki/index.json`/`wiki/index.md`; nunca edite o índice à mão.
10. Converta a bibliografia original para `## Referências` segundo `## Formato de ## Referências — padrão AIAA` em `conventions/SKILL.md`: título em itálico, container completo e `[Link](url)` no final da entrada. Valide com `python scripts/check_references.py --file <slug>` e rode `python scripts/build_references.py`.
11. Mova o arquivo original de `raw/` para `wiki/sources/<subpasta-do-tipo>/`, preservando o nome original. Registre em `wiki/sources/manifest.md` e `wiki/sources/map.md`. `Tags:` reutiliza o mesmo vocabulário controlado das páginas.
12. Feche com o `## Fechamento padrão de essay único` de `conventions/SKILL.md`.
13. Log: `## [YYYY-MM-DD] import | Título do Essay`.

Uma única fonte pode tocar muitas páginas. Isso é normal.

## Convenções

- **O texto original não é alterado no momento da importação** — só depois, sob pedido explícito via `/expand`, `/proofread` etc.
- Não invente dados bibliográficos. Confirme fonte, autores, título e container antes de criar referência.

## Skills relacionadas

- `/digest` — fonte de terceiro
- `/absorb`, `/expand`, `/proofread`, `/polish`
