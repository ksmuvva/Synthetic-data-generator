"""
Conversation Manager - Orchestrates multi-turn conversation flow for the agent.
"""

import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from synth_agent.analysis.ambiguity_detector import AmbiguityDetector
from synth_agent.analysis.pattern_analyzer import PatternAnalyzer
from synth_agent.analysis.requirement_parser import RequirementParser
from synth_agent.core.config import Config
from synth_agent.core.exceptions import SynthAgentError
from synth_agent.core.session import SessionManager, SessionState
from synth_agent.formats.manager import FormatManager
from synth_agent.generation.engine import DataGenerationEngine
from synth_agent.llm.manager import LLMManager


class ConversationPhase(Enum):
    """Phases of the conversation flow."""

    INITIAL = "initial"
    REQUIREMENT_CAPTURE = "requirement_capture"
    AMBIGUITY_RESOLUTION = "ambiguity_resolution"
    FORMAT_SELECTION = "format_selection"
    PATTERN_INQUIRY = "pattern_inquiry"
    PATTERN_ANALYSIS = "pattern_analysis"
    GENERATION_CONFIRMATION = "generation_confirmation"
    GENERATING = "generating"
    COMPLETED = "completed"


class ConversationManager:
    """Manages the end-to-end conversation flow."""

    def __init__(
        self,
        llm_manager: LLMManager,
        config: Config,
        session_manager: Optional[SessionManager] = None,
    ) -> None:
        """
        Initialize conversation manager.

        Args:
            llm_manager: LLM manager instance
            config: Configuration object
            session_manager: Optional session manager for persistence
        """
        self.llm_manager = llm_manager
        self.config = config
        self.session_manager = session_manager

        # Initialize components
        self.requirement_parser = RequirementParser(llm_manager)
        self.ambiguity_detector = AmbiguityDetector(llm_manager, config)
        self.pattern_analyzer = PatternAnalyzer(llm_manager, config)
        self.data_generator = DataGenerationEngine(config)
        self.format_manager = FormatManager(config)

        # Session state
        self.session_id = str(uuid.uuid4())
        self.phase = ConversationPhase.INITIAL
        self.requirements: Dict[str, Any] = {}
        self.ambiguities: List[Dict[str, Any]] = []
        self.format_config: Dict[str, Any] = {}
        self.pattern_data: Optional[Dict[str, Any]] = None
        self.generated_data: Optional[pd.DataFrame] = None
        self.conversation_history: List[Dict[str, str]] = []
        self.created_at = datetime.now()

    async def process_user_input(self, user_input: str) -> Dict[str, Any]:
        """
        Process user input and return response.

        Args:
            user_input: User's message

        Returns:
            Response dictionary with message and metadata
        """
        # Add to conversation history
        self._add_to_history("user", user_input)

        # Route based on current phase
        if self.phase == ConversationPhase.INITIAL:
            response = await self._handle_initial_input(user_input)

        elif self.phase == ConversationPhase.REQUIREMENT_CAPTURE:
            response = await self._handle_requirement_capture(user_input)

        elif self.phase == ConversationPhase.AMBIGUITY_RESOLUTION:
            response = await self._handle_ambiguity_resolution(user_input)

        elif self.phase == ConversationPhase.FORMAT_SELECTION:
            response = await self._handle_format_selection(user_input)

        elif self.phase == ConversationPhase.PATTERN_INQUIRY:
            response = await self._handle_pattern_inquiry(user_input)

        elif self.phase == ConversationPhase.PATTERN_ANALYSIS:
            response = await self._handle_pattern_analysis(user_input)

        elif self.phase == ConversationPhase.GENERATION_CONFIRMATION:
            response = await self._handle_generation_confirmation(user_input)

        elif self.phase == ConversationPhase.GENERATING:
            response = {
                "message": "Data generation is in progress. Please wait...",
                "phase": self.phase.value,
            }

        elif self.phase == ConversationPhase.COMPLETED:
            response = {
                "message": "This session has completed. Start a new session to generate more data.",
                "phase": self.phase.value,
            }

        else:
            response = {
                "message": f"Unknown phase: {self.phase.value}",
                "phase": self.phase.value,
                "error": True,
            }

        # Add to conversation history
        self._add_to_history("assistant", response.get("message", ""))

        # Save session if manager is available
        if self.session_manager:
            self._save_session()

        return response

    async def _handle_initial_input(self, user_input: str) -> Dict[str, Any]:
        """Handle initial user input."""
        # Parse requirements
        self.requirements = await self.requirement_parser.parse_requirements(user_input)

        # Move to next phase
        self.phase = ConversationPhase.AMBIGUITY_RESOLUTION

        # Check for ambiguities
        analysis = await self.ambiguity_detector.detect_ambiguities(self.requirements)

        if analysis.get("has_ambiguities", False):
            self.ambiguities = analysis.get("ambiguities", [])
            questions = await self.ambiguity_detector.generate_questions(self.ambiguities)

            return {
                "message": self.ambiguity_detector.format_questions_for_display(questions),
                "phase": self.phase.value,
                "requirements": self.requirements,
                "questions": questions,
            }
        else:
            # No ambiguities, move to format selection
            self.phase = ConversationPhase.FORMAT_SELECTION
            return {
                "message": "Great! I understand your requirements. What output format would you like? (csv, json)",
                "phase": self.phase.value,
                "requirements": self.requirements,
            }

    async def _handle_requirement_capture(self, user_input: str) -> Dict[str, Any]:
        """Handle requirement refinement."""
        # This phase is for iterative refinement
        self.requirements = await self.requirement_parser.parse_requirements(user_input)
        self.phase = ConversationPhase.AMBIGUITY_RESOLUTION

        return await self._handle_ambiguity_resolution("")

    async def _handle_ambiguity_resolution(self, user_input: str) -> Dict[str, Any]:
        """Handle ambiguity resolution."""
        if user_input:
            # Parse clarifications from user input
            clarifications = {"clarification": user_input}
            self.requirements = await self.requirement_parser.refine_requirements(
                self.requirements, clarifications
            )

        # Check if we still have critical ambiguities
        analysis = await self.ambiguity_detector.detect_ambiguities(self.requirements)

        if self.ambiguity_detector.has_critical_ambiguities(analysis):
            self.ambiguities = analysis.get("ambiguities", [])
            questions = await self.ambiguity_detector.generate_questions(self.ambiguities)

            return {
                "message": "I need a bit more information:\n\n"
                + self.ambiguity_detector.format_questions_for_display(questions),
                "phase": self.phase.value,
                "questions": questions,
            }
        else:
            # Ambiguities resolved, move to format selection
            self.phase = ConversationPhase.FORMAT_SELECTION
            summary = self.requirement_parser.get_requirement_summary(self.requirements)

            return {
                "message": f"Perfect! Here's what I understood:\n\n{summary}\n\nWhat output format would you like? (csv, json)",
                "phase": self.phase.value,
                "requirements": self.requirements,
            }

    async def _handle_format_selection(self, user_input: str) -> Dict[str, Any]:
        """Handle format selection."""
        format_name = user_input.strip().lower()

        if not self.format_manager.is_format_supported(format_name):
            supported = ", ".join(self.format_manager.get_supported_formats())
            return {
                "message": f"Sorry, '{format_name}' is not supported. Available formats: {supported}",
                "phase": self.phase.value,
            }

        self.format_config = {"format": format_name}
        self.phase = ConversationPhase.PATTERN_INQUIRY

        return {
            "message": f"Great! I'll generate the data in {format_name.upper()} format.\n\n"
            "Do you have sample/pattern data that I should match? (yes/no)",
            "phase": self.phase.value,
            "format": format_name,
        }

    async def _handle_pattern_inquiry(self, user_input: str) -> Dict[str, Any]:
        """Handle pattern data inquiry."""
        response = user_input.strip().lower()

        if response in ["yes", "y"]:
            return {
                "message": "Please provide the path to your sample data file (CSV, JSON, Excel, etc.):",
                "phase": ConversationPhase.PATTERN_ANALYSIS.value,
            }
        else:
            # No pattern data, move to generation confirmation
            self.phase = ConversationPhase.GENERATION_CONFIRMATION
            return {
                "message": "No problem! I'll generate data based on your requirements.\n\n"
                "Ready to generate? (yes to proceed)",
                "phase": self.phase.value,
            }

    async def _handle_pattern_analysis(self, user_input: str) -> Dict[str, Any]:
        """Handle pattern data analysis."""
        file_path = Path(user_input.strip())

        try:
            self.pattern_data = await self.pattern_analyzer.analyze_pattern_file(file_path)
            self.phase = ConversationPhase.GENERATION_CONFIRMATION

            return {
                "message": "Pattern data analyzed successfully!\n\n"
                f"Found {len(self.pattern_data.get('fields', []))} fields in your sample data.\n\n"
                "Ready to generate matching data? (yes to proceed)",
                "phase": self.phase.value,
                "pattern_data": self.pattern_data,
            }
        except Exception as e:
            return {
                "message": f"Error analyzing pattern file: {e}\n\nPlease provide a valid file path or type 'skip' to proceed without pattern data.",
                "phase": self.phase.value,
                "error": True,
            }

    async def _handle_generation_confirmation(self, user_input: str) -> Dict[str, Any]:
        """Handle generation confirmation and execute generation."""
        response = user_input.strip().lower()

        if response not in ["yes", "y"]:
            return {
                "message": "Please type 'yes' when you're ready to generate the data.",
                "phase": self.phase.value,
            }

        # Generate data
        self.phase = ConversationPhase.GENERATING

        try:
            # Create schema from requirements
            schema = self._create_schema_from_requirements()

            # Generate data
            num_rows = self.requirements.get("size", self.config.generation.default_rows)
            self.generated_data = self.data_generator.generate(
                schema=schema, num_rows=num_rows, pattern_analysis=self.pattern_data
            )

            # Export data
            output_dir = Path(self.config.storage.default_output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            format_name = self.format_config.get("format", "csv")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = output_dir / f"synthetic_data_{timestamp}.{format_name}"

            self.format_manager.export(self.generated_data, output_file, format_name)

            self.phase = ConversationPhase.COMPLETED

            return {
                "message": f"Success! Generated {len(self.generated_data)} rows of synthetic data.\n\n"
                f"Output saved to: {output_file}\n\n"
                f"Fields: {', '.join(self.generated_data.columns.tolist())}",
                "phase": self.phase.value,
                "output_file": str(output_file),
                "row_count": len(self.generated_data),
                "columns": self.generated_data.columns.tolist(),
            }

        except Exception as e:
            self.phase = ConversationPhase.GENERATION_CONFIRMATION
            raise SynthAgentError(f"Failed to generate data: {e}")

    def _create_schema_from_requirements(self) -> Dict[str, Any]:
        """Create generation schema from requirements."""
        fields = self.requirements.get("fields", [])

        return {
            "fields": fields,
            "relationships": self.requirements.get("relationships", []),
            "constraints": self.requirements.get("constraints", []),
            "quality_controls": self.requirements.get("quality_requirements", {}),
        }

    def _add_to_history(self, role: str, content: str) -> None:
        """Add message to conversation history."""
        self.conversation_history.append({"role": role, "content": content, "timestamp": datetime.now().isoformat()})

    def _save_session(self) -> None:
        """Save current session state."""
        if not self.session_manager:
            return

        state = SessionState(
            session_id=self.session_id,
            created_at=self.created_at,
            updated_at=datetime.now(),
            phase=self.phase.value,
            requirements=self.requirements,
            format_config=self.format_config,
            pattern_data=self.pattern_data,
            conversation_history=self.conversation_history,
            metadata={"format": self.format_config.get("format", "unknown")},
        )

        self.session_manager.save_session(state)

    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session."""
        return {
            "session_id": self.session_id,
            "phase": self.phase.value,
            "requirements": self.requirements,
            "format": self.format_config.get("format"),
            "has_pattern_data": self.pattern_data is not None,
            "message_count": len(self.conversation_history),
        }
