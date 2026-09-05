from __future__ import annotations

from collections.abc import Iterable

from anti_slop_python.diagnostics import Diagnostic
from anti_slop_python.rules.base import Rule, RuleContext

MAX_MODULE_LINES = 500


def _check(context: RuleContext) -> Iterable[Diagnostic]:
    # Normalize Python line endings without treating Unicode separators or
    # form feeds inside strings and comments as additional source lines.
    source = context.source.replace("\r\n", "\n").replace("\r", "\n")
    lines = source.count("\n") + int(bool(source) and not source.endswith("\n"))
    if lines > MAX_MODULE_LINES:
        yield Diagnostic(
            path=context.path,
            line=1,
            column=1,
            code=RULE.code,
            message=f"{RULE.message} ({lines} > {MAX_MODULE_LINES})",
        )


RULE = Rule(
    code="SPY003",
    name="too-many-module-lines",
    message="Too many lines in module",
    check=_check,
)
