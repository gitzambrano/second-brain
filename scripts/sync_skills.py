#!/usr/bin/env python3
"""
sync_skills.py - Espelha .agents/skills/ e .agents/agents/ para
.claude/skills/, .claude/agents/ e .codex/skills/. Fonte única é sempre
.agents/ - os espelhos são gerados, nunca editados à mão.

Lê:
    .agents/skills/**, .agents/agents/**

Gera:
    cópias idênticas nos destinos acima (remove espelho sem origem)

Uso:
    python scripts/sync_skills.py            # espelha e reporta o que mudou
    python scripts/sync_skills.py --check    # não escreve; exit 1 se houver drift
    python scripts/sync_skills.py --quiet    # reporta só se algo mudou (modo hook)

Flags:
    --check   apenas detecta drift, não escreve
    --quiet   silencia o relatório quando nada muda
"""

import argparse
import filecmp
import shutil
import sys
from pathlib import Path

import console_encoding  # noqa: F401  (UTF-8 no console; ver o módulo)

REPO_ROOT = Path(__file__).resolve().parent.parent

PAIRS = [
    (REPO_ROOT / ".agents" / "skills", REPO_ROOT / ".claude" / "skills"),
    (REPO_ROOT / ".agents" / "agents", REPO_ROOT / ".claude" / "agents"),
    (REPO_ROOT / ".agents" / "skills", REPO_ROOT / ".codex" / "skills"),
]


def relative_files(root: Path) -> set:
    """Todos os arquivos sob `root`, como caminhos relativos a ele."""
    if not root.is_dir():
        return set()
    return {p.relative_to(root) for p in root.rglob("*") if p.is_file()}


def sync_pair(source: Path, dest: Path, check_only: bool = False):
    """Retorna (copiados, removidos) como listas de caminhos relativos a `dest`."""
    if not source.is_dir():
        # Par opcional (ex: .agents/agents/ ainda não existe) — sem erro.
        return [], []

    src_files = relative_files(source)
    dest_files = relative_files(dest)

    to_copy = sorted(
        rel
        for rel in src_files
        if rel not in dest_files
        or not filecmp.cmp(source / rel, dest / rel, shallow=False)
    )
    to_remove = sorted(dest_files - src_files)

    if check_only:
        return to_copy, to_remove

    for rel in to_copy:
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / rel, target)

    for rel in to_remove:
        (dest / rel).unlink()

    if dest.is_dir():
        for path in sorted(dest.rglob("*"), key=lambda p: len(p.parts), reverse=True):
            if path.is_dir() and not any(path.iterdir()):
                path.rmdir()

    return to_copy, to_remove


def sync(check_only: bool = False):
    """Roda todos os pares fonte/espelho. Retorna lista de (source, dest, copiados, removidos)."""
    results = []
    for source, dest in PAIRS:
        copied, removed = sync_pair(source, dest, check_only=check_only)
        results.append((source, dest, copied, removed))
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="não escreve nada; sai com código 1 se houver dessincronia",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="silencia a saída quando já está sincronizado",
    )
    args = parser.parse_args()

    results = sync(check_only=args.check)
    any_drift = any(copied or removed for _, _, copied, removed in results)

    def label(source, dest):
        return f"{source.relative_to(REPO_ROOT)} -> {dest.relative_to(REPO_ROOT)}"

    if args.check:
        if any_drift:
            for source, dest, copied, removed in results:
                if not (copied or removed):
                    continue
                print(
                    f"DRIFT ({label(source, dest)}): {len(copied)} arquivo(s) "
                    f"desatualizado(s), {len(removed)} sobrando"
                )
                for rel in copied:
                    print(f"  desatualizado: {rel.as_posix()}")
                for rel in removed:
                    print(f"  sobrando:      {rel.as_posix()}")
            print("Rode: python scripts/sync_skills.py")
            sys.exit(1)
        if not args.quiet:
            print("skills e agents sincronizados")
        return

    if any_drift:
        for source, dest, copied, removed in results:
            if not (copied or removed):
                continue
            print(
                f"sincronizado ({label(source, dest)}): {len(copied)} copiado(s), "
                f"{len(removed)} removido(s)"
            )
            for rel in copied:
                print(f"  copiado:  {rel.as_posix()}")
            for rel in removed:
                print(f"  removido: {rel.as_posix()}")
    elif not args.quiet:
        print("skills e agents já sincronizados")


if __name__ == "__main__":
    main()
