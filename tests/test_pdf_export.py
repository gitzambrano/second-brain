import pymupdf as fitz
import pytest
from conftest import legacy_script_available, run_script

pytestmark=[pytest.mark.export,pytest.mark.pdf]
def test_pdf_fixture_export_content_and_layout(installed_mini_brain):
    if not legacy_script_available("export_essay_pdf.py"): pytest.skip("exporter absent")
    export=run_script("export_essay_pdf.py","kitchen-sink",timeout=600)
    assert export.returncode==0,export.stdout+export.stderr
    pp=installed_mini_brain/"output"/"pdf"/"kitchen-sink.pdf"
    assert pp.exists() and pp.stat().st_size>1000
    c=run_script("check_pdf_content.py","kitchen-sink","--json");assert c.returncode==0,c.stdout+c.stderr
    l=run_script("check_pdf_layout.py","kitchen-sink","--json");assert l.returncode==0,l.stdout+l.stderr


def test_pdf_keeps_chapter_with_one_following_line_after_display_math(installed_mini_brain):
    """A chapter that still fits with one body line must not be pushed early."""
    source = installed_mini_brain / "wiki" / "essays" / "page-break-boundary.md"
    spacer = "```{=latex}\n\\vspace*{387pt}\n```"
    source.write_text(
        """---
title: Limite de paginação
tags: [Tecnologia]
created: 2026-09-04
updated: 2026-09-04
summary: Documento sintético para verificar que um capítulo não salta cedo.
status: revisao
---

# Limite de paginação

> Estudo
> Gustavo Zambrano · Setembro de 2026

## Sumário

- [[#Primeiro capítulo]]
- [[#Capítulo que ainda cabe]]

---

## Primeiro capítulo

    Uma linha de abertura fixa a posição do capítulo seguinte.

    """ + spacer + """

$$
C_Y < 0.
$$

## Capítulo que ainda cabe

Uma linha de corpo deve permanecer na mesma página do título.

## Referências

[1] Fonte sintética.

## Conexões

""",
        encoding="utf-8",
    )
    export = run_script("export_essay_pdf.py", "page-break-boundary", timeout=600)
    assert export.returncode == 0, export.stdout + export.stderr
    pdf = installed_mini_brain / "output" / "pdf" / "page-break-boundary.pdf"
    with fitz.open(pdf) as document:
        pages_with_heading = []
        for index, page in enumerate(document):
            for block in page.get_text("dict")["blocks"]:
                if block.get("type") != 0:
                    continue
                for line in block["lines"]:
                    text = "".join(span["text"] for span in line["spans"])
                    size = max(span["size"] for span in line["spans"])
                    if text == "Capítulo que ainda cabe" and size > 17:
                        pages_with_heading.append(index)
    assert pages_with_heading == [2]
