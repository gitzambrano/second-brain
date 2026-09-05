from __future__ import annotations

from types import SimpleNamespace

import close_workspace


def test_no_subcommand_defaults_to_prepare(monkeypatch):
    called = []
    monkeypatch.setattr(close_workspace, "prepare", lambda: called.append("prepare"))
    assert close_workspace.main([]) == 0
    assert called == ["prepare"]


def test_commit_runs_prepare_before_commits(monkeypatch):
    called = []
    monkeypatch.setattr(close_workspace, "prepare", lambda: called.append("prepare"))
    monkeypatch.setattr(close_workspace, "_require_git_repo", lambda root, label: called.append(f"repo:{label}"))
    monkeypatch.setattr(close_workspace, "_commit_repo", lambda root, message: called.append((root, message)))
    monkeypatch.setattr(close_workspace, "_git", lambda *args, **kwargs: SimpleNamespace(returncode=0))

    close_workspace.commit("update: teste")

    assert called[0] == "prepare"
    assert called[1:3] == ["repo:data", "repo:engine"]
    assert called[3][1] == "update: teste"
    assert called[4][1] == "update: teste"


def test_push_checks_both_worktrees_before_any_push(monkeypatch):
    called = []
    monkeypatch.setattr(close_workspace, "_require_git_repo", lambda root, label: called.append(f"repo:{label}"))
    monkeypatch.setattr(close_workspace, "_require_clean", lambda root, label: called.append(f"clean:{label}"))
    monkeypatch.setattr(
        close_workspace,
        "_git",
        lambda root, *args, **kwargs: called.append((root, args)) or SimpleNamespace(returncode=0),
    )

    close_workspace.push()

    assert called[:4] == ["repo:data", "repo:engine", "clean:data", "clean:engine"]
    pushes = [item for item in called if isinstance(item, tuple)]
    assert len(pushes) == 2
    assert all(item[1] == ("push", "origin", "HEAD") for item in pushes)


def test_push_attempts_engine_even_if_data_push_fails(monkeypatch):
    attempts = []
    monkeypatch.setattr(close_workspace, "_require_git_repo", lambda *args: None)
    monkeypatch.setattr(close_workspace, "_require_clean", lambda *args: None)

    def fake_git(root, *args, **kwargs):
        attempts.append(root)
        return SimpleNamespace(returncode=1 if len(attempts) == 1 else 0)

    monkeypatch.setattr(close_workspace, "_git", fake_git)

    try:
        close_workspace.push()
    except close_workspace.CloseError:
        pass
    else:
        raise AssertionError("push parcial deve falhar")

    assert attempts == [close_workspace.DATA_ROOT, close_workspace.CODE_ROOT]
