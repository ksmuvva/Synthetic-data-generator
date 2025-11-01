"""
Metrics tracking for reasoning operations.

Tracks performance, quality, and usage statistics for reasoning methods.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any
from datetime import datetime
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ReasoningMetrics:
    """Metrics for reasoning operations."""

    method_name: str
    execution_time: float = 0.0
    confidence_score: float = 0.0
    steps_count: int = 0
    success: bool = True
    error_message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "method_name": self.method_name,
            "execution_time": self.execution_time,
            "confidence_score": self.confidence_score,
            "steps_count": self.steps_count,
            "success": self.success,
            "error_message": self.error_message,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


class MetricsTracker:
    """Tracks and aggregates reasoning metrics."""

    def __init__(self):
        """Initialize metrics tracker."""
        self.metrics_history: List[ReasoningMetrics] = []

    def record(self, metrics: ReasoningMetrics) -> None:
        """
        Record metrics for a reasoning operation.

        Args:
            metrics: Metrics to record
        """
        self.metrics_history.append(metrics)
        logger.info(
            "Reasoning metrics recorded",
            method=metrics.method_name,
            execution_time=metrics.execution_time,
            confidence=metrics.confidence_score,
            success=metrics.success,
        )

    def get_summary(self, method_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get summary statistics.

        Args:
            method_name: Optional filter by method name

        Returns:
            Dictionary with summary statistics
        """
        if method_name:
            filtered = [m for m in self.metrics_history if m.method_name == method_name]
        else:
            filtered = self.metrics_history

        if not filtered:
            return {
                "total_runs": 0,
                "success_rate": 0.0,
                "avg_execution_time": 0.0,
                "avg_confidence": 0.0,
            }

        total = len(filtered)
        successes = sum(1 for m in filtered if m.success)
        avg_time = sum(m.execution_time for m in filtered) / total
        avg_confidence = sum(m.confidence_score for m in filtered) / total

        return {
            "total_runs": total,
            "success_rate": successes / total,
            "avg_execution_time": avg_time,
            "avg_confidence": avg_confidence,
            "method_name": method_name,
        }

    def clear(self) -> None:
        """Clear all metrics history."""
        self.metrics_history.clear()
        logger.info("Metrics history cleared")


# Global metrics tracker instance
_global_tracker = MetricsTracker()


def get_metrics_tracker() -> MetricsTracker:
    """Get the global metrics tracker instance."""
    return _global_tracker
