#!/usr/bin/env python3
"""Manage the explicit public allowlist stored in essay frontmatter.

No args: list essays currently authorized with YAML `publish: true`.

Examples:
    python scripts/publication.py set-exclusive "Dutch Roll"
    python scripts/publication.py allow <slug>
    python scripts/publication.py deny <slug>

`set-exclusive` removes publish authorization from every other essay and aborts
unless the query resolves to exactly one essay.
"""
from __future__ import annotations

import argparse
import re
import unicodedata
from pathlib import Path

from repo_paths import ESSAYS_DIR

FM = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
H1 = re.compile(r"(?m)^#\s+(.+?)\s*$")
PUB = re.compile(r"(?m)^publish:\s*.*$\n?")

# Rewriting uses a stricter delimiter: `\s*` above greedily swallows blank lines
# *after* the closing `---`, which silently reflows the body. `[ \t]*` stops at the
# end of the delimiter line, so everything past it is preserved byte for byte.
FM_WRITE = re.compile(r"\A---[ \t]*\n(.*?)\n---[ \t]*\n", re.S)


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", s.casefold()).strip()


def title(path: Path) -> str:
    text = path.read_text(encoding="utf-8-sig")
    m = FM.match(text)
    body = text[m.end():] if m else text
    h = H1.search(body)
    return h.group(1).strip() if h else path.stem


def has_true(path: Path) -> bool:
    text = path.read_text(encoding="utf-8-sig")
    m = FM.match(text)
    if not m:
        return False
    return bool(re.search(r"(?m)^publish:\s*true\s*$", m.group(1)))


def set_publish(path: Path, enabled: bool) -> bool:
    """Set/clear `publish` in frontmatter. Returns True when the file changed."""
    text = path.read_text(encoding="utf-8-sig")
    m = FM_WRITE.match(text)
    if not m:
        raise RuntimeError(f"essay has no YAML frontmatter: {path}")
    front = PUB.sub("", m.group(1)).rstrip("\n")
    if enabled:
        front += "\npublish: true"
    new = "---\n" + front + "\n---\n" + text[m.end():]
    if new == text:
        return False
    path.write_text(new, encoding="utf-8")
    return True


def require_frontmatter(paths) -> None:
    """Abort before the first write if any essay could not be rewritten."""
    broken = [q for q in paths if not FM_WRITE.match(q.read_text(encoding="utf-8-sig"))]
    if broken:
        raise SystemExit(
            "refusing to mutate: essays without YAML frontmatter:\n"
            + "\n".join(f"  {q.name}" for q in broken)
        )


def essays():
    return sorted(p for p in ESSAYS_DIR.glob("*.md") if p.name != ".gitkeep")


def resolve(q: str) -> list[Path]:
    nq = norm(q)
    exact, partial = [], []
    for p in essays():
        t = norm(title(p))
        stem = norm(p.stem)
        if nq in {t, stem}:
            exact.append(p)
        elif nq and (nq in t or nq in stem):
            partial.append(p)
    return exact or partial


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd")
    allow = sub.add_parser("allow", help="authorize one essay by slug")
    allow.add_argument("slug")
    deny = sub.add_parser("deny", help="revoke authorization for one essay")
    deny.add_argument("slug")
    exclusive = sub.add_parser("set-exclusive", help="authorize exactly one essay")
    exclusive.add_argument("query")
    args = ap.parse_args()

    if args.cmd is None:
        public = [(p.stem, title(p)) for p in essays() if has_true(p)]
        print(f"publish:true essays: {len(public)}")
        for slug, essay_title in public:
            print(f"  {slug} — {essay_title}")
        return 0

    if args.cmd in {"allow", "deny"}:
        p = ESSAYS_DIR / args.slug
        if p.suffix.lower() != ".md":
            p = p.with_suffix(".md")
        if not p.exists():
            raise SystemExit(f"essay not found: {p}")
        set_publish(p, args.cmd == "allow")
        print(f"{args.cmd}: {p.stem}")
        return 0

    matches = resolve(args.query)
    if len(matches) != 1:
        print(f"query resolved to {len(matches)} essay(s); refusing mutation")
        for match in matches:
            print(f"  {match.stem} — {title(match)}")
        return 2

    target = matches[0]
    all_essays = essays()
    require_frontmatter(all_essays)
    changed = [p for p in all_essays if set_publish(p, p == target)]
    print(f"exclusive publication allowlist: {target.stem} — {title(target)}")
    print(f"essays rewritten: {len(changed)}")
    for p in changed:
        print(f"  {p.stem}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
