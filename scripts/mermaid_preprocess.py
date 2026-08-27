#!/usr/bin/env python3
"""
mermaid_preprocess.py - Converte blocos ```mermaid em imagens PNG antes do
Pandoc (HTML ou PDF). Sem este passo, o Pandoc emite o código Mermaid como
bloco de código literal; com ele, cada diagrama vira um ![fig](path.png).

Requer mmdc (Mermaid CLI):
    npm install -g @mermaid-js/mermaid-cli

Uso interno (chamado por export_essay_pdf.py e export_essay_html.py):
    from mermaid_preprocess import render_mermaid_blocks

    body, rendered = render_mermaid_blocks(body, output_dir, slug)
    # rendered: int — número de diagramas renderizados (0 = mmdc ausente/falhou)
"""

import re
import subprocess
import tempfile
from pathlib import Path


# ---------------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------------

import sys


def _find_mmdc() -> str | None:
    """Retorna o executável mmdc adequado para a plataforma, ou None.

    No Windows, instalações globais de npm ficam em %APPDATA%\\npm e o
    binário utilizável pelo subprocess é mmdc.cmd (não o .ps1 nem o sem
    extensão). No POSIX, 'mmdc' no PATH é suficiente.
    """
    candidates = ['mmdc']
    if sys.platform == 'win32':
        import os
        npm_dir = os.environ.get('APPDATA', '')
        if npm_dir:
            npm_dir = os.path.join(npm_dir, 'npm')
            candidates = [
                os.path.join(npm_dir, 'mmdc.cmd'),
                os.path.join(npm_dir, 'mmdc'),
                'mmdc.cmd',
                'mmdc',
            ]
        else:
            candidates = ['mmdc.cmd', 'mmdc']

    for cmd in candidates:
        try:
            result = subprocess.run(
                [cmd, '--version'],
                capture_output=True,
                timeout=15,
                shell=False,
            )
            if result.returncode == 0:
                return cmd
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            continue
    return None


_MMDC_CMD: str | None = None
_MMDC_CHECKED: bool = False


def _mmdc_available() -> bool:
    """Verifica (uma única vez) se mmdc está disponível."""
    global _MMDC_CMD, _MMDC_CHECKED
    if not _MMDC_CHECKED:
        _MMDC_CMD = _find_mmdc()
        _MMDC_CHECKED = True
    return _MMDC_CMD is not None


_MERMAID_RE = re.compile(r'```mermaid\s*\n(.*?)```', re.DOTALL)


def render_mermaid_blocks(body: str, output_dir: Path, slug: str) -> tuple[str, int]:
    """Substitui cada bloco ```mermaid pelo link ![diagrama](path.png).

    Parâmetros
    ----------
    body : str
        Corpo do markdown já pré-processado (sem frontmatter).
    output_dir : Path
        Pasta onde os PNGs ficam gravados (normalmente output/pdf/ ou output/html/).
    slug : str
        Identificador do essay, usado para nomear os arquivos de imagem.

    Retorna
    -------
    (body_modificado, n_renderizados)
        Se mmdc não estiver disponível ou falhar em todos, retorna (body original, 0).
    """
    if not _mmdc_available():
        return body, 0

    assets_dir = output_dir / "mermaid_assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    rendered = 0
    errors   = 0

    def _replace(m):
        nonlocal rendered, errors
        diagram_src = m.group(1)
        idx = rendered + errors
        png_path = assets_dir / f"{slug}_mermaid_{idx}.png"

        # mmdc lê de stdin com -i - ou de arquivo temporário
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.mmd', delete=False, encoding='utf-8'
        ) as tmp:
            tmp.write(diagram_src)
            tmp_path = Path(tmp.name)

        try:
            result = subprocess.run(
                [
                    _MMDC_CMD,
                    '-i', str(tmp_path),
                    '-o', str(png_path),
                    '--backgroundColor', 'white',
                    '--width', '1200',
                    '--scale', '2',
                ],
                capture_output=True,
                timeout=60
            )
            if result.returncode == 0 and png_path.exists():
                rendered += 1
                # Retorna link de imagem com legenda vazia (PDF usa alt como caption)
                return f'\n![Diagrama Mermaid {rendered}]({png_path})\n'
            else:
                errors += 1
                stderr = result.stderr.decode('utf-8', errors='replace') if result.stderr else ''
                print(f"  WARNING: mmdc falhou no diagrama {idx}: {stderr[:200]}")
                return m.group(0)  # mantém o bloco original
        except subprocess.TimeoutExpired:
            errors += 1
            print(f"  WARNING: mmdc timeout no diagrama {idx}")
            return m.group(0)
        finally:
            tmp_path.unlink(missing_ok=True)

    new_body = _MERMAID_RE.sub(_replace, body)
    return new_body, rendered


def has_mermaid(body: str) -> bool:
    """Heurística rápida: o corpo tem algum bloco ```mermaid?"""
    return bool(_MERMAID_RE.search(body))
