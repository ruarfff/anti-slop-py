from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

STATUS_DESCRIPTIONS = {
    100: "continue",
    200: "ok",
    201: "created",
    202: "accepted",
    204: "no content",
    301: "moved permanently",
    302: "found",
    400: "bad request",
    401: "unauthorized",
    403: "forbidden",
    404: "not found",
}


@dataclass(frozen=True)
class User:
    email: str


def first_email(users: list[User]) -> str:
    """Use a specific element type and direct attribute access."""

    return users[0].email


def notify(user: User, send_email: Callable[[str], None]) -> None:
    """Receive the dependency explicitly so tests can supply a local fake."""

    send_email(user.email)


def describe_status(status: int) -> str:
    """Keep data in a lookup instead of a long decision chain."""

    return STATUS_DESCRIPTIONS.get(status, "unknown")


def calculate_total() -> int:
    """Express the calculation without a long sequence of statements."""

    return sum(range(1, 41))


def parse_retry_count(value: str) -> int:
    """Catch only the conversion error that is expected here."""

    try:
        return int(value)
    except ValueError:
        return 0


def parse_user_id(value: str) -> int:
    """Catch only the conversion error that this operation can recover from."""

    try:
        return int(value)
    except ValueError:
        return 0
