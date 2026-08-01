---
name: html
description: >
  Exporta um ou todos os essays de wiki/essays/ para um arquivo HTML
  standalone e responsivo via scripts/export_essay_html.py
  (Pandoc). Use quando o Usuário disser "exporta esse essay para HTML",
  "manda um link/arquivo HTML desse ensaio", ou quiser uma versão
  web-friendly que abre bem em desktop ou celular sem precisar de
  LaTeX.
allowed-tools: Bash Read Glob
---

# HTML

Gera um `.html` autocontido (CSS e imagens embutidos, um único arquivo) a partir de um ou mais essays, via `scripts/export_essay_html.py`. Este skill só invoca o script existente — a lógica de conversão vive no script, não aqui.

## Quando usar

- "exporta [essay] para HTML"
- "gera uma versão web desse ensaio"
- "manda esse essay num formato que abre bem no celular"

Para PDF, use `/pdf` em vez deste skill — não duplique lógica de exportação aqui.

Os dois scripts compartilham a mesma preparação de markdown (frontmatter, byline, remoção de Conexões) importando de `export_essay_pdf.py`, então qualquer inconsistência entre PDF e HTML normalmente é bug no script, não neste skill.

## Uso

```bash
# Listar essays disponíveis
python scripts/export_essay_html.py --list

# Exportar um essay específico (nome do arquivo, com ou sem .md)
python scripts/export_essay_html.py nome-do-essay

# Exportar todos os essays
python scripts/export_essay_html.py --all

# Diretório de saída customizado (padrão: output/html/)
python scripts/export_essay_html.py nome-do-essay --output caminho/custom
```

## O que o script já garante (não precisa reimplementar)

1. Mesmo tratamento de conteúdo do export PDF: remove `## Conexões`, preserva `## Sumário`/`## Referências`, resolve imagens, limpa wikilinks residuais.
2. Layout responsivo próprio (`essay_template.html`), com a mesma paleta de cores do PDF (azul-título, azul-link, cinza-sutil) — visual consistente entre os dois formatos de export.
3. `## Sumário` vira um painel de navegação clicável (âncoras internas via IDs de heading gerados pelo Pandoc).
4. Blockquotes (epígrafes, callouts) ganham estilo de caixa com borda lateral.
5. Blocos de código com syntax highlighting (Pygments via Pandoc) e tabelas estilizadas.
6. **MathJax só é incluído se o essay tiver LaTeX** (`$...$`) — checagem automática por regex antes de montar o comando Pandoc, para não inflar o HTML de essays sem matemática.
7. `--embed-resources` embute imagens locais e CSS no próprio arquivo — o `.html` resultante é uma única página que funciona offline e pode ser mandada como anexo.

## Limitação a citar ao Usuário

Quando o essay usa matemática, o MathJax é carregado de um CDN (`cdn.jsdelivr.net`) no momento da exportação: **exportar um essay com LaTeX exige internet**. O HTML já exportado funciona offline depois (o script embute o script, não só referencia).

Se a exportação falhar por rede bloqueada, avise o Usuário em vez de remover o MathJax silenciosamente, o que quebraria as equações.

## Exportar um handout em vez de um essay

O mesmo script exporta handouts de `wiki/handouts/` com a flag `--handout`:

```bash
python scripts/export_essay_html.py <slug-do-essay> --handout --output output/handouts
```

Útil quando o handout vai ser mandado como link/arquivo que abre bem no celular, sem precisar do PDF. Ver skill `/handout` e `## Arquitetura` (bloco `output/`) no AGENTS.md.

## Depois de exportar

1. Confira o output: `OK: <arquivo>.html (<tamanho> KB)` por essay, ou `ERROR` com o `STDERR` do Pandoc.
2. Avise o Usuário do caminho final do(s) HTML(s).
3. Não precisa atualizar `wiki/log.md` — é export de leitura, não uma operação de conteúdo da wiki.

## Skills relacionadas

- `/pdf` — mesma essência, saída PDF via LaTeX
