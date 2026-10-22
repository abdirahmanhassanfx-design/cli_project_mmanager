"""Input rules shared by the service layer."""

import re
from datetime import datetime

from utils.exceptions import ValidationError

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
DATE_FORMAT = "%Y-%m-%d"


def require_non_empty(value: str, field_name: str) -> str:
    """Return stripped text or raise when the field is blank."""
    cleaned = value.strip()
    if not cleaned:
        raise ValidationError(f"{field_name} cannot be empty.")
    return cleaned


def validate_email(email: str) -> str:
    """Return a stripped email address after a basic format check."""
    cleaned = require_non_empty(email, "Email")
    if EMAIL_PATTERN.match(cleaned) is None:
        raise ValidationError(
            "Enter a valid email address, for example name@example.com."
        )
    return cleaned


def validate_choice(value: str, choices: tuple[str, ...], field_name: str) -> str:
    """Match a choice without caring about letter case.

    The returned value uses the canonical spelling from ``choices``.
    """
    cleaned = require_non_empty(value, field_name)
    for choice in choices:
        if cleaned.casefold() == choice.casefold():
            return choice
    options = ", ".join(choices)
    raise ValidationError(f"Invalid {field_name}. Choose one of: {options}.")


def validate_date(value: str, field_name: str = "Due date") -> str:
    """Return a YYYY-MM-DD date string after checking the calendar date."""
    cleaned = require_non_empty(value, field_name)
    try:
        parsed = datetime.strptime(cleaned, DATE_FORMAT)
    except ValueError as exc:
        raise ValidationError(
            f"Enter {field_name.lower()} in YYYY-MM-DD format."
        ) from exc
    return parsed.strftime(DATE_FORMAT)


def normalize_id(value: str, record_name: str) -> str:
    """Return an uppercase ID, or raise when the field is blank."""
    cleaned = require_non_empty(value, f"{record_name} ID")
    return cleaned.upper()
