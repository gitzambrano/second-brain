#!/usr/bin/env python3
"""Shared model of the public projection.

Reads DATA_ROOT and never writes there. Everything public flows through
``collect_public()``: an essay reaches the site only when its frontmatter has the
YAML boolean ``publish: true``. Any other value — absent, false, or the string
``"true"`` — is private.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import visibility
import yaml
from repo_paths import ESSAYS_DIR

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
H1_RE = re.compile(r"(?m)^#\s+(.+?)\s*$")
CONNECTIONS_RE = re.compile(r"(?ms)^##\s+Conex[õo]es\s*\n(.*?)(?=^##\s+|\Z)")
SUMARIO_RE = re.compile(r"(?ms)^##\s+Sumário\s*\n(.*?)(?=^##\s+|\Z)")
WIKILINK_RE = re.compile(r"\[\[([^|\]]+)(?:\|([^\]]+))?\]\]")


@dataclass(frozen=True)
class PublicEssay:
    slug: str
    path: Path
    title: str
    summary: str
    tags: tuple[str, ...]
    updated: str
    created: str
    status: str
    body: str
    published: bool = True
    visibility: str = visibility.PUBLIC


def parse(path: Path) -> tuple[dict[str, Any], str]:
    """Return (frontmatter mapping, body) for a wiki page."""
    text = path.read_text(encoding="utf-8-sig")
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    try:
        meta = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        # Unparseable frontmatter is not a licence to publish: treat it as if
        # the page declared nothing, which is the private default.
        return {}, text[match.end():]
    return (meta if isinstance(meta, dict) else {}), text[match.end():]


def strip_public_body(body: str) -> str:
    """Drop the parts of an essay that must not be republished verbatim.

    Removes the generated ``## Sumário``, the ``## Conexões`` block (private page
    names live there), the H1 (the template renders its own), and the byline
    blockquotes that precede the first section.
    """
    body = SUMARIO_RE.sub("", body)
    body = CONNECTIONS_RE.sub("", body)
    body = re.sub(r"(?m)^#\s+.+?\s*$\n?", "", body, count=1)

    lines = []
    in_preamble = True
    for line in body.splitlines():
        if in_preamble and line.startswith(">"):
            continue
        if line.startswith("## "):
            in_preamble = False
        lines.append(line)
    return "\n".join(lines).strip()


def _essay(path: Path, meta: dict, body: str, level: str) -> PublicEssay:
    heading = H1_RE.search(body)
    tags = meta.get("tags") or []
    if not isinstance(tags, list):
        tags = []
    return PublicEssay(
        slug=path.stem,
        path=path,
        title=heading.group(1).strip() if heading else path.stem,
        summary=str(meta.get("summary") or "").strip(),
        tags=tuple(str(t) for t in tags),
        updated=str(meta.get("updated") or ""),
        created=str(meta.get("created") or ""),
        status=str(meta.get("status") or ""),
        body=body,
        published=level == visibility.PUBLIC,
        visibility=level,
    )


def collect_all() -> list[PublicEssay]:
    """Every essay the site may name, each flagged with whether it may be read.

    The catalogue lists public and private essays — title, summary, tags,
    status. Only the public ones carry a page, and only their body is ever
    rendered. Hidden essays are skipped entirely.
    """
    if not ESSAYS_DIR.exists():
        return []
    essays = []
    for path in sorted(ESSAYS_DIR.glob("*.md")):
        if path.name == ".gitkeep":
            continue
        meta, body = parse(path)
        level = visibility.of(meta)
        # `hidden` means absent, not merely unreadable: it never reaches the
        # catalogue, the search index or the map.
        if level == visibility.HIDDEN:
            continue
        essays.append(_essay(path, meta, body, level))
    return essays


def collect_public() -> list[PublicEssay]:
    """Every essay explicitly authorized for publication, in slug order."""
    return [essay for essay in collect_all() if essay.published]


def public_connections(essay: PublicEssay, allowed: set[str]) -> list[str]:
    """Connections of `essay` that point at another public essay, deduplicated."""
    match = CONNECTIONS_RE.search(essay.body)
    if not match:
        return []
    targets: list[str] = []
    for target, _display in WIKILINK_RE.findall(match.group(1)):
        slug = target.split("#", 1)[0].strip()
        if slug in allowed and slug != essay.slug and slug not in targets:
            targets.append(slug)
    return targets


def plain_text(markdown: str) -> str:
    """Flatten markdown to a single searchable line."""
    markdown = re.sub(r"```.*?```", " ", markdown, flags=re.S)
    markdown = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", markdown)
    markdown = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", markdown)
    markdown = WIKILINK_RE.sub(lambda m: m.group(2) or m.group(1), markdown)
    markdown = re.sub(r"[#>*_`|~]", " ", markdown)
    return re.sub(r"\s+", " ", markdown).strip()


def sanitize_private_wikilinks(markdown: str, allowed_public: set[str]) -> str:
    """Remove private link targets from the public prose/search projection.

    Public→public links keep their visible label. A private link with an explicit
    display keeps only that display text. A private link without a display becomes
    a neutral placeholder, so neither the private slug nor its title leaks.
    """
    def replace(match: re.Match[str]) -> str:
        target = (match.group(1) or "").split("#", 1)[0].strip()
        display = (match.group(2) or "").strip()
        if target in allowed_public:
            return display or target
        return display or "referência interna"

    return WIKILINK_RE.sub(replace, markdown)


def public_body_for_index(essay: PublicEssay, allowed_public: set[str]) -> str:
    return sanitize_private_wikilinks(strip_public_body(essay.body), allowed_public)
