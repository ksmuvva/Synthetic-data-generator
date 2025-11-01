"""
Iterative Refinement reasoning for synthetic data generation.

General-purpose strategy that progressively improves data quality
through multiple passes. Suitable for all domains.
"""

from typing import Dict, Any, List, Optional
import copy

from .base import BaseReasoningStrategy, ReasoningResult


class IterativeRefinementReasoner(BaseReasoningStrategy):
    """
    Iterative Refinement reasoning strategy.

    Progressively refines requirements through multiple passes,
    improving quality incrementally. Works well for general cases.
    """

    def __init__(self, config: Optional[Any] = None):
        """Initialize Iterative Refinement reasoner."""
        super().__init__(config)

        self.max_iterations = 5
        if config and hasattr(config, "reasoning"):
            self.max_iterations = getattr(
                config.reasoning, "max_iterations", 5
            )

    async def reason(
        self,
        requirements: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> ReasoningResult:
        """
        Apply iterative refinement reasoning.

        Args:
            requirements: Initial requirements
            context: Optional context

        Returns:
            ReasoningResult with refined requirements
        """
        self.logger.info(
            "Starting Iterative Refinement reasoning",
            max_iterations=self.max_iterations,
        )

        current = copy.deepcopy(requirements)
        reasoning_steps = [
            "Starting Iterative Refinement",
            f"Maximum refinement passes: {self.max_iterations}",
        ]

        quality_scores = []

        for iteration in range(self.max_iterations):
            reasoning_steps.append(f"\n--- Refinement Pass {iteration + 1} ---")

            # Apply refinements
            current, refinements = self._refine_pass(current, iteration)

            reasoning_steps.extend(refinements)

            # Evaluate quality
            quality = self._evaluate_quality(current)
            quality_scores.append(quality)

            reasoning_steps.append(f"Quality score: {quality:.3f}")

            # Check convergence
            if iteration > 0 and abs(quality_scores[-1] - quality_scores[-2]) < 0.01:
                reasoning_steps.append("✓ Converged - quality improvement minimal")
                break

        reasoning_steps.extend([
            f"\nCompleted {len(quality_scores)} refinement passes",
            f"Final quality score: {quality_scores[-1]:.3f}",
        ])

        confidence = quality_scores[-1]

        self.logger.info(
            "Iterative Refinement completed",
            passes=len(quality_scores),
            final_quality=confidence,
        )

        return ReasoningResult(
            enhanced_requirements=current,
            reasoning_steps=reasoning_steps,
            confidence=confidence,
            metadata={
                "refinement_passes": len(quality_scores),
                "quality_progression": quality_scores,
                "converged": len(quality_scores) < self.max_iterations,
            },
        )

    def _refine_pass(
        self,
        requirements: Dict[str, Any],
        iteration: int,
    ) -> tuple[Dict[str, Any], List[str]]:
        """Perform one refinement pass."""
        refinements = []
        refined = copy.deepcopy(requirements)

        # Pass 1: Enhance field specifications
        if iteration == 0:
            refined, field_refinements = self._refine_fields(refined)
            refinements.extend(field_refinements)

        # Pass 2: Add constraints
        elif iteration == 1:
            refined, constraint_refinements = self._refine_constraints(refined)
            refinements.extend(constraint_refinements)

        # Pass 3: Enhance quality requirements
        elif iteration == 2:
            refined, quality_refinements = self._refine_quality(refined)
            refinements.extend(quality_refinements)

        # Pass 4: Add relationships
        elif iteration == 3:
            refined, relationship_refinements = self._refine_relationships(refined)
            refinements.extend(relationship_refinements)

        # Pass 5: Final polish
        else:
            refined, polish_refinements = self._final_polish(refined)
            refinements.extend(polish_refinements)

        return refined, refinements

    def _refine_fields(
        self,
        requirements: Dict[str, Any],
    ) -> tuple[Dict[str, Any], List[str]]:
        """Refine field specifications."""
        refinements = []

        if "fields" in requirements:
            for field in requirements["fields"]:
                if isinstance(field, dict):
                    field_name = field.get("name", "unknown")

                    # Add missing types
                    if "type" not in field:
                        field["type"] = "string"
                        refinements.append(f"  + Added default type 'string' to field '{field_name}'")

                    # Add descriptions
                    if "description" not in field:
                        field["description"] = f"Field for {field_name}"
                        refinements.append(f"  + Added description to field '{field_name}'")

        return requirements, refinements

    def _refine_constraints(
        self,
        requirements: Dict[str, Any],
    ) -> tuple[Dict[str, Any], List[str]]:
        """Refine constraints."""
        refinements = []

        if "constraints" not in requirements:
            requirements["constraints"] = []
            refinements.append("  + Initialized constraints list")

        # Add basic constraints if missing
        if not requirements["constraints"]:
            requirements["constraints"].append("Data must be valid and consistent")
            refinements.append("  + Added basic validity constraint")

        return requirements, refinements

    def _refine_quality(
        self,
        requirements: Dict[str, Any],
    ) -> tuple[Dict[str, Any], List[str]]:
        """Refine quality requirements."""
        refinements = []

        if "quality_requirements" not in requirements:
            requirements["quality_requirements"] = {}
            refinements.append("  + Initialized quality requirements")

        quality = requirements["quality_requirements"]

        if "quality_level" not in quality:
            quality["quality_level"] = "high"
            refinements.append("  + Set quality level to 'high'")

        if "null_percentage" not in quality:
            quality["null_percentage"] = 0.05
            refinements.append("  + Set null percentage to 5%")

        return requirements, refinements

    def _refine_relationships(
        self,
        requirements: Dict[str, Any],
    ) -> tuple[Dict[str, Any], List[str]]:
        """Refine relationships."""
        refinements = []

        if "relationships" not in requirements:
            requirements["relationships"] = []
            refinements.append("  + Initialized relationships list")

        # Detect potential relationships
        if "fields" in requirements:
            field_names = [
                f.get("name", "") for f in requirements["fields"]
                if isinstance(f, dict)
            ]

            for name in field_names:
                if "_id" in name.lower() and name.lower() != "id":
                    parent = name.replace("_id", "").replace("_ID", "")
                    requirements["relationships"].append({
                        "type": "foreign_key",
                        "from": name,
                        "to": f"{parent}.id",
                    })
                    refinements.append(f"  + Detected relationship: {name} → {parent}.id")

        return requirements, refinements

    def _final_polish(
        self,
        requirements: Dict[str, Any],
    ) -> tuple[Dict[str, Any], List[str]]:
        """Final polish pass."""
        refinements = []

        # Add metadata
        if "metadata" not in requirements:
            requirements["metadata"] = {
                "refined": True,
                "refinement_method": "iterative_refinement",
            }
            refinements.append("  + Added refinement metadata")

        # Ensure completeness flag
        requirements["metadata"]["complete"] = True
        refinements.append("  + Marked requirements as complete")

        return requirements, refinements

    def _evaluate_quality(self, requirements: Dict[str, Any]) -> float:
        """Evaluate current quality of requirements."""
        score = 0.2  # Base score

        # Field completeness
        if "fields" in requirements:
            fields = requirements["fields"]
            if fields:
                score += 0.2

                # Check field details
                complete_fields = sum(
                    1 for f in fields
                    if isinstance(f, dict) and "type" in f and "description" in f
                )

                if complete_fields == len(fields):
                    score += 0.2

        # Constraints
        if "constraints" in requirements and requirements["constraints"]:
            score += 0.1

        # Quality requirements
        if "quality_requirements" in requirements:
            score += 0.15

        # Relationships
        if "relationships" in requirements and requirements["relationships"]:
            score += 0.15

        return min(1.0, score)

    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about Iterative Refinement reasoning."""
        return {
            "name": "iterative_refinement",
            "description": "Iterative Refinement - Progressively improves quality through multiple passes",
            "use_cases": [
                "General data generation",
                "Quality improvement",
                "Incremental enhancement",
                "Default fallback strategy",
            ],
            "parameters": {
                "max_iterations": self.max_iterations,
            },
            "strengths": [
                "Works for all domains",
                "Steady quality improvement",
                "Good default choice",
                "Predictable behavior",
            ],
            "limitations": [
                "May be slower than single-pass",
                "Not specialized for any domain",
                "Generic approach",
            ],
        }
