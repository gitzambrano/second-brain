#!/usr/bin/env python3
"""Espelha .agents/skills/ para .claude/skills/.

A wiki mantém as skills em dois lugares porque cada agente procura num lugar
diferente: Claude Code lê `.claude/skills/`, os demais agentes leem
`.agents/skills/`. A fonte única é `.agents/skills/` — `.claude/skills/` é
artefato gerado, nunca editado à mão.

O mesmo vale para a documentação de topo, mas ali não é preciso script:
`CLAUDE.md` contém apenas `@AGENTS.md`, e o import é resolvido pelo Claude Code.

Uso:
    python scripts/sync_skills.py            # espelha e reporta o que mudou
    python scripts/sync_skills.py --check    # não escreve nada; sai 1 se houver drift
    python scripts/sync_skills.py --quiet    # só reporta se algo mudou (modo hook)
"""

import argparse
import filecmp
import shutil
import sys
from pathlib import Path

import console_encoding  # noqa: F401  (UTF-8 no console; ver o módulo)

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE = REPO_ROOT / ".agents" / "skills"
DEST = REPO_ROOT / ".claude" / "skills"


def relative_files(root: Path) -> set:
    """Todos os arquivos sob `root`, como caminhos relativos a ele."""
    if not root.is_dir():
        return set()
    return {p.relative_to(root) for p in root.rglob("*") if p.is_file()}


def sync(check_only: bool = False):
    """Retorna (copiados, removidos) como listas de caminhos relativos."""
    if not SOURCE.is_dir():
        print(f"ERRO: fonte não encontrada: {SOURCE}", file=sys.stderr)
        sys.exit(2)

    src_files = relative_files(SOURCE)
    dest_files = relative_files(DEST)

    to_copy = sorted(
        rel
        for rel in src_files
        if rel not in dest_files
        or not filecmp.cmp(SOURCE / rel, DEST / rel, shallow=False)
    )
    to_remove = sorted(dest_files - src_files)

    if check_only:
        return to_copy, to_remove

    for rel in to_copy:
        target = DEST / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SOURCE / rel, target)

    for rel in to_remove:
        (DEST / rel).unlink()

    # Diretórios que ficaram vazios depois da remoção.
    if DEST.is_dir():
        for path in sorted(DEST.rglob("*"), key=lambda p: len(p.parts), reverse=True):
            if path.is_dir() and not any(path.iterdir()):
                path.rmdir()

    return to_copy, to_remove


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

    copied, removed = sync(check_only=args.check)

    if args.check:
        if copied or removed:
            print(
                f"DRIFT: {len(copied)} arquivo(s) desatualizado(s), "
                f"{len(removed)} sobrando em .claude/skills/"
            )
            for rel in copied:
                print(f"  desatualizado: {rel.as_posix()}")
            for rel in removed:
                print(f"  sobrando:      {rel.as_posix()}")
            print("Rode: python scripts/sync_skills.py")
            sys.exit(1)
        if not args.quiet:
            print("skills sincronizadas (.agents/skills -> .claude/skills)")
        return

    if copied or removed:
        print(
            f"skills sincronizadas: {len(copied)} copiada(s), "
            f"{len(removed)} removida(s) (.agents/skills -> .claude/skills)"
        )
        for rel in copied:
            print(f"  copiada:  {rel.as_posix()}")
        for rel in removed:
            print(f"  removida: {rel.as_posix()}")
    elif not args.quiet:
        print("skills já sincronizadas (.agents/skills -> .claude/skills)")


if __name__ == "__main__":
    main()
