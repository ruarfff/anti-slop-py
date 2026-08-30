from __future__ import annotations

from anti_slop_python import check_source


def test_reports_multiple_violations_in_source_order() -> None:
    source = (
        "from typing import Any\n"
        "payload: dict[str, Any] = {}\n"
        'getattr(payload, "name")\n'
    )

    diagnostics = check_source(source, "example.py")

    assert [item.code for item in diagnostics] == ["SPY001", "SPY002"]


def test_reports_syntax_error_without_crashing() -> None:
    diagnostics = check_source("def broken(:\n", "broken.py")

    assert len(diagnostics) == 1
    assert diagnostics[0].code == "SyntaxError"
    assert diagnostics[0].line == 1
