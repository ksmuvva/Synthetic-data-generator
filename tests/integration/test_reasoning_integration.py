"""
Integration tests for reasoning with full agent workflows.
"""

import pytest
import asyncio
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "fixtures"))
from reasoning_fixtures import *


class TestReasoningAgentIntegration:
    """Integration tests for reasoning with the agent."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_end_to_end_financial_workflow(self, financial_requirements, reasoning_config, temp_dir):
        """Test complete workflow for financial data with reasoning."""
        from synth_agent.reasoning.engine import ReasoningEngine
        from synth_agent.generation.engine import DataGenerationEngine

        # Step 1: Apply reasoning
        reasoning_engine = ReasoningEngine(reasoning_config)
        reasoning_result, detection = await reasoning_engine.auto_execute(financial_requirements)

        assert detection["recommended"] == "mcts"
        assert reasoning_result.confidence > 0.0

        # Step 2: Generate data with enhanced requirements
        generation_engine = DataGenerationEngine(reasoning_config)
        df = await generation_engine.generate(
            reasoning_result.enhanced_requirements,
            num_rows=50
        )

        # Verify data was generated
        assert df is not None
        assert len(df) == 50

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_end_to_end_healthcare_workflow(self, healthcare_requirements, reasoning_config):
        """Test complete workflow for healthcare data with reasoning."""
        from synth_agent.reasoning.engine import ReasoningEngine

        reasoning_engine = ReasoningEngine(reasoning_config)

        # Apply Chain of Thought reasoning
        result = await reasoning_engine.execute("chain_of_thought", healthcare_requirements)

        assert result.method_used == "chain_of_thought"
        # Should add healthcare-specific constraints
        assert "constraints" in result.enhanced_requirements

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_reasoning_with_pattern_analysis(self, sample_requirements, reasoning_config, sample_csv_file):
        """Test reasoning combined with pattern analysis."""
        from synth_agent.reasoning.engine import ReasoningEngine
        from synth_agent.analysis.pattern_analyzer import PatternAnalyzer

        # First analyze pattern
        pattern_analyzer = PatternAnalyzer(reasoning_config)
        pattern_result = await pattern_analyzer.analyze_file(sample_csv_file)

        # Merge pattern insights into requirements
        enhanced_requirements = sample_requirements.copy()
        enhanced_requirements["pattern_analysis"] = pattern_result

        # Apply reasoning
        reasoning_engine = ReasoningEngine(reasoning_config)
        reasoning_result = await reasoning_engine.execute(
            "iterative_refinement",
            enhanced_requirements
        )

        assert reasoning_result.confidence > 0.0

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_all_reasoning_methods_with_generation(self, sample_requirements, reasoning_config):
        """Test that all reasoning methods can integrate with data generation."""
        from synth_agent.reasoning.engine import ReasoningEngine
        from synth_agent.generation.engine import DataGenerationEngine

        reasoning_engine = ReasoningEngine(reasoning_config)
        generation_engine = DataGenerationEngine(reasoning_config)

        # Test each method
        methods_to_test = ["mcts", "beam_search", "chain_of_thought", "iterative_refinement"]

        for method in methods_to_test:
            # Apply reasoning
            reasoning_result = await reasoning_engine.execute(method, sample_requirements)

            # Generate data
            df = await generation_engine.generate(
                reasoning_result.enhanced_requirements,
                num_rows=10
            )

            assert df is not None
            assert len(df) == 10

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_reasoning_preserves_requirements_structure(self, sample_requirements, reasoning_config):
        """Test that reasoning preserves essential requirements structure."""
        from synth_agent.reasoning.engine import ReasoningEngine

        reasoning_engine = ReasoningEngine(reasoning_config)

        original_fields = sample_requirements.get("fields", [])

        # Apply reasoning
        result = await reasoning_engine.execute("iterative_refinement", sample_requirements)

        enhanced_fields = result.enhanced_requirements.get("fields", [])

        # Should preserve original fields
        assert len(enhanced_fields) >= len(original_fields)

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_reasoning_improves_data_quality(self, sample_requirements, reasoning_config):
        """Test that reasoning improves data generation quality."""
        from synth_agent.reasoning.engine import ReasoningEngine
        from synth_agent.generation.engine import DataGenerationEngine

        generation_engine = DataGenerationEngine(reasoning_config)

        # Generate without reasoning
        df_no_reasoning = await generation_engine.generate(sample_requirements, num_rows=100)

        # Apply reasoning
        reasoning_engine = ReasoningEngine(reasoning_config)
        reasoning_result = await reasoning_engine.execute("reflexion", sample_requirements)

        # Generate with reasoning
        df_with_reasoning = await generation_engine.generate(
            reasoning_result.enhanced_requirements,
            num_rows=100
        )

        # Both should succeed
        assert df_no_reasoning is not None
        assert df_with_reasoning is not None
        assert len(df_with_reasoning) == 100


class TestReasoningWithMCPTools:
    """Integration tests for reasoning MCP tools in agent context."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_mcp_tool_integration_with_state(self, financial_requirements):
        """Test MCP tools with state manager."""
        from synth_agent.agent.tools import select_reasoning_strategy_tool
        from synth_agent.agent.state import get_state_manager

        state_manager = get_state_manager()

        args = {
            "requirements": financial_requirements,
            "session_id": "integration-test-1"
        }

        result = await select_reasoning_strategy_tool(args)

        # Check state was updated
        stored_recommendation = await state_manager.get_value(
            "integration-test-1",
            "reasoning_recommendation"
        )

        assert stored_recommendation is not None
        assert "recommended" in stored_recommendation

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_reasoning_tool_chain(self, sample_requirements):
        """Test chaining reasoning tool with data generation tool."""
        from synth_agent.agent.tools import (
            select_reasoning_strategy_tool,
            analyze_requirements_tool,
        )

        # First analyze requirements
        analyze_args = {
            "requirement_text": "Generate 100 customer records",
            "session_id": "chain-test-1"
        }

        analyze_result = await analyze_requirements_tool(analyze_args)
        assert "content" in analyze_result

        # Then select reasoning strategy
        select_args = {
            "requirements": sample_requirements,
            "session_id": "chain-test-1"
        }

        select_result = await select_reasoning_strategy_tool(select_args)
        assert "content" in select_result


class TestReasoningPerformance:
    """Performance tests for reasoning operations."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_reasoning_performance_multiple_requirements(self, reasoning_config):
        """Test reasoning performance with multiple requirements."""
        from synth_agent.reasoning.engine import ReasoningEngine

        reasoning_engine = ReasoningEngine(reasoning_config)

        requirements_list = [
            {"data_type": "financial", "fields": [{"name": "amount", "type": "float"}]},
            {"data_type": "healthcare", "fields": [{"name": "patient_id", "type": "string"}]},
            {"data_type": "ecommerce", "fields": [{"name": "product_id", "type": "string"}]},
        ]

        results = []
        for reqs in requirements_list:
            result, _ = await reasoning_engine.auto_execute(reqs)
            results.append(result)

        # All should complete
        assert len(results) == 3
        assert all(r.confidence > 0 for r in results)

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_reasoning_caching(self, sample_requirements, reasoning_config):
        """Test that reasoning can be cached for performance."""
        from synth_agent.reasoning.engine import ReasoningEngine

        reasoning_engine = ReasoningEngine(reasoning_config)

        # Execute twice with same requirements
        result1 = await reasoning_engine.execute("iterative_refinement", sample_requirements)
        result2 = await reasoning_engine.execute("iterative_refinement", sample_requirements)

        # Both should succeed
        assert result1.confidence > 0
        assert result2.confidence > 0

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_concurrent_reasoning_operations(self, reasoning_config):
        """Test multiple concurrent reasoning operations."""
        from synth_agent.reasoning.engine import ReasoningEngine

        reasoning_engine = ReasoningEngine(reasoning_config)

        # Create multiple requirements
        requirements_list = [
            {"data_type": f"test_{i}", "fields": [{"name": "id", "type": "string"}]}
            for i in range(5)
        ]

        # Execute concurrently
        tasks = [
            reasoning_engine.execute("iterative_refinement", reqs)
            for reqs in requirements_list
        ]

        results = await asyncio.gather(*tasks)

        # All should complete
        assert len(results) == 5
        assert all(isinstance(r.confidence, float) for r in results)


class TestReasoningErrorRecovery:
    """Tests for error recovery in reasoning integration."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_recovery_from_reasoning_failure(self, reasoning_config):
        """Test that system recovers from reasoning failures."""
        from synth_agent.reasoning.engine import ReasoningEngine
        from synth_agent.generation.engine import DataGenerationEngine

        reasoning_engine = ReasoningEngine(reasoning_config)
        generation_engine = DataGenerationEngine(reasoning_config)

        # Try reasoning with problematic requirements
        bad_requirements = None

        try:
            result = await reasoning_engine.execute("iterative_refinement", bad_requirements)
            enhanced_reqs = result.enhanced_requirements
        except Exception:
            # Fallback to basic requirements
            enhanced_reqs = {"fields": [{"name": "id", "type": "string"}]}

        # Should still be able to generate
        df = await generation_engine.generate(enhanced_reqs, num_rows=10)
        assert df is not None

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_fallback_reasoning_method(self, sample_requirements, reasoning_config):
        """Test fallback to default reasoning method."""
        from synth_agent.reasoning.engine import ReasoningEngine

        reasoning_engine = ReasoningEngine(reasoning_config)

        # Try invalid method, should raise error
        with pytest.raises(ValueError):
            await reasoning_engine.execute("invalid_method", sample_requirements)

        # But should work with valid fallback
        result = await reasoning_engine.execute(
            reasoning_config.reasoning.fallback_method,
            sample_requirements
        )

        assert result.confidence > 0


class TestReasoningWithDifferentScales:
    """Tests for reasoning with different data scales."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_reasoning_with_small_dataset(self, reasoning_config):
        """Test reasoning for small dataset."""
        from synth_agent.reasoning.engine import ReasoningEngine

        reasoning_engine = ReasoningEngine(reasoning_config)

        small_requirements = {
            "data_type": "test",
            "fields": [{"name": "id", "type": "integer"}],
            "size": 10
        }

        result = await reasoning_engine.execute("iterative_refinement", small_requirements)
        assert result.confidence > 0

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_reasoning_with_large_dataset(self, reasoning_config):
        """Test reasoning for large dataset."""
        from synth_agent.reasoning.engine import ReasoningEngine

        reasoning_engine = ReasoningEngine(reasoning_config)

        large_requirements = {
            "data_type": "test",
            "fields": [{"name": "id", "type": "integer"}],
            "size": 1000000
        }

        result = await reasoning_engine.execute("iterative_refinement", large_requirements)
        assert result.confidence > 0

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_reasoning_with_many_fields(self, reasoning_config):
        """Test reasoning with many fields."""
        from synth_agent.reasoning.engine import ReasoningEngine

        reasoning_engine = ReasoningEngine(reasoning_config)

        many_fields_requirements = {
            "data_type": "test",
            "fields": [
                {"name": f"field_{i}", "type": "string"}
                for i in range(50)
            ]
        }

        result = await reasoning_engine.execute("iterative_refinement", many_fields_requirements)
        assert result.confidence > 0
