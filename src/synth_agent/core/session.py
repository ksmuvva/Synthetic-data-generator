"""
Session management for persisting and resuming conversations.
"""

import json
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from synth_agent.core.exceptions import SessionError


@dataclass
class SessionState:
    """Represents the state of a session."""

    session_id: str
    created_at: datetime
    updated_at: datetime
    phase: str  # requirement_capture, format_selection, pattern_analysis, generation
    requirements: Dict[str, Any]
    format_config: Dict[str, Any]
    pattern_data: Optional[Dict[str, Any]]
    conversation_history: List[Dict[str, str]]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionState":
        """Create from dictionary."""
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        return cls(**data)


class SessionManager:
    """Manages session persistence using SQLite."""

    def __init__(self, db_path: Path) -> None:
        """
        Initialize session manager.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    phase TEXT NOT NULL,
                    requirements TEXT NOT NULL,
                    format_config TEXT NOT NULL,
                    pattern_data TEXT,
                    conversation_history TEXT NOT NULL,
                    metadata TEXT NOT NULL
                )
            """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_sessions_updated_at
                ON sessions(updated_at DESC)
            """
            )
            conn.commit()

    def save_session(self, state: SessionState) -> None:
        """
        Save session state.

        Args:
            state: Session state to save
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO sessions
                    (session_id, created_at, updated_at, phase, requirements,
                     format_config, pattern_data, conversation_history, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        state.session_id,
                        state.created_at.isoformat(),
                        state.updated_at.isoformat(),
                        state.phase,
                        json.dumps(state.requirements),
                        json.dumps(state.format_config),
                        json.dumps(state.pattern_data) if state.pattern_data else None,
                        json.dumps(state.conversation_history),
                        json.dumps(state.metadata),
                    ),
                )
                conn.commit()
        except sqlite3.Error as e:
            raise SessionError(f"Failed to save session: {e}")

    def load_session(self, session_id: str) -> Optional[SessionState]:
        """
        Load session state.

        Args:
            session_id: Session ID to load

        Returns:
            SessionState if found, None otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
                )
                row = cursor.fetchone()

                if not row:
                    return None

                return SessionState(
                    session_id=row["session_id"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"]),
                    phase=row["phase"],
                    requirements=json.loads(row["requirements"]),
                    format_config=json.loads(row["format_config"]),
                    pattern_data=json.loads(row["pattern_data"]) if row["pattern_data"] else None,
                    conversation_history=json.loads(row["conversation_history"]),
                    metadata=json.loads(row["metadata"]),
                )
        except (sqlite3.Error, json.JSONDecodeError) as e:
            raise SessionError(f"Failed to load session: {e}")

    def list_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        List recent sessions.

        Args:
            limit: Maximum number of sessions to return

        Returns:
            List of session summaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    """
                    SELECT session_id, created_at, updated_at, phase, metadata
                    FROM sessions
                    ORDER BY updated_at DESC
                    LIMIT ?
                """,
                    (limit,),
                )
                rows = cursor.fetchall()

                return [
                    {
                        "session_id": row["session_id"],
                        "created_at": row["created_at"],
                        "updated_at": row["updated_at"],
                        "phase": row["phase"],
                        "metadata": json.loads(row["metadata"]),
                    }
                    for row in rows
                ]
        except (sqlite3.Error, json.JSONDecodeError) as e:
            raise SessionError(f"Failed to list sessions: {e}")

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: Session ID to delete

        Returns:
            True if deleted, False if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise SessionError(f"Failed to delete session: {e}")

    def cleanup_old_sessions(self, max_sessions: int) -> int:
        """
        Remove old sessions if count exceeds max_sessions.

        Args:
            max_sessions: Maximum number of sessions to keep

        Returns:
            Number of sessions deleted
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    DELETE FROM sessions
                    WHERE session_id IN (
                        SELECT session_id FROM sessions
                        ORDER BY updated_at DESC
                        LIMIT -1 OFFSET ?
                    )
                """,
                    (max_sessions,),
                )
                conn.commit()
                return cursor.rowcount
        except sqlite3.Error as e:
            raise SessionError(f"Failed to cleanup sessions: {e}")
