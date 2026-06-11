"""Validation helpers."""

from __future__ import annotations

from typing import Any


class ValidationError(ValueError):
    """Raised when input data cannot be planned safely."""


def require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError(f"{label} must be a JSON object")
    return value


def require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValidationError(f"{label} must be a list")
    return value


def require_str(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{key} must be a non-empty string")
    return value.strip()


def require_float(data: dict[str, Any], key: str, *, minimum: float | None = None, maximum: float | None = None) -> float:
    value = data.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(f"{key} must be numeric")
    number = float(value)
    if minimum is not None and number < minimum:
        raise ValidationError(f"{key} must be >= {minimum}")
    if maximum is not None and number > maximum:
        raise ValidationError(f"{key} must be <= {maximum}")
    return number


def optional_bool(data: dict[str, Any], key: str, default: bool = False) -> bool:
    value = data.get(key, default)
    if not isinstance(value, bool):
        raise ValidationError(f"{key} must be boolean")
    return value


def string_list(value: Any, label: str) -> list[str]:
    if value is None:
        return []
    values = require_list(value, label)
    result = []
    for item in values:
        if not isinstance(item, str) or not item.strip():
            raise ValidationError(f"{label} entries must be non-empty strings")
        result.append(item.strip())
    return result


def int_list(value: Any, label: str) -> list[int]:
    if value is None:
        return []
    values = require_list(value, label)
    result = []
    for item in values:
        if isinstance(item, bool) or not isinstance(item, int):
            raise ValidationError(f"{label} entries must be integers")
        if item < 0 or item > 23:
            raise ValidationError(f"{label} entries must be 0..23")
        result.append(item)
    return sorted(set(result))

