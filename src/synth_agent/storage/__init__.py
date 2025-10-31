"""Cloud storage integration module."""

from synth_agent.storage.base import BaseCloudStorage
from synth_agent.storage.manager import StorageManager

__all__ = [
    "BaseCloudStorage",
    "StorageManager",
]
