from anti_slop_python.rules.base import Rule
from anti_slop_python.rules.no_any_containers import RULE as NO_ANY_CONTAINERS
from anti_slop_python.rules.no_dynamic_attribute_access import (
    RULE as NO_DYNAMIC_ATTRIBUTE_ACCESS,
)

RULES: tuple[Rule, ...] = (
    NO_ANY_CONTAINERS,
    NO_DYNAMIC_ATTRIBUTE_ACCESS,
)

__all__ = ["RULES", "Rule"]
