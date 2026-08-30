from __future__ import annotations

from typing import Any
from unittest.mock import patch


class User:
    def __init__(self, email: str) -> None:
        self.email = email


def first_email(records: list[Any]) -> str:
    """SPY001 and SPY002: the value contract and attribute are both dynamic."""

    attribute = "email"
    return getattr(records[0], attribute)


def send_email(address: str) -> None:
    print(f"Sending email to {address}")


def notify_with_patch(user: User) -> None:
    """TID251: runtime patching hides the notification dependency."""

    with patch("example_project.violations.send_email"):
        send_email(user.email)


def describe_status(status: int) -> str:
    """C901: a long decision chain makes the function hard to understand."""

    if status == 100:
        return "continue"
    if status == 200:
        return "ok"
    if status == 201:
        return "created"
    if status == 202:
        return "accepted"
    if status == 204:
        return "no content"
    if status == 301:
        return "moved permanently"
    if status == 302:
        return "found"
    if status == 400:
        return "bad request"
    if status == 401:
        return "unauthorized"
    if status == 403:
        return "forbidden"
    if status == 404:
        return "not found"
    return "unknown"


def calculate_total() -> int:
    """PLR0915: too many statements hide a simple calculation."""

    total = 0
    total += 1
    total += 2
    total += 3
    total += 4
    total += 5
    total += 6
    total += 7
    total += 8
    total += 9
    total += 10
    total += 11
    total += 12
    total += 13
    total += 14
    total += 15
    total += 16
    total += 17
    total += 18
    total += 19
    total += 20
    total += 21
    total += 22
    total += 23
    total += 24
    total += 25
    total += 26
    total += 27
    total += 28
    total += 29
    total += 30
    total += 31
    total += 32
    total += 33
    total += 34
    total += 35
    total += 36
    total += 37
    total += 38
    total += 39
    total += 40
    return total


def parse_retry_count(value: str) -> int:
    """E722: a bare handler also catches system-exiting exceptions."""

    try:
        return int(value)
    except:
        return 0


def parse_user_id(value: str) -> int:
    """BLE001: Exception hides which failures are expected."""

    try:
        return int(value)
    except Exception:
        return 0
