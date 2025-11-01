"""
Best-First Search reasoning for synthetic data generation.

Ideal for time-series data, sequential patterns, and scenarios where
prioritizing the most promising paths leads to better results.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import copy
import heapq

from .base import BaseReasoningStrategy, ReasoningResult


@dataclass(order=True)
class PrioritizedNode:
    """Node with priority for best-first search."""
    priority: float
    requirements: Dict[str, Any] = field(compare=False)
    depth: int = field(default=0, compare=False)


class BestFirstSearchReasoner(BaseReasoningStrategy):
    """
    Best-First Search reasoning strategy.

    Prioritizes the most promising requirement enhancement paths,
    ideal for sequential and time-series data generation.
    """

    def __init__(self, config: Optional[Any] = None):
        """Initialize Best-First Search reasoner."""
        super().__init__(config)

        self.max_nodes = 20
        self.max_depth = 5

    async def reason(
        self,
        requirements: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> ReasoningResult:
        """
        Apply best-first search reasoning.

        Args:
            requirements: Initial requirements
            context: Optional context

        Returns:
            ReasoningResult with best requirements
        """
        self.logger.info("Starting Best-First Search reasoning")

        reasoning_steps = [
            "Initializing Best-First Search",
            f"Maximum nodes to explore: {self.max_nodes}",
        ]

        # Priority queue (min-heap, so we negate priorities)
        initial_priority = -self._heuristic(requirements)
        queue = [PrioritizedNode(
            priority=initial_priority,
            requirements=copy.deepcopy(requirements),
            depth=0,
        )]

        best_node = None
        best_score = float('-inf')
        nodes_explored = 0

        while queue and nodes_explored < self.max_nodes:
            # Pop most promising node
            current = heapq.heappop(queue)
            nodes_explored += 1

            reasoning_steps.append(
                f"Exploring node {nodes_explored} (priority: {-current.priority:.3f}, depth: {current.depth})"
            )

            # Evaluate current node
            score = self._evaluate(current.requirements)

            if score > best_score:
                best_score = score
                best_node = current
                reasoning_steps.append(f"  → New best score: {score:.3f}")

            # Expand if not at max depth
            if current.depth < self.max_depth:
                successors = self._generate_successors(current)

                for successor in successors:
                    heapq.heappush(queue, successor)

        reasoning_steps.extend([
            f"Explored {nodes_explored} nodes",
            f"Best configuration score: {best_score:.3f}",
        ])

        confidence = min(1.0, best_score)

        self.logger.info(
            "Best-First Search completed",
            nodes_explored=nodes_explored,
            best_score=best_score,
        )

        return ReasoningResult(
            enhanced_requirements=best_node.requirements,
            reasoning_steps=reasoning_steps,
            confidence=confidence,
            metadata={
                "nodes_explored": nodes_explored,
                "best_score": best_score,
                "final_depth": best_node.depth,
            },
        )

    def _heuristic(self, requirements: Dict[str, Any]) -> float:
        """
        Heuristic function to estimate promise of requirements.

        Higher values = more promising.
        """
        score = 0.0

        # Favor specifications with temporal fields
        if "fields" in requirements:
            for field in requirements.get("fields", []):
                if isinstance(field, dict):
                    field_name = field.get("name", "").lower()
                    field_type = field.get("type", "").lower()

                    if any(kw in field_name for kw in ["time", "date", "timestamp"]):
                        score += 0.3

                    if "datetime" in field_type or "timestamp" in field_type:
                        score += 0.2

        # Favor sequential constraints
        if "constraints" in requirements:
            for constraint in requirements.get("constraints", []):
                if isinstance(constraint, str):
                    if "sequential" in constraint.lower() or "order" in constraint.lower():
                        score += 0.2

        # Favor time-series quality requirements
        if "quality_requirements" in requirements:
            quality = requirements["quality_requirements"]
            if "temporal_consistency" in quality:
                score += 0.2

        return score

    def _evaluate(self, requirements: Dict[str, Any]) -> float:
        """Evaluate quality of requirements."""
        score = 0.3  # Base score

        # Completeness
        if "fields" in requirements:
            score += 0.2

        if "constraints" in requirements:
            score += 0.15

        if "quality_requirements" in requirements:
            score += 0.15

        # Time-series specific
        if self._has_temporal_fields(requirements):
            score += 0.2

        return min(1.0, score)

    def _has_temporal_fields(self, requirements: Dict[str, Any]) -> bool:
        """Check if requirements have temporal fields."""
        if "fields" not in requirements:
            return False

        for field in requirements.get("fields", []):
            if isinstance(field, dict):
                field_name = field.get("name", "").lower()
                if any(kw in field_name for kw in ["time", "date", "timestamp"]):
                    return True

        return False

    def _generate_successors(self, node: PrioritizedNode) -> List[PrioritizedNode]:
        """Generate successor nodes."""
        successors = []

        # Enhancement 1: Add temporal constraints
        variant1 = copy.deepcopy(node.requirements)
        if "constraints" not in variant1:
            variant1["constraints"] = []
        variant1["constraints"].append("Maintain temporal ordering")

        priority1 = -self._heuristic(variant1)
        successors.append(PrioritizedNode(
            priority=priority1,
            requirements=variant1,
            depth=node.depth + 1,
        ))

        # Enhancement 2: Add time-series quality
        variant2 = copy.deepcopy(node.requirements)
        if "quality_requirements" not in variant2:
            variant2["quality_requirements"] = {}
        variant2["quality_requirements"]["temporal_consistency"] = True

        priority2 = -self._heuristic(variant2)
        successors.append(PrioritizedNode(
            priority=priority2,
            requirements=variant2,
            depth=node.depth + 1,
        ))

        return successors

    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about Best-First Search reasoning."""
        return {
            "name": "best_first_search",
            "description": "Best-First Search - Prioritizes most promising paths for sequential data",
            "use_cases": [
                "Time-series data generation",
                "Sequential pattern generation",
                "Temporal data with ordering",
                "Event streams",
            ],
            "parameters": {
                "max_nodes": self.max_nodes,
                "max_depth": self.max_depth,
            },
            "strengths": [
                "Efficient for sequential data",
                "Prioritizes promising paths",
                "Good heuristic-based exploration",
                "Fast convergence",
            ],
            "limitations": [
                "Depends on heuristic quality",
                "May miss optimal solution",
                "Not exhaustive",
            ],
        }
