"""
Unit tests for :mod:`kivymd.tools.argument_parser`.
"""

import sys

import pytest

from kivymd.tools.argument_parser import ArgumentParserWithHelp


def _make_parser():
    parser = ArgumentParserWithHelp(
        prog="kivymd-tool", description="A tool used for testing."
    )
    subparsers = parser.add_subparsers(dest="command")
    hello = subparsers.add_parser("hello", help="Say hello.")
    hello.add_argument("name")
    return parser


def test_parse_args_valid():
    parser = _make_parser()
    namespace = parser.parse_args(["hello", "world"])
    assert namespace.command == "hello"
    assert namespace.name == "world"


def test_parse_args_no_arguments_prints_help_and_exits(capsys, monkeypatch):
    # The "no arguments" guard also checks sys.argv, so make it look empty.
    monkeypatch.setattr(sys, "argv", ["kivymd-tool"])
    parser = _make_parser()
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args([])
    # Exit code 1 is used when no arguments are given.
    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "A tool used for testing." in captured.out


def test_error_prints_full_help_and_exits(capsys):
    parser = _make_parser()
    with pytest.raises(SystemExit) as exc_info:
        # Unknown sub-command triggers ArgumentParser.error().
        parser.parse_args(["does-not-exist"])
    # Exit code 2 is used on argument errors.
    assert exc_info.value.code == 2
    captured = capsys.readouterr()
    assert "Error:" in captured.err


def test_format_help_contains_usage_and_subparsers():
    parser = _make_parser()
    help_text = parser.format_help()
    assert "Usage:" in help_text
    assert "A tool used for testing." in help_text
    # The sub-command name is listed in the help output.
    assert "hello" in help_text


def test_format_help_with_epilog():
    parser = ArgumentParserWithHelp(
        prog="kivymd-tool",
        description="Desc.",
        epilog="Some epilog text.",
    )
    parser.add_subparsers(dest="command")
    help_text = parser.format_help()
    assert "Some epilog text." in help_text
