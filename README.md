# anti-slop-python

[![skills.sh](https://skills.sh/b/ruarfff/anti-slop-python)](https://skills.sh/ruarfff/anti-slop-python)

`anti-slop-python` is a small, opinionated architectural
linter for Python inspired by and largely copied from
[dmmulroy/anti-slop](https://github.com/dmmulroy/anti-slop).

It requires [ruff](https://github.com/astral-sh/ruff) so it is not a standalone linter.

`anti-slop-python` does not attempt to determine whether code was written by a human
or an agent. It rejects patterns that weaken evidence about types, invariants,
boundaries, and dependencies.

It also catches very common issues when using LLMs to generate Python code like functions
and files getting way too big.

## Setup

### Install it using the agent skill

The repository includes `install-anti-slop-python`, an Agent Skill that
installs and configures anti-slop-python in a target Python repository.

The [`skills` CLI](https://github.com/vercel-labs/skills) supports project and
global installs for many coding agents.

```bash
# Install interactively for the current project
npx skills add ruarfff/anti-slop-python --skill install-anti-slop-python
```

Make the skill available everywhere on your system:

```bash
npx skills add ruarfff/anti-slop-python --skill install-anti-slop-python --agent '*' --global --yes
```

See the [`skills` CLI documentation](https://github.com/vercel-labs/skills#supported-agents).

### Install it with pre-commit

This repository applies `anti-slop-python` to itself through the local hook in
`.pre-commit-config.yaml`.

The repository includes hook metadata. Add this entry to
`.pre-commit-config.yaml` and replace the revision with the release to use:

```yaml
repos:
  - repo: https://github.com/ruarfff/anti-slop-python
    rev: v0.1.0
    hooks:
      - id: anti-slop-python
```

Run against an entire project:

```bash
uv run pre-commit run anti-slop-python --all-files
```

#### Adopt it for selected directories

Use pre-commit's `files` regular expression to limit the hook to selected
parts of a project:

```yaml
repos:
  - repo: https://github.com/ruarfff/anti-slop-python
    rev: v0.1.0
    hooks:
      - id: anti-slop-python
        files: ^(?:src/a-specific-module/|tests/tests-for-that-module/)
```

Useful if you want to gradually introduce `anti-slop-python` to a project.

Expand the `files` expression as more directories adopt the policy.
This does not override the project's Ruff configuration for files outside the selected directories.

## Rules

Native `anti-slop-python` rules cover some checks that Ruff does not provide:

| Rule | Name | Rejected pattern |
| --- | --- | --- |
| SPY001 | `no-any-containers` | `dict`, `list`, `set`, or `tuple` parameterized with `Any` (including their `typing` aliases) |
| SPY002 | `no-dynamic-attribute-access` | Calls to `getattr()`, `setattr()`, or `delattr()` |

### Ruff-backed policy

`anti-slop-python` uses Ruff for checks that Ruff already provides. It enables this
policy by default:

| Rule | Default policy |
| --- | --- |
| [`C901`](https://docs.astral.sh/ruff/rules/complex-structure/) | Cyclomatic complexity of at most 10 |
| [`PLR0915`](https://docs.astral.sh/ruff/rules/too-many-statements/) | At most 40 statements per function or method |
| [`TID251`](https://docs.astral.sh/ruff/rules/banned-api/) | Ban `unittest.mock.patch` and `mock.patch` |
| [`E722`](https://docs.astral.sh/ruff/rules/bare-except/) | Reject bare exception handlers |
| [`BLE001`](https://docs.astral.sh/ruff/rules/blind-except/) | Reject broad exception handlers |

No Ruff configuration is required when you run `anti-slop-python`. Its defaults are
equivalent to:

```toml
[tool.ruff.lint]
extend-select = ["BLE001", "C901", "E722", "PLR0915", "TID251"]

[tool.ruff.lint.mccabe]
max-complexity = 10

[tool.ruff.lint.pylint]
max-statements = 40

[tool.ruff.lint.flake8-tidy-imports.banned-api]
"mock.patch".msg = "Avoid patching state. Pass the dependency explicitly instead."
"unittest.mock.patch".msg = "Avoid patching state. Pass the dependency explicitly instead."
```

Project Ruff settings remain authoritative. Use them only when the project
must change or extend the defaults. For example:

```toml
[tool.ruff.lint]
extend-ignore = ["C901"]

[tool.ruff.lint.pylint]
max-statements = 50
```

`ignore` and `extend-ignore` disable default rules. Explicit thresholds,
exclusions, per-file ignores, and `noqa` comments also apply.

If the project defines the `TID251` banned-API table, it replaces the default
provided by `anti-slop-python`.

Inline `noqa` comments can suppress a recommended Ruff diagnostic, so
`anti-slop-python` audits them and prints a non-failing policy notice with the
source location. Ruff exclusions apply to Ruff-backed checks. Native SPY rules
still check every Python file in the paths passed to `anti-slop-python`; use the
command paths or pre-commit `files`/`exclude` settings to control that scope.

When an override is weaker than the default policy, `anti-slop-python` prints a
non-failing policy notice. Stricter settings do not produce a notice. The
defaults apply only to Ruff runs started by `anti-slop-python`; add the equivalent
configuration above if a separate `ruff check` command must enforce the same
policy.

## Why these rules exist

These rules do not identify whether an LLM wrote the code. Humans produce the
same patterns.

The rules here are an opinionated set of guidelines that cover common issues
with LLM generated code and are an attempt to reduce the review burden.

An agent can add a large amount of locally plausible code without first "learning" the
project's types, boundaries, or dependency design. The rules help against some common
shortcuts LLMs use to make code fulfill an immediate goal while making later changes
harder to reason about.

The rules also try to encourage better design by pushing back on the most annoying
things LLMs tend to do like writing massive functions, files with thousands of lines,
tests that patch and mock everything, etc.

The following are some example rules and why they were added:

### SPY001 — Do not put `Any` in containers

`SPY001` rejects `dict`, `list`, `set`, and `tuple` types parameterized with
`Any`, including the equivalent aliases from `typing`. A container usually
carries data across several lines, functions, or layers. Once its element type
becomes `Any`, every value taken from it escapes useful static checking and can
spread uncertainty through the rest of the program.

An agent often introduces this pattern when it can see that a value is a list
or dictionary but has not established the shape of the contents. `Any` makes
the immediate type error disappear without resolving that missing knowledge.
The rule forces the implementation to name the real type. A burden you probably
wouldn't always want for yourself but an LLM can deal with it and maybe produce
better code because of it.

Ruff's [`ANN401`](https://docs.astral.sh/ruff/rules/any-type/) rule is related
but does not replace `SPY001`: `ANN401` checks function parameters annotated
directly with `Any`, while `SPY001` checks for `Any` inside container types such
as `list[Any]` and `dict[str, Any]`.

### SPY002 — Do not hide attributes behind strings

`SPY002` rejects calls to `getattr()`, `setattr()`, and `delattr()`. Dynamic
attribute access turns an interface into a runtime string convention. Type
checkers and refactoring tools have less evidence, misspelled names fail late,
and a default passed to `getattr()` can hide a missing invariant.

Generated code often uses `getattr(value, "name", None)` to support several
assumed object shapes without checking which shapes the application actually
allows. The rule requires direct attribute access for a known interface.

Ruff has related [`B009`](https://docs.astral.sh/ruff/rules/get-attr-with-constant/),
[`B010`](https://docs.astral.sh/ruff/rules/set-attr-with-constant/), and
preview-only [`B043`](https://docs.astral.sh/ruff/rules/del-attr-with-constant/)
rules. They flag `getattr()`, `setattr()`, and `delattr()` only when the
attribute name is a constant string. They therefore allow calls such as
`getattr(value, name)`, which may be intentional but still make an interface
depend on runtime strings. `SPY002` rejects
the built-ins regardless of whether the name is constant.

### [`C901`](https://docs.astral.sh/ruff/rules/complex-structure/) — Limit decision complexity

`C901` measures the number of paths through a function. Anti-slop-python uses a
maximum McCabe complexity of 10. A function can be short and still be complex
when it contains many branches, loops, or exception paths. Each added path
increases the number of states that a reader and a test suite must consider.

Coding agents tend to tack on more complexity to achieve a goal like making tests pass.

### [`PLR0915`](https://docs.astral.sh/ruff/rules/too-many-statements/) — Limit function size

`PLR0915` rejects functions or methods with more than 40 statements. This
complements `C901`: a long function can have simple control flow and still do
too much. 

Generated implementations tend to keep the full requested workflow in one
function because that is the easiest shape to produce in one pass. The
statement limit makes things like mixed responsibilities more visible. 

### [`TID251`](https://docs.astral.sh/ruff/rules/banned-api/) — Do not patch dependencies

Ruff's `TID251` rule can ban project-selected APIs. Anti-slop-python uses it to ban
`unittest.mock.patch` and `mock.patch`. Patching replaces module or object
state at runtime, so a test depends on where a symbol happens to be imported
rather than on an explicit interface. Refactoring an import can then break the
test even when behavior has not changed.

Agents frequently reach for `patch()` because it can isolate almost any call
without changing production design. There's a tendency to test implementation rather than behavior
when trying to improve test coverage.

This setting helps a little with directing a clearer interface-based design, although it is generally 
not enough by itself and LLMs need a lot of direction to get to this kind of design.

### [`E722`](https://docs.astral.sh/ruff/rules/bare-except/) — Do not use bare exception handlers

`E722` rejects a bare `except:` handler. A bare handler catches
`BaseException`, including `KeyboardInterrupt` and `SystemExit`. It can prevent
a process from stopping and can disguise failures that the code cannot
actually recover from.

LLMs tend to be good at building exception handling but occasionally they take shortcuts and 
this helps avoid that. 

### [`BLE001`](https://docs.astral.sh/ruff/rules/blind-except/) — Do not catch broad exceptions

`BLE001` flags broad named handlers such as `except Exception` and
`except BaseException` when they handle or swallow the error. 

Ruff permits broad handlers that re-raise and recognized logging patterns 
that retain the exception trace.

A coding agent may wrap a large generated block in `except Exception` because it
does not know the operation's failure contract. This setting forces the agent to 
work through the possible errors and make them clear.

## Usage

Run Ruff and the native checker together on directories or individual Python
files:

```console
uvx anti-slop-python .
uvx anti-slop-python src/
uvx anti-slop-python src/anti_slop_python/cli.py
```

Diagnostics use a conventional source format, and any diagnostic makes the
command exit with status 1:

```text
src/api/parser.py:41:12 SPY001 Avoid containers parameterized with Any
src/api/parser.py:45:8 SPY002 Avoid dynamic attribute access
src/orders/service.py:18:5 C901 `create_order` is too complex (14 > 10)
```

Policy notices are written to standard error and do not change the exit code:

```text
anti-slop-python policy notice: C901 is disabled; recommended: enabled
```

Ruff runs in check-only mode even if the project has `fix = true`.

For local development:

```console
uv sync --dev
uv run pre-commit install
uv run anti-slop-python src tests
uv run pre-commit run --all-files
uv run pytest
uv run ruff format --check .
uv run ruff check .
```

## Examples

[`examples/basic_project`](examples/basic_project) is a small Python project
with intentional native and Ruff-backed violations, plus preferred
alternatives. This repository's Ruff and pre-commit checks exclude `examples/`;
its direct self-check targets `src` and `tests`.

Run the example explicitly to see its diagnostics:

```console
uv run anti-slop-python examples/basic_project
```

## Scope and limitations

Native checks use Python's built-in `ast` and a pragmatic import alias map.
They do not perform scope-aware name resolution, type checking, cross-file
analysis, configuration, suppressions, or autofixes. Ruff-backed checks use
the project's effective Ruff configuration and suppression behavior.

## License

[MIT](LICENSE)
