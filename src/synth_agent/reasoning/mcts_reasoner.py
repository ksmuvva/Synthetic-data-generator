"""
Monte Carlo Tree Search (MCTS) reasoning for synthetic data generation.

Ideal for financial data, risk analysis, and scenarios requiring exploration
of multiple generation paths to find optimal distributions.
"""

import random
import math
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import copy

from .base import BaseReasoningStrategy, ReasoningResult


@dataclass
class MCTSNode:
    """Node in the MCTS tree."""
    requirements: Dict[str, Any]
    visits: int = 0
    value: float = 0.0
    parent: Optional['MCTSNode'] = None
    children: List['MCTSNode'] = None

    def __post_init__(self):
        if self.children is None:
            self.children = []


class MCTSReasoner(BaseReasoningStrategy):
    """
    Monte Carlo Tree Search reasoning strategy.

    Explores multiple requirement enhancement paths and selects the best one
    based on simulated outcomes. Ideal for financial and risk analysis scenarios.
    """

    def __init__(self, config: Optional[Any] = None):
        """Initialize MCTS reasoner."""
        super().__init__(config)

        # MCTS parameters
        self.iterations = 100
        self.exploration_factor = math.sqrt(2)

        if config and hasattr(config, "reasoning"):
            self.iterations = getattr(config.reasoning, "mcts_iterations", 100)
            self.exploration_factor = getattr(
                config.reasoning, "mcts_exploration_factor", math.sqrt(2)
            )

    async def reason(
        self,
        requirements: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> ReasoningResult:
        """
        Apply MCTS reasoning to enhance requirements.

        Args:
            requirements: Initial requirements
            context: Optional context

        Returns:
            ReasoningResult with best requirements found
        """
        self.logger.info("Starting MCTS reasoning", iterations=self.iterations)

        reasoning_steps = [
            "Initializing Monte Carlo Tree Search",
            f"Running {self.iterations} simulations",
        ]

        # Create root node
        root = MCTSNode(requirements=copy.deepcopy(requirements))

        # Run MCTS iterations
        for i in range(self.iterations):
            # Selection
            node = self._select(root)

            # Expansion
            if node.visits > 0:
                node = self._expand(node)

            # Simulation
            value = self._simulate(node)

            # Backpropagation
            self._backpropagate(node, value)

            if (i + 1) % 20 == 0:
                reasoning_steps.append(f"Completed {i + 1} simulations")

        # Select best child
        best_node = max(root.children, key=lambda n: n.value / max(n.visits, 1))

        reasoning_steps.extend([
            f"Explored {len(root.children)} requirement variations",
            "Selected optimal requirement configuration",
            f"Best configuration quality score: {best_node.value / max(best_node.visits, 1):.3f}",
        ])

        confidence = min(1.0, best_node.value / max(best_node.visits, 1))

        self.logger.info(
            "MCTS reasoning completed",
            nodes_explored=len(root.children),
            confidence=confidence,
        )

        return ReasoningResult(
            enhanced_requirements=best_node.requirements,
            reasoning_steps=reasoning_steps,
            confidence=confidence,
            metadata={
                "iterations": self.iterations,
                "nodes_explored": len(root.children),
                "best_visits": best_node.visits,
                "best_value": best_node.value,
            },
        )

    def _select(self, node: MCTSNode) -> MCTSNode:
        """Select most promising node using UCB1."""
        while node.children:
            node = max(node.children, key=lambda n: self._ucb1(n))
        return node

    def _ucb1(self, node: MCTSNode) -> float:
        """Calculate UCB1 score for node selection."""
        if node.visits == 0:
            return float('inf')

        exploitation = node.value / node.visits
        exploration = self.exploration_factor * math.sqrt(
            math.log(node.parent.visits) / node.visits
        )
        return exploitation + exploration

    def _expand(self, node: MCTSNode) -> MCTSNode:
        """Expand node by creating child with modified requirements."""
        # Create variations of requirements
        child_requirements = self._create_variation(node.requirements)

        child = MCTSNode(
            requirements=child_requirements,
            parent=node,
        )
        node.children.append(child)
        return child

    def _simulate(self, node: MCTSNode) -> float:
        """Simulate quality of requirements."""
        requirements = node.requirements

        # Quality scoring based on completeness and consistency
        score = 0.0

        # Check for essential fields
        if "fields" in requirements:
            score += 0.3
            fields = requirements["fields"]

            # Bonus for detailed field specifications
            if isinstance(fields, list):
                for field in fields:
                    if isinstance(field, dict):
                        if "type" in field:
                            score += 0.05
                        if "constraints" in field:
                            score += 0.05

        # Check for constraints
        if "constraints" in requirements and requirements["constraints"]:
            score += 0.2

        # Check for relationships (important for financial data)
        if "relationships" in requirements and requirements["relationships"]:
            score += 0.2

        # Check for quality requirements
        if "quality_requirements" in requirements:
            score += 0.15

        # Add randomness to simulate uncertainty
        score += random.uniform(-0.1, 0.1)

        return max(0.0, min(1.0, score))

    def _backpropagate(self, node: MCTSNode, value: float) -> None:
        """Backpropagate value up the tree."""
        while node:
            node.visits += 1
            node.value += value
            node = node.parent

    def _create_variation(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Create a variation of requirements."""
        variation = copy.deepcopy(requirements)

        # Add quality enhancements for financial data
        if "quality_requirements" not in variation:
            variation["quality_requirements"] = {}

        # Enhance quality requirements
        quality = variation["quality_requirements"]

        # Financial data often needs high precision
        if "precision" not in quality:
            quality["precision"] = random.choice(["high", "very_high"])

        # Financial data needs referential integrity
        if "referential_integrity" not in quality:
            quality["referential_integrity"] = True

        # Add distribution hints for numeric fields
        if "fields" in variation:
            for field in variation.get("fields", []):
                if isinstance(field, dict) and field.get("type") in ["number", "integer", "float"]:
                    if "distribution" not in field:
                        field["distribution"] = random.choice(
                            ["normal", "lognormal", "uniform"]
                        )

        return variation

    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about MCTS reasoning."""
        return {
            "name": "mcts",
            "description": "Monte Carlo Tree Search - Explores multiple generation paths to find optimal data distributions",
            "use_cases": [
                "Financial data generation",
                "Risk analysis scenarios",
                "Portfolio optimization",
                "Fraud detection patterns",
                "Trading data with correlations",
            ],
            "parameters": {
                "iterations": self.iterations,
                "exploration_factor": self.exploration_factor,
            },
            "strengths": [
                "Explores diverse solution space",
                "Balances exploration and exploitation",
                "Finds optimal distributions for correlated data",
                "Handles uncertainty well",
            ],
            "limitations": [
                "Computationally intensive",
                "May require tuning of exploration factor",
                "Performance depends on simulation quality",
            ],
        }
