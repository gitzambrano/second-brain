"""O digest do selo tem de ser o mesmo nas duas pontas.

O selo é gravado no Windows, pelo engine, e reconferido no runner Linux, pela
portaria do repositório `site/`. `sorted()` sobre `Path` não serve para isso:
`WindowsPath` compara case-folded e `PosixPath` compara byte a byte, então as
fontes web em CamelCase do artefato alimentavam o hash em ordens diferentes. O
deploy morria dizendo que o conteúdo mudou depois do selo, em toda publicação
legítima.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest
from conftest import ROOT, SCRIPTS

sys.path.insert(0, str(SCRIPTS))
import seal_publication  # noqa: E402

SITE_GATE = ROOT / "site/.github/scripts/check_artifact.py"

# Nomes reais do artefato: as fontes vêm do Google Fonts com hash em CamelCase,
# e são elas que separam as duas ordenações.
ARQUIVOS = {
    "index.html": b"<p>x</p>\r\n",
    "assets/fonts/fonts.css": b"@font-face{}\n",
    "assets/fonts/UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa1ZL7.woff2": b"\x00\x01binario",
    "assets/fonts/Zzz.woff2": b"\x00\x02binario",
    "essays/um-essay.html": b"<h1>t</h1>\r\n",
}


def _tree(tmp_path: Path) -> Path:
    root = tmp_path / "site"
    for rel, data in ARQUIVOS.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    return root


def _digest_em_ordem_posix(root: Path) -> str:
    """Referência independente: ordem pela string de caminho, como no runner."""
    h = hashlib.sha256()
    arquivos = sorted(
        (p for p in root.rglob("*") if p.is_file()),
        key=lambda p: p.relative_to(root).as_posix(),
    )
    for path in arquivos:
        dados = path.read_bytes()
        if path.suffix.lower() in seal_publication.TEXT_SUFFIXES:
            dados = dados.replace(b"\r\n", b"\n")
        h.update(path.relative_to(root).as_posix().encode("utf-8"))
        h.update(b"\0")
        h.update(hashlib.sha256(dados).digest())
    return h.hexdigest()


def test_digest_do_engine_usa_a_ordem_do_runner(tmp_path):
    root = _tree(tmp_path)
    assert seal_publication.artifact_digest(root) == _digest_em_ordem_posix(root)


def test_quebra_de_linha_nao_muda_o_digest(tmp_path):
    """CRLF no disco do autor, LF no checkout do runner: mesmo digest."""
    a = _tree(tmp_path / "crlf")
    b = tmp_path / "lf" / "site"
    for rel, data in ARQUIVOS.items():
        p = b / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data.replace(b"\r\n", b"\n"))
    assert seal_publication.artifact_digest(a) == seal_publication.artifact_digest(b)


@pytest.mark.skipif(not SITE_GATE.is_file(), reason="repositório site/ ausente")
def test_portaria_do_site_calcula_o_mesmo_digest(tmp_path):
    """As duas implementações são cópias e têm de continuar concordando."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("check_artifact", SITE_GATE)
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    root = _tree(tmp_path)
    assert gate.artifact_digest(root) == seal_publication.artifact_digest(root)
