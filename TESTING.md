# Testing and Repository Quality

The public engine repository contains **no personal corpus**. The wiki, plan, raw inbox
and generated outputs live in the private nested repository `data/`, which the engine Git
ignores completely. CI never needs `data/` or `site/`, never clones the private
repository and never receives a private credential.

Path resolution goes through `scripts/repo_paths.py`:

```text
CODE_ROOT  this engine checkout
DATA_ROOT  data/  (override: SECOND_BRAIN_DATA_ROOT)
SITE_ROOT  site/  (override: SECOND_BRAIN_SITE_ROOT)
```

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

A checkout without a populated `data/` returns `SKIP` for corpus/export groups.

`--quick` also validates nested-Git isolation (`check_workspace.py`) and path discipline
(`check_path_discipline.py`). `--wiki` also runs `check_freshness.py` and
`check_publication.py`.

The public site is a **separate, explicit gate** and is never built by `check_repo.py`:

```bash
python scripts/build_site.py --check
python scripts/check_site_privacy.py
```

## Synthetic corpus

`tests/fixtures/mini-brain/` is artificial. It contains no personal content and exercises frontmatter, byline, headings, internal/external links, LaTeX, tables, code, images, references and connections.

Integration tests copy this fixture into a pytest `tmp_path` and point the scripts at it
with `SECOND_BRAIN_DATA_ROOT`. **Tests never write into the engine checkout or into the
real `data/` repository** — that isolation is a privacy requirement, not a convenience.

`tests/test_site_privacy.py` is the sentinel leak test: it builds a synthetic site with one
public essay and one private essay carrying a unique sentinel, plus a public→private
connection, and proves the private body, slug, title, graph node and graph edge never reach
the site output. Do not weaken or remove it.

## pytest

```bash
python -m pytest -q
python -m pytest -m html
python -m pytest -m pdf
python -m pytest -m "not slow"
```

There is a single `.agents/` source tree and no generated skill mirror;
`tests/test_no_agent_mirrors.py` enforces that.

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
