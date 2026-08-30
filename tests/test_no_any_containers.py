from __future__ import annotations

import pytest

from anti_slop_python import check_source


@pytest.mark.parametrize(
    "source",
    [
        "from typing import Any\nvalue: dict[str, Any]\n",
        "from typing import Any\nvalue: list[Any]\n",
        "from typing import Any\nvalue: set[Any]\n",
        "from typing import Any\nvalue: tuple[Any, ...]\n",
        "import typing as t\nvalue: t.Dict[str, t.Any]\n",
        "from typing import Any as Unknown\nvalue: list[Unknown]\n",
        "from typing import Any\nvalue: list[int | Any]\n",
        "from typing import Any\nvalue: dict[str, Any | None]\n",
        "from typing import Any, Optional\nvalue: list[Optional[Any]]\n",
        "from typing import Any, Union\nvalue: list[Union[int, Any]]\n",
        "from typing_extensions import Any\nvalue: list[Any]\n",
        "import typing_extensions as te\nvalue: te.List[te.Any]\n",
    ],
)
def test_reports_any_containers(source: str) -> None:
    diagnostics = check_source(source, "example.py")

    assert [diagnostic.code for diagnostic in diagnostics] == ["SPY001"]


@pytest.mark.parametrize(
    "source",
    [
        "value: dict[str, object]\n",
        "value: list[str]\n",
        "from somewhere import Any\nvalue: list[Any]\n",
        "from typing import Any\nvalue: Result[Any]\n",
        "from . import Any\nvalue: list[Any]\n",
        "from ..types import Any\nvalue: list[Any]\n",
    ],
)
def test_accepts_specific_or_non_container_types(source: str) -> None:
    assert check_source(source) == []


def test_reports_container_location() -> None:
    diagnostic = check_source(
        "from typing import Any\nvalue: dict[str, Any]\n", "example.py"
    )[0]

    assert (diagnostic.line, diagnostic.column) == (2, 8)
