#!/usr/bin/env python3
"""check_html_export.py - Auditoria estrutural dos HTMLs exportados.

Roda sobre output/html/*.html e caça defeitos reais, ignorando falsos
positivos de payloads base64 (fontes) e de JavaScript embutido (MathJax):

  1. Fenced div ':::' que sobrou como texto literal
  2. Bracketed span '[texto]{.classe}' não parseado pelo Pandoc
  3. <blockquote> residual (deveriam ter virado .quote/.pull-quote/.box/.card)
  4. Wikilink [[...]] visível no texto renderizado
  5. Pilha de <br> (>3) em prosa FORA de componentes de citação — quebra
     dura dentro de .quote/.pull-quote é intencional (verso/cena)
  6. Âncora do Sumário apontando para id inexistente

Uso: python check_html_export.py            (audita output/html inteiro)
"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(__file__).resolve().parent.parent / "output" / "html"


def strip_noise(h):
    """Remove data URIs (fontes base64), CSS e JS para análise do conteúdo."""
    h = re.sub(r'data:[\w/+.-]+;base64,[A-Za-z0-9+/=]+', '', h)
    h = re.sub(r'<style.*?</style>', '', h, flags=re.S)
    return h


def audit_file(html_path):
    raw = html_path.read_text(encoding="utf-8", errors="replace")
    # JS do MathJax embutido gera [[...]] falso positivo; remove blocos <script>.
    body = re.sub(r'<script.*?</script>', '', strip_noise(raw), flags=re.S)

    errs = []

    if re.search(r':::\s*\{', body):
        errs.append("fenced div literal no output (':::' virou texto)")

    spans = re.findall(r'\[[^\]\n]{1,40}\]\{\.[\w-]+\}', body)
    if spans:
        errs.append(f"bracketed span não parseado: {spans[:2]}")

    bq = body.count("<blockquote>")
    if bq:
        i = body.find("<blockquote>")
        ctx = re.sub(r"<[^>]+>", " ", body[i:i + 160])[:80].strip()
        errs.append(f"blockquote residual x{bq}: {ctx!r}")

    visible = re.sub(r"<[^>]+>", "", body)
    wl = re.findall(r"\[\[[^\]\n]{2,80}\]\]", visible)
    if wl:
        errs.append(f"wikilink visível: {wl[:3]}")

    for m in re.finditer(r"<p>(.*?)</p>", body, re.S):
        p = m.group(1)
        nbr = p.count("<br />") + p.count("<br>")
        plain = re.sub(r"<[^>]+>", "", p).strip()
        if len(plain) > 220 and nbr >= 3:
            antes = re.findall(
                r'<div class="([\w -]+)"', body[max(0, m.start() - 3000):m.start()])
            container = antes[-1] if antes else ""
            if not any(c in container for c in ("quote", "pull-quote", "box", "card")):
                errs.append(f"prosa com pilha de <br> x{nbr} fora de citação: {plain[:70]!r}")

    broken = [m.group(1) for m in re.finditer(r'<a href="#([^"]+)"', body)
              if f'id="{m.group(1)}"' not in body]
    if broken:
        errs.append(f"âncoras quebradas x{len(broken)}: {broken[:4]}")

    return errs


def main():
    files = sorted(OUT.glob("*.html"))
    problems = {}
    for f in files:
        errs = audit_file(f)
        if errs:
            problems[f.name] = errs

    if not files:
        print(f"Nenhum HTML em {OUT}")
        return 1

    if problems:
        print(f"{len(problems)}/{len(files)} arquivo(s) com problemas:\n")
        for name, errs in sorted(problems.items()):
            print(f"--- {name}")
            for e in errs:
                print(f"   * {e}")
        return 1
    print(f"TODOS OS {len(files)} HTMLS LIMPOS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
