"""Unit tests for utility helper functions."""

import json
from pathlib import Path

import pytest

from synth_agent.core.exceptions import ValidationError
from synth_agent.utils.helpers import (
    extract_json_from_text,
    format_bytes,
    merge_dicts,
    sanitize_user_input,
    validate_file_path,
)


class TestExtractJsonFromText:
    """Tests for extract_json_from_text function."""

    def test_extract_plain_json(self):
        """Test extracting plain JSON."""
        json_str = '{"name": "test", "value": 123}'
        result = extract_json_from_text(json_str)
        assert result == {"name": "test", "value": 123}

    def test_extract_json_from_code_block(self):
        """Test extracting JSON from markdown code block."""
        text = '''Here is the JSON:
```json
{
  "name": "test",
  "value": 123
}
```
That's it!'''
        result = extract_json_from_text(text)
        assert result == {"name": "test", "value": 123}

    def test_extract_json_from_generic_code_block(self):
        """Test extracting JSON from generic code block."""
        text = '''```
{"name": "test", "value": 123}
```'''
        result = extract_json_from_text(text)
        assert result == {"name": "test", "value": 123}

    def test_extract_json_array(self):
        """Test extracting JSON array."""
        json_str = '[{"id": 1}, {"id": 2}]'
        result = extract_json_from_text(json_str)
        assert result == [{"id": 1}, {"id": 2}]

    def test_extract_json_with_whitespace(self):
        """Test extracting JSON with surrounding whitespace."""
        json_str = '  \n  {"name": "test"}  \n  '
        result = extract_json_from_text(json_str)
        assert result == {"name": "test"}

    def test_invalid_json_raises_error(self):
        """Test that invalid JSON raises ValidationError."""
        with pytest.raises(ValidationError, match="Failed to parse JSON"):
            extract_json_from_text('{"name": invalid}')

    def test_unclosed_json_block_raises_error(self):
        """Test that unclosed JSON block raises ValidationError."""
        with pytest.raises(ValidationError, match="Unclosed JSON code block"):
            extract_json_from_text('```json\n{"name": "test"}')

    def test_empty_content_raises_error(self):
        """Test that empty content raises ValidationError."""
        with pytest.raises(ValidationError, match="Empty JSON content"):
            extract_json_from_text('```json\n\n```')

    def test_complex_nested_json(self):
        """Test extracting complex nested JSON."""
        json_str = '''{
            "users": [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25}
            ],
            "metadata": {
                "count": 2,
                "timestamp": "2024-01-01"
            }
        }'''
        result = extract_json_from_text(json_str)
        assert len(result["users"]) == 2
        assert result["metadata"]["count"] == 2


class TestValidateFilePath:
    """Tests for validate_file_path function."""

    def test_valid_file(self, temp_dir):
        """Test validation of valid file."""
        file_path = temp_dir / "test.csv"
        file_path.write_text("test content")

        # Should not raise
        validate_file_path(file_path, allowed_extensions=[".csv"])

    def test_nonexistent_file_raises_error(self, temp_dir):
        """Test that nonexistent file raises ValidationError."""
        file_path = temp_dir / "nonexistent.csv"

        with pytest.raises(ValidationError, match="File does not exist"):
            validate_file_path(file_path)

    def test_directory_raises_error(self, temp_dir):
        """Test that directory path raises ValidationError."""
        with pytest.raises(ValidationError, match="Path is not a file"):
            validate_file_path(temp_dir)

    def test_invalid_extension_raises_error(self, temp_dir):
        """Test that invalid file extension raises ValidationError."""
        file_path = temp_dir / "test.txt"
        file_path.write_text("test")

        with pytest.raises(ValidationError, match="File extension.*not allowed"):
            validate_file_path(file_path, allowed_extensions=[".csv", ".json"])

    def test_case_insensitive_extension(self, temp_dir):
        """Test that extension check is case insensitive."""
        file_path = temp_dir / "test.CSV"
        file_path.write_text("test")

        # Should not raise
        validate_file_path(file_path, allowed_extensions=[".csv"])

    def test_file_too_large_raises_error(self, temp_dir):
        """Test that oversized file raises ValidationError."""
        file_path = temp_dir / "large.txt"
        # Create a file larger than 1 MB
        file_path.write_text("x" * (2 * 1024 * 1024))

        with pytest.raises(ValidationError, match="File size.*exceeds maximum"):
            validate_file_path(file_path, max_size_mb=1)

    def test_no_extension_check_when_none(self, temp_dir):
        """Test that any extension is allowed when None."""
        file_path = temp_dir / "test.xyz"
        file_path.write_text("test")

        # Should not raise
        validate_file_path(file_path, allowed_extensions=None)


class TestSanitizeUserInput:
    """Tests for sanitize_user_input function."""

    def test_sanitize_normal_input(self):
        """Test sanitizing normal input."""
        result = sanitize_user_input("  Hello World  ")
        assert result == "Hello World"

    def test_remove_null_bytes(self):
        """Test removing null bytes."""
        result = sanitize_user_input("Hello\x00World")
        assert result == "HelloWorld"
        assert "\x00" not in result

    def test_input_too_long_raises_error(self):
        """Test that input exceeding max length raises ValidationError."""
        long_input = "x" * 10001

        with pytest.raises(ValidationError, match="Input too long"):
            sanitize_user_input(long_input, max_length=10000)

    def test_empty_after_sanitization_raises_error(self):
        """Test that empty input after sanitization raises ValidationError."""
        with pytest.raises(ValidationError, match="Input cannot be empty"):
            sanitize_user_input("   ")

    def test_non_string_input_raises_error(self):
        """Test that non-string input raises ValidationError."""
        with pytest.raises(ValidationError, match="Input must be a string"):
            sanitize_user_input(123)

    def test_multiline_input(self):
        """Test sanitizing multiline input."""
        input_str = "  Line 1\nLine 2\nLine 3  "
        result = sanitize_user_input(input_str)
        assert result == "Line 1\nLine 2\nLine 3"

    def test_custom_max_length(self):
        """Test with custom max length."""
        input_str = "x" * 100
        result = sanitize_user_input(input_str, max_length=100)
        assert len(result) == 100


class TestFormatBytes:
    """Tests for format_bytes function."""

    def test_format_bytes(self):
        """Test bytes formatting."""
        assert format_bytes(0) == "0.00 B"
        assert format_bytes(1024) == "1.00 KB"
        assert format_bytes(1024 * 1024) == "1.00 MB"
        assert format_bytes(1024 * 1024 * 1024) == "1.00 GB"
        assert format_bytes(1024 * 1024 * 1024 * 1024) == "1.00 TB"

    def test_format_bytes_with_decimals(self):
        """Test bytes formatting with decimal values."""
        assert "1.50 KB" in format_bytes(1536)
        assert "2.50 MB" in format_bytes(int(2.5 * 1024 * 1024))

    def test_format_large_bytes(self):
        """Test formatting very large byte values."""
        petabyte = 1024 * 1024 * 1024 * 1024 * 1024
        result = format_bytes(petabyte)
        assert "PB" in result


class TestMergeDicts:
    """Tests for merge_dicts function."""

    def test_merge_simple_dicts(self):
        """Test merging simple dictionaries."""
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}
        result = merge_dicts(base, override)

        assert result == {"a": 1, "b": 3, "c": 4}

    def test_merge_nested_dicts(self):
        """Test merging nested dictionaries."""
        base = {
            "level1": {
                "level2": {
                    "a": 1,
                    "b": 2
                }
            }
        }
        override = {
            "level1": {
                "level2": {
                    "b": 3,
                    "c": 4
                }
            }
        }
        result = merge_dicts(base, override)

        assert result["level1"]["level2"]["a"] == 1
        assert result["level1"]["level2"]["b"] == 3
        assert result["level1"]["level2"]["c"] == 4

    def test_merge_does_not_modify_originals(self):
        """Test that merge doesn't modify original dicts."""
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}
        result = merge_dicts(base, override)

        assert base == {"a": 1, "b": 2}
        assert override == {"b": 3, "c": 4}

    def test_merge_with_empty_override(self):
        """Test merging with empty override."""
        base = {"a": 1, "b": 2}
        override = {}
        result = merge_dicts(base, override)

        assert result == base

    def test_merge_with_empty_base(self):
        """Test merging with empty base."""
        base = {}
        override = {"a": 1, "b": 2}
        result = merge_dicts(base, override)

        assert result == override

    def test_merge_replaces_non_dict_values(self):
        """Test that non-dict values are replaced."""
        base = {"a": 1, "b": {"nested": "value"}}
        override = {"a": [1, 2, 3], "b": "string"}
        result = merge_dicts(base, override)

        assert result["a"] == [1, 2, 3]
        assert result["b"] == "string"
