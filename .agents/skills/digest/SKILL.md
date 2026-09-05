---
name: digest
description: >
  Resume e arquiva uma fonte de terceiro sem gerar essay. Use para papers,
  livros, clippings, documentação e transcrições; para incorporar uma fonte já
  processada a páginas existentes, use /absorb.
metadata:
  second-brain-role: "source-ingestion"
  second-brain-mode: "write"
  second-brain-scope: "source"
  second-brain-approval: "none"
  second-brain-closure: "source"
allowed-tools: Bash Read Write Edit Glob Grep WebSearch WebFetch AskUserQuestion
---
# Digest

Processa uma fonte que **não** é um essay completo do próprio Usuário. Produz resumo e arquivo permanente; nunca cria essay.

## Fluxo

1. Leia a fonte inteira.
2. Classifique `Tipo:` conforme `conventions/SKILL.md`.
3. Extraia figura para `wiki/assets/` apenas quando ela for necessária ao resumo.
4. Escreva `wiki/sources/resumos/<slug>.md` com claims principais, método quando aplicável, limitações e síntese parafraseada. Use frontmatter `fonte:`, `tipo:` e `created:`.
5. Entregue a mesma síntese ao Usuário.
6. Arquive o original em `wiki/sources/<subpasta-do-tipo>/`, preservando nome e conteúdo.
7. Atualize `wiki/sources/manifest.md` e `wiki/sources/map.md`, reutilizando o vocabulário controlado de tags.
8. Registre:

```markdown
## [YYYY-MM-DD] digest | Título da Fonte
```

## Depois

Não execute `/absorb` automaticamente.

Se o Usuário quiser continuar:

- incorporar a fonte a páginas existentes → `/absorb`;
- desenvolver tese própria → `/outline` → `/essay`;
- guardar uma ideia curta → `/insight add`.

Cada skill de destino cuida do próprio fechamento e dos próprios derivados.

## Limites

- Resumo de source não recebe `## Sumário`, `## Referências` formal nem `## Conexões`.
- Parafraseie; não reproduza trechos longos.
- `/import` é reservado a texto completo do próprio autor.
- Prosa e tipos de source seguem `conventions/SKILL.md`.
