"""Reexporta lib.console_encoding no caminho plano antigo.

Existe porque scripts importam este módulo antes de `repo_paths` pôr
`scripts/lib/` no `sys.path`; sem o shim, esses imports quebrariam.
"""
from lib.console_encoding import *  # noqa: F401, F403
