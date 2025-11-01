"""
Reflexion (Self-Reflection) reasoning for synthetic data generation.

Ideal for iterative quality improvement scenarios where learning from
previous generation attempts improves subsequent results.
"""

from typing import Dict, Any, List, Optional
import copy

from .base import BaseReasoningStrategy, ReasoningResult


class ReflexionReasoner(BaseReasoningStrategy):
    """
    Reflexion (Self-Reflection) reasoning strategy.

    Learns from previous generation attempts and iteratively improves
    requirements based on self-reflection.
    """

    def __init__(self, config: Optional[Any] = None):
        """Initialize Reflexion reasoner."""
        super().__init__(config)

        self.max_iterations = 3
        if config and hasattr(config, "reasoning"):
            self.max_iterations = getattr(
                config.reasoning, "reflexion_max_iterations", 3
            )

    async def reason(
        self,
        requirements: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> ReasoningResult:
        """
        Apply reflexion reasoning with iterative improvement.

        Args:
            requirements: Initial requirements
            context: Optional context

        Returns:
            ReasoningResult with improved requirements
        """
        self.logger.info(
            "Starting Reflexion reasoning",
            max_iterations=self.max_iterations,
        )

        current = copy.deepcopy(requirements)
        reasoning_steps = [
            "Starting Reflexion (Self-Reflection) reasoning",
            f"Maximum iterations: {self.max_iterations}",
        ]

        # Iteration history for learning
        history = []

        for iteration in range(self.max_iterations):
            reasoning_steps.append(f"\n--- Iteration {iteration + 1} ---")

            # Generate with current requirements
            reasoning_steps.append("Generating with current requirements")

            # Reflect on potential issues
            reasoning_steps.append("Reflecting on requirements quality")
            issues = self._reflect_on_requirements(current, history)

            if not issues:
                reasoning_steps.append("✓ No issues found, requirements are optimal")
                break

            reasoning_steps.extend(issues)

            # Learn and improve
            reasoning_steps.append("Learning from reflection, improving requirements")
            current = self._learn_and_improve(current, issues)

            # Store in history
            history.append({
                "iteration": iteration + 1,
                "requirements": copy.deepcopy(current),
                "issues": issues,
            })

            reasoning_steps.append(f"Completed iteration {iteration + 1}")

        reasoning_steps.extend([
            f"\nCompleted {len(history)} reflection cycles",
            "Final requirements optimized",
        ])

        confidence = self._calculate_confidence(history)

        self.logger.info(
            "Reflexion completed",
            iterations=len(history),
            confidence=confidence,
        )

        return ReasoningResult(
            enhanced_requirements=current,
            reasoning_steps=reasoning_steps,
            confidence=confidence,
            metadata={
                "iterations": len(history),
                "max_iterations": self.max_iterations,
                "improvements_made": len(history),
            },
        )

    def _reflect_on_requirements(
        self,
        requirements: Dict[str, Any],
        history: List[Dict[str, Any]],
    ) -> List[str]:
        """Reflect on requirements to identify potential issues."""
        issues = []

        # Check field completeness
        if "fields" in requirements:
            fields = requirements["fields"]
            for field in fields:
                if isinstance(field, dict):
                    field_name = field.get("name", "unknown")

                    # Missing type
                    if "type" not in field:
                        issues.append(f"  ⚠ Field '{field_name}' missing type specification")

                    # Missing description
                    if "description" not in field:
                        issues.append(f"  ⚠ Field '{field_name}' missing description")

        # Check quality requirements
        if "quality_requirements" not in requirements:
            issues.append("  ⚠ No quality requirements specified")
        else:
            quality = requirements["quality_requirements"]
            if "quality_level" not in quality:
                issues.append("  ⚠ Quality level not specified")

        # Check constraints
        if "constraints" not in requirements or not requirements["constraints"]:
            issues.append("  ⚠ No constraints defined")

        # Learn from history
        if history:
            last_issues = history[-1]["issues"]
            if len(issues) >= len(last_issues):
                issues.append("  ⚠ Not improving from previous iteration")

        return issues

    def _learn_and_improve(
        self,
        requirements: Dict[str, Any],
        issues: List[str],
    ) -> Dict[str, Any]:
        """Learn from issues and improve requirements."""
        improved = copy.deepcopy(requirements)

        # Fix missing types
        if any("missing type" in issue for issue in issues):
            if "fields" in improved:
                for field in improved["fields"]:
                    if isinstance(field, dict) and "type" not in field:
                        # Infer type based on name
                        name = field.get("name", "").lower()
                        if "email" in name:
                            field["type"] = "email"
                        elif "age" in name:
                            field["type"] = "integer"
                        else:
                            field["type"] = "string"

        # Fix missing descriptions
        if any("missing description" in issue for issue in issues):
            if "fields" in improved:
                for field in improved["fields"]:
                    if isinstance(field, dict) and "description" not in field:
                        field_name = field.get("name", "")
                        field["description"] = f"Auto-generated description for {field_name}"

        # Add quality requirements
        if any("No quality requirements" in issue for issue in issues):
            improved["quality_requirements"] = {
                "quality_level": "high",
                "null_percentage": 0.0,
            }

        # Add constraints
        if any("No constraints" in issue for issue in issues):
            improved["constraints"] = ["Data must be valid and consistent"]

        return improved

    def _calculate_confidence(self, history: List[Dict[str, Any]]) -> float:
        """Calculate confidence based on improvement over iterations."""
        if not history:
            return 0.5

        # Confidence increases with iterations
        base_confidence = 0.5
        improvement_bonus = len(history) * 0.15

        # Check if we stopped early (good sign)
        if len(history) < self.max_iterations:
            improvement_bonus += 0.1

        return min(1.0, base_confidence + improvement_bonus)

    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about Reflexion reasoning."""
        return {
            "name": "reflexion",
            "description": "Reflexion - Learns from mistakes and iteratively improves requirements",
            "use_cases": [
                "Iterative quality improvement",
                "Learning from previous attempts",
                "Continuous optimization",
                "Quality-focused generation",
            ],
            "parameters": {
                "max_iterations": self.max_iterations,
            },
            "strengths": [
                "Continuous improvement",
                "Learns from mistakes",
                "Self-correcting",
                "Good for quality focus",
            ],
            "limitations": [
                "Requires multiple iterations",
                "May converge slowly",
                "Overhead of reflection",
            ],
        }
