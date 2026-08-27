#!/usr/bin/env python3
"""
mermaid_to_png.py — Converte um arquivo .mmd (diagrama Mermaid) em PNG.

Requer mmdc (Mermaid CLI):
    npm install -g @mermaid-js/mermaid-cli

Uso:
    python scripts/mermaid_to_png.py <arquivo.mmd> [saída.png]
    python scripts/mermaid_to_png.py <arquivo.mmd> --assets  # salva em wiki/assets/

Exemplos:
    python scripts/mermaid_to_png.py diagrama.mmd
    python scripts/mermaid_to_png.py diagrama.mmd wiki/assets/meu-diagrama.png
    python scripts/mermaid_to_png.py diagrama.mmd --assets

Sem argumento de saída: salva como <arquivo>.png no mesmo diretório.
Com --assets: salva em wiki/assets/<arquivo>.png.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT_DIR / "wiki" / "assets"


def find_mmdc() -> str | None:
    """Localiza o executável mmdc adequado para a plataforma."""
    if sys.platform == "win32":
        npm_dir = os.environ.get("APPDATA", "")
        candidates = (
            [
                os.path.join(npm_dir, "npm", "mmdc.cmd"),
                os.path.join(npm_dir, "npm", "mmdc"),
                "mmdc.cmd",
                "mmdc",
            ]
            if npm_dir
            else ["mmdc.cmd", "mmdc"]
        )
    else:
        candidates = ["mmdc"]

    for cmd in candidates:
        try:
            r = subprocess.run([cmd, "--version"], capture_output=True, timeout=10)
            if r.returncode == 0:
                return cmd
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            continue
    return None


def convert(src: Path, dst: Path, width: int = 1400, scale: int = 2, bg: str = "white") -> bool:
    """Converte src (.mmd) em dst (.png). Retorna True se OK."""
    cmd = find_mmdc()
    if not cmd:
        print("ERRO: mmdc não encontrado.")
        print("Instale com: npm install -g @mermaid-js/mermaid-cli")
        return False

    dst.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [cmd, "-i", str(src), "-o", str(dst),
         "--backgroundColor", bg, "--width", str(width), "--scale", str(scale)],
        capture_output=True,
        timeout=120,
    )
    if result.returncode == 0 and dst.exists():
        size_kb = dst.stat().st_size // 1024
        print(f"OK: {dst} ({size_kb} KB)")
        return True

    stderr = (result.stderr or b"").decode("utf-8", errors="replace")
    print(f"ERRO: mmdc falhou.\n{stderr[:400]}")
    return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Converte arquivo .mmd (Mermaid) em PNG via mmdc."
    )
    parser.add_argument("src", help="Arquivo .mmd de entrada")
    parser.add_argument("dst", nargs="?", help="Arquivo .png de saída (opcional)")
    parser.add_argument(
        "--assets", action="store_true",
        help="Salva em wiki/assets/<nome>.png"
    )
    parser.add_argument("--width", type=int, default=1400, help="Largura em px (default: 1400)")
    parser.add_argument("--scale", type=int, default=2, help="Fator de escala (default: 2)")
    parser.add_argument("--bg", default="white", help="Cor de fundo (default: white)")
    args = parser.parse_args()

    src = Path(args.src)
    if not src.exists():
        print(f"ERRO: arquivo não encontrado: {src}")
        return 1

    if args.dst:
        dst = Path(args.dst)
    elif args.assets:
        dst = ASSETS_DIR / src.with_suffix(".png").name
    else:
        dst = src.with_suffix(".png")

    ok = convert(src, dst, width=args.width, scale=args.scale, bg=args.bg)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
