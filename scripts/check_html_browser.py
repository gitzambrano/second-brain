#!/usr/bin/env python3
"""
Validação em navegador dos arquivos HTML standalone exportados.

Default sem argumentos: auditar cada ``output/html/*.html`` nos viewports de
celular e de desktop. Se não existir HTML (modo esqueleto, normal), reportar
SKIP.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from repo_paths import HTML_DIR
from sanity_common import (
    CHROMIUM_ABSENT,
    PLAYWRIGHT_ABSENT,
    CheckResult,
    resolve_chromium,
)

VIEWPORTS = ((390, 844, "mobile"), (1440, 900, "desktop"))


def audit_file(browser, path: Path, result: CheckResult) -> None:
    for width, height, label in VIEWPORTS:
        page = browser.new_page(viewport={"width": width, "height": height})
        console_errors: list[str] = []
        failed: list[str] = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("requestfailed", lambda req: failed.append(req.url))
        raw = path.read_text(encoding="utf-8", errors="replace")
        page.set_content(raw, wait_until="load")
        # Wait for MathJax before measuring. A page caught mid-typeset
        # still has raw TeX laid out as running text, which reports a
        # width the finished page does not have — and the naive
        # "MathJax is absent" guard passed instantly, because at that
        # moment its script had simply not run yet.
        if "MathJax" in raw:
            try:
                # Await MathJax's own startup promise. A state() >= N
                # guard is not enough: the early states are reached
                # almost immediately, so the page was still measured
                # mid-typeset, with raw TeX laid out as running text.
                page.wait_for_function(
                    "() => !!(window.MathJax && window.MathJax.startup"
                    " && window.MathJax.startup.promise)",
                    timeout=30000,
                )
                # Bounded: a document whose typeset never settles would
                # otherwise hang the whole audit on an await with no timeout.
                page.evaluate(
                    "async () => {"
                    " const p = window.MathJax && window.MathJax.startup"
                    " && window.MathJax.startup.promise;"
                    " if (!p) return;"
                    " await Promise.race([p, new Promise(r => setTimeout(r, 20000))]); }"
                )
            except Exception:  # noqa: BLE001 - measure anyway, never hang
                pass
        page.wait_for_timeout(400)
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


def audit(slug: str | None = None) -> CheckResult:
    result = CheckResult("html-render")
    files = sorted(HTML_DIR.glob(f"{slug or '*'}.html")) if HTML_DIR.exists() else []
    if not files:
        result.skip("NO_HTML", f"no HTML exports in {HTML_DIR}")
        return result
    estado, executable, detalhe = resolve_chromium()
    if estado == PLAYWRIGHT_ABSENT:
        result.skip("PLAYWRIGHT_MISSING", f"browser validation unavailable; {detalhe}")
        return result
    if estado == CHROMIUM_ABSENT:
        result.skip("CHROMIUM_MISSING", detalhe)
        return result

    from playwright.sync_api import sync_playwright

    # One browser for the whole audit. Launching Chromium per file cost more
    # than the checking did: 47 exports meant 47 cold starts.
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=executable)
        try:
            for path in files:
                audit_file(browser, path, result)
        finally:
            browser.close()

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
