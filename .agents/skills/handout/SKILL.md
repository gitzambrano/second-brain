---
name: handout
description: >
  Gera uma versão curta, de cerca de uma página, a partir de um essay existente.
  Use quando o Usuário pedir handout/resumo executivo; mantém a fonte canônica em
  wiki/handouts/ e copia o derivado para output/handouts/.
metadata:
  second-brain-role: "derivative-author"
  second-brain-mode: "write"
  second-brain-scope: "handout"
  second-brain-approval: "none"
  second-brain-closure: "artifact"
allowed-tools: Bash Read Write Edit Glob AskUserQuestion
---
# Handout

Gera `wiki/handouts/<slug>.md` a partir de um essay existente. Só roda sob pedido explícito.

## Conteúdo

1. Leia o essay inteiro.
2. Escreva uma frase com a tese central.
3. Extraia 3 a 5 conclusões principais em prosa curta.
4. Use o template:

```markdown
---
tags: [tag1, tag2]
sources: []
essay: <slug-do-essay>
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# <Título do Essay>

<Uma frase com a tese central.>

<Conclusão 1.>

<Conclusão 2.>

<Conclusão 3 a 5.>

Leia o essay completo: [<Título do Essay>](../essays/<slug>.md)
```

`tags:` copia as do essay. `sources:` fica vazio porque o handout não introduz fonte nova.

Não inclua `## Sumário`, `## Referências` nem `## Conexões`.

Se o handout já existir, regenere o mesmo arquivo e atualize `updated:`.

## Fonte e output

- `wiki/handouts/<slug>.md` é a fonte canônica do handout;
- copie o resultado para `output/handouts/<slug>.md` como artefato derivado;
- não atualize `wiki/index.*` nem `wiki/log.md`.

PDF/HTML só sob pedido explícito:

```bash
python scripts/export_essay_pdf.py <slug> --handout --output output/handouts
python scripts/export_essay_html.py <slug> --handout --output output/handouts
```

Informe os caminhos gerados. Outras skills podem oferecer `/handout`, mas não devem executá-lo automaticamente.
