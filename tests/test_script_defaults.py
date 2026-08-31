import json

from conftest import run_script


def test_every_executable_python_script_has_noarg_default():
    proc = run_script("check_script_defaults.py", "--json")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["errors"] == 0


def test_legacy_parameter_tools_have_safe_empty_defaults():
    for script in ("retag.py", "find_text.py", "check_title.py", "mermaid_to_png.py"):
        proc = run_script(script)
        assert proc.returncode in (0, 2), f"{script}: {proc.stdout}\n{proc.stderr}"
        # check_title uses 2 when a real corpus already contains fuzzy collisions;
        # the important contract is that argparse does not abort for missing args.
        assert "required" not in proc.stderr.lower()
