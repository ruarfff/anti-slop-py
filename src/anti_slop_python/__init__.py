"""Opinionated checks for Python patterns that weaken code evidence."""

from anti_slop_python.checker import check_file, check_source
from anti_slop_python.diagnostics import Diagnostic

__all__ = ["Diagnostic", "check_file", "check_source"]
