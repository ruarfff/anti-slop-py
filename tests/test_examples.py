from __future__ import annotations

from pathlib import Path

from anti_slop_python.cli import main

REPOSITORY_ROOT = Path(__file__).parents[1]
EXAMPLE_ROOT = REPOSITORY_ROOT / "examples" / "basic_project"


def test_basic_example_demonstrates_every_policy_rule(capsys) -> None:
    exit_code = main([str(EXAMPLE_ROOT)])
    captured = capsys.readouterr()

    codes = {line.split()[1] for line in captured.out.splitlines()}

    assert exit_code == 1
    assert len(captured.out.splitlines()) == 7
    assert codes == {"SPY001", "SPY002", "BLE001", "C901", "E722", "PLR0915", "TID251"}
    assert captured.err == ""


def test_basic_example_preferred_design_passes(capsys) -> None:
    preferred = EXAMPLE_ROOT / "src" / "example_project" / "preferred.py"

    exit_code = main([str(preferred)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.out == ""
    assert captured.err == ""
