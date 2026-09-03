#!/usr/bin/env python3
"""Unified repository quality gate.

No-argument default is the most complete useful diagnosis (``full``). A fresh
skeleton clone is valid: corpus/export checks report SKIP when there is nothing
to inspect. The checker never creates or edits wiki content.
"""
from __future__ import annotations

import console_encoding  # noqa: F401 — força UTF-8 em stdout/stderr no Windows
import argparse
import json
import subprocess
import sys
from typing import Any

from repo_paths import CODE_ROOT, HTML_DIR, PDF_DIR, SCRIPTS_DIR, SITE_ROOT, corpus_has_essays
from sanity_common import CheckResult


def run_status_command(name: str, cmd: list[str], result: CheckResult) -> None:
    """Run a checker emitting {"status", "errors", "warnings"} and fold it in.

    These checkers already exit non-zero on a blocking problem; this only makes
    their individual messages visible in the unified report.
    """
    proc = subprocess.run(cmd, cwd=CODE_ROOT, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        if proc.returncode:
            result.error("CHECK_FAILED", f"{name} exited {proc.returncode}: "
                                         f"{(proc.stdout + proc.stderr).strip()[:1000]}")
        else:
            result.warning("JSON_UNPARSEABLE", f"{name} --json did not return pure JSON")
        return
    errors = payload.get("errors") or []
    # check_freshness reports a warning *count*; the others report a list.
    warnings = payload.get("warnings") or []
    if isinstance(warnings, int):
        warnings = [f"{warnings} freshness candidate(s)"] if warnings else []
    for message in errors:
        result.error("FRAMEWORK_ISSUE", f"{name}: {message}")
    for message in warnings:
        result.warning("FRAMEWORK_WARNING", f"{name}: {message}")
    if not errors and not warnings:
        result.info("CHECK_OK", name)


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
    run_status_command(
        "git isolation",
        [sys.executable, str(SCRIPTS_DIR / "check_git_isolation.py"), "--json"],
        result,
    )
    run_status_command(
        "path discipline",
        [sys.executable, str(SCRIPTS_DIR / "check_path_discipline.py"), "--json"],
        result,
    )
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
    for script in ("check_freshness.py", "check_visibility_field.py"):
        path = SCRIPTS_DIR / script
        if path.exists():
            run_status_command(script, [sys.executable, str(path), "--json"], result)


def exports(result: CheckResult) -> None:
    if not any(HTML_DIR.glob("*.html")) if HTML_DIR.exists() else True:
        result.skip("NO_HTML_EXPORTS", "no HTML exports to validate")
    else:
        for script in ("check_html_structure.py", "check_html_browser.py"):
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


def site(result: CheckResult) -> None:
    if not corpus_has_essays():
        result.skip("SKELETON_NO_ESSAYS", "no essays present; site privacy validation skipped")
        return
    if not (SITE_ROOT / ".second-brain-site").exists():
        result.skip("NO_SITE", "site checkout not initialized; site privacy validation skipped")
        return
    path = SCRIPTS_DIR / "check_site_privacy.py"
    if path.exists():
        run_status_command("check_site_privacy.py", [sys.executable, str(path), "--json"], result)


def audit(mode: str) -> CheckResult:
    result = CheckResult("repository")
    if mode in {"quick", "full"}:
        quick(result)
    if mode in {"wiki", "full"}:
        wiki(result)
    if mode in {"exports", "full"}:
        exports(result)
    if mode in {"site", "full"}:
        site(result)
    result.meta["mode"] = mode
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    group = ap.add_mutually_exclusive_group()
    group.add_argument("--quick", action="store_true", help="fast repository/skill/CLI checks")
    group.add_argument("--wiki", action="store_true", help="corpus checks only")
    group.add_argument("--exports", action="store_true", help="existing HTML/PDF checks only")
    group.add_argument("--site", action="store_true", help="site privacy checks only")
    group.add_argument("--full", action="store_true", help="all checks (also the no-argument default)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--fail-on-warning", action="store_true")
    args = ap.parse_args()
    mode = "quick" if args.quick else "wiki" if args.wiki else "exports" if args.exports else "site" if args.site else "full"
    result = audit(mode)
    result.print(args.json)
    return result.exit_code(args.fail_on_warning)


if __name__ == "__main__":
    raise SystemExit(main())
