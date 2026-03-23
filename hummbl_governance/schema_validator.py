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


def _validate(instance: Any, schema: dict[str, Any], path: str = "") -> list[str]:
    """Core validation logic."""
    errors: list[str] = []

    # const
    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: expected const {schema['const']!r}, got {instance!r}")
        return errors

    # type
    if "type" in schema:
        type_name = schema["type"]
        if isinstance(type_name, list):
            expected = tuple(t for name in type_name for t in _TYPE_MAP.get(name, ()))
        else:
            expected = _TYPE_MAP.get(type_name, ())
        if expected and not isinstance(instance, expected):
            errors.append(
                f"{path}: expected type {type_name!r}, got {type(instance).__name__}"
            )
            return errors

    # enum
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: {instance!r} not in enum {schema['enum']}")

    # pattern (string)
    if "pattern" in schema and isinstance(instance, str):
        try:
            if not re.search(schema["pattern"], instance):
                errors.append(
                    f"{path}: {instance!r} does not match pattern {schema['pattern']!r}"
                )
        except re.error as e:
            errors.append(f"{path}: invalid regex pattern {schema['pattern']!r}: {e}")

    # minLength / maxLength (string)
    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(
                f"{path}: string length {len(instance)} < minLength {schema['minLength']}"
            )
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            errors.append(
                f"{path}: string length {len(instance)} > maxLength {schema['maxLength']}"
            )

    # minimum / maximum (number)
    if isinstance(instance, (int, float)):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: {instance} < minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: {instance} > maximum {schema['maximum']}")

    # object validation
    if isinstance(instance, dict):
        for req in schema.get("required", []):
            if req not in instance:
                errors.append(f"{path}: missing required property {req!r}")

        props = schema.get("properties", {})
        for key, prop_schema in props.items():
            if key in instance:
                sub_path = f"{path}.{key}" if path else key
                errors.extend(_validate(instance[key], prop_schema, sub_path))

        if "additionalProperties" in schema:
            ap = schema["additionalProperties"]
            known_keys = set(props.keys())
            for key in instance:
                if key not in known_keys:
                    if ap is False:
                        errors.append(f"{path}: unexpected property {key!r}")
                    elif isinstance(ap, dict):
                        sub_path = f"{path}.{key}" if path else key
                        errors.extend(_validate(instance[key], ap, sub_path))

    # array validation
    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(
                f"{path}: array length {len(instance)} < minItems {schema['minItems']}"
            )
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append(
                f"{path}: array length {len(instance)} > maxItems {schema['maxItems']}"
            )
        if "items" in schema:
            for i, item in enumerate(instance):
                sub_path = f"{path}[{i}]"
                errors.extend(_validate(item, schema["items"], sub_path))

    # oneOf
    if "oneOf" in schema:
        match_count = sum(1 for s in schema["oneOf"] if not _validate(instance, s, path))
        if match_count != 1:
            errors.append(
                f"{path}: expected exactly one of oneOf to match, got {match_count}"
            )

    # anyOf
    if "anyOf" in schema and not any(
        not _validate(instance, s, path) for s in schema["anyOf"]
    ):
        errors.append(f"{path}: none of anyOf schemas matched")

    return errors
