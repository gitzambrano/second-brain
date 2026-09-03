#!/usr/bin/env python3
"""Audit executable Python scripts for a useful no-argument default.

The repository contract is intentionally simple: an executable script must not
have a required positional CLI argument. A script may still accept optional
positionals (``nargs='?'``/``'*'``) and validate partial invocations itself.

No-argument default: audit every executable ``scripts/*.py`` file.
"""
from __future__ import annotations

import argparse
import ast
from pathlib import Path

from repo_paths import CODE_ROOT, SCRIPTS_DIR
from sanity_common import CheckResult

HELPER_MODULES: set[str] = set()


def is_executable_script(path: Path, tree: ast.AST) -> bool:
    if path.name in HELPER_MODULES:
        return False
    try:
        first = path.read_text(encoding="utf-8-sig").splitlines()[0]
    except (OSError, IndexError):
        first = ""
    if first.startswith("#!"):
        return True
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare) and isinstance(node.left, ast.Name) and node.left.id == "__name__":
            return True
    return False


def _literal(node: ast.AST | None):
    try:
        return ast.literal_eval(node) if node is not None else None
    except (ValueError, TypeError):
        return None


def audit_file(path: Path, result: CheckResult) -> None:
    try:
        source = path.read_text(encoding="utf-8-sig")
        tree = ast.parse(source, filename=str(path))
    except (OSError, SyntaxError) as exc:
        result.error("SCRIPT_PARSE_ERROR", str(exc), path.relative_to(CODE_ROOT))
        return
    if not is_executable_script(path, tree):
        return

    subparsers: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Call):
            continue
        func = node.value.func
        if isinstance(func, ast.Attribute) and func.attr == "add_parser":
            for target in node.targets:
                if isinstance(target, ast.Name):
                    subparsers.add(target.id)

    required: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if (
            not isinstance(node, ast.Call)
            or not isinstance(node.func, ast.Attribute)
            or node.func.attr != "add_argument"
        ):
            continue
        if not node.args:
            continue
        receiver = node.func.value
        if isinstance(receiver, ast.Name) and receiver.id in subparsers:
            continue
        name = _literal(node.args[0])
        if not isinstance(name, str) or name.startswith("-"):
            continue
        kwargs = {kw.arg: _literal(kw.value) for kw in node.keywords if kw.arg}
        if kwargs.get("nargs") in {"?", "*"} or "default" in kwargs:
            continue
        required.append((name, getattr(node, "lineno", 0)))
    for name, line in required:
        result.error(
            "CLI_REQUIRED_POSITIONAL",
            f"positional '{name}' is mandatory; no-argument execution must choose a useful global/default mode",
            path.relative_to(CODE_ROOT), line=line,
        )

    # Raw sys.argv indexing is not necessarily wrong, but it often bypasses the
    # no-argument contract. Report as warning for manual review.
    for node in ast.walk(tree):
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Attribute):
            if isinstance(node.value.value, ast.Name) and node.value.value.id == "sys" and node.value.attr == "argv":
                idx = _literal(node.slice)
                if isinstance(idx, int) and idx >= 1:
                    result.warning("CLI_RAW_ARGV", f"direct sys.argv[{idx}] access; confirm no-arg path is guarded",
                                   path.relative_to(CODE_ROOT), line=getattr(node, "lineno", None))
                    break


def audit(paths: list[Path] | None = None) -> CheckResult:
    result = CheckResult("script-defaults")
    targets = paths or sorted(SCRIPTS_DIR.glob("*.py"))
    for path in targets:
        audit_file(path, result)
    result.meta["scripts_scanned"] = len(targets)
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("path", nargs="?", help="optional single Python script; default audits scripts/*.py")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--fail-on-warning", action="store_true")
    args = ap.parse_args()
    paths = [Path(args.path).resolve()] if args.path else None
    result = audit(paths)
    result.print(args.json)
    return result.exit_code(args.fail_on_warning)


if __name__ == "__main__":
    raise SystemExit(main())
