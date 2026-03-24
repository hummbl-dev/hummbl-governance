"""Schema Validator -- Stdlib-only JSON Schema validator (Draft 2020-12 subset).

Supported keywords:
    type, required, properties, enum, pattern, minimum, maximum,
    minLength, maxLength, minItems, maxItems, items, additionalProperties,
    const, oneOf, anyOf

Usage:
    from hummbl_governance import SchemaValidator

    validator = SchemaValidator()
    errors = validator.validate({"name": "test"}, {"type": "object", "required": ["name"]})
    # errors == []  (valid)

Stdlib-only. Zero third-party dependencies.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

# JSON Schema type name -> Python type(s)
_TYPE_MAP: dict[str, tuple[type, ...]] = {
    "string": (str,),
    "number": (int, float),
    "integer": (int,),
    "boolean": (bool,),
    "array": (list,),
    "object": (dict,),
    "null": (type(None),),
}


class ValidationError(Exception):
    """Raised when a value fails schema validation."""

    def __init__(self, message: str, path: str = "") -> None:
        self.path = path
        super().__init__(f"{path}: {message}" if path else message)


class SchemaValidator:
    """JSON Schema validator using only Python stdlib.

    Supports a subset of Draft 2020-12 sufficient for validating
    structured governance data.
    """

    @staticmethod
    def validate(instance: Any, schema: dict[str, Any], path: str = "") -> list[str]:
        """Validate *instance* against *schema*.

        Returns a list of error strings (empty = valid).
        """
        return _validate(instance, schema, path)

    @staticmethod
    def validate_file(
        instance_path: str | Path,
        schema_path: str | Path,
    ) -> tuple[bool, list[str]]:
        """Validate a JSON file against a JSON Schema file.

        Returns (is_valid, errors).
        """
        instance = json.loads(Path(instance_path).read_text(encoding="utf-8"))
        schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
        errors = _validate(instance, schema)
        return len(errors) == 0, errors

    @staticmethod
    def validate_dict(
        entry: dict[str, Any],
        schema: dict[str, Any],
    ) -> tuple[bool, list[str]]:
        """Validate a dictionary against a schema.

        Returns (is_valid, errors).
        """
        errors = _validate(entry, schema)
        return len(errors) == 0, errors


def _check_type(instance: Any, schema: dict[str, Any], path: str) -> str | None:
    """Check type constraint. Returns error string or None."""
    if "type" not in schema:
        return None
    type_name = schema["type"]
    if isinstance(type_name, list):
        expected = tuple(t for name in type_name for t in _TYPE_MAP.get(name, ()))
    else:
        expected = _TYPE_MAP.get(type_name, ())
    if expected and not isinstance(instance, expected):
        return f"{path}: expected type {type_name!r}, got {type(instance).__name__}"
    return None


def _validate(instance: Any, schema: dict[str, Any], path: str = "") -> list[str]:
    """Core validation logic -- dispatches to type-specific validators."""
    # const (early return)
    if "const" in schema and instance != schema["const"]:
        return [f"{path}: expected const {schema['const']!r}, got {instance!r}"]

    # type check (early return on mismatch)
    type_error = _check_type(instance, schema, path)
    if type_error:
        return [type_error]

    errors: list[str] = []

    # enum
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: {instance!r} not in enum {schema['enum']}")

    # type-specific validation
    if isinstance(instance, str):
        errors.extend(_validate_string(instance, schema, path))
    elif isinstance(instance, (int, float)):
        errors.extend(_validate_number(instance, schema, path))
    elif isinstance(instance, dict):
        errors.extend(_validate_object(instance, schema, path))
    elif isinstance(instance, list):
        errors.extend(_validate_array(instance, schema, path))

    # composition keywords
    errors.extend(_validate_composition(instance, schema, path))

    return errors


def _validate_string(instance: str, schema: dict[str, Any], path: str) -> list[str]:
    """Validate string-specific keywords: pattern, minLength, maxLength."""
    errors: list[str] = []
    if "pattern" in schema:
        try:
            if not re.search(schema["pattern"], instance):
                errors.append(f"{path}: {instance!r} does not match pattern {schema['pattern']!r}")
        except re.error as e:
            errors.append(f"{path}: invalid regex pattern {schema['pattern']!r}: {e}")
    if "minLength" in schema and len(instance) < schema["minLength"]:
        errors.append(f"{path}: string length {len(instance)} < minLength {schema['minLength']}")
    if "maxLength" in schema and len(instance) > schema["maxLength"]:
        errors.append(f"{path}: string length {len(instance)} > maxLength {schema['maxLength']}")
    return errors


def _validate_number(instance: int | float, schema: dict[str, Any], path: str) -> list[str]:
    """Validate number-specific keywords: minimum, maximum."""
    errors: list[str] = []
    if "minimum" in schema and instance < schema["minimum"]:
        errors.append(f"{path}: {instance} < minimum {schema['minimum']}")
    if "maximum" in schema and instance > schema["maximum"]:
        errors.append(f"{path}: {instance} > maximum {schema['maximum']}")
    return errors


def _validate_object(instance: dict, schema: dict[str, Any], path: str) -> list[str]:
    """Validate object-specific keywords: required, properties, additionalProperties."""
    errors: list[str] = []
    for req in schema.get("required", []):
        if req not in instance:
            errors.append(f"{path}: missing required property {req!r}")

    props = schema.get("properties", {})
    for key, prop_schema in props.items():
        if key in instance:
            sub_path = f"{path}.{key}" if path else key
            errors.extend(_validate(instance[key], prop_schema, sub_path))

    if "additionalProperties" in schema:
        errors.extend(_validate_additional_props(instance, schema["additionalProperties"], props, path))
    return errors


def _validate_additional_props(
    instance: dict, ap: bool | dict, known_props: dict[str, Any], path: str
) -> list[str]:
    """Validate additionalProperties constraint."""
    errors: list[str] = []
    known_keys = set(known_props.keys())
    for key in instance:
        if key not in known_keys:
            if ap is False:
                errors.append(f"{path}: unexpected property {key!r}")
            elif isinstance(ap, dict):
                sub_path = f"{path}.{key}" if path else key
                errors.extend(_validate(instance[key], ap, sub_path))
    return errors


def _validate_array(instance: list, schema: dict[str, Any], path: str) -> list[str]:
    """Validate array-specific keywords: minItems, maxItems, items."""
    errors: list[str] = []
    if "minItems" in schema and len(instance) < schema["minItems"]:
        errors.append(f"{path}: array length {len(instance)} < minItems {schema['minItems']}")
    if "maxItems" in schema and len(instance) > schema["maxItems"]:
        errors.append(f"{path}: array length {len(instance)} > maxItems {schema['maxItems']}")
    if "items" in schema:
        for i, item in enumerate(instance):
            errors.extend(_validate(item, schema["items"], f"{path}[{i}]"))
    return errors


def _validate_composition(instance: Any, schema: dict[str, Any], path: str) -> list[str]:
    """Validate composition keywords: oneOf, anyOf."""
    errors: list[str] = []
    if "oneOf" in schema:
        match_count = sum(1 for s in schema["oneOf"] if not _validate(instance, s, path))
        if match_count != 1:
            errors.append(f"{path}: expected exactly one of oneOf to match, got {match_count}")
    if "anyOf" in schema and not any(not _validate(instance, s, path) for s in schema["anyOf"]):
        errors.append(f"{path}: none of anyOf schemas matched")
    return errors
