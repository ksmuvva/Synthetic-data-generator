"""
Pytest configuration and fixtures for the test suite.
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock

import pandas as pd
import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "name": ["Alice", "Bob", "Charlie", "David", "Eve"],
        "age": [25, 30, 35, 40, 45],
        "email": ["alice@example.com", "bob@example.com", "charlie@example.com",
                  "david@example.com", "eve@example.com"],
        "salary": [50000, 60000, 70000, 80000, 90000]
    })


@pytest.fixture
def empty_dataframe():
    """Create an empty DataFrame for testing."""
    return pd.DataFrame()


@pytest.fixture
def mock_llm_response():
    """Create a mock LLM response."""
    return {
        "content": "Mock LLM response",
        "model": "gpt-4",
        "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
    }


@pytest.fixture
def sample_config_dict() -> Dict[str, Any]:
    """Sample configuration dictionary for testing."""
    return {
        "llm": {
            "provider": "openai",
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 2000
        },
        "generation": {
            "default_rows": 100,
            "quality_level": "high"
        },
        "storage": {
            "default_output_dir": "./test_output"
        }
    }


@pytest.fixture
def mock_openai_client():
    """Create a mock OpenAI client."""
    mock = Mock()
    mock.chat.completions.create.return_value = Mock(
        choices=[
            Mock(
                message=Mock(
                    content='{"result": "test"}',
                    role="assistant"
                )
            )
        ],
        usage=Mock(
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30
        )
    )
    return mock


@pytest.fixture
def mock_anthropic_client():
    """Create a mock Anthropic client."""
    mock = Mock()
    mock.messages.create.return_value = Mock(
        content=[Mock(text='{"result": "test"}')],
        usage=Mock(
            input_tokens=10,
            output_tokens=20
        )
    )
    return mock


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment variables before each test."""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def sample_csv_file(temp_dir, sample_dataframe):
    """Create a sample CSV file for testing."""
    csv_path = temp_dir / "sample.csv"
    sample_dataframe.to_csv(csv_path, index=False)
    return csv_path


@pytest.fixture
def sample_json_file(temp_dir, sample_dataframe):
    """Create a sample JSON file for testing."""
    json_path = temp_dir / "sample.json"
    sample_dataframe.to_json(json_path, orient="records", indent=2)
    return json_path
