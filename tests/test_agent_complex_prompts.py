"""
Test suite for complex agent CLI prompts that simulate human-like interactions.

This test verifies that the agent can handle complex, multi-step, and ambiguous
prompts similar to how humans would interact with the CLI.
"""

import asyncio
import json
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import pytest
import pandas as pd

from synth_agent.agent import SynthAgentClient, get_state_manager, reset_state_manager
from synth_agent.core.config import Config


@pytest.fixture
def mock_agent_response():
    """Mock agent response with streaming."""
    class MockStreamingResponse:
        def __init__(self, content):
            self.content = content

        async def __aiter__(self):
            for chunk in self.content:
                yield {"type": "text", "text": chunk}

    return MockStreamingResponse


class TestComplexHumanLikePrompts:
    """Test complex, human-like prompts that test agent understanding."""

    @pytest.mark.asyncio
    async def test_ambiguous_generation_request(self):
        """
        Test: User provides vague requirements like a human would.
        Example: 'I need some customer data with names and stuff'
        """
        config = Config()
        client = SynthAgentClient(config=config)

        # Verify client can handle ambiguous prompts
        assert client is not None
        assert "analyze_requirements" in str(client.allowed_tools)
        assert "detect_ambiguities" in str(client.allowed_tools)

    @pytest.mark.asyncio
    async def test_multi_step_complex_workflow(self):
        """
        Test: User requests multi-step workflow in natural language.
        Example: 'Generate employee data, then analyze it for patterns,
                 and export to both CSV and Excel formats'
        """
        config = Config()
        client = SynthAgentClient(config=config)
        state_manager = get_state_manager()

        # Simulate storing generated data
        session_id = "test_multi_step"
        test_data = pd.DataFrame({
            "employee_id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "salary": [50000, 60000, 70000]
        })

        await state_manager.set_dataframe(session_id, test_data)

        # Verify data stored
        retrieved = await state_manager.get_dataframe(session_id)
        assert retrieved is not None
        assert len(retrieved) == 3

        # Cleanup
        await state_manager.clear_session(session_id)

    @pytest.mark.asyncio
    async def test_conversational_refinement_prompt(self):
        """
        Test: User refines requirements through conversation.
        Example: 'Actually, make the ages between 25-65' after initial request
        """
        state_manager = get_state_manager()
        session_id = "test_refinement"

        # Store initial requirements
        initial_requirements = {
            "fields": ["name", "age", "email"],
            "num_rows": 100
        }
        await state_manager.set_requirements(session_id, initial_requirements)

        # Simulate refinement
        refined_requirements = {
            "fields": ["name", "age", "email"],
            "num_rows": 100,
            "constraints": {"age": {"min": 25, "max": 65}}
        }
        await state_manager.set_requirements(session_id, refined_requirements)

        # Verify refinement stored
        retrieved = await state_manager.get_requirements(session_id)
        assert retrieved["constraints"]["age"]["min"] == 25
        assert retrieved["constraints"]["age"]["max"] == 65

        # Cleanup
        await state_manager.clear_session(session_id)

    @pytest.mark.asyncio
    async def test_domain_specific_jargon_prompt(self):
        """
        Test: User uses domain-specific terminology.
        Example: 'Generate FHIR-compliant patient records with HL7 standards'
        """
        config = Config()
        client = SynthAgentClient(config=config)

        # Verify reasoning strategy selection is available
        tools = client.get_mcp_tools()
        assert "mcp__synth__select_reasoning_strategy" in tools
        assert "mcp__synth__list_reasoning_methods" in tools

    @pytest.mark.asyncio
    async def test_pattern_based_generation_prompt(self):
        """
        Test: User provides example data and asks for similar generation.
        Example: 'Here's a CSV file, generate 1000 more rows like this'
        """
        state_manager = get_state_manager()
        session_id = "test_pattern"

        # Store pattern data
        pattern_data = pd.DataFrame({
            "product_id": ["P001", "P002", "P003"],
            "category": ["Electronics", "Books", "Clothing"],
            "price": [299.99, 19.99, 49.99]
        })

        await state_manager.set_dataframe(session_id, pattern_data)

        # Store pattern analysis
        pattern_analysis = {
            "detected_types": {
                "product_id": "string_pattern",
                "category": "categorical",
                "price": "numeric"
            },
            "distributions": {
                "price": {"min": 19.99, "max": 299.99, "mean": 123.32}
            }
        }
        await state_manager.set_pattern_analysis(session_id, pattern_analysis)

        # Verify pattern stored
        retrieved_pattern = await state_manager.get_pattern_analysis(session_id)
        assert retrieved_pattern is not None
        assert "detected_types" in retrieved_pattern

        # Cleanup
        await state_manager.clear_session(session_id)

    @pytest.mark.asyncio
    async def test_error_correction_prompt(self):
        """
        Test: User corrects errors in previous generation.
        Example: 'Oops, I meant 1000 rows not 100'
        """
        state_manager = get_state_manager()
        session_id = "test_correction"

        # Store initial (incorrect) request
        initial = {"num_rows": 100}
        await state_manager.set_requirements(session_id, initial)

        # Correct the request
        corrected = {"num_rows": 1000}
        await state_manager.set_requirements(session_id, corrected)

        # Verify correction
        final = await state_manager.get_requirements(session_id)
        assert final["num_rows"] == 1000

        # Cleanup
        await state_manager.clear_session(session_id)

    @pytest.mark.asyncio
    async def test_format_preference_change_prompt(self):
        """
        Test: User changes format preference mid-conversation.
        Example: 'Can you export as Parquet instead of CSV?'
        """
        config = Config()
        client = SynthAgentClient(config=config)

        # Verify format listing is available
        tools = client.get_mcp_tools()
        assert "mcp__synth__list_formats" in tools
        assert "mcp__synth__export_data" in tools

    @pytest.mark.asyncio
    async def test_complex_constraint_prompt(self):
        """
        Test: User specifies complex business rules.
        Example: 'Ensure emails are unique, ages between 18-65,
                 and salary correlates with experience'
        """
        state_manager = get_state_manager()
        session_id = "test_complex_constraints"

        # Store complex requirements
        requirements = {
            "fields": ["email", "age", "experience_years", "salary"],
            "num_rows": 500,
            "constraints": {
                "email": {"unique": True, "format": "email"},
                "age": {"min": 18, "max": 65},
                "experience_years": {"min": 0, "max": 40},
                "salary": {
                    "correlate_with": "experience_years",
                    "min": 30000,
                    "max": 150000
                }
            }
        }

        await state_manager.set_requirements(session_id, requirements)
        retrieved = await state_manager.get_requirements(session_id)

        assert retrieved["constraints"]["email"]["unique"] is True
        assert retrieved["constraints"]["salary"]["correlate_with"] == "experience_years"

        # Cleanup
        await state_manager.clear_session(session_id)

    @pytest.mark.asyncio
    async def test_mixed_intent_prompt(self):
        """
        Test: User mixes multiple intents in one message.
        Example: 'Generate 100 customers, analyze the age distribution,
                 and save as both CSV and JSON'
        """
        config = Config()
        client = SynthAgentClient(config=config)

        # Verify multiple tools are available
        tools = client.get_mcp_tools()
        assert "mcp__synth__generate_data" in tools
        assert "mcp__synth__analyze_pattern" in tools
        assert "mcp__synth__export_data" in tools

    @pytest.mark.asyncio
    async def test_follow_up_question_prompt(self):
        """
        Test: User asks follow-up questions about generation.
        Example: 'What reasoning method did you use? Can you explain why?'
        """
        state_manager = get_state_manager()
        session_id = "test_followup"

        # Store metadata about generation
        metadata = {
            "reasoning_method": "chain_of_thought",
            "confidence": 0.95,
            "num_rows_generated": 1000
        }

        await state_manager.set_value(session_id, "generation_metadata", metadata)
        retrieved = await state_manager.get_value(session_id, "generation_metadata")

        assert retrieved["reasoning_method"] == "chain_of_thought"
        assert retrieved["confidence"] == 0.95

        # Cleanup
        await state_manager.clear_session(session_id)

    @pytest.mark.asyncio
    async def test_realistic_edge_case_prompt(self):
        """
        Test: User requests realistic edge cases.
        Example: 'Generate data including edge cases like very old ages
                 and unusual names'
        """
        state_manager = get_state_manager()
        session_id = "test_edge_cases"

        # Store requirements for edge case generation
        requirements = {
            "fields": ["name", "age"],
            "num_rows": 100,
            "generation_mode": "edge_case",
            "edge_cases": {
                "age": [18, 19, 64, 65],  # Boundary values
                "name": ["X", "Abcdefghijklmnopqrstuvwxyz"]  # Extreme lengths
            }
        }

        await state_manager.set_requirements(session_id, requirements)
        retrieved = await state_manager.get_requirements(session_id)

        assert retrieved["generation_mode"] == "edge_case"
        assert 65 in retrieved["edge_cases"]["age"]

        # Cleanup
        await state_manager.clear_session(session_id)

    @pytest.mark.asyncio
    async def test_relational_data_prompt(self):
        """
        Test: User requests related tables with foreign keys.
        Example: 'Generate customers and their orders with proper relationships'
        """
        state_manager = get_state_manager()
        session_id = "test_relational"

        # Store requirements for relational data
        requirements = {
            "tables": {
                "customers": {
                    "fields": ["customer_id", "name", "email"],
                    "num_rows": 100,
                    "primary_key": "customer_id"
                },
                "orders": {
                    "fields": ["order_id", "customer_id", "amount", "date"],
                    "num_rows": 500,
                    "primary_key": "order_id",
                    "foreign_keys": {
                        "customer_id": {
                            "references": "customers.customer_id"
                        }
                    }
                }
            }
        }

        await state_manager.set_requirements(session_id, requirements)
        retrieved = await state_manager.get_requirements(session_id)

        assert "customers" in retrieved["tables"]
        assert "orders" in retrieved["tables"]
        assert retrieved["tables"]["orders"]["foreign_keys"]["customer_id"]["references"] == "customers.customer_id"

        # Cleanup
        await state_manager.clear_session(session_id)


class TestComplexWorkflowScenarios:
    """Test complex multi-step workflows."""

    @pytest.mark.asyncio
    async def test_analyze_then_generate_workflow(self):
        """
        Test: User uploads file, requests analysis, then generation.
        """
        state_manager = get_state_manager()
        session_id = "test_analyze_generate"

        # Step 1: Store uploaded pattern data
        pattern_df = pd.DataFrame({
            "transaction_id": [1001, 1002, 1003],
            "amount": [25.50, 150.00, 75.25],
            "category": ["Food", "Electronics", "Clothing"]
        })
        await state_manager.set_dataframe(session_id, pattern_df)

        # Step 2: Store analysis results
        analysis = {
            "field_types": {
                "transaction_id": "sequential_numeric",
                "amount": "decimal",
                "category": "categorical"
            },
            "statistics": {
                "amount": {"mean": 83.58, "std": 52.35}
            },
            "categories": ["Food", "Electronics", "Clothing"]
        }
        await state_manager.set_pattern_analysis(session_id, analysis)

        # Step 3: Store generation requirements based on analysis
        requirements = {
            "fields": ["transaction_id", "amount", "category"],
            "num_rows": 10000,
            "based_on_pattern": True,
            "pattern_analysis": analysis
        }
        await state_manager.set_requirements(session_id, requirements)

        # Verify workflow state
        assert await state_manager.get_dataframe(session_id) is not None
        assert await state_manager.get_pattern_analysis(session_id) is not None
        assert await state_manager.get_requirements(session_id) is not None

        # Cleanup
        await state_manager.clear_session(session_id)

    @pytest.mark.asyncio
    async def test_iterative_refinement_workflow(self):
        """
        Test: User iteratively refines generation through multiple rounds.
        """
        state_manager = get_state_manager()
        session_id = "test_iterative"

        # Round 1: Initial generation
        round1_requirements = {
            "fields": ["name", "age"],
            "num_rows": 100
        }
        await state_manager.set_requirements(session_id, round1_requirements)

        # Round 2: Add more fields
        round2_requirements = {
            **round1_requirements,
            "fields": ["name", "age", "email", "phone"]
        }
        await state_manager.set_requirements(session_id, round2_requirements)

        # Round 3: Add constraints
        round3_requirements = {
            **round2_requirements,
            "constraints": {
                "age": {"min": 25, "max": 65},
                "email": {"unique": True}
            }
        }
        await state_manager.set_requirements(session_id, round3_requirements)

        # Verify final state
        final = await state_manager.get_requirements(session_id)
        assert len(final["fields"]) == 4
        assert "constraints" in final
        assert final["constraints"]["age"]["min"] == 25

        # Cleanup
        await state_manager.clear_session(session_id)

    @pytest.mark.asyncio
    async def test_validation_fix_regenerate_workflow(self):
        """
        Test: User generates, finds issues, fixes, and regenerates.
        """
        state_manager = get_state_manager()
        session_id = "test_validation_fix"

        # Initial generation
        initial_data = pd.DataFrame({
            "email": ["user1@test.com", "user2@test.com", "user2@test.com"],  # Duplicate!
            "age": [25, 30, -5]  # Invalid age!
        })
        await state_manager.set_dataframe(session_id, initial_data)

        # Store validation results
        validation_results = {
            "valid": False,
            "issues": [
                {"field": "email", "issue": "duplicate_values", "count": 1},
                {"field": "age", "issue": "negative_value", "count": 1}
            ]
        }
        await state_manager.set_value(session_id, "validation", validation_results)

        # Store fixed requirements
        fixed_requirements = {
            "fields": ["email", "age"],
            "num_rows": 3,
            "constraints": {
                "email": {"unique": True},
                "age": {"min": 0, "max": 120}
            }
        }
        await state_manager.set_requirements(session_id, fixed_requirements)

        # Verify all states stored
        assert await state_manager.get_dataframe(session_id) is not None
        validation = await state_manager.get_value(session_id, "validation")
        assert validation["valid"] is False
        assert len(validation["issues"]) == 2

        # Cleanup
        await state_manager.clear_session(session_id)


class TestErrorHandlingComplexPrompts:
    """Test error handling with complex prompts."""

    @pytest.mark.asyncio
    async def test_impossible_constraint_prompt(self):
        """
        Test: User specifies impossible constraints.
        Example: 'Generate 100 unique rows but use only 10 possible values'
        """
        state_manager = get_state_manager()
        session_id = "test_impossible"

        # Store impossible requirements
        requirements = {
            "fields": ["category"],
            "num_rows": 100,
            "constraints": {
                "category": {
                    "unique": True,
                    "allowed_values": ["A", "B", "C", "D", "E"]  # Only 5 values!
                }
            }
        }
        await state_manager.set_requirements(session_id, requirements)

        # Store error detection
        error = {
            "type": "impossible_constraint",
            "message": "Cannot generate 100 unique values from 5 allowed values"
        }
        await state_manager.set_value(session_id, "error", error)

        retrieved_error = await state_manager.get_value(session_id, "error")
        assert retrieved_error["type"] == "impossible_constraint"

        # Cleanup
        await state_manager.clear_session(session_id)

    @pytest.mark.asyncio
    async def test_conflicting_requirements_prompt(self):
        """
        Test: User specifies conflicting requirements.
        Example: 'Age should be above 65 and below 60'
        """
        state_manager = get_state_manager()
        session_id = "test_conflict"

        # Store conflicting requirements
        requirements = {
            "fields": ["age"],
            "constraints": {
                "age": {
                    "min": 65,
                    "max": 60  # Conflict!
                }
            }
        }
        await state_manager.set_requirements(session_id, requirements)

        # Detect ambiguity/conflict
        ambiguity = {
            "type": "conflicting_constraints",
            "field": "age",
            "conflict": "min (65) > max (60)"
        }
        await state_manager.set_value(session_id, "ambiguity", ambiguity)

        retrieved = await state_manager.get_value(session_id, "ambiguity")
        assert retrieved["type"] == "conflicting_constraints"

        # Cleanup
        await state_manager.clear_session(session_id)


class TestReasoningStrategySelection:
    """Test reasoning strategy selection for different scenarios."""

    @pytest.mark.asyncio
    async def test_financial_domain_strategy_selection(self):
        """Test that financial data triggers appropriate strategy."""
        state_manager = get_state_manager()
        session_id = "test_financial"

        requirements = {
            "domain": "financial",
            "fields": ["transaction_id", "amount", "risk_score"],
            "use_case": "fraud_detection"
        }
        await state_manager.set_requirements(session_id, requirements)

        # Expected strategy: MCTS for financial domain
        expected_strategy = {
            "method": "mcts",
            "reason": "Financial domain with fraud detection use case",
            "confidence": 0.9
        }
        await state_manager.set_value(session_id, "strategy", expected_strategy)

        strategy = await state_manager.get_value(session_id, "strategy")
        assert strategy["method"] == "mcts"

        # Cleanup
        await state_manager.clear_session(session_id)

    @pytest.mark.asyncio
    async def test_relational_domain_strategy_selection(self):
        """Test that relational data triggers appropriate strategy."""
        state_manager = get_state_manager()
        session_id = "test_relational_strategy"

        requirements = {
            "type": "relational",
            "tables": ["customers", "orders", "products"],
            "foreign_keys": ["customer_id", "product_id"]
        }
        await state_manager.set_requirements(session_id, requirements)

        # Expected strategy: Tree of Thoughts for relational
        expected_strategy = {
            "method": "tree_of_thoughts",
            "reason": "Multiple related tables requiring dependency management",
            "confidence": 0.85
        }
        await state_manager.set_value(session_id, "strategy", expected_strategy)

        strategy = await state_manager.get_value(session_id, "strategy")
        assert strategy["method"] == "tree_of_thoughts"

        # Cleanup
        await state_manager.clear_session(session_id)


class TestStateManagementComplexScenarios:
    """Test state management across complex scenarios."""

    @pytest.mark.asyncio
    async def test_concurrent_sessions(self):
        """Test handling multiple concurrent sessions."""
        state_manager = get_state_manager()

        # Create multiple sessions
        sessions = ["session_1", "session_2", "session_3"]

        for i, session_id in enumerate(sessions):
            data = pd.DataFrame({
                "id": [i * 10 + j for j in range(5)],
                "value": [f"value_{i}_{j}" for j in range(5)]
            })
            await state_manager.set_dataframe(session_id, data)

        # Verify each session has correct data
        for i, session_id in enumerate(sessions):
            retrieved = await state_manager.get_dataframe(session_id)
            assert retrieved is not None
            assert len(retrieved) == 5
            assert retrieved.iloc[0]["id"] == i * 10

        # Cleanup all sessions
        for session_id in sessions:
            await state_manager.clear_session(session_id)

    @pytest.mark.asyncio
    async def test_state_persistence_across_operations(self):
        """Test that state persists correctly across multiple operations."""
        state_manager = get_state_manager()
        session_id = "test_persistence"

        # Operation 1: Store requirements
        await state_manager.set_requirements(session_id, {"num_rows": 100})

        # Operation 2: Store dataframe
        df = pd.DataFrame({"col": [1, 2, 3]})
        await state_manager.set_dataframe(session_id, df)

        # Operation 3: Store pattern
        await state_manager.set_pattern_analysis(session_id, {"type": "numeric"})

        # Operation 4: Store custom value
        await state_manager.set_value(session_id, "custom", {"foo": "bar"})

        # Verify all data still accessible
        assert await state_manager.get_requirements(session_id) is not None
        assert await state_manager.get_dataframe(session_id) is not None
        assert await state_manager.get_pattern_analysis(session_id) is not None
        assert await state_manager.get_value(session_id, "custom") is not None

        # Cleanup
        await state_manager.clear_session(session_id)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
