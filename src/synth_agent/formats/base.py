"""
Base formatter interface for all output formats.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict

import pandas as pd


class BaseFormatter(ABC):
    """Abstract base class for format handlers."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize formatter.

        Args:
            config: Format-specific configuration
        """
        self.config = config

    @abstractmethod
    def export(self, df: pd.DataFrame, output_path: Path) -> None:
        """
        Export DataFrame to file.

        Args:
            df: DataFrame to export
            output_path: Output file path
        """
        pass

    @abstractmethod
    def get_extension(self) -> str:
        """
        Get file extension for this format.

        Returns:
            File extension (including dot)
        """
        pass

    @abstractmethod
    def validate(self, df: pd.DataFrame) -> bool:
        """
        Validate DataFrame can be exported in this format.

        Args:
            df: DataFrame to validate

        Returns:
            True if valid
        """
        pass
