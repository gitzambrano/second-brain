#!/usr/bin/env python3
"""
Abre cada página do site público construído num navegador real e a audita.

`check_html_browser.py` cobre o export HTML standalone. As páginas do site são
outro artefato — o mesmo template de essay mais a sobreposição do Atlas, o
cromo próprio e a folha de estilo própria — e ninguém estava olhando para elas.
Este script olha: sobe SITE_ROOT numa porta local, abre cada página, espera o
MathJax e reporta o que um leitor encontraria de fato.

Verificado num celular e num desktop:
    overflow horizontal, imagem quebrada, âncora interna morta, requisição que
    falhou, erro de console, Markdown vazando no texto renderizado e — num
    essay — a barra do site, um sumário com entradas e um título de capa sem
    marcadores de Markdown.

Default sem argumentos: auditar todas as páginas de SITE_ROOT.
"""
from __future__ import annotations

import argparse
import http.server
import shutil
import socketserver
import threading
from functools import partial
from pathlib import Path

import console_encoding  # noqa: F401  (UTF-8 no console; ver o módulo)
from repo_paths import SITE_ROOT
from sanity_common import CheckResult

VIEWPORTS = ((390, 844, "mobile"), (1440, 900, "desktop"))

# The two maps are one 700 KB page each, with a force simulation that never
# settles inside a check's budget. They are audited by check_site_privacy.py
# on content, not opened here.
SKIP = {"graph.html", "sphere.html"}

PROBE = r"""() => {
  const content = document.querySelector('.content') || document.body;
  const text = content.innerText || '';
  return {
    docWidth: document.documentElement.scrollWidth,
    innerWidth: window.innerWidth,
    badImages: [...document.images]
      .filter(i => !i.complete || i.naturalWidth === 0)
      .map(i => i.getAttribute('src')),
    brokenAnchors: [...document.querySelectorAll('a[href^="#"]')]
      .map(a => a.getAttribute('href').slice(1))
      .filter(id => id && !document.getElementById(id)),
    rawWikilink: /\[\[[^\]\n]{1,80}\]\]/.test(text),
    rawFencedDiv: text.includes(':::{') || text.includes('::: {'),
    isEssay: !!document.querySelector('.sb-bar'),
    hasFab: !!document.querySelector('.sb-toc-fab'),
    tocLinks: document.querySelectorAll('#sbTocList a').length,
    headings: document.querySelectorAll('.content h2').length,
    coverTitle: (document.querySelector('.hero-title') || {}).textContent || ''
  };
}"""

# `_` and `*` in a rendered cover title mean the Markdown emphasis of the H1
# survived into text that no longer renders Markdown.
MARKDOWN_MARKERS = ("_", "*")


class SiteServer:
    """Serve SITE_ROOT on an ephemeral port for the duration of the audit.

    Loading the pages over `file://` is not equivalent: the browser blocks the
    index's own `fetch("graph.json")` as a cross-origin request, so the check
    would report a failure the deployed site never has.
    """

    def __init__(self, root: Path):
        handler = partial(QuietHandler, directory=str(root))
        self.server = socketserver.ThreadingTCPServer(("127.0.0.1", 0), handler)
        self.server.daemon_threads = True
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def __enter__(self) -> str:
        self.thread.start()
        return f"http://127.0.0.1:{self.port}"

    def __exit__(self, *exc) -> None:
        self.server.shutdown()
        self.server.server_close()


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args) -> None:  # noqa: D102 - keep the report clean
        pass


def audit_page(page, url: str, path: Path, label: str, result: CheckResult,
               console_errors: list[str], failed: list[str]) -> None:
    console_errors.clear()
    failed.clear()
    page.goto(url, wait_until="load", timeout=60000)
    try:
        page.wait_for_function(
            "() => !document.querySelector('script[src*=mathjax]')"
            " || !!(window.MathJax && window.MathJax.startup"
            " && window.MathJax.startup.promise)",
            timeout=20000,
        )
        # Bounded: an await on a promise that never settles has no timeout of
        # its own and would hang the audit instead of failing the page.
        page.evaluate(
            "async () => {"
            " const p = window.MathJax && window.MathJax.startup"
            " && window.MathJax.startup.promise;"
            " if (!p) return;"
            " await Promise.race([p, new Promise(r => setTimeout(r, 20000))]); }"
        )
    except Exception:  # noqa: BLE001 - measure anyway, never hang the check
        pass
    page.wait_for_timeout(300)

    data = page.evaluate(PROBE)
    name = path.name

    if data["docWidth"] > data["innerWidth"] + 2:
        result.error(
            "PAGE_HORIZONTAL_OVERFLOW",
            f"{label}: document {data['docWidth']}px > viewport {data['innerWidth']}px",
            name,
        )
    for src in data["badImages"]:
        result.error("IMAGE_NOT_LOADED", f"{label}: {src}", name)
    for anchor in data["brokenAnchors"]:
        result.error("BROKEN_ANCHOR", f"{label}: #{anchor}", name)
    if data["rawWikilink"]:
        result.error("RAW_WIKILINK", f"{label}: [[...]] visible in the page", name)
    if data["rawFencedDiv"]:
        result.error("RAW_FENCED_DIV", f"{label}: ::: block visible in the page", name)

    if data["isEssay"]:
        if data["headings"] and not data["tocLinks"]:
            result.error("EMPTY_SUMMARY", f"{label}: essay has chapters but no summary", name)
        if not data["hasFab"]:
            result.error("NO_SUMMARY_CONTROL", f"{label}: summary cannot be opened", name)
        title = data["coverTitle"]
        if any(marker in title for marker in MARKDOWN_MARKERS):
            result.error("MARKDOWN_IN_COVER_TITLE", f"{label}: {title[:60]}", name)

    for message in console_errors:
        if "favicon" in message.lower():
            continue
        result.error("CONSOLE_ERROR", f"{label}: {message[:160]}", name)
    for url in dict.fromkeys(failed):
        if "favicon" in url:
            continue
        result.error("FAILED_REQUEST", f"{label}: {url}", name)


def audit(name: str | None = None) -> CheckResult:
    result = CheckResult("site-pages")

    if not (SITE_ROOT / ".second-brain-site").exists():
        result.skip("NO_SITE", f"site checkout not initialized: {SITE_ROOT}")
        return result

    pages = [p for p in sorted(SITE_ROOT.glob("*.html")) if p.name not in SKIP]
    pages += sorted((SITE_ROOT / "essays").glob("*.html"))
    if name:
        pages = [p for p in pages if p.name == name or p.stem == name]
    if not pages:
        result.skip("NO_PAGES", f"no pages to audit in {SITE_ROOT}")
        return result

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        result.skip("PLAYWRIGHT_MISSING", "browser validation unavailable; install playwright")
        return result

    with sync_playwright() as p:
        managed = Path(p.chromium.executable_path)
        names = ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable")
        system = next((shutil.which(x) for x in names if shutil.which(x)), None)
        executable = str(managed) if managed.exists() else system
        if not executable:
            result.skip("CHROMIUM_MISSING", "no Playwright-managed or system Chromium/Chrome found")
            return result

        browser = p.chromium.launch(headless=True, executable_path=executable)
        try:
            with SiteServer(SITE_ROOT) as base:
                for width, height, label in VIEWPORTS:
                    context = browser.new_context(viewport={"width": width, "height": height})
                    page = context.new_page()
                    console_errors: list[str] = []
                    failed: list[str] = []
                    page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
                    page.on("pageerror", lambda e: console_errors.append(str(e)))
                    page.on("requestfailed", lambda r: failed.append(r.url))
                    # A 404 is a *successful* response as far as Playwright is
                    # concerned, so `requestfailed` never sees it — and the console
                    # only says "404", never which file. Name it here.
                    page.on("response", lambda r: failed.append(f"{r.status} {r.url}")
                            if r.status >= 400 else None)
                    for path in pages:
                        relative = path.relative_to(SITE_ROOT).as_posix()
                        audit_page(page, f"{base}/{relative}", path, label,
                                   result, console_errors, failed)
                    context.close()
        finally:
            browser.close()

    result.meta["pages"] = len(pages)
    result.meta["viewports"] = len(VIEWPORTS)
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("page", nargs="?", help="optional page name or stem; default audits all")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--fail-on-warning", action="store_true")
    args = ap.parse_args()
    result = audit(args.page)
    result.print(args.json)
    return result.exit_code(args.fail_on_warning)


if __name__ == "__main__":
    raise SystemExit(main())
