"""
Beam Search reasoning for synthetic data generation.

Ideal for e-commerce, product catalogs, and scenarios requiring diverse
but high-quality output candidates.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import copy

from .base import BaseReasoningStrategy, ReasoningResult


@dataclass
class Candidate:
    """Candidate requirement configuration."""
    requirements: Dict[str, Any]
    score: float = 0.0


class BeamSearchReasoner(BaseReasoningStrategy):
    """
    Beam Search reasoning strategy.

    Maintains top-k best candidates during requirement enhancement,
    ensuring diverse but high-quality outputs.
    """

    def __init__(self, config: Optional[Any] = None):
        """Initialize Beam Search reasoner."""
        super().__init__(config)

        # Beam search parameters
        self.beam_width = 5
        self.max_depth = 3

        if config and hasattr(config, "reasoning"):
            self.beam_width = getattr(config.reasoning, "beam_width", 5)

    async def reason(
        self,
        requirements: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> ReasoningResult:
        """
        Apply beam search reasoning to enhance requirements.

        Args:
            requirements: Initial requirements
            context: Optional context

        Returns:
            ReasoningResult with best requirements
        """
        self.logger.info(
            "Starting Beam Search reasoning",
            beam_width=self.beam_width,
            max_depth=self.max_depth,
        )

        reasoning_steps = [
            "Initializing Beam Search",
            f"Beam width: {self.beam_width}",
            f"Search depth: {self.max_depth}",
        ]

        # Initialize beam with original requirements
        beam = [Candidate(requirements=copy.deepcopy(requirements), score=0.0)]

        # Iteratively expand and prune
        for depth in range(self.max_depth):
            reasoning_steps.append(f"Depth {depth + 1}: Expanding candidates")

            # Generate successors for each candidate
            all_successors = []
            for candidate in beam:
                successors = self._generate_successors(candidate, depth)
                all_successors.extend(successors)

            reasoning_steps.append(
                f"Generated {len(all_successors)} candidate variations"
            )

            # Score all successors
            for successor in all_successors:
                successor.score = self._score_candidate(successor)

            # Keep top-k candidates
            all_successors.sort(key=lambda c: c.score, reverse=True)
            beam = all_successors[:self.beam_width]

            reasoning_steps.append(
                f"Retained top {len(beam)} candidates (scores: {[f'{c.score:.3f}' for c in beam[:3]]})"
            )

        # Select best candidate
        best = max(beam, key=lambda c: c.score)

        reasoning_steps.extend([
            f"Explored {self.beam_width * self.max_depth} configurations",
            f"Selected best configuration with score: {best.score:.3f}",
        ])

        confidence = min(1.0, best.score)

        self.logger.info(
            "Beam Search completed",
            final_beam_size=len(beam),
            best_score=best.score,
        )

        return ReasoningResult(
            enhanced_requirements=best.requirements,
            reasoning_steps=reasoning_steps,
            confidence=confidence,
            metadata={
                "beam_width": self.beam_width,
                "max_depth": self.max_depth,
                "final_candidates": len(beam),
                "best_score": best.score,
            },
        )

    def _generate_successors(
        self,
        candidate: Candidate,
        depth: int,
    ) -> List[Candidate]:
        """Generate successor candidates."""
        successors = []

        # Different enhancement strategies based on depth
        if depth == 0:
            # First level: Add field enhancements
            successors.extend(self._enhance_fields(candidate))
        elif depth == 1:
            # Second level: Add format and quality options
            successors.extend(self._enhance_quality(candidate))
        else:
            # Third level: Add variation parameters
            successors.extend(self._enhance_variation(candidate))

        return successors

    def _enhance_fields(self, candidate: Candidate) -> List[Candidate]:
        """Enhance field specifications."""
        variants = []

        base_req = candidate.requirements

        # Variant 1: Add detailed descriptions
        variant1 = copy.deepcopy(base_req)
        if "fields" in variant1:
            for field in variant1.get("fields", []):
                if isinstance(field, dict) and "description" not in field:
                    field["description"] = f"Enhanced description for {field.get('name', 'field')}"
        variants.append(Candidate(requirements=variant1))

        # Variant 2: Add example values
        variant2 = copy.deepcopy(base_req)
        if "fields" in variant2:
            for field in variant2.get("fields", []):
                if isinstance(field, dict) and "examples" not in field:
                    field["examples"] = []
        variants.append(Candidate(requirements=variant2))

        return variants

    def _enhance_quality(self, candidate: Candidate) -> List[Candidate]:
        """Enhance quality specifications."""
        variants = []

        base_req = candidate.requirements

        # Variant 1: High quality, low diversity
        variant1 = copy.deepcopy(base_req)
        variant1["quality_requirements"] = {
            "null_percentage": 0.0,
            "duplicate_percentage": 0.0,
            "quality_level": "high",
        }
        variants.append(Candidate(requirements=variant1))

        # Variant 2: Balanced quality and diversity
        variant2 = copy.deepcopy(base_req)
        variant2["quality_requirements"] = {
            "null_percentage": 0.05,
            "duplicate_percentage": 0.02,
            "quality_level": "medium",
        }
        variants.append(Candidate(requirements=variant2))

        return variants

    def _enhance_variation(self, candidate: Candidate) -> List[Candidate]:
        """Enhance variation parameters."""
        variants = []

        base_req = candidate.requirements

        # Variant 1: High variation
        variant1 = copy.deepcopy(base_req)
        variant1["variation_params"] = {"diversity": "high"}
        variants.append(Candidate(requirements=variant1))

        # Variant 2: Low variation (more realistic)
        variant2 = copy.deepcopy(base_req)
        variant2["variation_params"] = {"diversity": "low", "realistic": True}
        variants.append(Candidate(requirements=variant2))

        return variants

    def _score_candidate(self, candidate: Candidate) -> float:
        """Score a candidate based on completeness and quality."""
        requirements = candidate.requirements
        score = 0.0

        # Completeness scoring
        if "fields" in requirements:
            score += 0.3
            fields = requirements["fields"]
            if isinstance(fields, list):
                for field in fields:
                    if isinstance(field, dict):
                        if "description" in field:
                            score += 0.05
                        if "examples" in field:
                            score += 0.03

        # Quality specifications
        if "quality_requirements" in requirements:
            score += 0.2

        # Variation parameters
        if "variation_params" in requirements:
            score += 0.1

        # Constraints
        if "constraints" in requirements:
            score += 0.15

        return min(1.0, score)

    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about Beam Search reasoning."""
        return {
            "name": "beam_search",
            "description": "Beam Search - Maintains top-k best candidates for diverse high-quality outputs",
            "use_cases": [
                "E-commerce product catalogs",
                "Retail inventory data",
                "Marketing campaign data",
                "Product variant generation",
            ],
            "parameters": {
                "beam_width": self.beam_width,
                "max_depth": self.max_depth,
            },
            "strengths": [
                "Ensures diverse outputs",
                "Maintains quality threshold",
                "Efficient exploration",
                "Good for variant generation",
            ],
            "limitations": [
                "May miss optimal solution",
                "Beam width needs tuning",
                "Memory intensive for large beams",
            ],
        }
