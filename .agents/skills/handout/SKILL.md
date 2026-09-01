---
name: handout
description: >
  Gera um handout de uma página para um essay existente, em
  wiki/handouts/: linha de tese, 3 a 5 conclusões em prosa, e link de
  volta para o essay completo. Use quando o Usuário disser "gera um
  handout desse essay", "resume isso numa página para eu mandar pro
  fulano", ou quiser uma versão executiva rápida de um essay para
  alguém que não vai ler o texto inteiro.
allowed-tools: Bash Read Write Edit Glob AskUserQuestion
---
# Handout

Gera `wiki/handouts/<slug-do-essay>.md`: uma versão curta do essay para compartilhamento.

## Quando usar

Somente sob pedido explícito. Outras skills podem oferecer `/handout`, mas não executá-lo automaticamente.

## Passo a passo

1. Leia o essay completo.
2. Escreva uma frase com a tese central.
3. Extraia 3 a 5 conclusões principais em prosa curta.
4. Monte:

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

<Conclusão 1 em prosa curta.>

<Conclusão 2 em prosa curta.>

<Conclusão 3 a 5, conforme necessário.>

Leia o essay completo: [<Título do Essay>](../essays/<slug>.md)
```

`tags:` copia as do essay. `sources:` fica vazio porque o handout não introduz fonte nova.

5. Não inclua `## Sumário`, `## Referências` nem `## Conexões`.
6. Se já existir handout, regenere o mesmo arquivo e atualize `updated:`.
7. Não atualize `wiki/index.*` nem `wiki/log.md`.

## Handout como output

`wiki/handouts/<slug>.md` é a fonte de trabalho do handout dentro da wiki; como o restante de `wiki/`, não depende de versionamento Git.

Depois de gerar ou atualizar:

1. copie para `output/handouts/<slug>.md`;
2. pergunte se o Usuário quer PDF e/ou HTML:

```bash
python scripts/export_essay_pdf.py <slug> --handout --output output/handouts
python scripts/export_essay_html.py <slug> --handout --output output/handouts
```

3. Não gere PDF/HTML automaticamente.

## Depois

Informe os caminhos em `wiki/handouts/` e `output/handouts/`. Ofereça também exportar o essay completo via `/pdf` ou `/html`.

## Skills relacionadas

- `/essay`
- `/expand`, `/chapter`, `/proofread`, `/polish`
- `/pdf`, `/html`
