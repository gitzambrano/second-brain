import json

from conftest import run_script


def test_quick_repository_gate():
    proc = run_script("check_repo.py", "--quick", "--json")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["errors"] == 0


def test_full_noarg_is_valid_on_skeleton_or_corpus():
    proc = run_script("check_repo.py", "--json")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["meta"]["mode"] == "full"
