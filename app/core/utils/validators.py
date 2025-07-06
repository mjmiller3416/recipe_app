from typing import Any, Dict, Iterable


def strip_string_values(values: Dict[str, Any], fields: Iterable[str]) -> Dict[str, Any]:
    """Return *values* with whitespace stripped from specified string fields."""
    for field in fields:
        value = values.get(field)
        if isinstance(value, str):
            values[field] = value.strip()
    return values

