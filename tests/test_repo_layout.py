import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
def test_default_data_and_site_are_nested():
    env=os.environ.copy();env.pop("SECOND_BRAIN_DATA_ROOT",None);env.pop("SECOND_BRAIN_SITE_ROOT",None)
    p=subprocess.run([sys.executable,str(ROOT/"scripts/repo_paths.py")],cwd=ROOT,env=env,capture_output=True,text=True)
    assert p.returncode==0
    assert f"DATA_ROOT={ROOT/'data'}" in p.stdout
    assert f"SITE_ROOT={ROOT/'site'}" in p.stdout


# A raiz do engine é allowlist, não denylist: `_count.py`, `_out.txt`, `_p3.txt`,
# `_pytest.txt` e `_pytest2.txt` chegaram a `main` como resíduo de diagnóstico, e
# `_pytest2.txt` ainda vazava um caminho `C:\Users\...` da máquina do autor num
# repositório público. Uma regra em `.gitignore` protege só o prefixo `_`; este
# teste fecha o resto da porta.
ROOT_ALLOWLIST = {
    ".gitignore",
    "AGENTS.md",
    "CLAUDE.md",
    "README.md",
    "SCRIPTS.md",
    "TESTING.md",
    "pyproject.toml",
    "requirements-ci.txt",
}


def test_no_unexpected_tracked_files_at_root():
    """Reprova rascunho de diagnóstico COMMITADO na raiz do engine.

    Olha `git ls-files`, não o diretório de trabalho: o Usuário gera rascunho
    local o tempo todo e um teste sobre o working tree ficaria vermelho por
    ruído, treinando todo mundo a ignorá-lo. O defeito real é o arquivo que
    entra no índice — foi assim que caminho de máquina local acabou publicado.
    """
    try:
        p = subprocess.run(
            ["git", "ls-files", "-z", "--", ":(top)*"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
    except (OSError, FileNotFoundError):
        pytest.skip("git indisponível no PATH")
    if p.returncode != 0:
        pytest.skip("não é um repositório Git")

    # Profundidade 1: só o que está na raiz, sem varrer scripts/, tests/ etc.
    root_files = {entry for entry in p.stdout.split("\0") if entry and "/" not in entry}
    unexpected = sorted(root_files - ROOT_ALLOWLIST)
    assert not unexpected, (
        "Arquivo versionado inesperado na raiz do engine: "
        + ", ".join(unexpected)
        + ".\nSe for rascunho ou saída de diagnóstico, rode `git rm --cached <arquivo>` e apague-o.\n"
        + "Se for parte legítima do framework, acrescente o nome a ROOT_ALLOWLIST em "
        + "tests/test_repo_layout.py, no mesmo commit que o introduz."
    )
