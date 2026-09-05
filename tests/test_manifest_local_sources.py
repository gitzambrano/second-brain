from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

check_wiki = importlib.import_module("check_wiki")


def _manifest(filename: str = "original.pdf") -> str:
    return f"""# Manifesto de Sources

## [2026-09-05] {filename}
Tipo: Ensaio Completo Importado.
Tags: Engenharia
Pasta: wiki/sources/ensaio-importado/
Virou: [[essay-existente|Essay Existente]] (essay novo).
Verificação: referências bibliográficas confirmadas.
"""


def _prepare(monkeypatch, tmp_path):
    sources = tmp_path / "wiki" / "sources"
    (sources / "ensaio-importado").mkdir(parents=True)
    (sources / "manifest.md").write_text(_manifest(), encoding="utf-8")
    handouts = tmp_path / "wiki" / "handouts"
    handouts.mkdir(parents=True)
    monkeypatch.setattr(check_wiki, "SOURCES_DIR", sources)
    monkeypatch.setattr(check_wiki, "HANDOUTS_DIR", handouts)
    return sources


def test_manifest_entry_may_outlive_local_raw_source(monkeypatch, tmp_path):
    _prepare(monkeypatch, tmp_path)
    issues = check_wiki.check_sources_manifest({"essay-existente"})
    assert not [i for i in issues if i["code"] == "MANIFEST_ENTRY_NO_FILE"]
    assert not [i for i in issues if i["severity"] in {"ERROR", "CRITICAL"}]


def test_present_raw_source_still_requires_manifest_entry(monkeypatch, tmp_path):
    sources = _prepare(monkeypatch, tmp_path)
    (sources / "ensaio-importado" / "sem-manifesto.pdf").write_bytes(b"raw")
    issues = check_wiki.check_sources_manifest({"essay-existente"})
    assert any(i["code"] == "MANIFEST_MISSING_ENTRY" for i in issues)
