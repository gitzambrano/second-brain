#!/usr/bin/env python3
"""Static contract checker for skills, subagents, scripts and documentation.

No-argument default: audit all source skills/subagents plus AGENTS.md/README.md.
``.agents/`` is the single source tree; there is no generated mirror to check.
"""
from __future__ import annotations

import argparse
import ast
import re
from collections import Counter
from pathlib import Path

import yaml
from repo_paths import CODE_ROOT, SCRIPTS_DIR, SKILLS_DIR, SUBAGENTS_DIR
from sanity_common import CheckResult

TOP_LEVEL_PATH_WORDS = {"wiki", "raw", "plan", "scripts", "output", "agents", "claude", "codex", "mnt", "tmp"}
WEB_TOOLS = {"WebFetch", "WebSearch"}
SCRIPT_REF_RE = re.compile(r"scripts/([A-Za-z0-9_.-]+\.(?:py|sh|bat|lua|html))")
SLASH_REF_RE = re.compile(r"(?<![/\w.])/(?:[a-z][a-z0-9-]*)")
PY_COMMAND_RE = re.compile(r"python(?:3)?\s+scripts/([A-Za-z0-9_.-]+\.py)([^\n`]*)")
FLAG_RE = re.compile(r"(?<!\w)(--[a-zA-Z0-9][a-zA-Z0-9-]*)")


def split_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end < 0:
        return {}, text
    raw = text[4:end]
    body_start = text.find("\n", end + 1)
    body = text[body_start + 1:] if body_start >= 0 else ""
    return yaml.safe_load(raw) or {}, body


def allowed_tools(meta: dict) -> set[str]:
    raw = meta.get("allowed-tools", meta.get("tools", []))
    if isinstance(raw, str):
        return {x for x in re.split(r"[\s,]+", raw) if x}
    if isinstance(raw, list):
        return {str(x) for x in raw}
    return set()


def script_options(path: Path) -> set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    except (OSError, SyntaxError):
        return set()
    options: set[str] = set()
    for node in ast.walk(tree):
        if (
            not isinstance(node, ast.Call)
            or not isinstance(node.func, ast.Attribute)
            or node.func.attr != "add_argument"
        ):
            continue
        current: list[str] = []
        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str) and arg.value.startswith("-"):
                current.append(arg.value)
                options.add(arg.value)
        action = next((kw.value for kw in node.keywords if kw.arg == "action"), None)
        if isinstance(action, ast.Attribute) and action.attr == "BooleanOptionalAction":
            for opt in current:
                if opt.startswith("--") and not opt.startswith("--no-"):
                    options.add("--no-" + opt[2:])
    return options


def adjacent_duplicate_sentences(body: str) -> list[str]:
    plain = re.sub(r"```.*?```", " ", body, flags=re.S)
    sentences = [re.sub(r"\s+", " ", x).strip() for x in re.split(r"(?<=[.!?])\s+", plain)]
    return [b for a, b in zip(sentences, sentences[1:]) if len(b) >= 60 and a == b]


def consecutive_duplicate_paragraphs(body: str) -> list[str]:
    paragraphs: list[str] = []
    current: list[str] = []
    in_fence = False
    for line in body.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            if current:
                paragraphs.append(" ".join(current))
                current = []
            continue
        if in_fence or line.lstrip().startswith("|"):
            continue
        if not line.strip():
            if current:
                paragraphs.append(" ".join(current))
                current = []
            continue
        if line.startswith("#"):
            if current:
                paragraphs.append(" ".join(current))
                current = []
            continue
        current.append(line.strip())
    if current:
        paragraphs.append(" ".join(current))
    normalized = [re.sub(r"\s+", " ", p).strip() for p in paragraphs]
    return [b for a, b in zip(normalized, normalized[1:]) if len(b) >= 80 and a == b]


def audit() -> CheckResult:
    result = CheckResult("skills")
    skill_files = sorted(SKILLS_DIR.glob("*/SKILL.md")) if SKILLS_DIR.exists() else []
    agent_files = sorted(SUBAGENTS_DIR.glob("*.md")) if SUBAGENTS_DIR.exists() else []
    skill_names = {p.parent.name for p in skill_files}
    declared: Counter[str] = Counter()
    agents = {p.stem for p in agent_files}

    for path in skill_files + agent_files:
        rel = path.relative_to(CODE_ROOT)
        text = path.read_text(encoding="utf-8-sig")
        try:
            meta, body = split_frontmatter(text)
        except yaml.YAMLError as exc:
            result.error("FRONTMATTER_INVALID", str(exc), rel)
            continue
        name = str(meta.get("name", "")).strip()
        if not name:
            result.error("NAME_MISSING", "frontmatter must define name", rel)
        else:
            declared[name] += 1
            expected = path.parent.name if path.name == "SKILL.md" else path.stem
            if name != expected:
                result.error("NAME_PATH_MISMATCH", f"name '{name}' != path name '{expected}'", rel)

        duplicates = consecutive_duplicate_paragraphs(body) + adjacent_duplicate_sentences(body)
        for duplicate in dict.fromkeys(duplicates):
            result.error("DUPLICATE_RULE", f"consecutive duplicated rule: {duplicate[:120]}", rel)

        allowed = allowed_tools(meta)
        for tool in WEB_TOOLS:
            if re.search(rf"\b{re.escape(tool)}\b", body) and tool not in allowed:
                result.error(
                    "TOOL_NOT_ALLOWED",
                    f"body instructs use of {tool}, but frontmatter does not allow it",
                    rel,
                )

        for script in sorted(set(SCRIPT_REF_RE.findall(body))):
            if not (SCRIPTS_DIR / script).exists():
                result.error("SCRIPT_NOT_FOUND", f"referenced scripts/{script} does not exist", rel)

        for match in SLASH_REF_RE.finditer(body):
            ref = match.group(0)[1:]
            if ref in TOP_LEVEL_PATH_WORDS or ref in skill_names or ref in agents:
                continue
            # Unknown /fragments are too ambiguous to diagnose reliably:
            # paths, examples and prose commonly contain them. Known skills
            # are validated elsewhere by name/path and documentation coverage.

        for cmd in PY_COMMAND_RE.finditer(body):
            script, tail = cmd.group(1), cmd.group(2)
            spath = SCRIPTS_DIR / script
            if not spath.exists():
                continue
            known = script_options(spath)
            for flag in FLAG_RE.findall(tail):
                if flag not in known:
                    result.warning("CLI_FLAG_UNKNOWN", f"{script} is documented with unknown flag {flag}", rel)

    for name, count in declared.items():
        if count > 1:
            result.error("DUPLICATE_NAME", f"name '{name}' declared {count} times")

    agents_path = CODE_ROOT / "AGENTS.md"
    agents_md = agents_path.read_text(encoding="utf-8-sig", errors="replace") if agents_path.exists() else ""
    readme_path = CODE_ROOT / "README.md"
    readme = readme_path.read_text(encoding="utf-8-sig", errors="replace") if readme_path.exists() else ""
    for name in sorted(skill_names):
        if f"/{name}" not in agents_md and name != "conventions":
            result.error("SKILL_NOT_IN_AGENTS", f"/{name} is not documented in AGENTS.md")
        if f"/{name}" not in readme and name not in {"conventions", "doctor"}:
            result.warning("SKILL_NOT_IN_README", f"/{name} is not mentioned in README.md")

    result.meta.update(skills=len(skill_files), agents=len(agent_files))
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--fail-on-warning", action="store_true")
    args = ap.parse_args()
    result = audit()
    result.print(args.json)
    return result.exit_code(args.fail_on_warning)


if __name__ == "__main__":
    raise SystemExit(main())
