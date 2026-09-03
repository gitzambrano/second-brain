"""Reexporta lib.site_common no caminho plano antigo.

Existe porque scripts importam este módulo antes de `repo_paths` pôr
`scripts/lib/` no `sys.path`; sem o shim, esses imports quebrariam.
"""
from lib.site_common import *  # noqa: F401, F403
