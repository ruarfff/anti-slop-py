from __future__ import annotations

import ast
from collections.abc import Iterable

from anti_slop_python.diagnostics import Diagnostic
from anti_slop_python.rules.base import Rule, RuleContext

_CONTAINERS = {
    "dict",
    "list",
    "set",
    "tuple",
    "typing.Dict",
    "typing.List",
    "typing.Set",
    "typing.Tuple",
    "typing_extensions.Dict",
    "typing_extensions.List",
    "typing_extensions.Set",
    "typing_extensions.Tuple",
}
_ANY_NAMES = {"Any", "typing.Any", "typing_extensions.Any"}


def _check(context: RuleContext) -> Iterable[Diagnostic]:
    for node in ast.walk(context.tree):
        if not isinstance(node, ast.Subscript):
            continue
        if context.qualified_name(node.value) not in _CONTAINERS:
            continue
        if _contains_any(context, node.slice):
            yield context.diagnostic(RULE, node)


def _contains_any(context: RuleContext, node: ast.AST) -> bool:
    if (
        isinstance(node, ast.Subscript)
        and context.qualified_name(node.value) in _CONTAINERS
    ):
        return False
    if (
        isinstance(node, (ast.Name, ast.Attribute))
        and context.qualified_name(node) in _ANY_NAMES
    ):
        return True
    return any(_contains_any(context, child) for child in ast.iter_child_nodes(node))


RULE = Rule(
    code="SPY001",
    name="no-any-containers",
    message="Avoid containers parameterized with Any",
    check=_check,
)
