"""
Requirement Parser - Extracts structured requirements from natural language.
"""

import json
from typing import Any, Dict, List, Optional

from synth_agent.core.exceptions import ValidationError
from synth_agent.llm.base import LLMMessage
from synth_agent.llm.manager import LLMManager
from synth_agent.llm.prompts import REQUIREMENT_EXTRACTION_PROMPT, SYSTEM_PROMPT, format_prompt


class RequirementParser:
    """Parses user requirements from natural language input."""

    def __init__(self, llm_manager: LLMManager) -> None:
        """
        Initialize requirement parser.

        Args:
            llm_manager: LLM manager instance
        """
        self.llm_manager = llm_manager

    async def parse_requirements(self, user_input: str) -> Dict[str, Any]:
        """
        Parse user input and extract structured requirements.

        Args:
            user_input: Natural language description of requirements

        Returns:
            Dictionary with structured requirements

        Raises:
            ValidationError: If parsing fails
        """
        try:
            # Create prompt
            prompt = format_prompt(REQUIREMENT_EXTRACTION_PROMPT, user_input=user_input)

            # Create messages
            messages = [
                LLMMessage(role="system", content=SYSTEM_PROMPT),
                LLMMessage(role="user", content=prompt),
            ]

            # Get LLM response
            response = await self.llm_manager.chat(messages)

            # Parse JSON response
            requirements = self._extract_json(response.content)

            # Validate requirements structure
            self._validate_requirements(requirements)

            return requirements

        except json.JSONDecodeError as e:
            raise ValidationError(f"Failed to parse LLM response as JSON: {e}")
        except Exception as e:
            raise ValidationError(f"Failed to parse requirements: {e}")

    async def refine_requirements(
        self, current_requirements: Dict[str, Any], clarifications: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Refine requirements based on user clarifications.

        Args:
            current_requirements: Current requirements
            clarifications: User clarifications

        Returns:
            Updated requirements
        """
        try:
            prompt = f"""Update the following requirements based on user clarifications:

Current Requirements:
{json.dumps(current_requirements, indent=2)}

User Clarifications:
{json.dumps(clarifications, indent=2)}

Return the updated requirements in the same JSON format, incorporating the clarifications."""

            messages = [
                LLMMessage(role="system", content=SYSTEM_PROMPT),
                LLMMessage(role="user", content=prompt),
            ]

            response = await self.llm_manager.chat(messages)
            updated_requirements = self._extract_json(response.content)
            self._validate_requirements(updated_requirements)

            return updated_requirements

        except Exception as e:
            raise ValidationError(f"Failed to refine requirements: {e}")

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """
        Extract JSON from LLM response (handles markdown code blocks).

        Args:
            text: Text potentially containing JSON

        Returns:
            Parsed JSON object
        """
        # Try to extract JSON from markdown code blocks
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            json_text = text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            json_text = text[start:end].strip()
        else:
            json_text = text.strip()

        return json.loads(json_text)

    def _validate_requirements(self, requirements: Dict[str, Any]) -> None:
        """
        Validate requirements structure.

        Args:
            requirements: Requirements dictionary

        Raises:
            ValidationError: If requirements are invalid
        """
        required_keys = ["data_type", "fields", "confidence"]

        for key in required_keys:
            if key not in requirements:
                raise ValidationError(f"Missing required key in requirements: {key}")

        if not isinstance(requirements["fields"], list):
            raise ValidationError("'fields' must be a list")

        if not isinstance(requirements["confidence"], (int, float)):
            raise ValidationError("'confidence' must be a number")

        if not 0.0 <= requirements["confidence"] <= 1.0:
            raise ValidationError("'confidence' must be between 0.0 and 1.0")

    def get_requirement_summary(self, requirements: Dict[str, Any]) -> str:
        """
        Generate a human-readable summary of requirements.

        Args:
            requirements: Requirements dictionary

        Returns:
            Summary string
        """
        lines = [
            f"Data Type: {requirements.get('data_type', 'Unknown')}",
            f"Number of Fields: {len(requirements.get('fields', []))}",
            f"Dataset Size: {requirements.get('size', 'Not specified')} records",
            f"Output Format: {requirements.get('format', 'Not specified')}",
        ]

        fields = requirements.get("fields", [])
        if fields:
            lines.append("\nFields:")
            for field in fields:
                field_name = field.get("name", "Unknown")
                field_type = field.get("type", "Unknown")
                lines.append(f"  - {field_name}: {field_type}")

        constraints = requirements.get("constraints", [])
        if constraints:
            lines.append(f"\nConstraints: {len(constraints)} defined")

        relationships = requirements.get("relationships", [])
        if relationships:
            lines.append(f"Relationships: {len(relationships)} defined")

        confidence = requirements.get("confidence", 0.0)
        lines.append(f"\nConfidence: {confidence:.1%}")

        return "\n".join(lines)

    def extract_fields(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract field definitions from requirements.

        Args:
            requirements: Requirements dictionary

        Returns:
            List of field definitions
        """
        return requirements.get("fields", [])

    def extract_constraints(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract constraints from requirements.

        Args:
            requirements: Requirements dictionary

        Returns:
            List of constraints
        """
        return requirements.get("constraints", [])

    def extract_relationships(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract relationships from requirements.

        Args:
            requirements: Requirements dictionary

        Returns:
            List of relationships
        """
        return requirements.get("relationships", [])
