from __future__ import annotations

import pytest

from anti_slop_python import check_source


@pytest.mark.parametrize("function", ["getattr", "setattr", "delattr"])
def test_reports_dynamic_attribute_access(function: str) -> None:
    diagnostics = check_source(f"{function}(target, name)\n")

    assert [diagnostic.code for diagnostic in diagnostics] == ["SPY002"]


def test_accepts_static_attribute_access() -> None:
    assert check_source("target.name\n") == []


def test_accepts_same_method_name() -> None:
    assert check_source("registry.getattr(target, name)\n") == []


def test_reports_builtins_attribute_access() -> None:
    diagnostics = check_source('import builtins\nbuiltins.getattr(target, "name")\n')

    assert [diagnostic.code for diagnostic in diagnostics] == ["SPY002"]


def test_reports_aliased_builtin_import() -> None:
    diagnostics = check_source(
        "from builtins import getattr as read_attribute\n"
        'read_attribute(target, "name")\n'
    )

    assert [diagnostic.code for diagnostic in diagnostics] == ["SPY002"]


def test_accepts_imported_function_with_same_name() -> None:
    assert check_source('from custom import getattr\ngetattr(target, "name")\n') == []


def test_accepts_relative_imported_function_with_same_name() -> None:
    assert check_source('from . import getattr\ngetattr(target, "name")\n') == []
    assert check_source('from ..utils import getattr\ngetattr(target, "name")\n') == []
    assert (
        check_source('from .module import setattr\nsetattr(target, "name", 1)\n') == []
    )
