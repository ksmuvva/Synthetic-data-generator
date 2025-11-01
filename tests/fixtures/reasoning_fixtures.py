"""
Pytest fixtures for reasoning tests.
"""

from typing import Dict, Any
import pytest
from synth_agent.core.config import Config


@pytest.fixture
def sample_requirements():
    """Sample requirements for testing."""
    return {
        "data_type": "customer data",
        "fields": [
            {"name": "id", "type": "integer", "constraints": {"unique": True}},
            {"name": "name", "type": "string"},
            {"name": "email", "type": "email"},
            {"name": "age", "type": "integer", "constraints": {"min": 18, "max": 100}},
        ],
        "constraints": ["All fields must be valid"],
        "size": 100,
    }


@pytest.fixture
def financial_requirements():
    """Financial domain requirements for testing."""
    return {
        "data_type": "financial transactions",
        "fields": [
            {"name": "transaction_id", "type": "string"},
            {"name": "amount", "type": "float"},
            {"name": "currency", "type": "string"},
            {"name": "timestamp", "type": "datetime"},
            {"name": "account_id", "type": "string"},
        ],
        "constraints": ["Transactions must balance", "Amounts must be positive"],
        "size": 1000,
    }


@pytest.fixture
def healthcare_requirements():
    """Healthcare domain requirements for testing."""
    return {
        "data_type": "patient records",
        "fields": [
            {"name": "patient_id", "type": "string"},
            {"name": "name", "type": "string"},
            {"name": "diagnosis", "type": "string"},
            {"name": "medication", "type": "string"},
            {"name": "date_of_visit", "type": "date"},
        ],
        "constraints": ["HIPAA compliance required", "PHI must be anonymizable"],
        "size": 500,
    }


@pytest.fixture
def ecommerce_requirements():
    """E-commerce domain requirements for testing."""
    return {
        "data_type": "product catalog",
        "fields": [
            {"name": "product_id", "type": "string"},
            {"name": "name", "type": "string"},
            {"name": "price", "type": "float"},
            {"name": "category", "type": "string"},
            {"name": "inventory", "type": "integer"},
        ],
        "constraints": ["Prices must be positive", "Inventory must be non-negative"],
        "size": 200,
    }


@pytest.fixture
def network_requirements():
    """Network/graph domain requirements for testing."""
    return {
        "data_type": "social network",
        "fields": [
            {"name": "user_id", "type": "string"},
            {"name": "follower_id", "type": "string"},
            {"name": "connection_type", "type": "string"},
            {"name": "timestamp", "type": "datetime"},
        ],
        "relationships": [
            {"type": "foreign_key", "from": "follower_id", "to": "user.id"}
        ],
        "size": 1000,
    }


@pytest.fixture
def timeseries_requirements():
    """Time-series domain requirements for testing."""
    return {
        "data_type": "sensor readings",
        "fields": [
            {"name": "sensor_id", "type": "string"},
            {"name": "timestamp", "type": "datetime"},
            {"name": "temperature", "type": "float"},
            {"name": "humidity", "type": "float"},
        ],
        "constraints": ["Maintain temporal ordering"],
        "size": 5000,
    }


@pytest.fixture
def relational_requirements():
    """Relational database requirements for testing."""
    return {
        "data_type": "order database",
        "fields": [
            {"name": "order_id", "type": "string"},
            {"name": "customer_id", "type": "string"},
            {"name": "product_id", "type": "string"},
            {"name": "quantity", "type": "integer"},
        ],
        "relationships": [
            {"type": "foreign_key", "from": "customer_id", "to": "customer.id"},
            {"type": "foreign_key", "from": "product_id", "to": "product.id"},
        ],
        "size": 300,
    }


@pytest.fixture
def reasoning_config():
    """Configuration with reasoning settings."""
    config = Config()
    # Set reasoning-specific configurations
    config.reasoning.auto_detect = True
    config.reasoning.confidence_threshold = 0.75
    config.reasoning.mcts_iterations = 50  # Reduced for testing
    config.reasoning.beam_width = 3
    config.reasoning.cot_max_steps = 5
    return config


@pytest.fixture
def mock_reasoning_context():
    """Mock context for reasoning operations."""
    return {
        "session_id": "test-session-123",
        "user_preferences": {"quality": "high"},
        "previous_generations": [],
    }


@pytest.fixture
def expected_reasoning_result():
    """Expected structure of a reasoning result."""
    return {
        "enhanced_requirements": dict,
        "reasoning_steps": list,
        "confidence": float,
        "metadata": dict,
        "execution_time": float,
        "method_used": str,
    }
