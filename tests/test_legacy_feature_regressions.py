from __future__ import annotations

import os
import subprocess
import sys

from conftest import ROOT, SCRIPTS, run_script


def test_find_text_keeps_separate_context_blocks():
    sys.path.insert(0, str(SCRIPTS))
    import find_text
    assert find_text.merge_ranges([(1, 2), (8, 9), (15, 16)]) == [(1, 2), (8, 9), (15, 16)]
    assert find_text.merge_ranges([(1, 3), (3, 5), (10, 11)]) == [(1, 5), (10, 11)]


def test_retag_explicit_mode_still_changes_page_and_manifest(mini_brain):
    env = os.environ.copy(); env["SECOND_BRAIN_DATA_ROOT"] = str(mini_brain)
    essay = mini_brain / "wiki/essays/kitchen-sink.md"
    manifest = mini_brain / "wiki/sources/manifest.md"
    before = essay.read_text(encoding="utf-8")
    assert "Teste" in before
    proc = subprocess.run([sys.executable, str(SCRIPTS/"retag.py"), "Teste", "Qualidade"], cwd=ROOT, env=env,
                          capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    after = essay.read_text(encoding="utf-8")
    assert "Qualidade" in after and "Teste" not in after.split("---", 2)[1]
    assert "Qualidade" in manifest.read_text(encoding="utf-8")


def test_retag_dry_run_preserves_files(mini_brain):
    env = os.environ.copy(); env["SECOND_BRAIN_DATA_ROOT"] = str(mini_brain)
    essay = mini_brain / "wiki/essays/kitchen-sink.md"
    manifest = mini_brain / "wiki/sources/manifest.md"
    before = (essay.read_bytes(), manifest.read_bytes())
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "retag.py"), "Teste", "Qualidade", "--dry-run"],
        cwd=ROOT,
        env=env,
                          capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert proc.returncode == 0
    assert before == (essay.read_bytes(), manifest.read_bytes())


def test_find_text_query_mode_still_finds_multiple_occurrences(mini_brain):
    proc = run_script("find_text.py", "teste", "--ignore-case", data_root=mini_brain)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "ocorrência" in proc.stdout and "kitchen-sink.md" in proc.stdout


def test_check_title_explicit_modes_are_preserved(mini_brain):
    exact = run_script("check_title.py", "Qualification Essay", "--force-scan", data_root=mini_brain)
    assert exact.returncode == 1 and "MATCH EXATO" in exact.stdout
    free = run_script("check_title.py", "Título Completamente Novo", "--force-scan", data_root=mini_brain)
    assert free.returncode == 0 and "livre" in free.stdout


def test_mermaid_explicit_mode_preserves_output_semantics(tmp_path, mini_brain):
    fakebin = tmp_path / "bin"; fakebin.mkdir()
    if os.name == "nt":
        mmdc = fakebin / "mmdc.cmd"
        mmdc.write_text(
            "@echo off\n"
            "if \"%~1\"==\"--version\" (echo 1.0 & exit /b 0)\n"
            ":loop\n"
            "if \"%~1\"==\"\" goto done\n"
            "if not \"%~1\"==\"-o\" goto next\n"
            "set \"out=%~2\"\n"
            "shift\n"
            ":next\n"
            "shift\n"
            "goto loop\n"
            ":done\n"
            "> \"%out%\" <nul set /p \"=PNG\"\n"
            "exit /b 0\n",
            encoding="utf-8",
        )
    else:
        mmdc = fakebin / "mmdc"
        mmdc.write_text(
            "#!/bin/sh\n"
            "if [ \"$1\" = \"--version\" ]; then echo 1.0; exit 0; fi\n"
            "out=\"\"; while [ $# -gt 0 ]; do "
            "if [ \"$1\" = \"-o\" ]; then shift; out=\"$1\"; fi; shift; done\n"
            "printf PNG > \"$out\"\n",
            encoding="utf-8",
        )
    mmdc.chmod(0o755)
    src = tmp_path / "diagram.mmd"; src.write_text("graph TD; A-->B", encoding="utf-8")
    dst = tmp_path / "diagram.png"
    env = os.environ.copy()
    env["PATH"] = str(fakebin) + os.pathsep + env.get("PATH", "")
    env["APPDATA"] = str(tmp_path / "empty-appdata")
    env["SECOND_BRAIN_DATA_ROOT"] = str(mini_brain)
    proc = subprocess.run([sys.executable, str(SCRIPTS/"mermaid_to_png.py"), str(src), str(dst)], cwd=ROOT, env=env,
                          capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert dst.read_bytes() == b"PNG"


def test_find_text_explicit_query_keeps_empty_corpus_error(tmp_path):
    data = tmp_path / "empty"; (data / "wiki/essays").mkdir(parents=True)
    proc = run_script("find_text.py", "anything", data_root=data)
    assert proc.returncode == 1
    assert "Nenhum arquivo encontrado" in proc.stdout


def test_html_br_stack_inside_quote_is_not_regression(tmp_path):
    sys.path.insert(0, str(SCRIPTS))
    import check_html_structure as check_html_export
    html = tmp_path / "quote.html"
    long = "linha de citação " * 30
    html.write_text(
        f'<!DOCTYPE html><html><body><div class="wikiquote quote">'
        f"<p>{long}<br><br><br></p></div></body></html>",
        encoding="utf-8",
    )
    codes = [i["code"] for i in check_html_export.audit_file(html)]
    assert "PROSE_BR_STACK" not in codes
