import json

from conftest import run_script


def test_site_gate_defers_browser_audit_unless_visual_is_requested(monkeypatch, tmp_path):
    import check_repo
    from sanity_common import CheckResult

    marker = tmp_path / ".second-brain-site"
    marker.write_text("site", encoding="utf-8")
    calls = []
    monkeypatch.setattr(check_repo, "SITE_ROOT", tmp_path)
    monkeypatch.setattr(check_repo, "corpus_has_essays", lambda: True)
    monkeypatch.setattr(
        check_repo,
        "run_status_command",
        lambda name, cmd, result: calls.append((name, cmd)),
    )

    check_repo.site(CheckResult("repository"), visual=False)
    assert "check_site_pages.py" not in [name for name, _ in calls]

    calls.clear()
    check_repo.site(CheckResult("repository"), visual=True)
    assert "check_site_pages.py" in [name for name, _ in calls]


def test_quick_repository_gate():
    proc = run_script("check_repo.py", "--quick", "--json")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["errors"] == 0


def test_full_noarg_is_valid_on_skeleton(tmp_path):
    data_root = tmp_path / "empty-brain"
    data_root.mkdir()
    proc = run_script("check_repo.py", "--json", data_root=data_root)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["meta"]["mode"] == "full"
