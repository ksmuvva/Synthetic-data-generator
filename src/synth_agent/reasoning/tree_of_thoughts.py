"""
Tree of Thoughts (ToT) reasoning for synthetic data generation.

Ideal for complex relational data and multi-table database generation
requiring exploration of multiple reasoning branches.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import copy

from .base import BaseReasoningStrategy, ReasoningResult


@dataclass
class ThoughtNode:
    """Node in the tree of thoughts."""
    requirements: Dict[str, Any]
    depth: int
    score: float = 0.0
    children: List['ThoughtNode'] = None

    def __post_init__(self):
        if self.children is None:
            self.children = []


class TreeOfThoughtsReasoner(BaseReasoningStrategy):
    """
    Tree of Thoughts reasoning strategy.

    Explores multiple reasoning branches simultaneously to find the best
    requirement enhancement path for complex relational data.
    """

    def __init__(self, config: Optional[Any] = None):
        """Initialize Tree of Thoughts reasoner."""
        super().__init__(config)

        self.branches = 3
        self.max_depth = 3

        if config and hasattr(config, "reasoning"):
            self.branches = getattr(config.reasoning, "tot_branches", 3)

    async def reason(
        self,
        requirements: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> ReasoningResult:
        """
        Apply tree of thoughts reasoning.

        Args:
            requirements: Initial requirements
            context: Optional context

        Returns:
            ReasoningResult with best requirements
        """
        self.logger.info(
            "Starting Tree of Thoughts reasoning",
            branches=self.branches,
            max_depth=self.max_depth,
        )

        reasoning_steps = [
            "Initializing Tree of Thoughts",
            f"Exploring {self.branches} branches per node",
            f"Maximum depth: {self.max_depth}",
        ]

        # Create root node
        root = ThoughtNode(requirements=copy.deepcopy(requirements), depth=0)

        # Build tree by exploring branches
        self._build_tree(root, reasoning_steps)

        # Evaluate all leaf nodes
        leaf_nodes = self._get_leaf_nodes(root)
        for node in leaf_nodes:
            node.score = self._evaluate_node(node)

        # Select best path
        best_leaf = max(leaf_nodes, key=lambda n: n.score)

        reasoning_steps.extend([
            f"Explored {len(leaf_nodes)} complete thought paths",
            f"Best path score: {best_leaf.score:.3f}",
            "Selected optimal requirement configuration",
        ])

        confidence = best_leaf.score

        self.logger.info(
            "Tree of Thoughts completed",
            leaf_nodes=len(leaf_nodes),
            best_score=best_leaf.score,
        )

        return ReasoningResult(
            enhanced_requirements=best_leaf.requirements,
            reasoning_steps=reasoning_steps,
            confidence=confidence,
            metadata={
                "branches": self.branches,
                "max_depth": self.max_depth,
                "paths_explored": len(leaf_nodes),
                "best_score": best_leaf.score,
            },
        )

    def _build_tree(self, node: ThoughtNode, reasoning_steps: List[str]) -> None:
        """Recursively build tree of thoughts."""
        if node.depth >= self.max_depth:
            return

        reasoning_steps.append(f"Depth {node.depth + 1}: Generating {self.branches} thought branches")

        # Generate branches
        for i in range(self.branches):
            child_requirements = self._generate_branch(node.requirements, i)
            child = ThoughtNode(
                requirements=child_requirements,
                depth=node.depth + 1,
            )
            node.children.append(child)

            # Recursively build children
            self._build_tree(child, reasoning_steps)

    def _generate_branch(
        self,
        requirements: Dict[str, Any],
        branch_index: int,
    ) -> Dict[str, Any]:
        """Generate a branch variation of requirements."""
        branch = copy.deepcopy(requirements)

        # Different enhancement strategies per branch
        if branch_index == 0:
            # Branch 0: Focus on relationships
            branch = self._enhance_relationships(branch)
        elif branch_index == 1:
            # Branch 1: Focus on constraints
            branch = self._enhance_constraints(branch)
        else:
            # Branch 2+: Focus on data quality
            branch = self._enhance_data_quality(branch)

        return branch

    def _enhance_relationships(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance relationship specifications."""
        if "relationships" not in requirements:
            requirements["relationships"] = []

        # Add referential integrity
        requirements["relationships"].append({
            "type": "referential_integrity",
            "enforce": True,
        })

        # Add cascade rules
        requirements["cascade_rules"] = {
            "on_delete": "cascade",
            "on_update": "cascade",
        }

        return requirements

    def _enhance_constraints(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance constraint specifications."""
        if "constraints" not in requirements:
            requirements["constraints"] = []

        # Add unique constraints
        if "fields" in requirements:
            for field in requirements["fields"]:
                if isinstance(field, dict):
                    if field.get("name", "").lower() in ["id", "email", "username"]:
                        field["unique"] = True

        # Add check constraints
        requirements["constraints"].append({
            "type": "check",
            "description": "Validate data consistency",
        })

        return requirements

    def _enhance_data_quality(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance data quality specifications."""
        if "quality_requirements" not in requirements:
            requirements["quality_requirements"] = {}

        quality = requirements["quality_requirements"]
        quality["referential_integrity"] = True
        quality["null_percentage"] = 0.02
        quality["duplicate_percentage"] = 0.0

        return requirements

    def _get_leaf_nodes(self, node: ThoughtNode) -> List[ThoughtNode]:
        """Get all leaf nodes in the tree."""
        if not node.children:
            return [node]

        leaves = []
        for child in node.children:
            leaves.extend(self._get_leaf_nodes(child))

        return leaves

    def _evaluate_node(self, node: ThoughtNode) -> float:
        """Evaluate quality of a thought node."""
        requirements = node.requirements
        score = 0.5  # Base score

        # Relationships
        if "relationships" in requirements and requirements["relationships"]:
            score += 0.2

        # Constraints
        if "constraints" in requirements and requirements["constraints"]:
            score += 0.15

        # Quality requirements
        if "quality_requirements" in requirements:
            score += 0.15

        # Bonus for depth (more refined)
        score += node.depth * 0.05

        return min(1.0, score)

    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about Tree of Thoughts reasoning."""
        return {
            "name": "tree_of_thoughts",
            "description": "Tree of Thoughts - Explores multiple reasoning branches for complex relational data",
            "use_cases": [
                "Multi-table database generation",
                "Complex relational data",
                "Interconnected datasets",
                "Schema design assistance",
            ],
            "parameters": {
                "branches": self.branches,
                "max_depth": self.max_depth,
            },
            "strengths": [
                "Excellent for relational data",
                "Explores multiple strategies",
                "Finds optimal schema designs",
                "Good for complex relationships",
            ],
            "limitations": [
                "Exponential complexity",
                "Memory intensive",
                "May be overkill for simple schemas",
            ],
        }
