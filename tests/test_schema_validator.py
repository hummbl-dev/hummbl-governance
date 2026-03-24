"""Tests for hummbl_governance.schema_validator."""

import json
import tempfile
from pathlib import Path


from hummbl_governance.schema_validator import SchemaValidator


class TestTypeValidation:
    """Test type keyword validation."""

    def test_string_valid(self):
        errors = SchemaValidator.validate("hello", {"type": "string"})
        assert errors == []

    def test_string_invalid(self):
        errors = SchemaValidator.validate(42, {"type": "string"})
        assert len(errors) == 1

    def test_integer_valid(self):
        errors = SchemaValidator.validate(42, {"type": "integer"})
        assert errors == []

    def test_number_valid(self):
        errors = SchemaValidator.validate(3.14, {"type": "number"})
        assert errors == []

    def test_boolean_valid(self):
        errors = SchemaValidator.validate(True, {"type": "boolean"})
        assert errors == []

    def test_array_valid(self):
        errors = SchemaValidator.validate([1, 2, 3], {"type": "array"})
        assert errors == []

    def test_object_valid(self):
        errors = SchemaValidator.validate({"a": 1}, {"type": "object"})
        assert errors == []

    def test_null_valid(self):
        errors = SchemaValidator.validate(None, {"type": "null"})
        assert errors == []

    def test_multi_type(self):
        errors = SchemaValidator.validate("hello", {"type": ["string", "null"]})
        assert errors == []
        errors = SchemaValidator.validate(None, {"type": ["string", "null"]})
        assert errors == []


class TestObjectValidation:
    """Test object schema validation."""

    def test_required_present(self):
        schema = {"type": "object", "required": ["name"]}
        errors = SchemaValidator.validate({"name": "test"}, schema)
        assert errors == []

    def test_required_missing(self):
        schema = {"type": "object", "required": ["name"]}
        errors = SchemaValidator.validate({}, schema)
        assert len(errors) == 1
        assert "name" in errors[0]

    def test_properties(self):
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
            },
        }
        errors = SchemaValidator.validate({"name": "Alice", "age": 30}, schema)
        assert errors == []

    def test_property_type_mismatch(self):
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
        }
        errors = SchemaValidator.validate({"name": 42}, schema)
        assert len(errors) == 1

    def test_additional_properties_false(self):
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "additionalProperties": False,
        }
        errors = SchemaValidator.validate({"name": "test", "extra": 1}, schema)
        assert len(errors) == 1
        assert "extra" in errors[0]

    def test_additional_properties_schema(self):
        schema = {
            "type": "object",
            "properties": {},
            "additionalProperties": {"type": "string"},
        }
        errors = SchemaValidator.validate({"a": "ok", "b": 42}, schema)
        assert len(errors) == 1  # b is not a string


class TestStringValidation:
    """Test string-specific keywords."""

    def test_min_length(self):
        errors = SchemaValidator.validate("ab", {"type": "string", "minLength": 3})
        assert len(errors) == 1

    def test_max_length(self):
        errors = SchemaValidator.validate("abcd", {"type": "string", "maxLength": 3})
        assert len(errors) == 1

    def test_pattern_match(self):
        errors = SchemaValidator.validate("abc123", {"type": "string", "pattern": r"^[a-z]+\d+$"})
        assert errors == []

    def test_pattern_no_match(self):
        errors = SchemaValidator.validate("123abc", {"type": "string", "pattern": r"^[a-z]+$"})
        assert len(errors) == 1

    def test_enum(self):
        errors = SchemaValidator.validate("a", {"enum": ["a", "b", "c"]})
        assert errors == []

    def test_enum_invalid(self):
        errors = SchemaValidator.validate("d", {"enum": ["a", "b", "c"]})
        assert len(errors) == 1


class TestNumberValidation:
    """Test number-specific keywords."""

    def test_minimum(self):
        errors = SchemaValidator.validate(5, {"type": "integer", "minimum": 10})
        assert len(errors) == 1

    def test_maximum(self):
        errors = SchemaValidator.validate(15, {"type": "integer", "maximum": 10})
        assert len(errors) == 1

    def test_within_range(self):
        errors = SchemaValidator.validate(7, {"type": "integer", "minimum": 0, "maximum": 10})
        assert errors == []


class TestArrayValidation:
    """Test array-specific keywords."""

    def test_min_items(self):
        errors = SchemaValidator.validate([1], {"type": "array", "minItems": 2})
        assert len(errors) == 1

    def test_max_items(self):
        errors = SchemaValidator.validate([1, 2, 3], {"type": "array", "maxItems": 2})
        assert len(errors) == 1

    def test_items_schema(self):
        schema = {"type": "array", "items": {"type": "string"}}
        errors = SchemaValidator.validate(["a", "b"], schema)
        assert errors == []

    def test_items_schema_invalid(self):
        schema = {"type": "array", "items": {"type": "string"}}
        errors = SchemaValidator.validate(["a", 42], schema)
        assert len(errors) == 1


class TestCompositionKeywords:
    """Test oneOf and anyOf."""

    def test_one_of_match(self):
        schema = {"oneOf": [{"type": "string"}, {"type": "integer"}]}
        errors = SchemaValidator.validate("hello", schema)
        assert errors == []

    def test_one_of_no_match(self):
        schema = {"oneOf": [{"type": "string"}, {"type": "integer"}]}
        errors = SchemaValidator.validate(3.14, schema)
        assert len(errors) == 1

    def test_any_of_match(self):
        schema = {"anyOf": [{"type": "string"}, {"type": "integer"}]}
        errors = SchemaValidator.validate(42, schema)
        assert errors == []

    def test_any_of_no_match(self):
        schema = {"anyOf": [{"type": "string"}, {"type": "integer"}]}
        errors = SchemaValidator.validate(3.14, schema)
        assert len(errors) == 1

    def test_const(self):
        errors = SchemaValidator.validate("exact", {"const": "exact"})
        assert errors == []

    def test_const_mismatch(self):
        errors = SchemaValidator.validate("wrong", {"const": "exact"})
        assert len(errors) == 1


class TestValidateDict:
    """Test validate_dict convenience method."""

    def test_valid(self):
        schema = {"type": "object", "required": ["name"]}
        valid, errors = SchemaValidator.validate_dict({"name": "test"}, schema)
        assert valid is True
        assert errors == []

    def test_invalid(self):
        schema = {"type": "object", "required": ["name"]}
        valid, errors = SchemaValidator.validate_dict({}, schema)
        assert valid is False
        assert len(errors) == 1


class TestValidateFile:
    """Test file validation."""

    def test_validate_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            instance_path = Path(tmpdir) / "data.json"
            schema_path = Path(tmpdir) / "schema.json"

            instance_path.write_text(json.dumps({"name": "test"}))
            schema_path.write_text(json.dumps({
                "type": "object",
                "required": ["name"],
                "properties": {"name": {"type": "string"}},
            }))

            valid, errors = SchemaValidator.validate_file(instance_path, schema_path)
            assert valid is True

    def test_validate_file_invalid(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            instance_path = Path(tmpdir) / "data.json"
            schema_path = Path(tmpdir) / "schema.json"

            instance_path.write_text(json.dumps({"count": "not a number"}))
            schema_path.write_text(json.dumps({
                "type": "object",
                "properties": {"count": {"type": "integer"}},
            }))

            valid, errors = SchemaValidator.validate_file(instance_path, schema_path)
            assert valid is False
