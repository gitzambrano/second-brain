---
name: query
description: >
  Responde perguntas usando somente o conhecimento registrado na wiki. Use para
  localizar, resumir, comparar ou cruzar essays e páginas relacionadas; para
  pesquisa externa use /study, e para síntese emergente use /synthesize.
metadata:
  second-brain-role: "knowledge-query"
  second-brain-mode: "read"
  second-brain-scope: "wiki"
  second-brain-approval: "none"
  second-brain-closure: "none"
allowed-tools: Bash Read Glob Grep
---
# Query

Busca e sintetiza o conhecimento que já está registrado. **É read-only.**

## Busca

1. Comece por `wiki/index.json` para identificar essays relevantes por título, summary e tags.
2. Busque o conteúdo com:

```bash
qmd query "termos da busca"
```

Se qmd não estiver disponível ou a collection `secondbrain` não existir, use:

```bash
python scripts/find_text.py "termos da busca" --ignore-case
```

3. Leia integralmente os essays que realmente sustentam a resposta.
4. Siga `## Conexões` para concepts/entities relevantes quando isso acrescentar contexto.
5. Consulte `wiki/sources/` apenas quando a informação necessária não estiver coberta pelas páginas processadas.

Prefira responder a partir da página processada porque ela já expressa o conhecimento incorporado à wiki; não presuma que ela esteja traduzida ou que reproduza integralmente a fonte original.

## Resposta

Adapte a forma à pergunta: resposta direta, comparação, narrativa ou catálogo. Cite as páginas de origem com wikilinks no formato de `conventions/SKILL.md` e não atribua à wiki uma afirmação que ela não sustenta.

Se a resposta exigir informação nova da web, pare de tratar o pedido como `/query` e encaminhe para `/study` ou `/scout` conforme o objetivo.

## Persistência

`/query` nunca cria nem edita páginas e não escreve em `wiki/log.md`.

Se o Usuário pedir para salvar algo que surgiu na resposta:

- ideia curta ou ponte → `/insight add`;
- tese nova → `/outline` e depois `/essay`;
- mudança em essay existente → `/expand` ou `/chapter`.

A skill de destino é responsável por validação, frontmatter, log e derivados.

## Limites

- Sem pesquisa web.
- Sem escrita na wiki.
- Sem criação direta de essay/insight.
- `/synthesize` procura conhecimento emergente; `/query` responde à pergunta dada.
