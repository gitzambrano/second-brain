from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
FIXTURE = ROOT / "tests" / "fixtures" / "mini-brain"
PAGE_DIRS = [ROOT / "wiki" / x for x in ("essays", "concepts", "entities", "insights")]
OUTPUT_DIRS = [ROOT / "output" / x for x in ("html", "pdf", "handouts")]


def run_script(name: str, *args: str, data_root: Path | None = None, timeout: int = 120):
    env = os.environ.copy()
    if data_root is not None:
        env["SECOND_BRAIN_DATA_ROOT"] = str(data_root)
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *args], cwd=ROOT, env=env,
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout,
    )


def recursive_severities(obj):
    out = []
    if isinstance(obj, dict):
        sev = str(obj.get("severity", "")).upper()
        if sev:
            out.append((sev, obj.get("code")))
        for value in obj.values():
            out.extend(recursive_severities(value))
    elif isinstance(obj, list):
        for value in obj:
            out.extend(recursive_severities(value))
    return out


@pytest.fixture
def mini_brain(tmp_path: Path) -> Path:
    target = tmp_path / "mini-brain"
    shutil.copytree(FIXTURE, target)
    for sub in ("html", "pdf", "handouts", "stats", "graph"):
        (target / "output" / sub).mkdir(parents=True, exist_ok=True)
    return target


def _non_skeleton_files():
    found = []
    for d in PAGE_DIRS:
        if d.exists():
            found.extend(p for p in d.glob("*.md") if p.name != ".gitkeep")
    for d in OUTPUT_DIRS:
        if d.exists():
            found.extend(p for p in d.iterdir() if p.name != ".gitkeep")
    return found


@pytest.fixture
def installed_mini_brain():
    existing = _non_skeleton_files()
    if existing:
        pytest.skip("checkout contains real corpus/output; integration fixture refuses to touch it")
    copied: list[Path] = []
    for src_root_name in ("wiki", "plan"):
        src_root = FIXTURE / src_root_name
        for src in src_root.rglob("*"):
            if not src.is_file():
                continue
            rel = src.relative_to(FIXTURE)
            dst = ROOT / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            copied.append(dst)
    try:
        yield ROOT
    finally:
        for path in sorted(copied, key=lambda p: len(p.parts), reverse=True):
            try:
                path.unlink()
            except FileNotFoundError:
                pass
        for d in OUTPUT_DIRS:
            if d.exists():
                for p in sorted(d.rglob("*"), key=lambda item: len(item.parts), reverse=True):
                    if p.name == ".gitkeep":
                        continue
                    if p.is_file() or p.is_symlink():
                        p.unlink()
                    elif p.is_dir() and not any(p.iterdir()):
                        p.rmdir()
        # remove generated corpus artifacts that integration commands may create
        for p in (ROOT / "wiki" / "index.md", ROOT / "wiki" / "index.json",
                  ROOT / "wiki" / "references.md", ROOT / "wiki" / "references.json"):
            if p.exists():
                p.unlink()


def legacy_script_available(name: str, min_bytes: int = 500) -> bool:
    path = SCRIPTS / name
    return path.exists() and path.stat().st_size >= min_bytes
