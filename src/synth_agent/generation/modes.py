"""
Generation modes for synthetic data.

Modes:
- exact_match: Closely mirrors original statistical properties
- realistic_variant: Similar patterns with intentional variance
- edge_case: Include boundary conditions and outliers
- balanced: Mix of typical and edge cases
"""

from typing import Dict, Any, Optional
from enum import Enum
import structlog

logger = structlog.get_logger(__name__)


class GenerationMode(str, Enum):
    """Generation mode enumeration."""
    EXACT_MATCH = "exact_match"
    REALISTIC_VARIANT = "realistic_variant"
    EDGE_CASE = "edge_case"
    BALANCED = "balanced"


class GenerationModeConfig:
    """
    Configuration for different generation modes.
    """

    MODES = {
        GenerationMode.EXACT_MATCH: {
            "name": "Exact Match",
            "description": "Closely mirrors original statistical properties",
            "variance_multiplier": 0.1,  # Very low variance
            "include_outliers": False,
            "outlier_ratio": 0.0,
            "distribution_fidelity": 0.99,  # 99% match to original
            "edge_case_ratio": 0.01,  # 1% edge cases
            "use_case": "When you need synthetic data that very closely matches the original patterns",
        },
        GenerationMode.REALISTIC_VARIANT: {
            "name": "Realistic Variant",
            "description": "Similar patterns with intentional variance",
            "variance_multiplier": 1.2,  # 20% more variance
            "include_outliers": True,
            "outlier_ratio": 0.05,  # 5% outliers
            "distribution_fidelity": 0.85,  # 85% match
            "edge_case_ratio": 0.10,  # 10% edge cases
            "use_case": "When you need realistic data with natural variation",
        },
        GenerationMode.EDGE_CASE: {
            "name": "Edge Case",
            "description": "Include boundary conditions and outliers",
            "variance_multiplier": 2.0,  # 2x variance
            "include_outliers": True,
            "outlier_ratio": 0.30,  # 30% outliers
            "distribution_fidelity": 0.60,  # 60% match
            "edge_case_ratio": 0.50,  # 50% edge cases
            "use_case": "For stress testing and boundary condition testing",
        },
        GenerationMode.BALANCED: {
            "name": "Balanced",
            "description": "Mix of typical and edge cases",
            "variance_multiplier": 1.0,  # Normal variance
            "include_outliers": True,
            "outlier_ratio": 0.10,  # 10% outliers
            "distribution_fidelity": 0.90,  # 90% match
            "edge_case_ratio": 0.20,  # 20% edge cases
            "use_case": "General purpose synthetic data with good coverage",
        },
    }

    @classmethod
    def get_mode_config(cls, mode: GenerationMode | str) -> Dict[str, Any]:
        """
        Get configuration for a specific generation mode.

        Args:
            mode: Generation mode

        Returns:
            Mode configuration dictionary
        """
        if isinstance(mode, str):
            try:
                mode = GenerationMode(mode)
            except ValueError:
                logger.warning(f"Invalid mode: {mode}, using balanced")
                mode = GenerationMode.BALANCED

        config = cls.MODES.get(mode, cls.MODES[GenerationMode.BALANCED])
        logger.info("Retrieved mode config", mode=mode.value, name=config["name"])

        return config.copy()

    @classmethod
    def list_modes(cls) -> Dict[str, Dict[str, Any]]:
        """
        List all available generation modes.

        Returns:
            Dictionary of modes with descriptions
        """
        return {
            mode.value: {
                "name": config["name"],
                "description": config["description"],
                "use_case": config["use_case"],
            }
            for mode, config in cls.MODES.items()
        }


class ModeAwareGenerator:
    """
    Wrapper that applies mode-specific adjustments to data generation.
    """

    def __init__(self, mode: GenerationMode | str = GenerationMode.BALANCED):
        """
        Initialize mode-aware generator.

        Args:
            mode: Generation mode to use
        """
        self.mode = mode if isinstance(mode, GenerationMode) else GenerationMode(mode)
        self.config = GenerationModeConfig.get_mode_config(self.mode)

        logger.info("ModeAwareGenerator initialized", mode=self.mode.value)

    def adjust_parameters(self, base_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adjust generation parameters based on mode.

        Args:
            base_params: Base generation parameters

        Returns:
            Adjusted parameters
        """
        adjusted = base_params.copy()

        # Apply variance multiplier
        if "variance" in adjusted:
            adjusted["variance"] *= self.config["variance_multiplier"]

        # Apply outlier settings
        adjusted["include_outliers"] = self.config["include_outliers"]
        adjusted["outlier_ratio"] = self.config["outlier_ratio"]

        # Apply edge case ratio
        adjusted["edge_case_ratio"] = self.config["edge_case_ratio"]

        # Apply distribution fidelity
        adjusted["distribution_fidelity"] = self.config["distribution_fidelity"]

        logger.debug(
            "Parameters adjusted",
            mode=self.mode.value,
            variance_mult=self.config["variance_multiplier"],
        )

        return adjusted

    def should_generate_outlier(self, field_name: str, row_index: int, total_rows: int) -> bool:
        """
        Determine if this row should be an outlier for the given field.

        Args:
            field_name: Name of the field
            row_index: Current row index
            total_rows: Total number of rows

        Returns:
            True if should generate outlier
        """
        if not self.config["include_outliers"]:
            return False

        # Use deterministic approach based on row index
        outlier_frequency = int(1.0 / max(self.config["outlier_ratio"], 0.01))
        return row_index % outlier_frequency == 0

    def should_generate_edge_case(self, field_name: str, row_index: int, total_rows: int) -> bool:
        """
        Determine if this row should be an edge case.

        Args:
            field_name: Name of the field
            row_index: Current row index
            total_rows: Total number of rows

        Returns:
            True if should generate edge case
        """
        edge_case_frequency = int(1.0 / max(self.config["edge_case_ratio"], 0.01))
        return row_index % edge_case_frequency == 0

    def get_variance_multiplier(self) -> float:
        """Get variance multiplier for this mode."""
        return self.config["variance_multiplier"]

    def get_distribution_fidelity(self) -> float:
        """Get distribution fidelity target for this mode."""
        return self.config["distribution_fidelity"]


def select_mode_from_requirements(requirements: Dict[str, Any]) -> GenerationMode:
    """
    Auto-select generation mode based on requirements.

    Args:
        requirements: Data generation requirements

    Returns:
        Recommended generation mode
    """
    # Check for explicit mode request
    if "generation_mode" in requirements:
        mode_str = requirements["generation_mode"]
        try:
            return GenerationMode(mode_str)
        except ValueError:
            logger.warning(f"Invalid mode in requirements: {mode_str}")

    # Auto-detect based on use case
    use_case = requirements.get("use_case", "").lower()

    if "test" in use_case or "edge" in use_case or "stress" in use_case:
        return GenerationMode.EDGE_CASE

    if "exact" in use_case or "match" in use_case or "precise" in use_case:
        return GenerationMode.EXACT_MATCH

    if "variant" in use_case or "diverse" in use_case:
        return GenerationMode.REALISTIC_VARIANT

    # Default to balanced
    return GenerationMode.BALANCED
