"""
State management system for Claude Agent SDK tools.

This module provides a thread-safe state manager for sharing data between tool calls
in the Claude Agent SDK context. Since tools are stateless functions, we need a
centralized state store to share generated DataFrames, requirements, and analysis results.
"""

import asyncio
from typing import Any, Dict, Optional
from pathlib import Path
import pandas as pd
import structlog
from datetime import datetime, timedelta


logger = structlog.get_logger(__name__)


class ToolStateManager:
    """
    Thread-safe state manager for sharing data between tool calls.

    This manager stores:
    - Generated DataFrames
    - Parsed requirements
    - Pattern analysis results
    - Session metadata

    Features:
    - Thread-safe access using asyncio locks
    - Automatic cleanup of stale data
    - Multiple session support
    - Memory-efficient storage with configurable TTL
    """

    def __init__(self, ttl_minutes: int = 60):
        """
        Initialize the state manager.

        Args:
            ttl_minutes: Time-to-live for stored data in minutes (default: 60)
        """
        self._data_store: Dict[str, Dict[str, Any]] = {}
        self._locks: Dict[str, asyncio.Lock] = {}
        self._ttl = timedelta(minutes=ttl_minutes)
        self._master_lock = asyncio.Lock()

        logger.info("ToolStateManager initialized", ttl_minutes=ttl_minutes)

    async def _get_lock(self, session_id: str) -> asyncio.Lock:
        """Get or create a lock for a specific session."""
        async with self._master_lock:
            if session_id not in self._locks:
                self._locks[session_id] = asyncio.Lock()
            return self._locks[session_id]

    async def set_dataframe(self, session_id: str, df: pd.DataFrame, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Store a DataFrame for a session.

        Args:
            session_id: Unique session identifier
            df: DataFrame to store
            metadata: Optional metadata about the DataFrame
        """
        lock = await self._get_lock(session_id)
        async with lock:
            if session_id not in self._data_store:
                self._data_store[session_id] = {}

            self._data_store[session_id]["dataframe"] = df
            self._data_store[session_id]["dataframe_metadata"] = metadata or {}
            self._data_store[session_id]["dataframe_timestamp"] = datetime.now()

            logger.info(
                "DataFrame stored",
                session_id=session_id,
                rows=len(df),
                columns=len(df.columns)
            )

    async def get_dataframe(self, session_id: str) -> Optional[pd.DataFrame]:
        """
        Retrieve a DataFrame for a session.

        Args:
            session_id: Unique session identifier

        Returns:
            Stored DataFrame or None if not found
        """
        lock = await self._get_lock(session_id)
        async with lock:
            if session_id not in self._data_store:
                logger.warning("Session not found", session_id=session_id)
                return None

            # Check TTL
            timestamp = self._data_store[session_id].get("dataframe_timestamp")
            if timestamp and datetime.now() - timestamp > self._ttl:
                logger.warning("DataFrame expired", session_id=session_id)
                del self._data_store[session_id]["dataframe"]
                return None

            df = self._data_store[session_id].get("dataframe")
            if df is not None:
                logger.info("DataFrame retrieved", session_id=session_id, rows=len(df))
            return df

    async def set_requirements(self, session_id: str, requirements: Dict[str, Any]) -> None:
        """
        Store parsed requirements for a session.

        Args:
            session_id: Unique session identifier
            requirements: Structured requirements dictionary
        """
        lock = await self._get_lock(session_id)
        async with lock:
            if session_id not in self._data_store:
                self._data_store[session_id] = {}

            self._data_store[session_id]["requirements"] = requirements
            self._data_store[session_id]["requirements_timestamp"] = datetime.now()

            logger.info("Requirements stored", session_id=session_id)

    async def get_requirements(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve parsed requirements for a session.

        Args:
            session_id: Unique session identifier

        Returns:
            Stored requirements or None if not found
        """
        lock = await self._get_lock(session_id)
        async with lock:
            if session_id not in self._data_store:
                return None

            return self._data_store[session_id].get("requirements")

    async def set_pattern_analysis(self, session_id: str, analysis: Dict[str, Any]) -> None:
        """
        Store pattern analysis results for a session.

        Args:
            session_id: Unique session identifier
            analysis: Pattern analysis results
        """
        lock = await self._get_lock(session_id)
        async with lock:
            if session_id not in self._data_store:
                self._data_store[session_id] = {}

            self._data_store[session_id]["pattern_analysis"] = analysis
            self._data_store[session_id]["pattern_analysis_timestamp"] = datetime.now()

            logger.info("Pattern analysis stored", session_id=session_id)

    async def get_pattern_analysis(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve pattern analysis results for a session.

        Args:
            session_id: Unique session identifier

        Returns:
            Stored pattern analysis or None if not found
        """
        lock = await self._get_lock(session_id)
        async with lock:
            if session_id not in self._data_store:
                return None

            return self._data_store[session_id].get("pattern_analysis")

    async def set_value(self, session_id: str, key: str, value: Any) -> None:
        """
        Store an arbitrary value for a session.

        Args:
            session_id: Unique session identifier
            key: Key to store value under
            value: Value to store
        """
        lock = await self._get_lock(session_id)
        async with lock:
            if session_id not in self._data_store:
                self._data_store[session_id] = {}

            self._data_store[session_id][key] = value
            self._data_store[session_id][f"{key}_timestamp"] = datetime.now()

            logger.debug("Value stored", session_id=session_id, key=key)

    async def get_value(self, session_id: str, key: str, default: Any = None) -> Any:
        """
        Retrieve an arbitrary value for a session.

        Args:
            session_id: Unique session identifier
            key: Key to retrieve value for
            default: Default value if key not found

        Returns:
            Stored value or default if not found
        """
        lock = await self._get_lock(session_id)
        async with lock:
            if session_id not in self._data_store:
                return default

            return self._data_store[session_id].get(key, default)

    async def clear_session(self, session_id: str) -> None:
        """
        Clear all data for a session.

        Args:
            session_id: Unique session identifier
        """
        lock = await self._get_lock(session_id)
        async with lock:
            if session_id in self._data_store:
                del self._data_store[session_id]
                logger.info("Session cleared", session_id=session_id)

    async def cleanup_expired(self) -> int:
        """
        Remove expired sessions based on TTL.

        Returns:
            Number of sessions cleaned up
        """
        async with self._master_lock:
            now = datetime.now()
            expired_sessions = []

            for session_id, data in self._data_store.items():
                # Check if any timestamp is expired
                timestamps = [
                    v for k, v in data.items()
                    if k.endswith("_timestamp") and isinstance(v, datetime)
                ]

                if timestamps and all(now - ts > self._ttl for ts in timestamps):
                    expired_sessions.append(session_id)

            for session_id in expired_sessions:
                del self._data_store[session_id]
                if session_id in self._locks:
                    del self._locks[session_id]

            if expired_sessions:
                logger.info("Expired sessions cleaned up", count=len(expired_sessions))

            return len(expired_sessions)

    async def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a session.

        Args:
            session_id: Unique session identifier

        Returns:
            Session info including available data and timestamps
        """
        lock = await self._get_lock(session_id)
        async with lock:
            if session_id not in self._data_store:
                return None

            data = self._data_store[session_id]
            info = {
                "session_id": session_id,
                "has_dataframe": "dataframe" in data,
                "has_requirements": "requirements" in data,
                "has_pattern_analysis": "pattern_analysis" in data,
                "timestamps": {
                    k: v.isoformat() for k, v in data.items()
                    if k.endswith("_timestamp") and isinstance(v, datetime)
                }
            }

            if "dataframe" in data:
                df = data["dataframe"]
                info["dataframe_info"] = {
                    "rows": len(df),
                    "columns": list(df.columns),
                }

            return info

    def get_active_sessions(self) -> list[str]:
        """
        Get list of active session IDs.

        Returns:
            List of session IDs with stored data
        """
        return list(self._data_store.keys())


# Global state manager instance
_global_state_manager: Optional[ToolStateManager] = None


def get_state_manager(ttl_minutes: int = 60) -> ToolStateManager:
    """
    Get or create the global state manager instance.

    Args:
        ttl_minutes: Time-to-live for stored data in minutes

    Returns:
        Global ToolStateManager instance
    """
    global _global_state_manager
    if _global_state_manager is None:
        _global_state_manager = ToolStateManager(ttl_minutes=ttl_minutes)
    return _global_state_manager


def reset_state_manager() -> None:
    """Reset the global state manager (mainly for testing)."""
    global _global_state_manager
    _global_state_manager = None
