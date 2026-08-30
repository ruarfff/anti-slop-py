# Basic rule demonstration

This small project demonstrates the current `anti-slop-python` policy. The
`violations.py` module contains an intentional violation of each native or
Ruff-backed rule. The `preferred.py` module shows a clearer alternative. Its
`pyproject.toml` does not repeat the policy because `anti-slop-python` supplies the
defaults.

| Code | Demonstration |
| --- | --- |
| `SPY001` | Replace a container of `Any` with a specific element type |
| `SPY002` | Replace dynamic attribute access with direct access |
| `C901` | Replace a complex decision chain with data |
| `PLR0915` | Replace a long sequence of statements with one operation |
| `TID251` | Replace runtime patching with dependency injection |
| `E722` | Replace a bare exception handler with a specific exception |
| `BLE001` | Replace `except Exception` with a specific exception |

From the repository root, scan the project explicitly:

```console
$ uv run anti-slop-python examples/basic_project
```

The command reports all seven codes from `violations.py` and exits with status
1. `preferred.py` produces no diagnostics:

```console
$ uv run anti-slop-python examples/basic_project/src/example_project/preferred.py
```

The root project excludes `examples/` from Ruff and pre-commit checks because
these violations are intentional. Its direct self-check targets `src` and
`tests`.
