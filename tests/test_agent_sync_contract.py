"""O contrato de arquitetura de agentes: `.agents/` é fonte, `.claude/` é saída.

`test_sync_skills.py` prova que `sync_skills.py` funciona num repositório
sintético. Este arquivo prova algo diferente e mais forte: que ESTE repositório
respeita o contrato agora — cada arquivo de `.agents/skills/` e `.agents/agents/`
tem espelho idêntico em `.claude/`, nenhum arquivo extra sobrou lá, e a
documentação não voltou a descrever a arquitetura antiga de plugin.

Os espelhos são gitignorados, então num clone novo eles não existem ainda: os
testes de paridade pulam nesse caso, e o teste de reprodutibilidade cobre o que
importa de qualquer jeito, gerando os espelhos num diretório temporário.
"""
from __future__ import annotations

import filecmp
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from conftest import ROOT

PAIRS = [
    (ROOT / ".agents" / "skills", ROOT / ".claude" / "skills"),
    (ROOT / ".agents" / "agents", ROOT / ".claude" / "agents"),
]


def _relative_files(root: Path) -> set[Path]:
    if not root.is_dir():
        return set()
    return {p.relative_to(root) for p in root.rglob("*") if p.is_file()}


def _mirrors_present() -> bool:
    return any(dest.is_dir() for _, dest in PAIRS)


@pytest.mark.parametrize("source,dest", PAIRS, ids=lambda p: p.name)
def test_every_source_file_has_a_mirror(source: Path, dest: Path):
    if not _mirrors_present():
        pytest.skip("mirrors not generated in this checkout")
    missing = sorted(_relative_files(source) - _relative_files(dest))
    assert not missing, (
        f"sem espelho em {dest.relative_to(ROOT)}: "
        + ", ".join(p.as_posix() for p in missing)
        + " — rode: python scripts/sync_skills.py"
    )


@pytest.mark.parametrize("source,dest", PAIRS, ids=lambda p: p.name)
def test_no_extra_file_survives_in_the_mirror(source: Path, dest: Path):
    if not _mirrors_present():
        pytest.skip("mirrors not generated in this checkout")
    extra = sorted(_relative_files(dest) - _relative_files(source))
    assert not extra, (
        f"sobrando em {dest.relative_to(ROOT)} (sem origem em .agents/): "
        + ", ".join(p.as_posix() for p in extra)
        + " — rode: python scripts/sync_skills.py"
    )


@pytest.mark.parametrize("source,dest", PAIRS, ids=lambda p: p.name)
def test_mirror_content_is_identical(source: Path, dest: Path):
    """Edição manual no espelho é drift silencioso: byte a byte ou nada."""
    if not _mirrors_present():
        pytest.skip("mirrors not generated in this checkout")
    shared = sorted(_relative_files(source) & _relative_files(dest))
    differing = [
        rel.as_posix()
        for rel in shared
        if not filecmp.cmp(source / rel, dest / rel, shallow=False)
    ]
    assert not differing, (
        f"conteúdo divergente em {dest.relative_to(ROOT)}: "
        + ", ".join(differing)
        + " — o espelho foi editado à mão; a fonte é .agents/"
    )


def test_check_flag_detects_drift(tmp_path: Path):
    """`--check` precisa reprovar um espelho adulterado, não só um ausente."""
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    shutil.copy2(ROOT / "scripts" / "sync_skills.py", repo / "scripts" / "sync_skills.py")
    (repo / "scripts" / "repo_paths.py").write_text(
        f"from pathlib import Path\nCODE_ROOT = Path(r'{repo}')\n", encoding="utf-8"
    )
    skill = repo / ".agents" / "skills" / "demo" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("---\nname: demo\n---\n# Demo\n", encoding="utf-8")

    cmd = [sys.executable, str(repo / "scripts" / "sync_skills.py")]
    assert subprocess.run(cmd, cwd=repo, capture_output=True, text=True).returncode == 0
    assert subprocess.run([*cmd, "--check"], cwd=repo, capture_output=True).returncode == 0

    mirror = repo / ".claude" / "skills" / "demo" / "SKILL.md"
    mirror.write_text("---\nname: demo\n---\n# Editado à mão\n", encoding="utf-8")
    drift = subprocess.run([*cmd, "--check"], cwd=repo, capture_output=True, text=True)
    assert drift.returncode == 1, drift.stdout + drift.stderr
    assert "DRIFT" in drift.stdout

    intruder = repo / ".claude" / "skills" / "intruso.md"
    intruder.write_text("nasceu no espelho\n", encoding="utf-8")
    assert subprocess.run([*cmd, "--check"], cwd=repo, capture_output=True).returncode == 1


def test_mirrors_are_reproducible_from_the_source(tmp_path: Path):
    """O espelho é derivado: `.agents/` sozinho tem que reconstruí-lo inteiro."""
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    shutil.copy2(ROOT / "scripts" / "sync_skills.py", repo / "scripts" / "sync_skills.py")
    (repo / "scripts" / "repo_paths.py").write_text(
        f"from pathlib import Path\nCODE_ROOT = Path(r'{repo}')\n", encoding="utf-8"
    )
    shutil.copytree(ROOT / ".agents", repo / ".agents")

    run = subprocess.run(
        [sys.executable, str(repo / "scripts" / "sync_skills.py")],
        cwd=repo, capture_output=True, text=True,
    )
    assert run.returncode == 0, run.stdout + run.stderr

    for source, dest in PAIRS:
        rebuilt = repo / dest.relative_to(ROOT)
        assert _relative_files(rebuilt) == _relative_files(repo / source.relative_to(ROOT))
        if dest.is_dir():
            assert _relative_files(rebuilt) == _relative_files(dest)


def test_the_legacy_plugin_registration_is_gone():
    """A descoberta por plugin local foi abandonada; o diretório não volta."""
    assert not (ROOT / ".claude-plugin").exists(), (
        ".claude-plugin/ é código morto desde a migração para sync_skills.py"
    )


OBSOLETE = [
    "claude-plugin",
    "extraKnownMarketplaces",
    "enabledPlugins",
    "não existem mirrors",
    "não há passo de sincronização",
]


def test_docs_do_not_describe_the_abandoned_architecture():
    """Vocabulário da arquitetura antiga não pode reaparecer na documentação."""
    docs = sorted(list(ROOT.glob("*.md")) + list(ROOT.glob(".agents/**/*.md")))
    offenders = []
    for doc in docs:
        text = doc.read_text(encoding="utf-8")
        for term in OBSOLETE:
            if re.search(re.escape(term), text, re.IGNORECASE):
                offenders.append(f"{doc.relative_to(ROOT)}: {term!r}")
    assert not offenders, "termos da arquitetura abandonada:\n" + "\n".join(offenders)


def test_settings_json_only_bootstraps_the_sync():
    """`.claude/settings.json` é o único arquivo versionado de `.claude/`."""
    settings = (ROOT / ".claude" / "settings.json").read_text(encoding="utf-8")
    assert "sync_skills.py" in settings
    assert "SessionStart" in settings
    for term in ("plugin", "marketplace"):
        assert term not in settings.lower(), f"settings.json ainda cita {term}"
