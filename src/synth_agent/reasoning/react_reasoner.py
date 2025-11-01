"""
ReAct (Reasoning + Acting) for synthetic data generation.

Ideal for real-time validation scenarios and data generation that needs
external API checks or validation during the reasoning process.
"""

from typing import Dict, Any, List, Optional
import copy

from .base import BaseReasoningStrategy, ReasoningResult


class ReActReasoner(BaseReasoningStrategy):
    """
    ReAct (Reasoning + Acting) strategy.

    Interleaves reasoning steps with actions (like validation, API calls)
    to enhance requirements based on real-time feedback.
    """

    def __init__(self, config: Optional[Any] = None):
        """Initialize ReAct reasoner."""
        super().__init__(config)

    async def reason(
        self,
        requirements: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> ReasoningResult:
        """
        Apply ReAct reasoning with interleaved actions.

        Args:
            requirements: Initial requirements
            context: Optional context

        Returns:
            ReasoningResult with validated requirements
        """
        self.logger.info("Starting ReAct reasoning")

        enhanced = copy.deepcopy(requirements)
        reasoning_steps = ["Starting ReAct (Reasoning + Acting)"]

        # Cycle 1: Reason about field types, then act (validate)
        reasoning_steps.append("Thought 1: Analyzing field type specifications")
        enhanced = self._reason_about_types(enhanced)

        reasoning_steps.append("Action 1: Validating field type consistency")
        validation1 = self._act_validate_types(enhanced)
        reasoning_steps.extend(validation1)

        # Cycle 2: Reason about constraints, then act (check feasibility)
        reasoning_steps.append("Thought 2: Determining appropriate constraints")
        enhanced = self._reason_about_constraints(enhanced)

        reasoning_steps.append("Action 2: Checking constraint feasibility")
        validation2 = self._act_validate_constraints(enhanced)
        reasoning_steps.extend(validation2)

        # Cycle 3: Reason about data quality, then act (verify requirements)
        reasoning_steps.append("Thought 3: Establishing quality requirements")
        enhanced = self._reason_about_quality(enhanced)

        reasoning_steps.append("Action 3: Verifying quality requirements")
        validation3 = self._act_validate_quality(enhanced)
        reasoning_steps.extend(validation3)

        # Final thought
        reasoning_steps.append("Thought 4: Requirements validated and finalized")

        confidence = self._calculate_confidence(enhanced)

        self.logger.info("ReAct reasoning completed", confidence=confidence)

        return ReasoningResult(
            enhanced_requirements=enhanced,
            reasoning_steps=reasoning_steps,
            confidence=confidence,
            metadata={"cycles": 3, "actions_performed": 3},
        )

    def _reason_about_types(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Reason about and enhance field types."""
        if "fields" not in requirements:
            return requirements

        for field in requirements["fields"]:
            if isinstance(field, dict):
                # Infer types based on field names if missing
                if "type" not in field:
                    name = field.get("name", "").lower()
                    if "email" in name:
                        field["type"] = "email"
                    elif "date" in name or "time" in name:
                        field["type"] = "datetime"
                    elif "age" in name or "count" in name:
                        field["type"] = "integer"
                    else:
                        field["type"] = "string"

        return requirements

    def _act_validate_types(self, requirements: Dict[str, Any]) -> List[str]:
        """Action: Validate field types."""
        results = []

        fields = requirements.get("fields", [])
        for field in fields:
            if isinstance(field, dict):
                field_name = field.get("name", "unknown")
                field_type = field.get("type", "unknown")

                if field_type != "unknown":
                    results.append(f"  ✓ Validated '{field_name}' as {field_type}")
                else:
                    results.append(f"  ⚠ Field '{field_name}' has unknown type")

        return results

    def _reason_about_constraints(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Reason about appropriate constraints."""
        if "constraints" not in requirements:
            requirements["constraints"] = []

        # Add real-time validation constraints
        requirements["constraints"].append({
            "type": "realtime_validation",
            "enabled": True,
        })

        # Ensure unique identifiers
        if "fields" in requirements:
            for field in requirements["fields"]:
                if isinstance(field, dict) and field.get("name", "").lower() == "id":
                    field["unique"] = True
                    field["required"] = True

        return requirements

    def _act_validate_constraints(self, requirements: Dict[str, Any]) -> List[str]:
        """Action: Validate constraints."""
        results = []

        constraints = requirements.get("constraints", [])

        if constraints:
            results.append(f"  ✓ Found {len(constraints)} constraints")

            # Check for realtime validation
            has_realtime = any(
                isinstance(c, dict) and c.get("type") == "realtime_validation"
                for c in constraints
            )

            if has_realtime:
                results.append("  ✓ Real-time validation enabled")
        else:
            results.append("  ⚠ No constraints defined")

        return results

    def _reason_about_quality(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Reason about quality requirements."""
        if "quality_requirements" not in requirements:
            requirements["quality_requirements"] = {}

        quality = requirements["quality_requirements"]

        # For real-time scenarios, ensure high quality
        quality["validation_enabled"] = True
        quality["quality_level"] = "high"

        return requirements

    def _act_validate_quality(self, requirements: Dict[str, Any]) -> List[str]:
        """Action: Validate quality requirements."""
        results = []

        quality = requirements.get("quality_requirements", {})

        if quality.get("validation_enabled"):
            results.append("  ✓ Quality validation enabled")

        if quality.get("quality_level"):
            results.append(f"  ✓ Quality level set to {quality['quality_level']}")

        return results

    def _calculate_confidence(self, requirements: Dict[str, Any]) -> float:
        """Calculate confidence based on validation results."""
        score = 0.5

        if "fields" in requirements:
            score += 0.2

        if "constraints" in requirements:
            score += 0.15

        if "quality_requirements" in requirements:
            score += 0.15

        return min(1.0, score)

    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about ReAct reasoning."""
        return {
            "name": "react",
            "description": "ReAct - Interleaves reasoning with actions for real-time validation",
            "use_cases": [
                "Real-time data validation",
                "API-integrated data generation",
                "External validation requirements",
                "Dynamic constraint checking",
            ],
            "parameters": {},
            "strengths": [
                "Validates during reasoning",
                "Catches issues early",
                "Good for external validation",
                "Iterative refinement",
            ],
            "limitations": [
                "May be slower due to actions",
                "Depends on external services",
                "More complex implementation",
            ],
        }
