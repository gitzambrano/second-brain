import os
import re
from pathlib import Path

WIKI_ROOT = Path(__file__).resolve().parent.parent

def load_file_content(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return f.read()

def save_file_content(path, content):
    with open(path, "w", encoding="utf-8-sig") as f:
        f.write(content)

def fix_heading_spacing(content):
    lines = content.splitlines()
    new_lines = []
    for i, line in enumerate(lines):
        new_lines.append(line)
        if re.match(r"^#{1,6} ", line):
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                if next_line.strip() != "" and not next_line.strip().startswith("#"):
                    new_lines.append("")
    return "\n".join(new_lines) + ("\n" if content.endswith("\n") else "")

def fix_wikilinks_colons(content):
    # Find all [[wikilink]] patterns
    def repl(match):
        raw_link = match.group(1)
        if "|" in raw_link:
            target, display = raw_link.split("|", 1)
        else:
            target, display = raw_link, None
            
        # Fix colon in target
        if ": " in target:
            target = target.replace(": ", " — ")
        elif ":" in target:
            target = target.replace(":", " — ")
            
        # Fix colon in display
        if display:
            if ": " in display:
                display = display.replace(": ", " — ")
            elif ":" in display:
                display = display.replace(":", " — ")
            return f"[[{target.strip()}|{display.strip()}]]"
        else:
            return f"[[{target.strip()}]]"
            
    # Regex for [[anything but brackets]]
    return re.sub(r"\[\[([^\]]+)\]\]", repl, content)

def main():
    fixed_files_count = 0
    
    # Iterate through all md files under wiki
    for file in WIKI_ROOT.rglob("*.md"):
        if file.name == "log.md":
            continue
            
        content = load_file_content(file)
        orig_content = content
        
        # 1. Spacing after headings
        content = fix_heading_spacing(content)
        
        # 2. Fix wikilinks colons
        content = fix_wikilinks_colons(content)
        
        if content != orig_content:
            save_file_content(file, content)
            print(f"Fixed formatting and/or links in: {file.relative_to(WIKI_ROOT)}")
            fixed_files_count += 1
            
    print(f"\nCompleted auto-fix. Modified {fixed_files_count} files.")

if __name__ == "__main__":
    main()
