#!/usr/bin/env python3
"""Browser-level validation of exported standalone HTML files.

No-argument default: audit every ``output/html/*.html`` file at mobile and
desktop viewports. If no HTML exists (normal skeleton mode), report SKIP.
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from repo_paths import HTML_DIR
from sanity_common import CheckResult

VIEWPORTS = ((390, 844, "mobile"), (1440, 900, "desktop"))


def audit_file(path: Path, result: CheckResult) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        result.skip("PLAYWRIGHT_MISSING", "browser validation unavailable; install playwright", path.name)
        return

    with sync_playwright() as p:
        managed = Path(p.chromium.executable_path)
        browser_names = ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable")
        system = next((shutil.which(x) for x in browser_names if shutil.which(x)), None)
        executable = str(managed) if managed.exists() else system
        if not executable:
            result.skip("CHROMIUM_MISSING", "no Playwright-managed or system Chromium/Chrome found", path.name)
            return
        browser = p.chromium.launch(headless=True, executable_path=executable)
        try:
            for width, height, label in VIEWPORTS:
                page = browser.new_page(viewport={"width": width, "height": height})
                console_errors: list[str] = []
                failed: list[str] = []
                page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
                page.on("requestfailed", lambda req: failed.append(req.url))
                raw = path.read_text(encoding="utf-8", errors="replace")
                page.set_content(raw, wait_until="load")
                page.wait_for_timeout(250)
                data = page.evaluate("""() => ({
                  docWidth: document.documentElement.scrollWidth,
                  innerWidth: window.innerWidth,
                  badImages: [...document.images].filter(i => !i.complete || i.naturalWidth === 0).map(i => i.src),
                  brokenAnchors: [...document.querySelectorAll('a[href^="#"]')]
                    .map(a => a.getAttribute('href').slice(1)).filter(id => id && !document.getElementById(id)),
                  rawWikilinks: (() => {
                  const clean = document.body.cloneNode(true);
                  clean.querySelectorAll('pre, code, script, style').forEach(el => el.remove());
                  const text = clean.textContent || '';
                  return text.includes('[[') && text.includes(']]');
                  })(),
                  rawFencedDiv: document.body.innerText.includes(':::{') || document.body.innerText.includes('::: {')
                })""")
                if data["docWidth"] > data["innerWidth"] + 2:
                    result.error(
                        "PAGE_HORIZONTAL_OVERFLOW",
                        f"{label}: document {data['docWidth']}px > viewport {data['innerWidth']}px",
                        path.name,
                    )
                if data["badImages"]:
                    result.error(
                        "BROKEN_IMAGE",
                        f"{label}: {len(data['badImages'])} image(s) failed",
                        path.name,
                        details=data["badImages"][:5],
                    )
                if data["brokenAnchors"]:
                    result.error(
                        "BROKEN_TOC_NAVIGATION",
                        f"{label}: broken anchors {data['brokenAnchors'][:5]}",
                        path.name,
                    )
                if data["rawWikilinks"]:
                    result.error("VISIBLE_WIKILINK", f"{label}: raw [[wikilink]] visible", path.name)
                if data["rawFencedDiv"]:
                    result.error("VISIBLE_FENCED_DIV", f"{label}: fenced div marker visible", path.name)
                for message in console_errors[:5]:
                    result.error("CONSOLE_ERROR", f"{label}: {message}", path.name)
                for url in failed[:5]:
                    # file:// requests for intentionally absent local links are not page resources.
                    if not url.startswith("file://"):
                        result.error("FAILED_REQUEST", f"{label}: {url}", path.name)
                page.close()
        finally:
            browser.close()


def audit(slug: str | None = None) -> CheckResult:
    result = CheckResult("html-render")
    files = sorted(HTML_DIR.glob(f"{slug or '*'}.html")) if HTML_DIR.exists() else []
    if not files:
        result.skip("NO_HTML", f"no HTML exports in {HTML_DIR}")
        return result
    for path in files:
        audit_file(path, result)
    result.meta["files"] = len(files)
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("slug", nargs="?", help="optional export stem; default audits all HTML")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--fail-on-warning", action="store_true")
    args = ap.parse_args()
    result = audit(args.slug)
    result.print(args.json)
    return result.exit_code(args.fail_on_warning)


if __name__ == "__main__":
    raise SystemExit(main())
