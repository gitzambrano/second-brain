"""Força UTF-8 na saída de console dos scripts da wiki.

Basta importar: o efeito acontece no import, não há função a chamar.

O console padrão do Windows usa cp1252, que não cobre os caracteres de caixa
(`─`), o sinal de aviso (`⚠`) nem parte da pontuação usada nos relatórios. Sem
isto, `check_wiki.py`, `stats.py` e `build_graph.py` abortam com UnicodeEncodeError
depois de já terem feito todo o trabalho, e a saída se perde.

`errors="replace"` em vez de `"strict"` porque um caractere que o terminal não
consegue desenhar nunca deve derrubar um relatório inteiro.
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
