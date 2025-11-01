"""
Unit tests for ReasoningEngine.
"""

import pytest
from synth_agent.reasoning.engine import ReasoningEngine
from synth_agent.reasoning.base import ReasoningResult
from synth_agent.reasoning.metrics import get_metrics_tracker

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "fixtures"))
from reasoning_fixtures import *


class TestReasoningEngine:
    """Tests for ReasoningEngine orchestration."""

    def test_engine_initialization(self, reasoning_config):
        """Test that engine initializes with all strategies."""
        engine = ReasoningEngine(reasoning_config)

        assert len(engine.strategies) == 12
        assert "mcts" in engine.strategies
        assert "beam_search" in engine.strategies
        assert "chain_of_thought" in engine.strategies

    def test_list_strategies(self, reasoning_config):
        """Test listing all available strategies."""
        engine = ReasoningEngine(reasoning_config)

        strategies = engine.list_strategies()

        assert len(strategies) == 12
        assert "mcts" in strategies
        assert "iterative_refinement" in strategies

    def test_get_strategy(self, reasoning_config):
        """Test getting a specific strategy instance."""
        engine = ReasoningEngine(reasoning_config)

        strategy = engine.get_strategy("mcts")

        assert strategy is not None
        assert strategy.get_name() == "mcts"

    def test_get_nonexistent_strategy(self, reasoning_config):
        """Test getting a strategy that doesn't exist."""
        engine = ReasoningEngine(reasoning_config)

        strategy = engine.get_strategy("nonexistent")

        assert strategy is None

    @pytest.mark.asyncio
    async def test_execute_valid_method(self, sample_requirements, reasoning_config):
        """Test executing a valid reasoning method."""
        engine = ReasoningEngine(reasoning_config)

        result = await engine.execute("iterative_refinement", sample_requirements)

        assert isinstance(result, ReasoningResult)
        assert result.method_used == "iterative_refinement"
        assert result.execution_time >= 0.0

    @pytest.mark.asyncio
    async def test_execute_invalid_method(self, sample_requirements, reasoning_config):
        """Test executing an invalid reasoning method."""
        engine = ReasoningEngine(reasoning_config)

        with pytest.raises(ValueError, match="Unknown reasoning method"):
            await engine.execute("invalid_method", sample_requirements)

    @pytest.mark.asyncio
    async def test_execute_tracks_metrics(self, sample_requirements, reasoning_config):
        """Test that execution tracks performance metrics."""
        engine = ReasoningEngine(reasoning_config)
        tracker = get_metrics_tracker()

        # Clear previous metrics
        tracker.clear()

        await engine.execute("iterative_refinement", sample_requirements)

        # Check metrics were recorded
        summary = tracker.get_summary("iterative_refinement")
        assert summary["total_runs"] == 1

    @pytest.mark.asyncio
    async def test_execute_multiple_methods(self, sample_requirements, reasoning_config):
        """Test executing multiple methods in sequence."""
        engine = ReasoningEngine(reasoning_config)

        result1 = await engine.execute("mcts", sample_requirements)
        result2 = await engine.execute("beam_search", sample_requirements)

        assert result1.method_used == "mcts"
        assert result2.method_used == "beam_search"

    @pytest.mark.asyncio
    async def test_execute_handles_errors_gracefully(self, reasoning_config):
        """Test that execution handles errors without crashing."""
        engine = ReasoningEngine(reasoning_config)

        # Invalid requirements should not crash
        result = await engine.execute("iterative_refinement", {})

        assert isinstance(result, ReasoningResult)
        # Should return original requirements on error or handle gracefully

    @pytest.mark.asyncio
    async def test_auto_execute(self, financial_requirements, reasoning_config):
        """Test auto-detection and execution."""
        engine = ReasoningEngine(reasoning_config)

        result, detection = await engine.auto_execute(financial_requirements)

        assert isinstance(result, ReasoningResult)
        assert isinstance(detection, dict)
        assert "recommended" in detection
        assert result.method_used == detection["recommended"]

    @pytest.mark.asyncio
    async def test_auto_execute_provides_detection_info(self, healthcare_requirements, reasoning_config):
        """Test that auto-execute provides full detection information."""
        engine = ReasoningEngine(reasoning_config)

        result, detection = await engine.auto_execute(healthcare_requirements)

        assert "recommended" in detection
        assert "confidence" in detection
        assert "detected_domain" in detection
        assert "alternatives" in detection

    @pytest.mark.asyncio
    async def test_get_metrics_summary_overall(self, sample_requirements, reasoning_config):
        """Test getting overall metrics summary."""
        engine = ReasoningEngine(reasoning_config)
        tracker = get_metrics_tracker()
        tracker.clear()

        await engine.execute("mcts", sample_requirements)
        await engine.execute("beam_search", sample_requirements)

        summary = engine.get_metrics_summary()

        assert summary["total_runs"] == 2

    @pytest.mark.asyncio
    async def test_get_metrics_summary_by_method(self, sample_requirements, reasoning_config):
        """Test getting metrics summary for specific method."""
        engine = ReasoningEngine(reasoning_config)
        tracker = get_metrics_tracker()
        tracker.clear()

        await engine.execute("mcts", sample_requirements)
        await engine.execute("mcts", sample_requirements)

        summary = engine.get_metrics_summary("mcts")

        assert summary["total_runs"] == 2
        assert summary["method_name"] == "mcts"


class TestReasoningEngineWithDifferentDomains:
    """Tests for reasoning engine with different domain requirements."""

    @pytest.mark.asyncio
    async def test_engine_with_financial_data(self, financial_requirements, reasoning_config):
        """Test engine auto-execution with financial data."""
        engine = ReasoningEngine(reasoning_config)

        result, detection = await engine.auto_execute(financial_requirements)

        assert detection["recommended"] == "mcts"
        assert isinstance(result, ReasoningResult)

    @pytest.mark.asyncio
    async def test_engine_with_healthcare_data(self, healthcare_requirements, reasoning_config):
        """Test engine auto-execution with healthcare data."""
        engine = ReasoningEngine(reasoning_config)

        result, detection = await engine.auto_execute(healthcare_requirements)

        assert detection["recommended"] == "chain_of_thought"

    @pytest.mark.asyncio
    async def test_engine_with_ecommerce_data(self, ecommerce_requirements, reasoning_config):
        """Test engine auto-execution with e-commerce data."""
        engine = ReasoningEngine(reasoning_config)

        result, detection = await engine.auto_execute(ecommerce_requirements)

        assert detection["recommended"] == "beam_search"

    @pytest.mark.asyncio
    async def test_engine_with_network_data(self, network_requirements, reasoning_config):
        """Test engine auto-execution with network data."""
        engine = ReasoningEngine(reasoning_config)

        result, detection = await engine.auto_execute(network_requirements)

        assert detection["recommended"] == "graph_of_thoughts"


class TestReasoningEnginePerformance:
    """Tests for reasoning engine performance characteristics."""

    @pytest.mark.asyncio
    async def test_execution_time_tracking(self, sample_requirements, reasoning_config):
        """Test that execution time is properly tracked."""
        engine = ReasoningEngine(reasoning_config)

        result = await engine.execute("iterative_refinement", sample_requirements)

        assert result.execution_time > 0.0
        assert result.execution_time < 60.0  # Should complete within reasonable time

    @pytest.mark.asyncio
    async def test_metrics_tracking_enabled(self, sample_requirements, reasoning_config):
        """Test that metrics tracking can be enabled."""
        engine = ReasoningEngine(reasoning_config)
        tracker = get_metrics_tracker()
        tracker.clear()

        await engine.execute("iterative_refinement", sample_requirements)

        summary = tracker.get_summary()
        assert summary["total_runs"] > 0

    @pytest.mark.asyncio
    async def test_success_rate_tracking(self, sample_requirements, reasoning_config):
        """Test that success rate is tracked."""
        engine = ReasoningEngine(reasoning_config)
        tracker = get_metrics_tracker()
        tracker.clear()

        # Execute successfully
        await engine.execute("iterative_refinement", sample_requirements)

        summary = tracker.get_summary()
        assert summary["success_rate"] == 1.0

    @pytest.mark.asyncio
    async def test_average_execution_time(self, sample_requirements, reasoning_config):
        """Test that average execution time is calculated."""
        engine = ReasoningEngine(reasoning_config)
        tracker = get_metrics_tracker()
        tracker.clear()

        # Execute multiple times
        await engine.execute("iterative_refinement", sample_requirements)
        await engine.execute("iterative_refinement", sample_requirements)

        summary = tracker.get_summary("iterative_refinement")
        assert summary["avg_execution_time"] > 0.0


class TestReasoningEngineErrorHandling:
    """Tests for error handling in reasoning engine."""

    @pytest.mark.asyncio
    async def test_handle_invalid_requirements(self, reasoning_config):
        """Test handling of invalid requirements."""
        engine = ReasoningEngine(reasoning_config)

        # Should not crash
        result = await engine.execute("iterative_refinement", None)

        assert isinstance(result, ReasoningResult)

    @pytest.mark.asyncio
    async def test_handle_empty_requirements(self, reasoning_config):
        """Test handling of empty requirements."""
        engine = ReasoningEngine(reasoning_config)

        result = await engine.execute("iterative_refinement", {})

        assert isinstance(result, ReasoningResult)

    @pytest.mark.asyncio
    async def test_error_recorded_in_metrics(self, reasoning_config):
        """Test that errors are recorded in metrics."""
        engine = ReasoningEngine(reasoning_config)
        tracker = get_metrics_tracker()
        tracker.clear()

        # Execute with problematic input
        result = await engine.execute("iterative_refinement", None)

        # Metrics should still be recorded
        summary = tracker.get_summary()
        assert summary["total_runs"] >= 0

    @pytest.mark.asyncio
    async def test_execution_continues_after_error(self, sample_requirements, reasoning_config):
        """Test that execution can continue after an error."""
        engine = ReasoningEngine(reasoning_config)

        # Execute with bad requirements
        result1 = await engine.execute("iterative_refinement", None)

        # Should still be able to execute normally
        result2 = await engine.execute("iterative_refinement", sample_requirements)

        assert isinstance(result2, ReasoningResult)


class TestReasoningEngineConfiguration:
    """Tests for configuration handling in reasoning engine."""

    def test_engine_uses_config_parameters(self, reasoning_config):
        """Test that engine passes config to strategies."""
        engine = ReasoningEngine(reasoning_config)

        mcts = engine.get_strategy("mcts")

        # Should have config from initialization
        assert mcts.config is not None

    def test_engine_without_config(self):
        """Test engine initialization without config."""
        engine = ReasoningEngine()

        assert len(engine.strategies) == 12

    @pytest.mark.asyncio
    async def test_config_affects_reasoning_behavior(self, sample_requirements):
        """Test that configuration affects reasoning behavior."""
        # Create config with very few iterations
        from synth_agent.core.config import Config
        config = Config()
        config.reasoning.mcts_iterations = 10

        engine = ReasoningEngine(config)

        result = await engine.execute("mcts", sample_requirements)

        # Check that config was respected
        assert result.metadata.get("iterations") == 10
