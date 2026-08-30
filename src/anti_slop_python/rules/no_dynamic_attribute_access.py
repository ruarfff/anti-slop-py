from __future__ import annotations

import ast
from collections.abc import Iterable

from anti_slop_python.diagnostics import Diagnostic
from anti_slop_python.rules.base import Rule, RuleContext

_DYNAMIC_ATTRIBUTE_FUNCTIONS = {
    "builtins.delattr",
    "builtins.getattr",
    "builtins.setattr",
    "delattr",
    "getattr",
    "setattr",
}


def _check(context: RuleContext) -> Iterable[Diagnostic]:
    for node in ast.walk(context.tree):
        if not isinstance(node, ast.Call):
            continue
        if context.qualified_name(node.func) in _DYNAMIC_ATTRIBUTE_FUNCTIONS:
            yield context.diagnostic(RULE, node)


RULE = Rule(
    code="SPY002",
    name="no-dynamic-attribute-access",
    message="Avoid dynamic attribute access",
    check=_check,
)
