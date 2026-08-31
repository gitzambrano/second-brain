---
name: html
description: >
  Exporta um ou todos os essays para HTML standalone via
  scripts/export_essay_html.py e valida o artefato antes de declará-lo pronto.
allowed-tools: Bash Read Glob
---
# HTML

Gera HTML standalone a partir de `wiki/essays/` ou handouts. Sem argumento, o exporter gera **todos** os essays, que é o default global dos scripts do repo.

## Fluxo obrigatório

```bash
python scripts/export_essay_html.py <slug-ou---all>
python scripts/check_html_export.py <slug-opcional>
python scripts/check_html_render.py <slug-opcional>
```

Para batch, omita o slug nos dois checkers: ambos auditam tudo por default.

Estados de saída:

- **EXPORT OK + VALIDATION PASS** — sucesso completo.
- **EXPORT OK + BROWSER SKIP** — checker estrutural passou, mas Playwright/Chromium não está disponível; diga isso explicitamente.
- **EXPORT OK + VALIDATION FAIL** — não declare o HTML validado; reporte os códigos.
- **EXPORT FAILED** — reporte STDERR/causa.

`check_html_export.py` cobre estrutura/DOM, anchors, resíduos, imagens e dependências externas. `check_html_render.py` abre mobile + desktop e cobre overflow, imagens, console e navegação interna.

Não atualize `wiki/log.md`: export é operação de leitura.
