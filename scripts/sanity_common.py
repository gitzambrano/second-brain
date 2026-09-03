"""Reexporta lib.sanity_common no caminho plano antigo.

Existe porque scripts importam este módulo antes de `repo_paths` pôr
`scripts/lib/` no `sys.path`; sem o shim, esses imports quebrariam.
"""
from lib.sanity_common import *  # noqa: F401, F403
from lib.sanity_common import main as _main

if __name__ == "__main__":
    raise SystemExit(_main())
