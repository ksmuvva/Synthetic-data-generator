"""
File validation utilities for document upload and format detection.

Supports: .txt, .json, .csv, .xlsx, .md, .pdf
"""

import mimetypes
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import structlog

logger = structlog.get_logger(__name__)


class FileValidator:
    """Validates uploaded files for pattern analysis."""

    # Supported formats with extensions and MIME types
    SUPPORTED_FORMATS = {
        "txt": {
            "extensions": [".txt"],
            "mime_types": ["text/plain"],
            "description": "Plain text file",
        },
        "json": {
            "extensions": [".json"],
            "mime_types": ["application/json", "text/json"],
            "description": "JSON data file",
        },
        "csv": {
            "extensions": [".csv"],
            "mime_types": ["text/csv", "application/csv"],
            "description": "Comma-separated values file",
        },
        "xlsx": {
            "extensions": [".xlsx", ".xls"],
            "mime_types": [
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "application/vnd.ms-excel",
            ],
            "description": "Excel spreadsheet",
        },
        "md": {
            "extensions": [".md", ".markdown"],
            "mime_types": ["text/markdown", "text/x-markdown"],
            "description": "Markdown document",
        },
        "pdf": {
            "extensions": [".pdf"],
            "mime_types": ["application/pdf"],
            "description": "PDF document",
        },
    }

    @staticmethod
    def validate_file(file_path: str | Path) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate file exists, is readable, and has supported format.

        Args:
            file_path: Path to file

        Returns:
            Tuple of (is_valid, validation_result)
            validation_result contains: format, size, error_message, file_info
        """
        result: Dict[str, Any] = {
            "valid": False,
            "format": None,
            "size": None,
            "error_message": None,
            "file_info": {},
        }

        try:
            path = Path(file_path)

            # Check file exists
            if not path.exists():
                result["error_message"] = f"File not found: {file_path}"
                logger.warning("File not found", path=str(file_path))
                return False, result

            # Check it's a file (not directory)
            if not path.is_file():
                result["error_message"] = f"Path is not a file: {file_path}"
                logger.warning("Path is not a file", path=str(file_path))
                return False, result

            # Check file is readable
            try:
                with open(path, "rb") as f:
                    f.read(1)  # Try to read 1 byte
            except PermissionError:
                result["error_message"] = f"File not readable (permission denied): {file_path}"
                logger.warning("File not readable", path=str(file_path))
                return False, result
            except Exception as e:
                result["error_message"] = f"File not readable: {str(e)}"
                logger.warning("File not readable", path=str(file_path), error=str(e))
                return False, result

            # Get file size
            file_size = path.stat().st_size
            result["size"] = file_size

            # Check if file is empty
            if file_size == 0:
                result["error_message"] = "File is empty"
                logger.warning("File is empty", path=str(file_path))
                return False, result

            # Detect format by extension
            extension = path.suffix.lower()
            detected_format = None

            for format_name, format_info in FileValidator.SUPPORTED_FORMATS.items():
                if extension in format_info["extensions"]:
                    detected_format = format_name
                    break

            if not detected_format:
                supported_exts = []
                for fmt_info in FileValidator.SUPPORTED_FORMATS.values():
                    supported_exts.extend(fmt_info["extensions"])
                result["error_message"] = (
                    f"Unsupported file format: {extension}. "
                    f"Supported: {', '.join(supported_exts)}"
                )
                logger.warning("Unsupported format", path=str(file_path), extension=extension)
                return False, result

            # Check for corrupted files (basic check)
            try:
                is_corrupted, corruption_message = FileValidator._check_corruption(
                    path, detected_format
                )
                if is_corrupted:
                    result["error_message"] = f"File appears corrupted: {corruption_message}"
                    logger.warning("File corrupted", path=str(file_path), message=corruption_message)
                    return False, result
            except Exception as e:
                logger.warning("Corruption check failed", path=str(file_path), error=str(e))
                # Don't fail validation if corruption check fails

            # Populate result
            result["valid"] = True
            result["format"] = detected_format
            result["file_info"] = {
                "name": path.name,
                "size": file_size,
                "size_human": FileValidator._format_size(file_size),
                "extension": extension,
                "format": detected_format,
                "description": FileValidator.SUPPORTED_FORMATS[detected_format]["description"],
                "absolute_path": str(path.absolute()),
            }

            logger.info(
                "File validated successfully",
                path=str(file_path),
                format=detected_format,
                size=file_size,
            )

            return True, result

        except Exception as e:
            result["error_message"] = f"Validation error: {str(e)}"
            logger.error("File validation error", path=str(file_path), error=str(e))
            return False, result

    @staticmethod
    def _check_corruption(path: Path, format_type: str) -> Tuple[bool, Optional[str]]:
        """
        Basic corruption check for different file types.

        Args:
            path: File path
            format_type: Detected format type

        Returns:
            Tuple of (is_corrupted, error_message)
        """
        try:
            if format_type == "json":
                import json

                with open(path, "r", encoding="utf-8") as f:
                    json.load(f)

            elif format_type == "csv":
                import csv

                with open(path, "r", encoding="utf-8") as f:
                    csv.reader(f).__next__()  # Try reading first row

            elif format_type == "xlsx":
                import openpyxl

                openpyxl.load_workbook(path, read_only=True, data_only=True)

            elif format_type == "pdf":
                # Basic PDF check - verify header
                with open(path, "rb") as f:
                    header = f.read(5)
                    if header != b"%PDF-":
                        return True, "Invalid PDF header"

            # For txt and md, just check if it's valid UTF-8
            elif format_type in ["txt", "md"]:
                with open(path, "r", encoding="utf-8") as f:
                    f.read(100)  # Try reading first 100 chars

            return False, None

        except json.JSONDecodeError:
            return True, "Invalid JSON structure"
        except csv.Error as e:
            return True, f"Invalid CSV structure: {str(e)}"
        except Exception as e:
            return True, f"File appears corrupted: {str(e)}"

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """
        Format file size in human-readable format.

        Args:
            size_bytes: Size in bytes

        Returns:
            Human-readable size string
        """
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    @staticmethod
    def get_supported_formats() -> Dict[str, Any]:
        """
        Get list of supported formats.

        Returns:
            Dictionary of supported formats with metadata
        """
        return FileValidator.SUPPORTED_FORMATS
