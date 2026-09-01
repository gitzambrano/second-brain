#!/usr/bin/env python3
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
REPO = Path.cwd()

src_html = ROOT / "scripts" / "check_html_render.py"
dst_html = REPO / "scripts" / "check_html_render.py"
dst_pdf = REPO / "scripts" / "pdf_boxes.lua"

if not dst_html.exists() or not dst_pdf.exists():
    raise SystemExit("Execute este script na raiz do repo second-brain.")

shutil.copy2(src_html, dst_html)

text = dst_pdf.read_text(encoding="utf-8")
old = "local s = pandoc.utils.stringify(cell)"
new = "local s = pandoc.utils.stringify(cell.contents)"

if new in text:
    pass
elif old in text:
    dst_pdf.write_text(text.replace(old, new, 1), encoding="utf-8")
else:
    raise SystemExit(
        "Linha esperada não encontrada em scripts/pdf_boxes.lua; "
        "arquivo não foi alterado."
    )

print("patched: scripts/check_html_render.py")
print("patched: scripts/pdf_boxes.lua")
print()
print("Agora rode:")
print("  python scripts/check_repo.py --quick")
print("  python -m pytest -q")
