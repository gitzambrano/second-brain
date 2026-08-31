#!/usr/bin/env python3
"""Diagnose runtime dependencies used by repository and export tooling.

No-argument default: run the complete environment diagnosis. Missing export
engines are warnings by default because core repository checks must work in a
minimal clone; ``--strict`` promotes them to errors.
"""
from __future__ import annotations

import argparse
import importlib.util
import shutil
import sys
from pathlib import Path

from sanity_common import CheckResult


def audit(core_only: bool = False, strict: bool = False) -> CheckResult:
    result = CheckResult("environment")
    result.info("PYTHON", sys.version.split()[0])
    modules = {"yaml": "PyYAML"} if core_only else {
        "yaml": "PyYAML",
        "pymupdf": "PyMuPDF",
        "bs4": "BeautifulSoup4",
        "html5lib": "html5lib",
    }
    for module, label in modules.items():
        if importlib.util.find_spec(module) is None:
            sev = "ERROR" if module in {"yaml"} else ("ERROR" if strict else "WARNING")
            result.add("MODULE_MISSING", sev, f"{label} ({module}) is not importable")
        else:
            result.info("MODULE_OK", f"{label} available")
    if core_only:
        return result

    for exe, label in (("pandoc", "Pandoc"), ("lualatex", "LuaLaTeX")):
        path = shutil.which(exe)
        if path:
            result.info("EXECUTABLE_OK", f"{label}: {path}")
        else:
            result.add("EXECUTABLE_MISSING", "ERROR" if strict else "WARNING", f"{label} not found")

    if importlib.util.find_spec("playwright") is None:
        result.add("PLAYWRIGHT_MISSING", "ERROR" if strict else "WARNING", "Playwright Python package not installed")
    else:
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser_path = Path(p.chromium.executable_path)
            browser_names = ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable")
            system_browser = next((shutil.which(x) for x in browser_names if shutil.which(x)), None)
            if browser_path.exists():
                result.info("CHROMIUM_OK", str(browser_path))
            elif system_browser:
                result.info("CHROMIUM_OK", f"system browser fallback: {system_browser}")
            else:
                result.add(
                    "CHROMIUM_MISSING",
                    "ERROR" if strict else "WARNING",
                    "no Playwright-managed or system Chromium/Chrome found",
                )
        except Exception as exc:  # environment probe only
            result.add("PLAYWRIGHT_PROBE_FAILED", "ERROR" if strict else "WARNING", str(exc))
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--core", action="store_true", help="check only Python/core dependencies")
    ap.add_argument("--strict", action="store_true", help="treat optional export dependencies as blocking")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    result = audit(args.core, args.strict)
    result.print(args.json)
    return result.exit_code()


if __name__ == "__main__":
    raise SystemExit(main())
