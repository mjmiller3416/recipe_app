"""Reusable validation helpers for Pydantic models."""

from typing import Any, Iterable


def strip_string(value: Any) -> Any:
    """Return the value stripped of whitespace if it is a string."""
    if isinstance(value, str):
        return value.strip()
    return value


def strip_string_fields(values: dict[str, Any], fields: Iterable[str]) -> dict[str, Any]:
    """Strip whitespace from selected keys if present and string valued."""
    for field in fields:
        val = values.get(field)
        if isinstance(val, str):
            values[field] = val.strip()
    return values

