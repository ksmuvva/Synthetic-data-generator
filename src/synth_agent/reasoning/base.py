"""
Base reasoning strategy interface for synthetic data generation.

All reasoning methods implement this interface to ensure consistent behavior.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime

import structlog


logger = structlog.get_logger(__name__)


@dataclass
class ReasoningResult:
    """
    Result of a reasoning operation.

    Attributes:
        enhanced_requirements: Updated requirements after reasoning
        reasoning_steps: List of reasoning steps taken
        confidence: Confidence score (0-1)
        metadata: Additional metadata about the reasoning process
        execution_time: Time taken to execute reasoning (seconds)
        method_used: Name of reasoning method used
    """
    enhanced_requirements: Dict[str, Any]
    reasoning_steps: List[str] = field(default_factory=list)
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    method_used: str = ""
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "enhanced_requirements": self.enhanced_requirements,
            "reasoning_steps": self.reasoning_steps,
            "confidence": self.confidence,
            "metadata": self.metadata,
            "execution_time": self.execution_time,
            "method_used": self.method_used,
            "timestamp": self.timestamp.isoformat(),
        }


class BaseReasoningStrategy(ABC):
    """
    Abstract base class for all reasoning strategies.

    Each reasoning method implements this interface to provide consistent
    behavior across different cognitive approaches.
    """

    def __init__(self, config: Optional[Any] = None):
        """
        Initialize reasoning strategy.

        Args:
            config: Configuration object (typically Config with ReasoningConfig)
        """
        self.config = config
        self.logger = structlog.get_logger(self.__class__.__name__)

    @abstractmethod
    async def reason(
        self,
        requirements: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> ReasoningResult:
        """
        Apply reasoning to enhance requirements.

        Args:
            requirements: Initial data requirements
            context: Optional context information

        Returns:
            ReasoningResult with enhanced requirements and metadata
        """
        pass

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about this reasoning method.

        Returns:
            Dictionary containing:
                - name: Method name
                - description: What this method does
                - use_cases: List of ideal use cases
                - parameters: Configurable parameters
                - strengths: What this method is good at
                - limitations: Known limitations
        """
        pass

    def get_name(self) -> str:
        """Get the name of this reasoning method."""
        return self.get_metadata().get("name", self.__class__.__name__)

    def get_description(self) -> str:
        """Get the description of this reasoning method."""
        return self.get_metadata().get("description", "")

    def get_use_cases(self) -> List[str]:
        """Get the ideal use cases for this reasoning method."""
        return self.get_metadata().get("use_cases", [])

    async def validate_requirements(self, requirements: Dict[str, Any]) -> bool:
        """
        Validate that requirements are suitable for this reasoning method.

        Args:
            requirements: Requirements to validate

        Returns:
            True if requirements are valid
        """
        # Basic validation - subclasses can override
        if not requirements:
            self.logger.warning("Empty requirements provided")
            return False

        if "fields" not in requirements and "data_type" not in requirements:
            self.logger.warning("Requirements missing fields or data_type")
            return False

        return True

    def _extract_domain(self, requirements: Dict[str, Any]) -> Optional[str]:
        """
        Extract domain/use case from requirements.

        Args:
            requirements: Data requirements

        Returns:
            Detected domain or None
        """
        # Check explicit domain field
        if "domain" in requirements:
            return requirements["domain"].lower()

        # Check data_type field
        if "data_type" in requirements:
            data_type = requirements["data_type"].lower()

            # Financial keywords
            if any(kw in data_type for kw in ["financial", "transaction", "payment", "trading"]):
                return "financial"

            # Healthcare keywords
            if any(kw in data_type for kw in ["patient", "medical", "healthcare", "diagnosis"]):
                return "healthcare"

            # E-commerce keywords
            if any(kw in data_type for kw in ["product", "order", "ecommerce", "retail"]):
                return "ecommerce"

            # Network keywords
            if any(kw in data_type for kw in ["network", "graph", "social", "connection"]):
                return "network"

        return None
