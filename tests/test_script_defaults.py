import json
import warnings
from pathlib import Path

from conftest import run_script

ROOT = Path(__file__).resolve().parents[1]


def test_every_executable_python_script_has_noarg_default():
    proc = run_script("check_script_defaults.py", "--json")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["errors"] == 0
    assert payload["meta"]["scripts_scanned"] >= payload["meta"]["executables"] > 0


def test_script_catalog_has_no_missing_documented_files():
    proc = run_script("check_script_defaults.py", "--json")
    payload = json.loads(proc.stdout)
    stale = [i for i in payload["issues"] if i["code"] == "SCRIPT_DOC_STALE"]
    assert not stale, stale


def test_scripts_compile_without_syntax_warnings():
    scripts = sorted((ROOT / "scripts").glob("*.py"))
    assert scripts
    with warnings.catch_warnings():
        warnings.simplefilter("error", SyntaxWarning)
        for path in scripts:
            source = path.read_text(encoding="utf-8-sig")
            compile(source, str(path), "exec")


def test_legacy_parameter_tools_have_safe_empty_defaults():
    for script in ("retag.py", "find_text.py", "check_title.py", "mermaid_to_png.py"):
        proc = run_script(script)
        assert proc.returncode in (0, 2), f"{script}: {proc.stdout}\n{proc.stderr}"
        assert "required" not in proc.stderr.lower()
