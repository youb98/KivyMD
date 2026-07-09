"""
Unit tests for :mod:`kivymd.tools.release.git_commands`.

``subprocess`` and ``input`` are patched so no real git commands run.
"""

import subprocess

import pytest

from kivymd.tools.release import git_commands


def test_command_capture_output(monkeypatch):
    calls = {}

    def fake_check_output(cmd):
        calls["cmd"] = cmd
        return b"output line\n"

    monkeypatch.setattr(subprocess, "check_output", fake_check_output)
    result = git_commands.command(["git", "status"], capture_output=True)
    assert result == "output line\n"
    assert calls["cmd"] == ["git", "status"]


def test_command_without_capture(monkeypatch):
    calls = {}

    def fake_check_call(cmd):
        calls["cmd"] = cmd
        return 0

    monkeypatch.setattr(subprocess, "check_call", fake_check_call)
    result = git_commands.command(["git", "status"])
    assert result == ""
    assert calls["cmd"] == ["git", "status"]


def test_get_previous_version(monkeypatch):
    outputs = iter(["", "1.1.1\n"])
    recorded = []

    def fake_command(cmd, capture_output=False):
        recorded.append(cmd)
        return next(outputs)

    monkeypatch.setattr(git_commands, "command", fake_command)
    version = git_commands.get_previous_version()
    # Trailing newline is stripped from the tag.
    assert version == "1.1.1"
    assert recorded[0] == ["git", "checkout", "master"]


def test_git_tag(monkeypatch):
    recorded = []
    monkeypatch.setattr(
        git_commands,
        "command",
        lambda cmd, capture_output=False: recorded.append(cmd) or "",
    )
    git_commands.git_tag("2.0.0")
    assert recorded == [["git", "tag", "2.0.0"]]


def test_git_commit_default_add_all(monkeypatch):
    recorded = []
    monkeypatch.setattr(
        git_commands,
        "command",
        lambda cmd, capture_output=False: recorded.append(cmd) or "",
    )
    git_commands.git_commit("my message")
    assert recorded[0] == ["git", "add", "-A"]
    assert recorded[1] == ["git", "commit", "--all", "-m", "my message"]


def test_git_commit_custom_files(monkeypatch):
    recorded = []
    monkeypatch.setattr(
        git_commands,
        "command",
        lambda cmd, capture_output=False: recorded.append(cmd) or "",
    )
    git_commands.git_commit("msg", add_files=["a.py", "b.py"])
    assert recorded[0] == ["git", "add", "a.py", "b.py"]


def test_git_commit_reraises_when_not_allowed(monkeypatch):
    def fake_command(cmd, capture_output=False):
        if cmd[:2] == ["git", "commit"]:
            raise subprocess.CalledProcessError(1, cmd)
        return ""

    monkeypatch.setattr(git_commands, "command", fake_command)
    with pytest.raises(subprocess.CalledProcessError):
        git_commands.git_commit("msg")


def test_git_commit_swallows_error_when_allowed(monkeypatch):
    def fake_command(cmd, capture_output=False):
        if cmd[:2] == ["git", "commit"]:
            raise subprocess.CalledProcessError(1, cmd)
        return ""

    monkeypatch.setattr(git_commands, "command", fake_command)
    # Should not raise.
    git_commands.git_commit("msg", allow_error=True)


def test_git_push_without_pushing(monkeypatch):
    recorded = []
    monkeypatch.setattr(
        git_commands,
        "command",
        lambda cmd, capture_output=False: recorded.append(cmd) or "",
    )
    git_commands.git_push(["dev"], ask=False, push=False)
    # Nothing is executed when push is disabled.
    assert recorded == []


def test_git_push_with_pushing(monkeypatch):
    recorded = []
    monkeypatch.setattr(
        git_commands,
        "command",
        lambda cmd, capture_output=False: recorded.append(cmd) or "",
    )
    git_commands.git_push(["dev"], ask=False, push=True)
    assert recorded == [["git", "push", "--tags", "origin", "master", "dev"]]


def test_git_push_ask_yes(monkeypatch):
    recorded = []
    monkeypatch.setattr("builtins.input", lambda *a, **k: "y")
    monkeypatch.setattr(
        git_commands,
        "command",
        lambda cmd, capture_output=False: recorded.append(cmd) or "",
    )
    git_commands.git_push([], ask=True)
    assert recorded == [["git", "push", "--tags", "origin", "master"]]


def test_git_clean_no_files(monkeypatch):
    recorded = []

    def fake_command(cmd, capture_output=False):
        recorded.append(cmd)
        return ""

    monkeypatch.setattr(git_commands, "command", fake_command)
    git_commands.git_clean(ask=True)
    # Dry-run returns nothing, so no prompt; clean + reset still run.
    assert ["git", "clean", "-dx", "--force"] in recorded
    assert ["git", "reset", "--hard"] in recorded
