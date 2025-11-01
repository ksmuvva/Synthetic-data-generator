"""
Chain of Thought (CoT) reasoning for synthetic data generation.

Ideal for healthcare, legal, education data with complex constraints
requiring step-by-step logical reasoning.
"""

from typing import Dict, Any, List, Optional
import copy

from .base import BaseReasoningStrategy, ReasoningResult


class ChainOfThoughtReasoner(BaseReasoningStrategy):
    """
    Chain of Thought reasoning strategy.

    Applies step-by-step logical reasoning to understand and enhance
    complex data requirements, especially useful for constrained domains.
    """

    def __init__(self, config: Optional[Any] = None):
        """Initialize Chain of Thought reasoner."""
        super().__init__(config)

        self.max_steps = 10
        if config and hasattr(config, "reasoning"):
            self.max_steps = getattr(config.reasoning, "cot_max_steps", 10)

    async def reason(
        self,
        requirements: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> ReasoningResult:
        """
        Apply chain of thought reasoning to requirements.

        Args:
            requirements: Initial requirements
            context: Optional context

        Returns:
            ReasoningResult with enhanced requirements
        """
        self.logger.info("Starting Chain of Thought reasoning")

        enhanced = copy.deepcopy(requirements)
        reasoning_steps = ["Starting Chain of Thought analysis"]

        # Step 1: Understand the domain
        domain = self._extract_domain(enhanced)
        reasoning_steps.append(f"Step 1: Identified domain as '{domain or 'general'}'")

        # Step 2: Analyze field requirements
        if "fields" in enhanced:
            reasoning_steps.append("Step 2: Analyzing field requirements")
            enhanced, field_insights = self._analyze_fields(enhanced)
            reasoning_steps.extend(field_insights)

        # Step 3: Identify implicit constraints
        reasoning_steps.append("Step 3: Identifying implicit constraints")
        enhanced, constraint_insights = self._identify_constraints(enhanced, domain)
        reasoning_steps.extend(constraint_insights)

        # Step 4: Determine relationships
        reasoning_steps.append("Step 4: Determining field relationships")
        enhanced, relationship_insights = self._determine_relationships(enhanced)
        reasoning_steps.extend(relationship_insights)

        # Step 5: Add quality requirements
        reasoning_steps.append("Step 5: Establishing quality requirements")
        enhanced, quality_insights = self._add_quality_requirements(enhanced, domain)
        reasoning_steps.extend(quality_insights)

        # Step 6: Validate consistency
        reasoning_steps.append("Step 6: Validating requirement consistency")
        consistency_check = self._validate_consistency(enhanced)
        reasoning_steps.extend(consistency_check)

        confidence = self._calculate_confidence(enhanced)

        reasoning_steps.append(
            f"Completed Chain of Thought reasoning with confidence: {confidence:.2f}"
        )

        self.logger.info(
            "Chain of Thought completed",
            steps=len(reasoning_steps),
            confidence=confidence,
        )

        return ReasoningResult(
            enhanced_requirements=enhanced,
            reasoning_steps=reasoning_steps,
            confidence=confidence,
            metadata={"steps_count": len(reasoning_steps), "domain": domain},
        )

    def _analyze_fields(
        self,
        requirements: Dict[str, Any],
    ) -> tuple[Dict[str, Any], List[str]]:
        """Analyze and enhance field specifications."""
        insights = []
        fields = requirements.get("fields", [])

        for field in fields:
            if isinstance(field, dict):
                field_name = field.get("name", "unknown")
                field_type = field.get("type", "string")

                # Add type-specific constraints
                if field_type in ["integer", "number", "float"]:
                    if "constraints" not in field:
                        field["constraints"] = {}
                    if "min" not in field["constraints"] and "max" not in field["constraints"]:
                        # Infer reasonable ranges based on name
                        if "age" in field_name.lower():
                            field["constraints"]["min"] = 0
                            field["constraints"]["max"] = 120
                            insights.append(f"  → Inferred age range (0-120) for field '{field_name}'")
                        elif "count" in field_name.lower() or "quantity" in field_name.lower():
                            field["constraints"]["min"] = 0
                            insights.append(f"  → Set minimum 0 for count field '{field_name}'")

                # Check for required fields
                if field_name.lower() in ["id", "identifier", "name"]:
                    field["required"] = True
                    field["unique"] = True
                    insights.append(f"  → Marked '{field_name}' as required and unique")

        return requirements, insights

    def _identify_constraints(
        self,
        requirements: Dict[str, Any],
        domain: Optional[str],
    ) -> tuple[Dict[str, Any], List[str]]:
        """Identify implicit constraints based on domain."""
        insights = []

        if "constraints" not in requirements:
            requirements["constraints"] = []

        # Domain-specific constraints
        if domain == "healthcare":
            requirements["constraints"].append("HIPAA compliance required")
            requirements["constraints"].append("PHI data must be anonymizable")
            insights.append("  → Added healthcare compliance constraints")
        elif domain == "financial":
            requirements["constraints"].append("Transactions must balance")
            requirements["constraints"].append("Amounts must have 2 decimal precision")
            insights.append("  → Added financial integrity constraints")
        elif domain == "legal":
            requirements["constraints"].append("All fields must be auditable")
            insights.append("  → Added legal auditability constraint")

        return requirements, insights

    def _determine_relationships(
        self,
        requirements: Dict[str, Any],
    ) -> tuple[Dict[str, Any], List[str]]:
        """Determine relationships between fields."""
        insights = []
        fields = requirements.get("fields", [])

        if "relationships" not in requirements:
            requirements["relationships"] = []

        # Look for foreign key relationships
        field_names = [f.get("name", "") for f in fields if isinstance(f, dict)]

        for name in field_names:
            if "_id" in name.lower() and name.lower() != "id":
                parent = name.replace("_id", "").replace("_ID", "")
                requirements["relationships"].append({
                    "type": "foreign_key",
                    "from": name,
                    "to": f"{parent}.id",
                })
                insights.append(f"  → Detected foreign key relationship: {name} → {parent}.id")

        return requirements, insights

    def _add_quality_requirements(
        self,
        requirements: Dict[str, Any],
        domain: Optional[str],
    ) -> tuple[Dict[str, Any], List[str]]:
        """Add quality requirements based on domain."""
        insights = []

        if "quality_requirements" not in requirements:
            requirements["quality_requirements"] = {}

        quality = requirements["quality_requirements"]

        # Domain-specific quality requirements
        if domain in ["healthcare", "legal", "financial"]:
            quality["null_percentage"] = 0.0
            quality["quality_level"] = "very_high"
            quality["validation_required"] = True
            insights.append(f"  → Set very high quality standards for {domain} domain")
        else:
            if "null_percentage" not in quality:
                quality["null_percentage"] = 0.05
            if "quality_level" not in quality:
                quality["quality_level"] = "high"
            insights.append("  → Applied standard quality requirements")

        return requirements, insights

    def _validate_consistency(self, requirements: Dict[str, Any]) -> List[str]:
        """Validate requirement consistency."""
        checks = []

        # Check if size is reasonable
        if "size" in requirements:
            size = requirements["size"]
            if size > 1000000:
                checks.append("  ⚠ Large dataset size may impact generation time")
            elif size < 10:
                checks.append("  ⚠ Small dataset size may not show pattern diversity")

        # Check if all required fields have types
        fields = requirements.get("fields", [])
        missing_types = [
            f.get("name", "unknown")
            for f in fields
            if isinstance(f, dict) and "type" not in f
        ]
        if missing_types:
            checks.append(f"  ⚠ Fields missing type specification: {', '.join(missing_types)}")
        else:
            checks.append("  ✓ All fields have type specifications")

        return checks

    def _calculate_confidence(self, requirements: Dict[str, Any]) -> float:
        """Calculate confidence based on requirement completeness."""
        score = 0.5  # Base confidence

        if "fields" in requirements and requirements["fields"]:
            score += 0.2

        if "quality_requirements" in requirements:
            score += 0.1

        if "relationships" in requirements and requirements["relationships"]:
            score += 0.1

        if "constraints" in requirements and requirements["constraints"]:
            score += 0.1

        return min(1.0, score)

    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about Chain of Thought reasoning."""
        return {
            "name": "chain_of_thought",
            "description": "Chain of Thought - Step-by-step reasoning for complex constrained data",
            "use_cases": [
                "Healthcare data with HIPAA compliance",
                "Legal documents with auditability",
                "Educational data with complex rules",
                "Any domain with intricate constraints",
            ],
            "parameters": {
                "max_steps": self.max_steps,
            },
            "strengths": [
                "Excellent for complex constraints",
                "Clear reasoning trail",
                "Domain-aware enhancements",
                "Good explainability",
            ],
            "limitations": [
                "Can be verbose",
                "May over-constrain simple cases",
                "Requires good domain knowledge",
            ],
        }
