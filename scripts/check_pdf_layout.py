#!/usr/bin/env python3
"""
check_pdf_layout.py - Audita a paginacao dos PDFs em output/pdf/.

Acha os dois defeitos que so aparecem depois de diagramado, e que nenhum lint
de markdown pega:

  VAZA_MARGEM    - linha de texto que passa da margem direita (ou da esquerda).
                   E o defeito que uma revisao por amostra nunca pega.
  TITULO_ORFAO   - a pagina termina num titulo (kicker de capitulo, `##`, `###`
                   ou `####`) sem nenhuma linha de corpo abaixo dele.
  PAGINA_VAZADA  - sobra mais que o limite de espaco no pe da pagina sem que
                   ela seja a ultima do documento nem termine numa figura.

Le:
    output/pdf/*.pdf (ou um slug via argumento)

Uso:
    python scripts/check_pdf_layout.py
    python scripts/check_pdf_layout.py <slug>
    python scripts/check_pdf_layout.py --json
"""

import sys
import json
import argparse
from pathlib import Path

import fitz

import console_encoding  # noqa: F401  (UTF-8 no console; ver o modulo)

ROOT_DIR = Path(__file__).resolve().parent.parent
PDF_DIR = ROOT_DIR / "output" / "pdf"

# Margens do documento (geometry em export_essay_pdf.py), em pontos.
TOP_MM, BOTTOM_MM = 17.0, 19.0
LEFT_MM, RIGHT_MM = 19.0, 19.0
MM = 72.0 / 25.4

# Folga antes de acusar vazamento: pontuacao pendurada e o proprio filete das
# caixas encostam na margem por desenho.
FOLGA_MARGEM_PT = 3.0

# Corpo do texto tem 12pt; titulos sao maiores. O kicker de capitulo e um
# filete mais um rotulo em versalete pequeno.
CORPO_MAX = 13.0

# Quanto de rodape em branco ja conta como pagina desperdicada.
VAZIO_LIMITE_PT = 170.0

# Corpo do titulo de capitulo (`\subsection`, 18pt). Serve para achar onde o
# Sumario acaba: o capitulo 1 sempre abre em pagina propria.
TITULO_CAPITULO_PT = (17.0, 19.5)

# A partir de que altura uma figura conta como "grande" — grande o bastante
# para nao caber no rodape da pagina anterior por conta propria.
FIGURA_GRANDE_PT = 200.0


def linhas_da_pagina(page):
    """[(y_baixo, tamanho_max_da_fonte, texto)] das linhas com texto real."""
    out = []
    d = page.get_text("dict")
    for bloco in d["blocks"]:
        if bloco.get("type") != 0:
            continue
        for linha in bloco["lines"]:
            txt = "".join(s["text"] for s in linha["spans"]).strip()
            if not txt:
                continue
            tam = max(s["size"] for s in linha["spans"])
            out.append((linha["bbox"][3], tam, txt))
    return sorted(out, key=lambda r: r[0])


def caixas_de_texto(page):
    """[(bbox, texto)] de cada linha, para medir vazamento lateral."""
    out = []
    for bloco in page.get_text("dict")["blocks"]:
        if bloco.get("type") != 0:
            continue
        for linha in bloco["lines"]:
            txt = "".join(s["text"] for s in linha["spans"]).strip()
            if txt:
                out.append((linha["bbox"], txt))
    return out


def desenhos_da_pagina(page):
    """y_baixo do desenho mais baixo (figura, filete, moldura de caixa)."""
    fundo = 0.0
    for d in page.get_drawings():
        fundo = max(fundo, d["rect"].y1)
    for img in page.get_image_info():
        fundo = max(fundo, img["bbox"][3])
    return fundo


def primeira_pagina_de_corpo(doc):
    """Indice (1-based) da pagina em que o capitulo 1 abre.

    Capa e Sumario terminam cedo por desenho, e o Sumario de um essay longo
    passa de uma pagina. Contar as duas primeiras como fixas dava falso
    positivo. O marco confiavel e o primeiro titulo de capitulo: o
    `\newpage` de `insert_page_break_after_sumario` garante que ele abre uma
    pagina nova.
    """
    for i, page in enumerate(doc):
        for _, tam, _ in linhas_da_pagina(page):
            if TITULO_CAPITULO_PT[0] <= tam <= TITULO_CAPITULO_PT[1]:
                return i + 1
    return 3


def figura_grande_no_topo(page):
    """A pagina abre com uma figura ou caixa alta demais para caber antes?"""
    alvo = None
    for img in page.get_image_info():
        alt = img["bbox"][3] - img["bbox"][1]
        if alt > FIGURA_GRANDE_PT:
            alvo = min(alvo, img["bbox"][1]) if alvo else img["bbox"][1]
    for d in page.get_drawings():
        alt = d["rect"].y1 - d["rect"].y0
        if alt > FIGURA_GRANDE_PT:
            alvo = min(alvo, d["rect"].y0) if alvo else d["rect"].y0
    return alvo is not None and alvo < 200.0


def auditar(pdf_path):
    doc = fitz.open(pdf_path)
    achados = []
    inicio = primeira_pagina_de_corpo(doc)
    for i, page in enumerate(doc):
        n = i + 1
        if n < inicio:
            continue
        altura = page.rect.height
        fim_mancha = altura - BOTTOM_MM * MM
        linhas = linhas_da_pagina(page)
        # O numero de pagina fica no rodape, fora da mancha: nao conta.
        linhas = [l for l in linhas if l[0] < fim_mancha + 2]
        if not linhas:
            continue

        # 0) Texto fora da mancha. Vale para toda linha da pagina, nao so a
        #    ultima, entao e checado antes e nao entra no elif dos demais.
        dir_ = page.rect.width - RIGHT_MM * MM
        for bbox, txt in caixas_de_texto(page):
            if bbox[2] > dir_ + FOLGA_MARGEM_PT:
                achados.append({
                    "pagina": n, "tipo": "VAZA_MARGEM",
                    "detalhe": "+%.0fpt: %s" % (bbox[2] - dir_, txt[:60]),
                })
            elif bbox[0] < LEFT_MM * MM - FOLGA_MARGEM_PT:
                achados.append({
                    "pagina": n, "tipo": "VAZA_MARGEM",
                    "detalhe": "-%.0fpt: %s" % (LEFT_MM * MM - bbox[0], txt[:60]),
                })

        ultima_y, ultimo_tam, ultimo_txt = linhas[-1]
        fundo = max(ultima_y, desenhos_da_pagina(page))
        sobra = fim_mancha - fundo

        ultima_pagina = (n == doc.page_count)

        # 1) Titulo orfao: a ultima linha da pagina esta em corpo de titulo.
        if not ultima_pagina and ultimo_tam > CORPO_MAX:
            achados.append({
                "pagina": n, "tipo": "TITULO_ORFAO",
                "detalhe": "%.1fpt: %s" % (ultimo_tam, ultimo_txt[:70]),
            })
        # 2) Pagina com rodape vazio grande. Se a pagina seguinte abre com
        #    figura alta, o vazio e consequencia da colocacao `[H]` (a figura
        #    nao caberia no rodape de jeito nenhum), nao defeito de paginacao.
        elif not ultima_pagina and sobra > VAZIO_LIMITE_PT:
            proxima = doc[i + 1]
            tipo = ("FIGURA_EMPURRADA" if figura_grande_no_topo(proxima)
                    else "PAGINA_VAZADA")
            achados.append({
                "pagina": n, "tipo": tipo,
                "detalhe": "%.0fpt vazios apos: %s" % (sobra, ultimo_txt[:60]),
            })
    doc.close()
    return achados


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug", nargs="?")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    alvos = sorted(PDF_DIR.glob("%s.pdf" % (args.slug or "*")))
    if not alvos:
        print("Nenhum PDF encontrado em %s" % PDF_DIR)
        return 1

    total = 0
    relatorio = {}
    for p in alvos:
        achados = auditar(p)
        if achados:
            relatorio[p.stem] = achados
            total += len(achados)

    if args.json:
        print(json.dumps(relatorio, ensure_ascii=False, indent=2))
        return 0

    graves = sum(1 for a in sum(relatorio.values(), [])
                 if a["tipo"] != "FIGURA_EMPURRADA")
    for slug, achados in sorted(relatorio.items(),
                                key=lambda kv: -len(kv[1])):
        print("\n%s  (%d)" % (slug, len(achados)))
        for a in achados:
            print("   p.%-4d %-14s %s" % (a["pagina"], a["tipo"], a["detalhe"]))

    print("\n%d PDF(s) auditado(s), %d achado(s) em %d arquivo(s) "
          "(%d de paginacao, %d de figura)"
          % (len(alvos), total, len(relatorio), graves, total - graves))
    return 0


if __name__ == "__main__":
    sys.exit(main())
