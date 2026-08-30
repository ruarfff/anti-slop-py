from __future__ import annotations

from pathlib import Path

import pytest

from anti_slop_python.ruff_integration import RuffFailure, check_with_ruff


def test_enforces_recommended_rules_when_project_has_no_configuration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "example.py"
    source.write_text("try:\n    value = 1\nexcept:\n    value = 0\n")
    monkeypatch.chdir(tmp_path)

    result = check_with_ruff([tmp_path], [source])

    assert [diagnostic.code for diagnostic in result.diagnostics] == ["E722"]
    assert result.notices == ()


def test_uses_recommended_statement_limit_by_default(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "example.py"
    statements = "".join(f"    total += {number}\n" for number in range(41))
    source.write_text(
        f"def calculate() -> int:\n    total = 0\n{statements}    return total\n"
    )
    monkeypatch.chdir(tmp_path)

    result = check_with_ruff([tmp_path], [source])

    assert [diagnostic.code for diagnostic in result.diagnostics] == ["PLR0915"]
    assert result.notices == ()


def test_bans_patching_by_default(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "example.py"
    source.write_text("from unittest.mock import patch\n\nvalue = patch\n")
    monkeypatch.chdir(tmp_path)

    result = check_with_ruff([tmp_path], [source])

    assert [diagnostic.code for diagnostic in result.diagnostics] == ["TID251"]
    assert result.notices == ()


def test_adds_defaults_to_an_existing_project_rule_selection(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        """[tool.ruff.lint]
select = ["F"]
"""
    )
    source = tmp_path / "example.py"
    source.write_text("try:\n    value = 1\nexcept Exception:\n    value = 0\n")

    result = check_with_ruff([tmp_path], [source])

    assert [diagnostic.code for diagnostic in result.diagnostics] == ["BLE001"]
    assert result.notices == ()


def test_runs_project_rules_without_applying_configured_fixes(tmp_path: Path) -> None:
    _write_recommended_config(tmp_path, extra_rules=["F401"], fix=True)
    source = tmp_path / "example.py"
    source.write_text("import os\n")

    result = check_with_ruff([tmp_path], [source])

    assert [diagnostic.code for diagnostic in result.diagnostics] == ["F401"]
    assert result.notices == ()
    assert source.read_text() == "import os\n"


def test_respects_project_exclusions_for_ruff_backed_rules(tmp_path: Path) -> None:
    _write_recommended_config(tmp_path, excluded_files=["excluded.py"])
    source = tmp_path / "excluded.py"
    source.write_text("try:\n    value = 1\nexcept:\n    value = 0\n")

    result = check_with_ruff([tmp_path], [source])

    assert result.diagnostics == ()


def test_uses_an_included_file_to_resolve_force_exclude_settings(
    tmp_path: Path,
) -> None:
    _write_recommended_config(
        tmp_path,
        excluded_files=["excluded.py"],
        force_exclude=True,
    )
    excluded = tmp_path / "excluded.py"
    excluded.write_text("try:\n    value = 1\nexcept:\n    value = 0\n")
    included = tmp_path / "included.py"
    included.write_text("try:\n    value = 1\nexcept:\n    value = 0\n")

    result = check_with_ruff([tmp_path], [excluded, included])

    assert [diagnostic.path for diagnostic in result.diagnostics] == [included]


def test_skips_a_ruff_scope_when_all_files_are_excluded(tmp_path: Path) -> None:
    _write_recommended_config(
        tmp_path,
        excluded_files=["*.py"],
        force_exclude=True,
    )
    source = tmp_path / "excluded.py"
    source.write_text("try:\n    value = 1\nexcept:\n    value = 0\n")

    result = check_with_ruff([tmp_path], [source])

    assert result.diagnostics == ()


def test_reports_disabled_recommendation_without_enforcing_it(tmp_path: Path) -> None:
    _write_recommended_config(tmp_path, ignored_rules=["C901"])
    source = tmp_path / "example.py"
    branches = "".join(
        f"    if value == {number}:\n        return {number}\n" for number in range(12)
    )
    source.write_text(f"def choose(value: int) -> int:\n{branches}    return -1\n")

    result = check_with_ruff([tmp_path], [source])

    assert all(diagnostic.code != "C901" for diagnostic in result.diagnostics)
    assert "C901 is disabled; recommended: enabled" in result.notices


@pytest.mark.parametrize("comment", ["# noqa: C901", "# noqa"])
def test_reports_noqa_suppression_of_a_recommended_rule(
    tmp_path: Path,
    comment: str,
) -> None:
    _write_recommended_config(tmp_path)
    source = tmp_path / "example.py"
    branches = "".join(
        f"    if value == {number}:\n        return {number}\n" for number in range(12)
    )
    source.write_text(
        f"def choose(value: int) -> int:  {comment}\n{branches}    return -1\n"
    )

    result = check_with_ruff([tmp_path], [source])

    assert all(diagnostic.code != "C901" for diagnostic in result.diagnostics)
    assert (
        f"C901 is suppressed by noqa at {source}:1; recommended for checked files"
        in result.notices
    )


def test_reports_only_weaker_limits_and_scoped_ignores(tmp_path: Path) -> None:
    _write_recommended_config(
        tmp_path,
        max_complexity=20,
        max_statements=30,
        per_file_ignores={"example.py": ["PLR0915"]},
    )
    source = tmp_path / "example.py"
    branches = "".join(
        f"    if value == {number}:\n        return {number}\n" for number in range(12)
    )
    source.write_text(f"def choose(value: int) -> int:\n{branches}    return -1\n")

    result = check_with_ruff([tmp_path], [source])

    assert all(diagnostic.code != "C901" for diagnostic in result.diagnostics)
    assert "C901 allows complexity 20; recommended maximum: 10" in result.notices
    assert (
        "PLR0915 is ignored for example.py; recommended for all checked files"
        in result.notices
    )
    assert all("allows 30 statements" not in notice for notice in result.notices)


def test_project_banned_apis_override_defaults_with_policy_notices(
    tmp_path: Path,
) -> None:
    _write_recommended_config(tmp_path, banned_apis=["custom.api"])
    source = tmp_path / "example.py"
    source.write_text(
        "from custom import api\n"
        "from unittest.mock import patch\n"
        "\n"
        "value = (api, patch)\n"
    )

    result = check_with_ruff([tmp_path], [source])

    assert [diagnostic.code for diagnostic in result.diagnostics] == ["TID251"]
    assert result.notices == (
        "TID251 does not ban mock.patch; recommended: ban this API",
        "TID251 does not ban unittest.mock.patch; recommended: ban this API",
    )


def test_accepts_broader_banned_apis(tmp_path: Path) -> None:
    _write_recommended_config(tmp_path, banned_apis=["mock", "unittest.mock"])
    source = tmp_path / "example.py"
    source.write_text("value = 1\n")

    result = check_with_ruff([tmp_path], [source])

    assert result.notices == ()


def test_respects_explicit_statement_limit_override(tmp_path: Path) -> None:
    _write_recommended_config(tmp_path, max_statements=50)
    source = tmp_path / "example.py"
    statements = "".join(f"    total += {number}\n" for number in range(41))
    source.write_text(
        f"def calculate() -> int:\n    total = 0\n{statements}    return total\n"
    )

    result = check_with_ruff([tmp_path], [source])

    assert all(diagnostic.code != "PLR0915" for diagnostic in result.diagnostics)
    assert "PLR0915 allows 50 statements; recommended maximum: 40" in result.notices


def test_invalid_ruff_configuration_is_an_integration_failure(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[tool.ruff\n")
    source = tmp_path / "example.py"
    source.write_text("value = 1\n")

    with pytest.raises(RuffFailure, match="Ruff failed"):
        check_with_ruff([tmp_path], [source])


def test_audits_each_nested_ruff_configuration(tmp_path: Path) -> None:
    _write_recommended_config(tmp_path)
    root_source = tmp_path / "root.py"
    root_source.write_text("root = 1\n")
    nested = tmp_path / "nested"
    nested.mkdir()
    _write_recommended_config(nested, ignored_rules=["C901"])
    nested_source = nested / "nested.py"
    nested_source.write_text("nested = 1\n")

    result = check_with_ruff([tmp_path], [root_source, nested_source])

    assert result.notices == (
        f"C901 is disabled; recommended: enabled "
        f"[Ruff settings: {nested / 'pyproject.toml'}]",
    )


def test_respects_legacy_unnested_configuration_keys(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        """[tool.ruff]
select = ["BLE001", "C901", "E722", "PLR0915", "TID251"]
extend-ignore = ["C901"]

[tool.ruff.mccabe]
max-complexity = 15

[tool.ruff.pylint]
max-statements = 50

[tool.ruff.flake8-tidy-imports.banned-api]
"custom.patch".msg = "Do not patch"
"""
    )
    source = tmp_path / "example.py"
    branches = "".join(
        f"    if value == {number}:\n        return {number}\n" for number in range(12)
    )
    statements = "".join(f"    total += {number}\n" for number in range(41))
    source.write_text(
        f"def choose(value: int) -> int:\n{branches}    return -1\n\n"
        f"def calculate() -> int:\n    total = 0\n{statements}    return total\n"
    )

    result = check_with_ruff([tmp_path], [source])

    assert all(diagnostic.code != "C901" for diagnostic in result.diagnostics)
    assert all(diagnostic.code != "PLR0915" for diagnostic in result.diagnostics)
    assert "C901 is disabled; recommended: enabled" in result.notices
    assert "PLR0915 allows 50 statements; recommended maximum: 40" in result.notices


def _write_recommended_config(
    root: Path,
    *,
    extra_rules: list[str] | None = None,
    ignored_rules: list[str] | None = None,
    max_complexity: int = 10,
    max_statements: int = 40,
    per_file_ignores: dict[str, list[str]] | None = None,
    banned_apis: list[str] | None = None,
    excluded_files: list[str] | None = None,
    force_exclude: bool = False,
    fix: bool = False,
) -> None:
    rules = ["BLE001", "C901", "E722", "PLR0915", "TID251"]
    rules.extend(extra_rules or [])
    ignored = ignored_rules or []
    apis = banned_apis or ["mock.patch", "unittest.mock.patch"]
    lines = [
        "[tool.ruff]",
        f"fix = {str(fix).lower()}",
        f"force-exclude = {str(force_exclude).lower()}",
        f"exclude = {excluded_files or []!r}",
        "",
        "[tool.ruff.lint]",
        f"select = {rules!r}",
        f"ignore = {ignored!r}",
    ]
    if per_file_ignores:
        lines.extend(["", "[tool.ruff.lint.per-file-ignores]"])
        for pattern, codes in per_file_ignores.items():
            lines.append(f'"{pattern}" = {codes!r}')
    lines.extend(
        [
            "",
            "[tool.ruff.lint.mccabe]",
            f"max-complexity = {max_complexity}",
            "",
            "[tool.ruff.lint.pylint]",
            f"max-statements = {max_statements}",
            "",
            "[tool.ruff.lint.flake8-tidy-imports.banned-api]",
        ]
    )
    for api in apis:
        lines.append(f'"{api}".msg = "Pass the dependency explicitly"')
    (root / "pyproject.toml").write_text("\n".join(lines) + "\n")
