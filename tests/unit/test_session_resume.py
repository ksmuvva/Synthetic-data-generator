"""Unit tests for session resume functionality."""

from datetime import datetime

import pytest

from synth_agent.conversation.manager import ConversationManager, ConversationPhase


class TestSessionResume:
    """Test session resume functionality."""

    def test_load_from_session(self, mock_llm_manager, mock_config, mock_session_manager):
        """Test loading state from a saved session."""
        # Create conversation manager
        conversation = ConversationManager(
            mock_llm_manager, mock_config, mock_session_manager
        )

        # Create sample session data
        session_data = {
            "session_id": "test-session-123",
            "phase": "format_selection",
            "created_at": "2024-01-01T10:00:00",
            "requirements": {
                "data_type": "customer_data",
                "fields": [
                    {"name": "id", "type": "integer"},
                    {"name": "name", "type": "string"}
                ],
                "size": 1000
            },
            "format_config": {"format": "csv"},
            "pattern_data": None,
            "conversation_history": [
                {"role": "user", "content": "Generate customer data"},
                {"role": "assistant", "content": "I'll help you generate customer data"}
            ]
        }

        # Load session
        conversation.load_from_session(session_data)

        # Verify state was loaded
        assert conversation.session_id == "test-session-123"
        assert conversation.phase == ConversationPhase.FORMAT_SELECTION
        assert conversation.requirements["data_type"] == "customer_data"
        assert conversation.format_config["format"] == "csv"
        assert len(conversation.conversation_history) == 2

    def test_load_from_session_with_invalid_phase(
        self, mock_llm_manager, mock_config, mock_session_manager
    ):
        """Test loading session with invalid phase falls back to INITIAL."""
        conversation = ConversationManager(
            mock_llm_manager, mock_config, mock_session_manager
        )

        session_data = {
            "session_id": "test-session-456",
            "phase": "invalid_phase_name",
            "created_at": "2024-01-01T10:00:00",
            "requirements": {},
            "format_config": {},
            "pattern_data": None,
            "conversation_history": []
        }

        conversation.load_from_session(session_data)

        # Should default to INITIAL phase
        assert conversation.phase == ConversationPhase.INITIAL

    def test_load_from_session_partial_data(
        self, mock_llm_manager, mock_config, mock_session_manager
    ):
        """Test loading session with partial data."""
        conversation = ConversationManager(
            mock_llm_manager, mock_config, mock_session_manager
        )

        # Minimal session data
        session_data = {
            "session_id": "test-session-789",
            "phase": "initial"
        }

        conversation.load_from_session(session_data)

        # Verify defaults are used for missing fields
        assert conversation.session_id == "test-session-789"
        assert conversation.phase == ConversationPhase.INITIAL
        assert conversation.requirements == {}
        assert conversation.format_config == {}
        assert conversation.pattern_data is None
        assert conversation.conversation_history == []

    def test_session_roundtrip(self, mock_llm_manager, mock_config, tmp_path):
        """Test saving and loading a session."""
        from synth_agent.core.session import SessionManager

        # Create session manager with temporary DB
        session_db = tmp_path / "test_sessions.db"
        session_manager = SessionManager(session_db)

        # Create conversation and set some state
        conversation1 = ConversationManager(
            mock_llm_manager, mock_config, session_manager
        )
        conversation1.phase = ConversationPhase.FORMAT_SELECTION
        conversation1.requirements = {"data_type": "test"}
        conversation1.format_config = {"format": "json"}
        conversation1._add_to_history("user", "test message")

        # Save session
        conversation1._save_session()
        session_id = conversation1.session_id

        # Load session into new conversation
        session_data = session_manager.load_session(session_id)
        conversation2 = ConversationManager(
            mock_llm_manager, mock_config, session_manager
        )
        conversation2.load_from_session(session_data)

        # Verify state matches
        assert conversation2.session_id == session_id
        assert conversation2.phase == ConversationPhase.FORMAT_SELECTION
        assert conversation2.requirements == {"data_type": "test"}
        assert conversation2.format_config == {"format": "json"}
        assert len(conversation2.conversation_history) == 1
        assert conversation2.conversation_history[0]["content"] == "test message"
