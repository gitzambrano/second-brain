---
name: pdf
description: >
  Exporta um ou todos os essays para PDF via Pandoc + LuaLaTeX e valida
  conteúdo e layout antes de declarar o artefato pronto.
allowed-tools: Bash Read Glob
---
# PDF

Gera PDF a partir de `wiki/essays/` ou handouts. Sem argumento, o exporter gera **todos** os essays, que é o default global dos scripts do repo.

## Fluxo obrigatório

```bash
python scripts/export_essay_pdf.py <slug-ou---all>
python scripts/check_pdf_content.py <slug-opcional>
python scripts/check_pdf_layout.py <slug-opcional>
```

Para batch, omita o slug nos checkers: ambos auditam tudo por default.

`check_pdf_content.py` valida abertura, A4, páginas vazias, título/autor, Sumário/Referências, links, imagens, encoding e ausência de `Conexões`. `check_pdf_layout.py` valida margem, título órfão e paginação vazada; `FIGURA_EMPURRADA` é informativo.

Se qualquer checker retornar erro bloqueante, não declare o PDF validado. Falta de Pandoc/LuaLaTeX é falha de ambiente e deve ser reportada, não contornada por outro exporter.

Não atualize `wiki/log.md`: export é operação de leitura.
