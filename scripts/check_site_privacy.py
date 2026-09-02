#!/usr/bin/env python3
"""Enforce what the public site may and may not expose.

The owner's decision, which this checker encodes:

    public   title, summary, tags, dates, draft status, connections, and the
             external URL of a bibliography entry — for the whole base
    private  the body of any page, any path into the private repository, and a
             working link to anything that is not an authorized essay

So an unpublished essay is catalogued and mapped, by name and abstract, and
cannot be opened. A static site cannot hide what it serves: everything in the
"public" row above is readable by anyone.

The maps embed their data as deflated base64 inside the HTML, so this checker
inflates that payload and inspects the real nodes rather than grepping text.

No-argument default: audit SITE_ROOT and report PASS/FAIL.
"""
from __future__ import annotations

import argparse
import base64
import json
import re
import zlib

from repo_paths import SITE_ROOT
from site_common import collect_all

MAP_FILES = ("graph.html", "sphere.html")
MACHINE_FILES = ("search-index.json", "graph.json", "site-manifest.json")
SCANNED_SUFFIXES = {".html", ".json"}

# Fields that would carry body content or point back at the private repository.
FORBIDDEN_NODE_FIELDS = ("file", "body", "text", "path")

EMBEDDED_PAYLOAD = re.compile(r'id="sb-graph-data">([^<]*)<')

# A generated link or metadata value must never point into the private
# repository. Prose may legitimately *mention* these paths — several essays are
# about this very system — so the check inspects link targets and JSON path
# values, not free text.
PRIVATE_TARGET = re.compile(
    r"""(?:href|src|action|data-[\w-]+)\s*=\s*["']([^"']*)["']"""
    r"""|"(?:url|path|file|htmlFile)"\s*:\s*"([^"]*)\"""",
    re.I,
)
PRIVATE_PATH = re.compile(r"(?:\A|/|\.\./)(?:data/)?(?:wiki|plan|raw|output)/", re.I)
EXTERNAL_URL = re.compile(r"\s*(?:[a-z][a-z0-9+.-]*:|//)", re.I)


def inflate(encoded: str) -> dict:
    """Undo `_deflate_b64` from build_graph: raw deflate, base64 wrapped."""
    return json.loads(zlib.decompress(base64.b64decode(encoded), -15))


def audit_nodes(nodes, allowed: set[str], where: str) -> list[str]:
    """The map may name everything; it may not open or embody anything."""
    errors: list[str] = []
    for node in nodes:
        node_id = node.get("id")
        slug = str(node_id or "").partition(":")[2]
        readable = bool(node.get("public"))

        if readable and slug not in allowed:
            errors.append(f"{where}: node marked public but not authorized: {node_id}")

        link = str(node.get("htmlFile") or "")
        if link and (not readable or link != f"essays/{slug}.html"):
            errors.append(f"{where}: unauthorized read link: {node_id} -> {link}")

        url = str(node.get("url") or "")
        if url and not url.startswith(("http://", "https://")):
            errors.append(f"{where}: non-external url: {node_id} -> {url}")

        for field in FORBIDDEN_NODE_FIELDS:
            if node.get(field):
                errors.append(f"{where}: private field '{field}' on node {node_id}")
    return errors


def audit_maps(allowed: set[str]) -> list[str]:
    errors: list[str] = []

    data = SITE_ROOT / "graph.json"
    if data.exists():
        payload = json.loads(data.read_text(encoding="utf-8"))
        errors.extend(audit_nodes(payload.get("nodes", []), allowed, "graph.json"))

    for name in MAP_FILES:
        path = SITE_ROOT / name
        if not path.exists():
            errors.append(f"missing {name}")
            continue
        match = EMBEDDED_PAYLOAD.search(path.read_text(encoding="utf-8"))
        if not match:
            errors.append(f"{name}: embedded graph payload not found")
            continue
        try:
            payload = inflate(match.group(1))
        except (ValueError, zlib.error) as exc:
            errors.append(f"{name}: embedded payload unreadable: {exc}")
            continue
        errors.extend(audit_nodes(payload.get("nodes", []), allowed, name))
    return errors


def audit_catalogue(allowed: set[str]) -> list[str]:
    """The reading index catalogues everything; only the authorized carry text."""
    errors: list[str] = []
    path = SITE_ROOT / "search-index.json"
    if not path.exists():
        return errors
    for entry in json.loads(path.read_text(encoding="utf-8")):
        slug = entry.get("slug")
        if entry.get("published"):
            if slug not in allowed:
                errors.append(f"search index: published but not authorized: {slug}")
        else:
            if entry.get("text"):
                errors.append(f"search index: body text for unpublished essay: {slug}")
            if entry.get("url"):
                errors.append(f"search index: link for unpublished essay: {slug}")
    return errors


def audit_pages(allowed: set[str]) -> list[str]:
    """Only an authorized essay may have a rendered page."""
    errors: list[str] = []
    essays_dir = SITE_ROOT / "essays"
    if essays_dir.exists():
        extra = {p.stem for p in essays_dir.glob("*.html")} - allowed
        if extra:
            errors.append(f"rendered page for unauthorized essay: {sorted(extra)}")
    return errors


def audit_bodies() -> list[str]:
    """No unpublished essay's prose may appear anywhere in the output."""
    errors: list[str] = []
    unpublished = [e for e in collect_all() if not e.published]
    if not unpublished:
        return errors

    probes = []
    for essay in unpublished:
        # Skip the frontmatter-derived lines and take a distinctive sentence.
        words = [w for w in " ".join(essay.body.split()).split(" ") if w]
        for start in (60, 200, 400):
            window = " ".join(words[start:start + 12])
            if len(window) > 60:
                probes.append((essay.slug, window))
                break

    blobs = []
    for path in sorted(SITE_ROOT.rglob("*")):
        if path.is_file() and path.suffix.lower() in SCANNED_SUFFIXES:
            blobs.append((path.relative_to(SITE_ROOT), path.read_text(
                encoding="utf-8", errors="replace")))

    for slug, probe in probes:
        for rel, text in blobs:
            if probe in text:
                errors.append(f"body text of unpublished essay '{slug}' found in {rel}")
                break
    return errors


def audit() -> list[str]:
    errors: list[str] = []
    if not SITE_ROOT.exists():
        return [f"SITE_ROOT does not exist: {SITE_ROOT}"]

    allowed = {e.slug for e in collect_all() if e.published}

    for name in MACHINE_FILES:
        if not (SITE_ROOT / name).exists():
            errors.append(f"missing {name}")

    errors.extend(audit_maps(allowed))
    errors.extend(audit_catalogue(allowed))
    errors.extend(audit_pages(allowed))
    errors.extend(audit_bodies())

    for path in sorted(SITE_ROOT.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SCANNED_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in PRIVATE_TARGET.finditer(text):
            target = match.group(1) or match.group(2) or ""
            # An external URL cannot reach the private repository, and plenty of
            # them legitimately contain a /wiki/ segment (Wikipedia, for one).
            if EXTERNAL_URL.match(target):
                continue
            if PRIVATE_PATH.search(target):
                errors.append(
                    f"link into the private repository in "
                    f"{path.relative_to(SITE_ROOT)}: {target[:120]}")

    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    errors = audit()
    if args.json:
        print(json.dumps(
            {"status": "fail" if errors else "pass", "errors": errors},
            ensure_ascii=False, indent=2,
        ))
    else:
        print("site-privacy: PASS" if not errors else "site-privacy: FAIL")
        for error in errors:
            print(f"  ERROR {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
