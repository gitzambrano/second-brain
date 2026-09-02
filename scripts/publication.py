#!/usr/bin/env python3
"""Set an essay's visibility in its frontmatter.

Three levels, described in `visibility.py`:

    public   the text is readable on the public site
    private  catalogued and mapped by name and summary; the text is not published
    hidden   absent everywhere, including the wiki's own index and graph

No args: list the corpus by level.

    python scripts/publication.py set-exclusive "Dutch Roll"
    python scripts/publication.py allow <slug>
    python scripts/publication.py deny  <slug>
    python scripts/publication.py hide  <slug>

`set-exclusive` makes exactly one essay public and returns every other public
essay to private. It never changes a hidden essay, and it aborts unless the
query resolves to exactly one essay.
"""
from __future__ import annotations

import argparse
import re
import unicodedata
from pathlib import Path

import visibility
from repo_paths import ESSAYS_DIR

FM = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
H1 = re.compile(r"(?m)^#\s+(.+?)\s*$")

# Rewriting uses a stricter delimiter: `\s*` above greedily swallows blank lines
# *after* the closing `---`, which silently reflows the body. `[ \t]*` stops at the
# end of the delimiter line, so everything past it is preserved byte for byte.
FM_WRITE = re.compile(r"\A---[ \t]*\n(.*?)\n---[ \t]*\n", re.S)

# Both spellings are stripped before the new one is written.
FIELD = re.compile(r"(?m)^(?:publish|visibility):\s*.*$\n?")


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", s.casefold()).strip()


def frontmatter(path: Path) -> dict:
    import yaml
    text = path.read_text(encoding="utf-8-sig")
    m = FM.match(text)
    if not m:
        return {}
    try:
        data = yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        # Unreadable frontmatter is treated as declaring nothing, i.e. private.
        return {}
    return data if isinstance(data, dict) else {}


def title(path: Path) -> str:
    text = path.read_text(encoding="utf-8-sig")
    m = FM.match(text)
    body = text[m.end():] if m else text
    h = H1.search(body)
    return h.group(1).strip() if h else path.stem


def level_of(path: Path) -> str:
    return visibility.of(frontmatter(path))


def set_level(path: Path, level: str) -> bool:
    """Write `visibility:`. Returns True when the file changed.

    Only the frontmatter is touched: everything after the closing `---` is
    preserved byte for byte.
    """
    text = path.read_text(encoding="utf-8-sig")
    m = FM_WRITE.match(text)
    if not m:
        raise RuntimeError(f"essay has no YAML frontmatter: {path}")
    front = FIELD.sub("", m.group(1)).rstrip("\n")
    front += f"\nvisibility: {level}"
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


def essays() -> list[Path]:
    if not ESSAYS_DIR.exists():
        return []
    return sorted(p for p in ESSAYS_DIR.glob("*.md") if p.name != ".gitkeep")


def resolve(query: str) -> list[Path]:
    nq = norm(query)
    exact, partial = [], []
    for p in essays():
        t, stem = norm(title(p)), norm(p.stem)
        if nq in {t, stem}:
            exact.append(p)
        elif nq and (nq in t or nq in stem):
            partial.append(p)
    return exact or partial


def one(slug: str) -> Path:
    path = ESSAYS_DIR / slug
    if path.suffix.lower() != ".md":
        path = path.with_suffix(".md")
    if not path.exists():
        raise SystemExit(f"essay not found: {path}")
    return path


def report() -> int:
    buckets: dict[str, list[Path]] = {level: [] for level in visibility.LEVELS}
    for path in essays():
        buckets[level_of(path)].append(path)
    for level in visibility.LEVELS:
        print(f"{level}: {len(buckets[level])}")
        if level != visibility.PRIVATE:
            for path in buckets[level]:
                print(f"  {path.stem} — {title(path)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd")
    allow = sub.add_parser("allow", help="make one essay public")
    allow.add_argument("slug")
    deny = sub.add_parser("deny", help="return one essay to private")
    deny.add_argument("slug")
    hide = sub.add_parser("hide", help="remove one essay from every listing")
    hide.add_argument("slug")
    exclusive = sub.add_parser("set-exclusive", help="make exactly one essay public")
    exclusive.add_argument("query")
    args = ap.parse_args()

    if args.cmd is None:
        return report()

    if args.cmd in {"allow", "deny", "hide"}:
        level = {"allow": visibility.PUBLIC,
                 "deny": visibility.PRIVATE,
                 "hide": visibility.HIDDEN}[args.cmd]
        path = one(args.slug)
        changed = set_level(path, level)
        print(f"{path.stem}: {level}" + ("" if changed else " (sem mudança)"))
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

    changed = []
    for path in all_essays:
        current = level_of(path)
        # A hidden essay stays hidden: publishing one essay must not surface another.
        if current == visibility.HIDDEN:
            continue
        wanted = visibility.PUBLIC if path == target else visibility.PRIVATE
        if set_level(path, wanted):
            changed.append(path)

    print(f"exclusive publication: {target.stem} — {title(target)}")
    print(f"essays rewritten: {len(changed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
