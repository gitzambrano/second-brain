"""
auto_fix_lint.py - Apply mechanical, unambiguous formatting fixes to wiki content.

Scope is intentionally narrow: only wiki/essays, wiki/concepts, wiki/entities,
wiki/synthesis (same DIRS as lint_all.py) -- never AGENTS.md, README.md,
.agents/skills/**, or wiki/sources/** (original, immutable documents). Fixing
the wiki's own documentation/skill files as if they were wiki *content* is
exactly the kind of over-reach this script must not do.

Two fixes, both applied only outside YAML frontmatter and fenced code blocks
(``` ... ```), so example snippets inside SKILL.md-style docs or an essay's
own code blocks are never rewritten:
  1. Blank line after a Markdown heading (#, ##, ... ######).
  2. Colon inside a [[wikilink]] target/display text -> em dash (Obsidian
     breaks on ':' inside [[...]]).
"""

import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
WIKI_ROOT = ROOT_DIR / "wiki"
ESSAYS_DIR = WIKI_ROOT / "essays"
CONCEPTS_DIR = WIKI_ROOT / "concepts"
ENTITIES_DIR = WIKI_ROOT / "entities"
SYNTHESIS_DIR = WIKI_ROOT / "synthesis"

# Same set of directories lint_all.py treats as "wiki content" -- sources are
# original/immutable documents and are excluded on purpose.
DIRS = [ESSAYS_DIR, CONCEPTS_DIR, ENTITIES_DIR, SYNTHESIS_DIR]

FENCE_RE = re.compile(r"^```.*$")


def load_file_content(path):
    # utf-8-sig strips a BOM on read if one happens to be present, but...
    with open(path, "r", encoding="utf-8-sig") as f:
        return f.read()


def save_file_content(path, content):
    # ...we always write plain utf-8, so this script never introduces a BOM
    # that wasn't already there. Injecting a BOM can break YAML frontmatter
    # parsers and Pandoc.
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def split_frontmatter(content):
    """Return (frontmatter_including_delimiters, body). frontmatter is '' if none."""
    if content.startswith("---\n"):
        end = content.find("\n---", 4)
        if end != -1:
            end_of_block = content.find("\n", end + 1)
            end_of_block = end_of_block + 1 if end_of_block != -1 else len(content)
            return content[:end_of_block], content[end_of_block:]
    return "", content


def apply_outside_fences(body, fn):
    """Apply fn(segment) only to segments of `body` that are NOT inside a
    fenced code block, leaving fences (and their contents) untouched."""
    lines = body.split("\n")
    out_segments = []
    buffer = []
    in_fence = False
    for line in lines:
        if FENCE_RE.match(line.strip()):
            out_segments.append(fn("\n".join(buffer)) if not in_fence else "\n".join(buffer))
            out_segments.append(line)
            buffer = []
            in_fence = not in_fence
            continue
        buffer.append(line)
    out_segments.append(fn("\n".join(buffer)) if not in_fence else "\n".join(buffer))
    return "\n".join(out_segments)


def fix_heading_spacing(segment):
    lines = segment.split("\n")
    new_lines = []
    for i, line in enumerate(lines):
        new_lines.append(line)
        if re.match(r"^#{1,6} ", line):
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                if next_line.strip() != "" and not next_line.strip().startswith("#"):
                    new_lines.append("")
    return "\n".join(new_lines)


def fix_wikilinks_colons(segment):
    def repl(match):
        raw_link = match.group(1)
        if "|" in raw_link:
            target, display = raw_link.split("|", 1)
        else:
            target, display = raw_link, None

        if ": " in target:
            target = target.replace(": ", " — ")
        elif ":" in target:
            target = target.replace(":", " — ")

        if display:
            if ": " in display:
                display = display.replace(": ", " — ")
            elif ":" in display:
                display = display.replace(":", " — ")
            return f"[[{target.strip()}|{display.strip()}]]"
        return f"[[{target.strip()}]]"

    return re.sub(r"\[\[([^\]]+)\]\]", repl, segment)


def fix_content(content):
    frontmatter, body = split_frontmatter(content)
    body = apply_outside_fences(body, fix_heading_spacing)
    body = apply_outside_fences(body, fix_wikilinks_colons)
    return frontmatter + body


def main():
    fixed_files_count = 0

    for d in DIRS:
        if not d.exists():
            continue
        for file in sorted(d.glob("*.md")):
            if file.name in ("log.md", "index.md", "manifest.md", "map.md"):
                continue

            content = load_file_content(file)
            new_content = fix_content(content)

            if new_content != content:
                save_file_content(file, new_content)
                print(f"Fixed formatting and/or links in: {file.relative_to(ROOT_DIR)}")
                fixed_files_count += 1

    print(f"\nCompleted auto-fix. Modified {fixed_files_count} files.")


if __name__ == "__main__":
    main()
