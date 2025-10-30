"""
Utility helper functions for the Synthetic Data Generator.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict

from synth_agent.core.exceptions import ValidationError

# Configure logger
logger = logging.getLogger(__name__)


def extract_json_from_text(text: str) -> Any:
    """
    Extract JSON from LLM response (handles markdown code blocks).

    This is a shared utility to avoid code duplication across modules.

    Args:
        text: Text potentially containing JSON

    Returns:
        Parsed JSON object

    Raises:
        ValidationError: If JSON cannot be parsed
    """
    try:
        # Try to extract JSON from markdown code blocks
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            if end == -1:
                raise ValidationError("Unclosed JSON code block")
            json_text = text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            if end == -1:
                raise ValidationError("Unclosed code block")
            json_text = text[start:end].strip()
        else:
            json_text = text.strip()

        if not json_text:
            raise ValidationError("Empty JSON content")

        return json.loads(json_text)

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}")
        raise ValidationError(f"Failed to parse JSON: {e}")
    except Exception as e:
        logger.error(f"Unexpected error extracting JSON: {e}")
        raise ValidationError(f"Failed to extract JSON from text: {e}")


def validate_file_path(file_path: Path, allowed_extensions: list[str] | None = None, max_size_mb: int = 500) -> None:
    """
    Validate file path for security and existence.

    Args:
        file_path: Path to validate
        allowed_extensions: List of allowed file extensions (e.g., ['.csv', '.json'])
        max_size_mb: Maximum allowed file size in MB

    Raises:
        ValidationError: If file path is invalid or unsafe
    """
    # Check if path exists
    if not file_path.exists():
        raise ValidationError(f"File does not exist: {file_path}")

    # Check if it's a file
    if not file_path.is_file():
        raise ValidationError(f"Path is not a file: {file_path}")

    # Check for path traversal attacks
    try:
        file_path.resolve(strict=True)
    except (OSError, RuntimeError) as e:
        raise ValidationError(f"Invalid file path: {e}")

    # Check file extension
    if allowed_extensions:
        if file_path.suffix.lower() not in [ext.lower() for ext in allowed_extensions]:
            raise ValidationError(
                f"File extension {file_path.suffix} not allowed. Allowed: {', '.join(allowed_extensions)}"
            )

    # Check file size
    file_size_mb = file_path.stat().st_size / (1024 * 1024)
    if file_size_mb > max_size_mb:
        raise ValidationError(f"File size ({file_size_mb:.2f} MB) exceeds maximum ({max_size_mb} MB)")

    logger.debug(f"File path validation successful: {file_path}")


def sanitize_user_input(user_input: str, max_length: int = 10000) -> str:
    """
    Sanitize user input to prevent injection attacks.

    Args:
        user_input: Raw user input
        max_length: Maximum allowed length

    Returns:
        Sanitized input

    Raises:
        ValidationError: If input is invalid
    """
    if not isinstance(user_input, str):
        raise ValidationError("Input must be a string")

    # Remove null bytes
    sanitized = user_input.replace("\x00", "")

    # Check length
    if len(sanitized) > max_length:
        raise ValidationError(f"Input too long (max {max_length} characters)")

    # Strip leading/trailing whitespace
    sanitized = sanitized.strip()

    if not sanitized:
        raise ValidationError("Input cannot be empty after sanitization")

    return sanitized


def format_bytes(size_bytes: int) -> str:
    """
    Format bytes to human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def merge_dicts(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries.

    Args:
        base: Base dictionary
        override: Override dictionary

    Returns:
        Merged dictionary
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result
