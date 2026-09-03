#!/usr/bin/env python3
"""
Modelo compartilhado de resultado dos checadores de sanidade do repositório.

Default sem argumentos: imprimir o vocabulário de severidade e o contrato de
código de saída.
"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


def _safe_print(*args, **kwargs) -> None:
    """Print with UTF-8 fallback on Windows cp1252 terminals."""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # Encode to UTF-8 bytes, decode back replacing unmappable chars.
        text = " ".join(str(a) for a in args)
        safe = text.encode(sys.stdout.encoding or "utf-8", errors="replace").decode(
            sys.stdout.encoding or "utf-8", errors="replace"
        )
        print(safe, **{k: v for k, v in kwargs.items() if k != "end"})

SEVERITIES = ("ERROR", "WARNING", "INFO", "SKIP")


def text_contains(haystack_norm: str, needle_norm: str) -> bool:
    """Presence test tolerant of typographic letter-spacing.

    The PDF template tracks section headings and the byline ("S U M A R I O"),
    so text extraction returns a space between every glyph and a plain substring
    test reports the heading as missing. Falling back to a space-free comparison
    keeps the check honest without weakening it: absent text is still absent.
    """
    if not needle_norm:
        return True
    if needle_norm in haystack_norm:
        return True
    return needle_norm.replace(" ", "") in haystack_norm.replace(" ", "")


@dataclass(slots=True)
class Issue:
    code: str
    severity: str
    message: str
    path: str | None = None
    line: int | None = None
    details: Any = None

    def __post_init__(self) -> None:
        self.severity = self.severity.upper()
        if self.severity not in SEVERITIES:
            raise ValueError(f"invalid severity: {self.severity}")


@dataclass
class CheckResult:
    check: str
    issues: list[Issue] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)

    def add(self, code: str, severity: str, message: str, path: str | Path | None = None,
            line: int | None = None, details: Any = None) -> None:
        self.issues.append(Issue(code, severity, message, str(path) if path else None, line, details))

    def error(self, code: str, message: str, path: str | Path | None = None, **kw: Any) -> None:
        self.add(code, "ERROR", message, path, **kw)

    def warning(self, code: str, message: str, path: str | Path | None = None, **kw: Any) -> None:
        self.add(code, "WARNING", message, path, **kw)

    def info(self, code: str, message: str, path: str | Path | None = None, **kw: Any) -> None:
        self.add(code, "INFO", message, path, **kw)

    def skip(self, code: str, message: str, path: str | Path | None = None, **kw: Any) -> None:
        self.add(code, "SKIP", message, path, **kw)

    def count(self, severity: str) -> int:
        return sum(i.severity == severity.upper() for i in self.issues)

    @property
    def status(self) -> str:
        if self.count("ERROR"):
            return "fail"
        if self.count("WARNING"):
            return "warn"
        if self.issues and all(i.severity == "SKIP" for i in self.issues):
            return "skip"
        return "pass"

    def exit_code(self, fail_on_warning: bool = False) -> int:
        if self.count("ERROR") or (fail_on_warning and self.count("WARNING")):
            return 1
        return 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "check": self.check,
            "status": self.status,
            "errors": self.count("ERROR"),
            "warnings": self.count("WARNING"),
            "info": self.count("INFO"),
            "skipped": self.count("SKIP"),
            "issues": [asdict(i) for i in self.issues],
            "meta": self.meta,
        }

    def print(self, json_mode: bool = False) -> None:
        if json_mode:
            _safe_print(json.dumps(self.to_dict(), ensure_ascii=False, indent=2))
            return
        _safe_print(f"{self.check}: {self.status.upper()} — {self.count('ERROR')} error(s), "
              f"{self.count('WARNING')} warning(s), {self.count('SKIP')} skip(s)")
        for issue in self.issues:
            where = f" [{issue.path}" if issue.path else ""
            if issue.line is not None:
                where += f":{issue.line}"
            if where:
                where += "]"
            _safe_print(f"  {issue.severity:<7} {issue.code}{where}: {issue.message}")


def main() -> int:
    print("severities: ERROR WARNING INFO SKIP")
    print("exit codes: 0=clean/warnings-only, 1=blocking issue, 2=checker execution/configuration failure")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
