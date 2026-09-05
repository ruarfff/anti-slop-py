# Coding-agent refactoring trial

This trial checks whether a smaller coding agent can use the `SPY003` diagnostic
to refactor the order-report example while preserving its behavior.

## Setup

- Date: 2026-09-05.
- Agent: `gpt-5.6-luna`, medium reasoning.
- The agent started without the parent conversation history.
- The original `src/example_project/order_report.py` remained at its existing path.
- The agent received an identical copy in `src/example_project/order_report_refactored/`.
- The agent could edit only that copied directory. The linter and configuration
  were outside its assigned scope.
- The parent prepared independent regression checks in
  `tests/test_order_report_refactoring.py` at the repository root.

The original file has 554 physical lines and this SHA-256 digest:

```text
29d3ce2a3d1263a2976222833704050da85b22a2e66b733c35ee5f8d8f8ac223
```

## Agent prompt

The following is the task prompt, with the local checkout path replaced by
`<repository-root>`. The runtime also supplied its common system and developer
instructions. The agent received no proposed module layout from the parent.

> Work in <repository-root>. Refactor the order-report example by following anti-slop-python's diagnostic guidance. First run `UV_CACHE_DIR=/tmp/anti-slop-python-uv-cache uv run anti-slop-python examples/basic_project/src/example_project/order_report.py` and read its output. The original file must remain unchanged. An identical copy is ready at examples/basic_project/src/example_project/order_report_refactored/order_report.py. Make all changes inside the order_report_refactored directory, including any new modules. Keep its order_report.py as the public import and direct-script entry point; preserve the original public functions, types, constants, CLI options, and behavior. Run anti-slop-python over the entire refactored directory until it passes. Verify behavior against the original. Do not modify linter code, configuration, exclusions, or thresholds. Do not commit or push. Read applicable AGENTS.md instructions. Use the installed uv environment; `uv run python -m pytest` works if the pytest executable is unavailable. Report the initial diagnostic, your module layout, checks performed, and any limitations. This is a single-agent trial; do not spawn further agents.

## Evaluation

A successful result must pass the linter across every extracted module. The
parent also compares the original and refactored versions for:

- Demo stdout and all four exported files, byte for byte.
- CSV input with rounding, discounts, shipping thresholds, ordering, stock
  shortages, multiple customers, and empty orders.
- Invalid quantities, references, dates, shipping methods, amounts, duplicate
  records, and the order of validation failures.
- CLI help, argument errors, public callable parameters and annotation presence,
  constants, and demo data values.
- Preservation of the original file by its SHA-256 digest.

Passing the checks is separate from the design review. That review looks for
cohesive responsibilities, clear imports, and attempts to satisfy the line limit
through compression or weakened contracts.

## First completion and review

The agent separated models, parsing, pricing, inventory, report aggregation,
presentation, exports, and demo data. `order_report.py` became a CLI and public
import facade. All nine files were under 500 lines, with no rule suppressions
or threshold changes.

The parent tests were available in the shared checkout during the agent's run.
They were independently written, but were not withheld. The agent reported that
they caught missing facade exports and constants, plus a changed validation
order. It fixed those failures before its first completion. The first completed
candidate passed all 28 regression cases and the linter.

The parent's design review found remaining defects that those checks missed:

- Five public functions had lost parameter and return annotations:
  `format_money`, `render_invoice_header`, `render_invoice_lines`,
  `render_invoice_totals`, and `load_report`.
- Several explicit keyword constructors had become positional calls;
  `parse_customer` used a generator unpack. These rewrites were unnecessary
  for separating responsibilities and made the field mapping less clear.
- Some explicit local collection annotations were removed.

The parent added an annotation-preservation assertion, verified that it failed,
and asked the same agent to restore annotations and the original keyword
arguments while keeping its module boundaries. The parent did not edit the
refactored implementation. This was a review repair, not a success achieved by
diagnostic guidance alone.

## Final result

The same agent completed the review repair. The parent then reran the checks:

- All 140 repository tests passed, including the 28 refactoring cases with the
  new annotation-preservation assertion.
- The whole refactored directory passed `anti-slop-python` with exit code 0
  and no output.
- Repository Ruff checks, the source/test self-check, and formatting checks
  passed. The refactored files also passed an explicit formatting check because
  the root project excludes examples.
- The original SHA-256 digest was unchanged.
- A static check of the relative imports found no dependency cycles.

| Module | Lines | Responsibility |
| --- | ---: | --- |
| `order_report.py` | 155 | Public API exports and CLI |
| `parsing.py` | 129 | CSV loading and validation |
| `exports.py` | 83 | Text, CSV, and JSON file export |
| `models.py` | 73 | Shared record types |
| `presentation.py` | 71 | Text rendering |
| `pricing.py` | 70 | Invoice calculations |
| `reporting.py` | 65 | Workflow and aggregate totals |
| `demo.py` | 53 | Sample data |
| `inventory.py` | 23 | Stock requests and shortages |

The split follows responsibilities and uses explicit imports. Total source
length grew from 554 to 722 lines, mainly from imports and the compatibility
facade. The result passes because each module has a smaller scope, rather than
because the agent removed enough source lines.

This is evidence that a smaller model can use the guidance with regression tests
and review. The first completion also exposed a gap: the guidance should make
preservation of type annotations and avoidance of unrelated rewrites explicit.
The linter's guidance was not changed during this trial.

After the trial, version `0.2.0` added Ruff's annotation rules to the default
policy. Missing function annotations now fail the linter directly. The test
counts and results above describe the policy at the time of the trial.

Reproduce the final checks from the repository root:

```console
uv run anti-slop-python examples/basic_project/src/example_project/order_report_refactored
uv run python -m pytest tests/test_order_report_refactoring.py
uv run python examples/basic_project/src/example_project/order_report_refactored/order_report.py --demo
```

## Limits

This is one guided trial, without a comparison run that omits the guidance.
It can demonstrate that this agent followed the guidance on this example; it
cannot establish that the guidance caused the result or that agents will
reliably follow it on other projects. The starting module already has section
comments that identify its responsibilities. The regression cases cover selected
behavior, not every possible input or external caller.
