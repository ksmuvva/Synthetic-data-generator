"""
Ambiguity Detector - Identifies unclear or conflicting requirements.
"""

import json
from typing import Any, Dict, List

from synth_agent.core.config import Config
from synth_agent.core.exceptions import AmbiguityError
from synth_agent.llm.base import LLMMessage
from synth_agent.llm.manager import LLMManager
from synth_agent.llm.prompts import (
    AMBIGUITY_DETECTION_PROMPT,
    QUESTION_GENERATION_PROMPT,
    SYSTEM_PROMPT,
    format_prompt,
)


class AmbiguityDetector:
    """Detects ambiguities and generates clarifying questions."""

    def __init__(self, llm_manager: LLMManager, config: Config) -> None:
        """
        Initialize ambiguity detector.

        Args:
            llm_manager: LLM manager instance
            config: Configuration object
        """
        self.llm_manager = llm_manager
        self.config = config

    async def detect_ambiguities(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect ambiguities in requirements.

        Args:
            requirements: Requirements dictionary

        Returns:
            Dictionary with ambiguity analysis
        """
        try:
            # Create prompt
            prompt = format_prompt(
                AMBIGUITY_DETECTION_PROMPT, requirements=json.dumps(requirements, indent=2)
            )

            # Create messages
            messages = [
                LLMMessage(role="system", content=SYSTEM_PROMPT),
                LLMMessage(role="user", content=prompt),
            ]

            # Get LLM response
            response = await self.llm_manager.chat(messages)

            # Parse response
            analysis = self._extract_json(response.content)

            return analysis

        except Exception as e:
            raise AmbiguityError(f"Failed to detect ambiguities: {e}")

    async def generate_questions(self, ambiguities: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Generate clarifying questions for ambiguities.

        Args:
            ambiguities: List of detected ambiguities

        Returns:
            List of clarifying questions
        """
        try:
            # Limit number of questions based on config
            max_questions = self.config.analysis.max_clarification_questions
            priority_ambiguities = self._prioritize_ambiguities(ambiguities, max_questions)

            # Create prompt
            prompt = format_prompt(
                QUESTION_GENERATION_PROMPT, ambiguities=json.dumps(priority_ambiguities, indent=2)
            )

            # Create messages
            messages = [
                LLMMessage(role="system", content=SYSTEM_PROMPT),
                LLMMessage(role="user", content=prompt),
            ]

            # Get LLM response
            response = await self.llm_manager.chat(messages)

            # Parse response
            questions = self._extract_json(response.content)

            if not isinstance(questions, list):
                raise AmbiguityError("Expected list of questions")

            return questions

        except Exception as e:
            raise AmbiguityError(f"Failed to generate questions: {e}")

    def has_critical_ambiguities(self, analysis: Dict[str, Any]) -> bool:
        """
        Check if there are critical ambiguities that block generation.

        Args:
            analysis: Ambiguity analysis

        Returns:
            True if critical ambiguities exist
        """
        if not analysis.get("has_ambiguities", False):
            return False

        severity = analysis.get("severity", "minor")
        can_proceed = analysis.get("can_proceed", True)

        return severity == "critical" or not can_proceed

    def _prioritize_ambiguities(
        self, ambiguities: List[Dict[str, Any]], max_count: int
    ) -> List[Dict[str, Any]]:
        """
        Prioritize ambiguities by importance.

        Args:
            ambiguities: List of ambiguities
            max_count: Maximum number to return

        Returns:
            Prioritized list of ambiguities
        """
        # Define importance ordering
        importance_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}

        # Sort by importance
        sorted_ambiguities = sorted(
            ambiguities, key=lambda x: importance_order.get(x.get("importance", "low"), 999)
        )

        return sorted_ambiguities[:max_count]

    def format_questions_for_display(self, questions: List[Dict[str, str]]) -> str:
        """
        Format questions for user-friendly display.

        Args:
            questions: List of question objects

        Returns:
            Formatted string
        """
        if not questions:
            return "No clarifying questions needed."

        lines = ["I have a few questions to help generate accurate data:\n"]

        for i, q in enumerate(questions, 1):
            lines.append(f"{i}. {q.get('question', '')}")

            context = q.get("context")
            if context:
                lines.append(f"   Context: {context}")

            examples = q.get("examples", [])
            if examples:
                lines.append(f"   Examples: {', '.join(examples)}")

            lines.append("")  # Empty line between questions

        return "\n".join(lines)

    def validate_confidence_threshold(self, requirements: Dict[str, Any]) -> bool:
        """
        Check if requirement confidence meets threshold.

        Args:
            requirements: Requirements dictionary

        Returns:
            True if confidence is sufficient
        """
        confidence = requirements.get("confidence", 0.0)
        threshold = self.config.analysis.confidence_threshold

        return confidence >= threshold

    def _extract_json(self, text: str) -> Any:
        """
        Extract JSON from LLM response.

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

    def get_ambiguity_summary(self, analysis: Dict[str, Any]) -> str:
        """
        Generate summary of ambiguity analysis.

        Args:
            analysis: Ambiguity analysis

        Returns:
            Summary string
        """
        if not analysis.get("has_ambiguities", False):
            return "No ambiguities detected. Requirements are clear."

        ambiguities = analysis.get("ambiguities", [])
        severity = analysis.get("severity", "unknown")
        can_proceed = analysis.get("can_proceed", True)

        lines = [
            f"Ambiguity Analysis:",
            f"  Severity: {severity}",
            f"  Total ambiguities: {len(ambiguities)}",
            f"  Can proceed: {'Yes' if can_proceed else 'No'}",
        ]

        # Count by importance
        importance_counts = {}
        for amb in ambiguities:
            imp = amb.get("importance", "unknown")
            importance_counts[imp] = importance_counts.get(imp, 0) + 1

        if importance_counts:
            lines.append("  By importance:")
            for imp, count in sorted(importance_counts.items()):
                lines.append(f"    {imp}: {count}")

        return "\n".join(lines)
