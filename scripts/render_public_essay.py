"""Reexporta lib.render_public_essay no caminho plano antigo.

Existe porque scripts importam este módulo antes de `repo_paths` pôr
`scripts/lib/` no `sys.path`; sem o shim, esses imports quebrariam.
"""
from lib.render_public_essay import *  # noqa: F401, F403
from lib.render_public_essay import main as _main

if __name__ == "__main__":
    raise SystemExit(_main())
