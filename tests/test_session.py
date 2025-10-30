"""
Tests for session management.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import pytest

from synth_agent.core.exceptions import SessionError
from synth_agent.core.session import SessionManager, SessionState


class TestSessionState:
    """Test SessionState dataclass."""

    def test_create_session_state(self) -> None:
        """Test creating a session state."""
        now = datetime.now()
        state = SessionState(
            session_id="test-123",
            created_at=now,
            updated_at=now,
            phase="requirement_capture",
            requirements={"rows": 1000, "format": "csv"},
            format_config={"delimiter": ","},
            pattern_data=None,
            conversation_history=[{"role": "user", "content": "Generate data"}],
            metadata={"user": "test"},
        )

        assert state.session_id == "test-123"
        assert state.created_at == now
        assert state.updated_at == now
        assert state.phase == "requirement_capture"
        assert state.requirements == {"rows": 1000, "format": "csv"}
        assert state.format_config == {"delimiter": ","}
        assert state.pattern_data is None
        assert len(state.conversation_history) == 1
        assert state.metadata == {"user": "test"}

    def test_to_dict(self) -> None:
        """Test converting session state to dictionary."""
        now = datetime.now()
        state = SessionState(
            session_id="test-123",
            created_at=now,
            updated_at=now,
            phase="generation",
            requirements={},
            format_config={},
            pattern_data={"mean": 100},
            conversation_history=[],
            metadata={},
        )

        data = state.to_dict()
        assert data["session_id"] == "test-123"
        assert data["created_at"] == now.isoformat()
        assert data["updated_at"] == now.isoformat()
        assert data["phase"] == "generation"
        assert data["pattern_data"] == {"mean": 100}

    def test_from_dict(self) -> None:
        """Test creating session state from dictionary."""
        now = datetime.now()
        data: Dict[str, Any] = {
            "session_id": "test-456",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "phase": "format_selection",
            "requirements": {"format": "json"},
            "format_config": {},
            "pattern_data": None,
            "conversation_history": [],
            "metadata": {},
        }

        state = SessionState.from_dict(data)
        assert state.session_id == "test-456"
        assert state.created_at == now
        assert state.updated_at == now
        assert state.phase == "format_selection"
        assert state.requirements == {"format": "json"}

    def test_round_trip_conversion(self) -> None:
        """Test converting to dict and back."""
        now = datetime.now()
        original = SessionState(
            session_id="test-789",
            created_at=now,
            updated_at=now,
            phase="pattern_analysis",
            requirements={"rows": 5000},
            format_config={"indent": 2},
            pattern_data={"distribution": "normal"},
            conversation_history=[{"role": "user", "content": "Test"}],
            metadata={"version": "1.0"},
        )

        data = original.to_dict()
        restored = SessionState.from_dict(data)

        assert restored.session_id == original.session_id
        assert restored.phase == original.phase
        assert restored.requirements == original.requirements
        assert restored.format_config == original.format_config
        assert restored.pattern_data == original.pattern_data
        assert restored.conversation_history == original.conversation_history
        assert restored.metadata == original.metadata


class TestSessionManager:
    """Test SessionManager class."""

    @pytest.fixture
    def db_path(self, tmp_path: Path) -> Path:
        """Create temporary database path."""
        return tmp_path / "test_sessions.db"

    @pytest.fixture
    def session_manager(self, db_path: Path) -> SessionManager:
        """Create session manager instance."""
        return SessionManager(db_path)

    @pytest.fixture
    def sample_state(self) -> SessionState:
        """Create sample session state."""
        now = datetime.now()
        return SessionState(
            session_id="test-session-1",
            created_at=now,
            updated_at=now,
            phase="requirement_capture",
            requirements={"rows": 1000, "columns": ["name", "age"]},
            format_config={"format": "csv"},
            pattern_data=None,
            conversation_history=[{"role": "user", "content": "Generate test data"}],
            metadata={"source": "test"},
        )

    def test_init_creates_database(self, db_path: Path, session_manager: SessionManager) -> None:
        """Test that initialization creates database and tables."""
        assert db_path.exists()

        # Verify tables were created
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'"
            )
            assert cursor.fetchone() is not None

    def test_save_session(
        self, session_manager: SessionManager, sample_state: SessionState
    ) -> None:
        """Test saving a session."""
        session_manager.save_session(sample_state)

        # Verify session was saved
        loaded = session_manager.load_session(sample_state.session_id)
        assert loaded is not None
        assert loaded.session_id == sample_state.session_id
        assert loaded.phase == sample_state.phase
        assert loaded.requirements == sample_state.requirements

    def test_save_session_twice_updates(
        self, session_manager: SessionManager, sample_state: SessionState
    ) -> None:
        """Test that saving same session twice updates it."""
        session_manager.save_session(sample_state)

        # Modify and save again
        sample_state.phase = "generation"
        sample_state.requirements["rows"] = 2000
        session_manager.save_session(sample_state)

        # Load and verify update
        loaded = session_manager.load_session(sample_state.session_id)
        assert loaded is not None
        assert loaded.phase == "generation"
        assert loaded.requirements["rows"] == 2000

    def test_load_nonexistent_session(self, session_manager: SessionManager) -> None:
        """Test loading a session that doesn't exist."""
        result = session_manager.load_session("nonexistent-session")
        assert result is None

    def test_load_session(
        self, session_manager: SessionManager, sample_state: SessionState
    ) -> None:
        """Test loading a saved session."""
        session_manager.save_session(sample_state)
        loaded = session_manager.load_session(sample_state.session_id)

        assert loaded is not None
        assert loaded.session_id == sample_state.session_id
        assert loaded.phase == sample_state.phase
        assert loaded.requirements == sample_state.requirements
        assert loaded.format_config == sample_state.format_config
        assert loaded.pattern_data == sample_state.pattern_data
        assert loaded.conversation_history == sample_state.conversation_history
        assert loaded.metadata == sample_state.metadata

    def test_list_sessions_empty(self, session_manager: SessionManager) -> None:
        """Test listing sessions when database is empty."""
        sessions = session_manager.list_sessions()
        assert sessions == []

    def test_list_sessions(self, session_manager: SessionManager) -> None:
        """Test listing sessions."""
        # Create multiple sessions
        now = datetime.now()
        for i in range(5):
            state = SessionState(
                session_id=f"session-{i}",
                created_at=now,
                updated_at=now,
                phase="requirement_capture",
                requirements={},
                format_config={},
                pattern_data=None,
                conversation_history=[],
                metadata={"index": i},
            )
            session_manager.save_session(state)

        # List sessions
        sessions = session_manager.list_sessions(limit=10)
        assert len(sessions) == 5
        assert all("session_id" in s for s in sessions)
        assert all("created_at" in s for s in sessions)
        assert all("updated_at" in s for s in sessions)
        assert all("phase" in s for s in sessions)
        assert all("metadata" in s for s in sessions)

    def test_list_sessions_limit(self, session_manager: SessionManager) -> None:
        """Test limiting the number of listed sessions."""
        now = datetime.now()
        for i in range(10):
            state = SessionState(
                session_id=f"session-{i}",
                created_at=now,
                updated_at=now,
                phase="requirement_capture",
                requirements={},
                format_config={},
                pattern_data=None,
                conversation_history=[],
                metadata={},
            )
            session_manager.save_session(state)

        sessions = session_manager.list_sessions(limit=3)
        assert len(sessions) == 3

    def test_delete_session(
        self, session_manager: SessionManager, sample_state: SessionState
    ) -> None:
        """Test deleting a session."""
        session_manager.save_session(sample_state)
        result = session_manager.delete_session(sample_state.session_id)
        assert result is True

        # Verify deletion
        loaded = session_manager.load_session(sample_state.session_id)
        assert loaded is None

    def test_delete_nonexistent_session(self, session_manager: SessionManager) -> None:
        """Test deleting a session that doesn't exist."""
        result = session_manager.delete_session("nonexistent")
        assert result is False

    def test_cleanup_old_sessions(self, session_manager: SessionManager) -> None:
        """Test cleaning up old sessions."""
        now = datetime.now()
        # Create 10 sessions
        for i in range(10):
            state = SessionState(
                session_id=f"session-{i}",
                created_at=now,
                updated_at=now,
                phase="requirement_capture",
                requirements={},
                format_config={},
                pattern_data=None,
                conversation_history=[],
                metadata={},
            )
            session_manager.save_session(state)

        # Keep only 5 most recent
        deleted = session_manager.cleanup_old_sessions(max_sessions=5)
        assert deleted == 5

        # Verify only 5 sessions remain
        sessions = session_manager.list_sessions(limit=100)
        assert len(sessions) == 5

    def test_cleanup_with_fewer_sessions(self, session_manager: SessionManager) -> None:
        """Test cleanup when there are fewer sessions than max."""
        now = datetime.now()
        # Create 3 sessions
        for i in range(3):
            state = SessionState(
                session_id=f"session-{i}",
                created_at=now,
                updated_at=now,
                phase="requirement_capture",
                requirements={},
                format_config={},
                pattern_data=None,
                conversation_history=[],
                metadata={},
            )
            session_manager.save_session(state)

        # Try to keep 10 (more than we have)
        deleted = session_manager.cleanup_old_sessions(max_sessions=10)
        assert deleted == 0

        # Verify all sessions still exist
        sessions = session_manager.list_sessions()
        assert len(sessions) == 3

    def test_session_with_pattern_data(self, session_manager: SessionManager) -> None:
        """Test session with pattern data."""
        now = datetime.now()
        state = SessionState(
            session_id="pattern-test",
            created_at=now,
            updated_at=now,
            phase="pattern_analysis",
            requirements={},
            format_config={},
            pattern_data={"distribution": "normal", "mean": 50, "std": 10},
            conversation_history=[],
            metadata={},
        )

        session_manager.save_session(state)
        loaded = session_manager.load_session("pattern-test")

        assert loaded is not None
        assert loaded.pattern_data == {"distribution": "normal", "mean": 50, "std": 10}

    def test_session_with_empty_pattern_data(self, session_manager: SessionManager) -> None:
        """Test session with None pattern data."""
        now = datetime.now()
        state = SessionState(
            session_id="no-pattern-test",
            created_at=now,
            updated_at=now,
            phase="requirement_capture",
            requirements={},
            format_config={},
            pattern_data=None,
            conversation_history=[],
            metadata={},
        )

        session_manager.save_session(state)
        loaded = session_manager.load_session("no-pattern-test")

        assert loaded is not None
        assert loaded.pattern_data is None

    def test_session_with_complex_conversation_history(
        self, session_manager: SessionManager
    ) -> None:
        """Test session with complex conversation history."""
        now = datetime.now()
        conversation = [
            {"role": "user", "content": "Generate customer data"},
            {"role": "assistant", "content": "What format would you like?"},
            {"role": "user", "content": "CSV format please"},
            {"role": "assistant", "content": "How many rows?"},
            {"role": "user", "content": "1000 rows"},
        ]

        state = SessionState(
            session_id="conversation-test",
            created_at=now,
            updated_at=now,
            phase="generation",
            requirements={},
            format_config={},
            pattern_data=None,
            conversation_history=conversation,
            metadata={},
        )

        session_manager.save_session(state)
        loaded = session_manager.load_session("conversation-test")

        assert loaded is not None
        assert loaded.conversation_history == conversation
        assert len(loaded.conversation_history) == 5
