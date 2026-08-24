"""Força UTF-8 (errors="replace") em stdout/stderr dos scripts da wiki.

Efeito acontece no import - não há função a chamar. Necessário porque o
console padrão do Windows (cp1252) não cobre caracteres como `─` e `⚠`
usados nos relatórios.

Uso:
    import console_encoding  # noqa: F401  (primeiro import do script)
"""

import sys

for _stream in (sys.stdout, sys.stderr):
    _reconfigure = getattr(_stream, "reconfigure", None)
    if _reconfigure is not None:
        try:
            _reconfigure(encoding="utf-8", errors="replace")
        except (ValueError, OSError):
            # Stream redirecionado para algo que não aceita reconfiguração;
            # seguir sem UTF-8 é melhor do que abortar na importação.
            pass
