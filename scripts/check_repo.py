#!/usr/bin/env python3
"""Unified repository quality gate.

No-argument default is the most complete useful diagnosis (``full``). A fresh
skeleton clone is valid: corpus/export checks report SKIP when there is nothing
to inspect. The checker never creates or edits wiki content.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any

from repo_paths import CODE_ROOT, HTML_DIR, PDF_DIR, SCRIPTS_DIR, corpus_has_essays
from sanity_common import CheckResult


def run_command(name: str, cmd: list[str], result: CheckResult, parse_json_severity: bool = False) -> None:
    proc = subprocess.run(cmd, cwd=CODE_ROOT, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    output = (proc.stdout + "\n" + proc.stderr).strip()
    if proc.returncode:
        result.error("CHECK_FAILED", f"{name} exited {proc.returncode}: {output[:1000]}")
        return
    if parse_json_severity:
        try:
            payload = json.loads(proc.stdout)
        except json.JSONDecodeError:
            result.warning("JSON_UNPARSEABLE", f"{name} --json did not return pure JSON; exit code was 0")
            return
        severities: list[tuple[str, str]] = []

        def walk(obj: Any) -> None:
            if isinstance(obj, dict):
                sev = str(obj.get("severity", "")).upper()
                if sev in {"CRITICAL", "ERROR", "WARNING"}:
                    severities.append((sev, str(obj.get("code", obj.get("message", "issue")))))
                for v in obj.values():
                    walk(v)
            elif isinstance(obj, list):
                for v in obj:
                    walk(v)
        walk(payload)
        for sev, code in severities:
            if sev in {"CRITICAL", "ERROR"}:
                result.error("LEGACY_ISSUE", f"{name}: {code}")
            else:
                result.warning("LEGACY_WARNING", f"{name}: {code}")
    else:
        result.info("CHECK_OK", name)


def quick(result: CheckResult) -> None:
    run_command("compile scripts", [sys.executable, "-m", "compileall", "-q", "scripts"], result)
    run_command(
        "script no-arg contract",
        [sys.executable, str(SCRIPTS_DIR / "check_script_defaults.py"), "--json"],
        result,
        parse_json_severity=True,
    )
    run_command(
        "skill contracts",
        [sys.executable, str(SCRIPTS_DIR / "check_skills.py"), "--json"],
        result,
        parse_json_severity=True,
    )
    run_command(
        "core environment",
        [sys.executable, str(SCRIPTS_DIR / "check_env.py"), "--core", "--json"],
        result,
        parse_json_severity=True,
    )


def wiki(result: CheckResult) -> None:
    if not corpus_has_essays():
        result.skip("SKELETON_NO_ESSAYS", "no essays present; corpus validation skipped")
        return
    for script, extra, parse_json in (
        ("check_wiki.py", ["--json"], True),
        ("check_references.py", ["--json"], True),
        ("check_dedupe.py", ["--json"], True),
        ("check_gaps.py", ["--skip-tags"], False),
    ):
        path = SCRIPTS_DIR / script
        if path.exists():
            run_command(script, [sys.executable, str(path), *extra], result, parse_json_severity=parse_json)


def exports(result: CheckResult) -> None:
    if not any(HTML_DIR.glob("*.html")) if HTML_DIR.exists() else True:
        result.skip("NO_HTML_EXPORTS", "no HTML exports to validate")
    else:
        for script in ("check_html_export.py", "check_html_render.py"):
            path = SCRIPTS_DIR / script
            if path.exists():
                run_command(script, [sys.executable, str(path), "--json"], result, parse_json_severity=True)
    if not any(PDF_DIR.glob("*.pdf")) if PDF_DIR.exists() else True:
        result.skip("NO_PDF_EXPORTS", "no PDF exports to validate")
    else:
        for script in ("check_pdf_content.py", "check_pdf_layout.py"):
            path = SCRIPTS_DIR / script
            if path.exists():
                run_command(script, [sys.executable, str(path), "--json"], result, parse_json_severity=True)
        parity = SCRIPTS_DIR / "check_export_parity.py"
        if parity.exists():
            run_command(
                "check_export_parity.py",
                [sys.executable, str(parity), "--json"],
                result,
                parse_json_severity=True,
            )


def audit(mode: str) -> CheckResult:
    result = CheckResult("repository")
    if mode in {"quick", "full"}:
        quick(result)
    if mode in {"wiki", "full"}:
        wiki(result)
    if mode in {"exports", "full"}:
        exports(result)
    result.meta["mode"] = mode
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    group = ap.add_mutually_exclusive_group()
    group.add_argument("--quick", action="store_true", help="fast repository/skill/CLI checks")
    group.add_argument("--wiki", action="store_true", help="corpus checks only")
    group.add_argument("--exports", action="store_true", help="existing HTML/PDF checks only")
    group.add_argument("--full", action="store_true", help="all checks (also the no-argument default)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--fail-on-warning", action="store_true")
    args = ap.parse_args()
    mode = "quick" if args.quick else "wiki" if args.wiki else "exports" if args.exports else "full"
    result = audit(mode)
    result.print(args.json)
    return result.exit_code(args.fail_on_warning)


if __name__ == "__main__":
    raise SystemExit(main())
