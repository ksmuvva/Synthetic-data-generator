"""
Self-Consistency reasoning for synthetic data generation.

Ideal for compliance, validation, and high-quality scenarios requiring
multiple independent solutions to ensure consistency.
"""

from typing import Dict, Any, List, Optional
import copy
from collections import Counter

from .base import BaseReasoningStrategy, ReasoningResult


class SelfConsistencyReasoner(BaseReasoningStrategy):
    """
    Self-Consistency reasoning strategy.

    Generates multiple independent requirement enhancements and selects
    the most consistent solution across all samples.
    """

    def __init__(self, config: Optional[Any] = None):
        """Initialize Self-Consistency reasoner."""
        super().__init__(config)

        self.samples = 5
        if config and hasattr(config, "reasoning"):
            self.samples = getattr(config.reasoning, "self_consistency_samples", 5)

    async def reason(
        self,
        requirements: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> ReasoningResult:
        """
        Apply self-consistency reasoning.

        Args:
            requirements: Initial requirements
            context: Optional context

        Returns:
            ReasoningResult with most consistent requirements
        """
        self.logger.info("Starting Self-Consistency reasoning", samples=self.samples)

        reasoning_steps = [
            "Initializing Self-Consistency reasoning",
            f"Generating {self.samples} independent enhancement samples",
        ]

        # Generate multiple independent enhancements
        candidates = []
        for i in range(self.samples):
            enhanced = self._generate_enhancement(requirements, i)
            candidates.append(enhanced)
            reasoning_steps.append(f"Generated sample {i + 1}/{self.samples}")

        # Find most consistent solution
        most_consistent = self._find_most_consistent(candidates)

        reasoning_steps.extend([
            "Analyzing consistency across samples",
            "Selected most consistent configuration",
        ])

        # Calculate confidence based on consistency
        confidence = self._calculate_consistency_score(candidates, most_consistent)

        reasoning_steps.append(
            f"Consistency confidence: {confidence:.2f}"
        )

        self.logger.info(
            "Self-Consistency completed",
            samples=self.samples,
            confidence=confidence,
        )

        return ReasoningResult(
            enhanced_requirements=most_consistent,
            reasoning_steps=reasoning_steps,
            confidence=confidence,
            metadata={
                "samples": self.samples,
                "consistency_score": confidence,
            },
        )

    def _generate_enhancement(
        self,
        requirements: Dict[str, Any],
        sample_index: int,
    ) -> Dict[str, Any]:
        """Generate an independent enhancement."""
        enhanced = copy.deepcopy(requirements)

        # Add quality requirements (consistent across samples)
        if "quality_requirements" not in enhanced:
            enhanced["quality_requirements"] = {}

        quality = enhanced["quality_requirements"]

        # All samples should agree on high quality for compliance
        quality["quality_level"] = "high"
        quality["validation_required"] = True

        # Add constraints based on domain
        if "constraints" not in enhanced:
            enhanced["constraints"] = []

        # Different samples may add different constraints
        if sample_index % 2 == 0:
            enhanced["constraints"].append("All fields must be validated")
        else:
            enhanced["constraints"].append("Data must pass integrity checks")

        # Add compliance markers
        if "compliance" not in enhanced:
            enhanced["compliance"] = []

        enhanced["compliance"].append("audit_trail_required")

        return enhanced

    def _find_most_consistent(
        self,
        candidates: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Find the most consistent solution across candidates."""
        # For simplicity, use voting on key features
        feature_votes = {}

        for candidate in candidates:
            # Vote on quality level
            if "quality_requirements" in candidate:
                quality_level = candidate["quality_requirements"].get("quality_level")
                if quality_level:
                    if "quality_level" not in feature_votes:
                        feature_votes["quality_level"] = []
                    feature_votes["quality_level"].append(quality_level)

            # Vote on validation requirement
            if "quality_requirements" in candidate:
                validation = candidate["quality_requirements"].get("validation_required")
                if validation is not None:
                    if "validation_required" not in feature_votes:
                        feature_votes["validation_required"] = []
                    feature_votes["validation_required"].append(validation)

        # Build most consistent solution
        result = copy.deepcopy(candidates[0])

        # Apply majority votes
        if "quality_requirements" not in result:
            result["quality_requirements"] = {}

        for feature, votes in feature_votes.items():
            if votes:
                # Get most common value
                most_common = Counter(votes).most_common(1)[0][0]
                result["quality_requirements"][feature] = most_common

        return result

    def _calculate_consistency_score(
        self,
        candidates: List[Dict[str, Any]],
        selected: Dict[str, Any],
    ) -> float:
        """Calculate consistency score."""
        if not candidates:
            return 0.0

        # Compare selected with all candidates
        similarity_scores = []

        for candidate in candidates:
            similarity = self._compare_requirements(selected, candidate)
            similarity_scores.append(similarity)

        # Average similarity is the consistency score
        return sum(similarity_scores) / len(similarity_scores)

    def _compare_requirements(
        self,
        req1: Dict[str, Any],
        req2: Dict[str, Any],
    ) -> float:
        """Compare two requirement sets for similarity."""
        score = 0.0
        comparisons = 0

        # Compare quality requirements
        if "quality_requirements" in req1 and "quality_requirements" in req2:
            q1 = req1["quality_requirements"]
            q2 = req2["quality_requirements"]

            for key in set(list(q1.keys()) + list(q2.keys())):
                comparisons += 1
                if key in q1 and key in q2 and q1[key] == q2[key]:
                    score += 1

        # Compare constraints
        if "constraints" in req1 and "constraints" in req2:
            c1 = set(req1["constraints"]) if isinstance(req1["constraints"], list) else set()
            c2 = set(req2["constraints"]) if isinstance(req2["constraints"], list) else set()

            if c1 and c2:
                comparisons += 1
                intersection = len(c1 & c2)
                union = len(c1 | c2)
                if union > 0:
                    score += intersection / union

        if comparisons == 0:
            return 0.5  # Neutral if nothing to compare

        return score / comparisons

    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about Self-Consistency reasoning."""
        return {
            "name": "self_consistency",
            "description": "Self-Consistency - Generates multiple solutions and selects most consistent",
            "use_cases": [
                "Compliance data generation",
                "High-quality validation scenarios",
                "Audit and regulatory data",
                "Safety-critical data",
            ],
            "parameters": {
                "samples": self.samples,
            },
            "strengths": [
                "High confidence in results",
                "Reduces variance",
                "Excellent for compliance",
                "Robust to noise",
            ],
            "limitations": [
                "Computationally expensive",
                "Slower than single-pass methods",
                "May be conservative",
            ],
        }
