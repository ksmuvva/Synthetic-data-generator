"""
Meta-Prompting reasoning for synthetic data generation.

Ideal for multi-domain data and scenarios requiring adaptive strategy
selection based on dynamic analysis of requirements.
"""

from typing import Dict, Any, List, Optional
import copy

from .base import BaseReasoningStrategy, ReasoningResult


class MetaPromptingReasoner(BaseReasoningStrategy):
    """
    Meta-Prompting reasoning strategy.

    Dynamically analyzes requirements and adaptively applies different
    reasoning strategies based on the domain and complexity.
    """

    def __init__(self, config: Optional[Any] = None):
        """Initialize Meta-Prompting reasoner."""
        super().__init__(config)

    async def reason(
        self,
        requirements: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> ReasoningResult:
        """
        Apply meta-prompting reasoning.

        Args:
            requirements: Initial requirements
            context: Optional context

        Returns:
            ReasoningResult with adaptively enhanced requirements
        """
        self.logger.info("Starting Meta-Prompting reasoning")

        reasoning_steps = [
            "Starting Meta-Prompting (Adaptive Reasoning)",
            "Analyzing requirements to determine optimal strategy",
        ]

        # Phase 1: Meta-analysis
        analysis = self._meta_analyze(requirements)

        reasoning_steps.extend([
            f"Domain detected: {analysis['domain']}",
            f"Complexity level: {analysis['complexity']}",
            f"Recommended sub-strategy: {analysis['strategy']}",
        ])

        # Phase 2: Apply adaptive enhancements
        enhanced = copy.deepcopy(requirements)

        if analysis["strategy"] == "constraint_focused":
            reasoning_steps.append("Applying constraint-focused enhancements")
            enhanced = self._apply_constraint_strategy(enhanced)

        elif analysis["strategy"] == "quality_focused":
            reasoning_steps.append("Applying quality-focused enhancements")
            enhanced = self._apply_quality_strategy(enhanced)

        elif analysis["strategy"] == "relationship_focused":
            reasoning_steps.append("Applying relationship-focused enhancements")
            enhanced = self._apply_relationship_strategy(enhanced)

        else:  # balanced
            reasoning_steps.append("Applying balanced enhancements")
            enhanced = self._apply_balanced_strategy(enhanced)

        # Phase 3: Cross-domain refinement
        reasoning_steps.append("Applying cross-domain refinements")
        enhanced = self._cross_domain_refinement(enhanced, analysis)

        confidence = self._calculate_confidence(analysis, enhanced)

        reasoning_steps.append(
            f"Meta-prompting completed with confidence: {confidence:.2f}"
        )

        self.logger.info(
            "Meta-Prompting completed",
            strategy=analysis["strategy"],
            confidence=confidence,
        )

        return ReasoningResult(
            enhanced_requirements=enhanced,
            reasoning_steps=reasoning_steps,
            confidence=confidence,
            metadata={
                "domain": analysis["domain"],
                "complexity": analysis["complexity"],
                "strategy_used": analysis["strategy"],
            },
        )

    def _meta_analyze(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Perform meta-analysis to determine strategy."""
        analysis = {
            "domain": "general",
            "complexity": "medium",
            "strategy": "balanced",
        }

        # Detect domain
        domain = self._extract_domain(requirements)
        if domain:
            analysis["domain"] = domain

        # Assess complexity
        complexity_score = 0

        if "fields" in requirements:
            fields_count = len(requirements["fields"])
            if fields_count > 20:
                complexity_score += 2
            elif fields_count > 10:
                complexity_score += 1

        if "relationships" in requirements and requirements["relationships"]:
            complexity_score += 2

        if "constraints" in requirements and len(requirements.get("constraints", [])) > 5:
            complexity_score += 1

        if complexity_score >= 4:
            analysis["complexity"] = "high"
        elif complexity_score >= 2:
            analysis["complexity"] = "medium"
        else:
            analysis["complexity"] = "low"

        # Determine strategy
        if len(requirements.get("constraints", [])) > len(requirements.get("fields", [])):
            analysis["strategy"] = "constraint_focused"
        elif "quality_requirements" in requirements:
            analysis["strategy"] = "quality_focused"
        elif "relationships" in requirements and requirements["relationships"]:
            analysis["strategy"] = "relationship_focused"

        return analysis

    def _apply_constraint_strategy(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Apply constraint-focused strategy."""
        if "constraints" not in requirements:
            requirements["constraints"] = []

        # Enhance constraints with validation
        requirements["constraint_validation"] = {
            "enabled": True,
            "level": "strict",
        }

        return requirements

    def _apply_quality_strategy(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Apply quality-focused strategy."""
        if "quality_requirements" not in requirements:
            requirements["quality_requirements"] = {}

        quality = requirements["quality_requirements"]
        quality["quality_level"] = "very_high"
        quality["validation_required"] = True
        quality["null_percentage"] = 0.0

        return requirements

    def _apply_relationship_strategy(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Apply relationship-focused strategy."""
        if "relationships" not in requirements:
            requirements["relationships"] = []

        # Add referential integrity
        requirements["referential_integrity"] = {
            "enabled": True,
            "cascade": True,
        }

        return requirements

    def _apply_balanced_strategy(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Apply balanced strategy."""
        # Add moderate enhancements across all areas

        if "quality_requirements" not in requirements:
            requirements["quality_requirements"] = {}

        requirements["quality_requirements"]["quality_level"] = "high"

        if "constraints" not in requirements:
            requirements["constraints"] = []

        if not requirements["constraints"]:
            requirements["constraints"].append("Data must be valid")

        return requirements

    def _cross_domain_refinement(
        self,
        requirements: Dict[str, Any],
        analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Apply cross-domain refinements."""
        # Add metadata about generation
        requirements["generation_metadata"] = {
            "domain": analysis["domain"],
            "complexity": analysis["complexity"],
            "strategy": analysis["strategy"],
        }

        return requirements

    def _calculate_confidence(
        self,
        analysis: Dict[str, Any],
        requirements: Dict[str, Any],
    ) -> float:
        """Calculate confidence based on analysis and enhancements."""
        score = 0.6  # Base confidence

        # Boost for clear domain detection
        if analysis["domain"] != "general":
            score += 0.1

        # Boost for appropriate strategy
        if analysis["strategy"] != "balanced":
            score += 0.1

        # Boost for completeness
        if "quality_requirements" in requirements:
            score += 0.1

        if "constraints" in requirements:
            score += 0.1

        return min(1.0, score)

    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about Meta-Prompting reasoning."""
        return {
            "name": "meta_prompting",
            "description": "Meta-Prompting - Dynamically adapts strategy based on requirements",
            "use_cases": [
                "Multi-domain data generation",
                "Adaptive strategy selection",
                "Cross-functional datasets",
                "Unknown or varied domains",
            ],
            "parameters": {},
            "strengths": [
                "Adapts to requirements",
                "Works across domains",
                "Flexible and versatile",
                "Good for mixed datasets",
            ],
            "limitations": [
                "May not specialize as well",
                "Requires good meta-analysis",
                "More complex logic",
            ],
        }
