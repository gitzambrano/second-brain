# Testing and Repository Quality

The repository is intentionally a **skeleton**. Personal essays are not versioned and are never required by CI.

## Defaults

Every executable script must do something useful with no positional CLI arguments. Read-only tools run the broadest audit/inventory; generators generate all applicable outputs; mutation tools that cannot choose a safe mutation fall back to a read-only global diagnosis.

Enforcement:

```bash
python scripts/check_script_defaults.py
```

## Main entry point

```bash
python scripts/check_repo.py          # full diagnosis (default)
python scripts/check_repo.py --quick
python scripts/check_repo.py --wiki
python scripts/check_repo.py --exports
```

A fresh skeleton returns `SKIP` for corpus/export groups when no essays/outputs exist.

## Synthetic corpus

`tests/fixtures/mini-brain/` is artificial. It contains no personal content and exercises frontmatter, byline, headings, internal/external links, LaTeX, tables, code, images, references and connections.

Integration tests may temporarily copy this fixture into the ignored `wiki/` tree **only when the checkout is confirmed to contain no real pages**. Tests abort/skip instead of touching a populated corpus.

## pytest

```bash
python -m pytest -q
python -m pytest -m html
python -m pytest -m pdf
python -m pytest -m "not slow"
```

HTML browser checks need Playwright Chromium:

```bash
python -m playwright install chromium
```

PDF export checks need Pandoc + LuaLaTeX.

## Bug regression rule

For deterministic mechanical bugs:

1. reproduce the bug with a fixture/mutation;
2. add a test that fails;
3. apply the fix;
4. confirm the focused test passes;
5. run the relevant suite.

Do not add real essays as regression fixtures.
