"""
A* Search reasoning for synthetic data generation.

Ideal for optimization problems, scheduling data, and resource allocation
scenarios requiring optimal path finding with heuristics.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import copy
import heapq

from .base import BaseReasoningStrategy, ReasoningResult


@dataclass(order=True)
class AStarNode:
    """Node for A* search."""
    f_score: float  # f(n) = g(n) + h(n)
    g_score: float = field(compare=False)  # Cost from start
    h_score: float = field(compare=False)  # Heuristic to goal
    requirements: Dict[str, Any] = field(compare=False)
    depth: int = field(default=0, compare=False)


class AStarReasoner(BaseReasoningStrategy):
    """
    A* Search reasoning strategy.

    Uses cost and heuristic functions to find optimal requirement
    enhancements for optimization and scheduling scenarios.
    """

    def __init__(self, config: Optional[Any] = None):
        """Initialize A* reasoner."""
        super().__init__(config)

        self.max_nodes = 30

    async def reason(
        self,
        requirements: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> ReasoningResult:
        """
        Apply A* search reasoning.

        Args:
            requirements: Initial requirements
            context: Optional context

        Returns:
            ReasoningResult with optimal requirements
        """
        self.logger.info("Starting A* Search reasoning")

        reasoning_steps = [
            "Initializing A* Search",
            "Using cost + heuristic for optimal path finding",
        ]

        # Initialize
        g_score = 0.0
        h_score = self._heuristic(requirements)
        f_score = g_score + h_score

        start_node = AStarNode(
            f_score=f_score,
            g_score=g_score,
            h_score=h_score,
            requirements=copy.deepcopy(requirements),
            depth=0,
        )

        open_set = [start_node]
        closed_set = set()

        best_node = start_node
        nodes_explored = 0

        while open_set and nodes_explored < self.max_nodes:
            # Pop node with lowest f_score
            current = heapq.heappop(open_set)
            nodes_explored += 1

            reasoning_steps.append(
                f"Node {nodes_explored}: f={current.f_score:.3f} (g={current.g_score:.3f}, h={current.h_score:.3f})"
            )

            # Check if goal reached
            if self._is_goal(current.requirements):
                best_node = current
                reasoning_steps.append("  ✓ Goal state reached!")
                break

            # Update best if better
            if current.h_score < best_node.h_score:
                best_node = current

            # Add to closed set
            closed_set.add(id(current))

            # Generate successors
            successors = self._generate_successors(current)

            for successor in successors:
                if id(successor) not in closed_set:
                    heapq.heappush(open_set, successor)

        reasoning_steps.extend([
            f"Explored {nodes_explored} nodes",
            f"Final heuristic score: {best_node.h_score:.3f}",
            "Optimal configuration found",
        ])

        confidence = max(0.5, 1.0 - best_node.h_score)

        self.logger.info(
            "A* Search completed",
            nodes_explored=nodes_explored,
            confidence=confidence,
        )

        return ReasoningResult(
            enhanced_requirements=best_node.requirements,
            reasoning_steps=reasoning_steps,
            confidence=confidence,
            metadata={
                "nodes_explored": nodes_explored,
                "final_g_score": best_node.g_score,
                "final_h_score": best_node.h_score,
                "final_f_score": best_node.f_score,
            },
        )

    def _heuristic(self, requirements: Dict[str, Any]) -> float:
        """
        Heuristic function estimating distance to goal.

        Lower values = closer to goal.
        """
        distance = 1.0  # Start far from goal

        # Goal: Have optimization-related specifications
        if "constraints" in requirements:
            constraints = requirements["constraints"]
            if any(
                isinstance(c, str) and ("optim" in c.lower() or "schedule" in c.lower())
                for c in constraints
            ):
                distance -= 0.3

        # Goal: Have resource allocation fields
        if "fields" in requirements:
            for field in requirements.get("fields", []):
                if isinstance(field, dict):
                    name = field.get("name", "").lower()
                    if any(kw in name for kw in ["resource", "allocation", "capacity", "schedule"]):
                        distance -= 0.2
                        break

        # Goal: Have optimization quality requirements
        if "quality_requirements" in requirements:
            quality = requirements["quality_requirements"]
            if "optimization_level" in quality:
                distance -= 0.3

        return max(0.0, distance)

    def _is_goal(self, requirements: Dict[str, Any]) -> bool:
        """Check if requirements represent goal state."""
        return self._heuristic(requirements) <= 0.1

    def _generate_successors(self, node: AStarNode) -> List[AStarNode]:
        """Generate successor nodes with costs."""
        successors = []

        # Action 1: Add optimization constraints (cost: 0.1)
        variant1 = copy.deepcopy(node.requirements)
        if "constraints" not in variant1:
            variant1["constraints"] = []
        variant1["constraints"].append("Optimize for efficiency")

        g1 = node.g_score + 0.1
        h1 = self._heuristic(variant1)
        successors.append(AStarNode(
            f_score=g1 + h1,
            g_score=g1,
            h_score=h1,
            requirements=variant1,
            depth=node.depth + 1,
        ))

        # Action 2: Add resource fields (cost: 0.2)
        variant2 = copy.deepcopy(node.requirements)
        if "quality_requirements" not in variant2:
            variant2["quality_requirements"] = {}
        variant2["quality_requirements"]["optimization_level"] = "high"

        g2 = node.g_score + 0.2
        h2 = self._heuristic(variant2)
        successors.append(AStarNode(
            f_score=g2 + h2,
            g_score=g2,
            h_score=h2,
            requirements=variant2,
            depth=node.depth + 1,
        ))

        return successors

    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about A* Search reasoning."""
        return {
            "name": "astar",
            "description": "A* Search - Optimal path finding for optimization and scheduling data",
            "use_cases": [
                "Optimization problem data",
                "Scheduling and planning data",
                "Resource allocation scenarios",
                "Constraint satisfaction problems",
            ],
            "parameters": {
                "max_nodes": self.max_nodes,
            },
            "strengths": [
                "Optimal solution finding",
                "Efficient with good heuristic",
                "Complete algorithm",
                "Guaranteed optimality",
            ],
            "limitations": [
                "Requires good heuristic",
                "Memory intensive",
                "May be slower than greedy methods",
            ],
        }
