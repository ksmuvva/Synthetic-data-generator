"""
Unit tests for all 12 reasoning modules.
"""

import pytest
from synth_agent.reasoning.mcts_reasoner import MCTSReasoner
from synth_agent.reasoning.beam_search_reasoner import BeamSearchReasoner
from synth_agent.reasoning.chain_of_thought import ChainOfThoughtReasoner
from synth_agent.reasoning.tree_of_thoughts import TreeOfThoughtsReasoner
from synth_agent.reasoning.self_consistency import SelfConsistencyReasoner
from synth_agent.reasoning.react_reasoner import ReActReasoner
from synth_agent.reasoning.reflexion_reasoner import ReflexionReasoner
from synth_agent.reasoning.best_first_search import BestFirstSearchReasoner
from synth_agent.reasoning.astar_reasoner import AStarReasoner
from synth_agent.reasoning.meta_prompting import MetaPromptingReasoner
from synth_agent.reasoning.iterative_refinement import IterativeRefinementReasoner
from synth_agent.reasoning.graph_of_thoughts import GraphOfThoughtsReasoner
from synth_agent.reasoning.base import ReasoningResult

# Add fixtures directory to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "fixtures"))
from reasoning_fixtures import *


class TestMCTSReasoner:
    """Tests for Monte Carlo Tree Search reasoner."""

    @pytest.mark.asyncio
    async def test_mcts_basic_reasoning(self, financial_requirements, reasoning_config):
        """Test basic MCTS reasoning."""
        reasoner = MCTSReasoner(reasoning_config)

        result = await reasoner.reason(financial_requirements)

        assert isinstance(result, ReasoningResult)
        assert result.enhanced_requirements is not None
        assert len(result.reasoning_steps) > 0
        assert 0.0 <= result.confidence <= 1.0
        assert result.method_used == "mcts"

    @pytest.mark.asyncio
    async def test_mcts_metadata(self, financial_requirements, reasoning_config):
        """Test MCTS metadata generation."""
        reasoner = MCTSReasoner(reasoning_config)

        metadata = reasoner.get_metadata()

        assert metadata["name"] == "mcts"
        assert "financial" in str(metadata["use_cases"]).lower()
        assert "iterations" in metadata["parameters"]

    @pytest.mark.asyncio
    async def test_mcts_enhances_financial_data(self, financial_requirements, reasoning_config):
        """Test that MCTS enhances financial data appropriately."""
        reasoner = MCTSReasoner(reasoning_config)

        result = await reasoner.reason(financial_requirements)

        # Check for financial-specific enhancements
        assert "quality_requirements" in result.enhanced_requirements or \
               result.enhanced_requirements != financial_requirements


class TestBeamSearchReasoner:
    """Tests for Beam Search reasoner."""

    @pytest.mark.asyncio
    async def test_beam_search_basic(self, ecommerce_requirements, reasoning_config):
        """Test basic beam search reasoning."""
        reasoner = BeamSearchReasoner(reasoning_config)

        result = await reasoner.reason(ecommerce_requirements)

        assert isinstance(result, ReasoningResult)
        assert result.confidence > 0.0
        assert "beam_width" in result.metadata

    @pytest.mark.asyncio
    async def test_beam_search_generates_variants(self, ecommerce_requirements, reasoning_config):
        """Test that beam search explores multiple variants."""
        reasoner = BeamSearchReasoner(reasoning_config)

        result = await reasoner.reason(ecommerce_requirements)

        # Should have explored multiple candidates
        assert result.metadata.get("final_candidates", 0) > 0


class TestChainOfThoughtReasoner:
    """Tests for Chain of Thought reasoner."""

    @pytest.mark.asyncio
    async def test_cot_healthcare(self, healthcare_requirements, reasoning_config):
        """Test CoT on healthcare data."""
        reasoner = ChainOfThoughtReasoner(reasoning_config)

        result = await reasoner.reason(healthcare_requirements)

        assert isinstance(result, ReasoningResult)
        # Should have multiple reasoning steps
        assert len(result.reasoning_steps) >= 5

    @pytest.mark.asyncio
    async def test_cot_adds_constraints(self, healthcare_requirements, reasoning_config):
        """Test that CoT adds appropriate constraints."""
        reasoner = ChainOfThoughtReasoner(reasoning_config)

        result = await reasoner.reason(healthcare_requirements)

        # Should add domain-specific constraints
        constraints = result.enhanced_requirements.get("constraints", [])
        assert len(constraints) > 0

    @pytest.mark.asyncio
    async def test_cot_step_by_step(self, sample_requirements, reasoning_config):
        """Test that CoT provides step-by-step reasoning."""
        reasoner = ChainOfThoughtReasoner(reasoning_config)

        result = await reasoner.reason(sample_requirements)

        # Check for step markers in reasoning
        steps_text = " ".join(result.reasoning_steps)
        assert "Step" in steps_text or "step" in steps_text


class TestTreeOfThoughtsReasoner:
    """Tests for Tree of Thoughts reasoner."""

    @pytest.mark.asyncio
    async def test_tot_relational_data(self, relational_requirements, reasoning_config):
        """Test ToT on relational data."""
        reasoner = TreeOfThoughtsReasoner(reasoning_config)

        result = await reasoner.reason(relational_requirements)

        assert isinstance(result, ReasoningResult)
        assert result.metadata.get("paths_explored", 0) > 0

    @pytest.mark.asyncio
    async def test_tot_explores_branches(self, relational_requirements, reasoning_config):
        """Test that ToT explores multiple branches."""
        reasoner = TreeOfThoughtsReasoner(reasoning_config)

        result = await reasoner.reason(relational_requirements)

        # Should have explored multiple paths
        assert result.metadata.get("paths_explored", 0) >= reasoning_config.reasoning.tot_branches


class TestSelfConsistencyReasoner:
    """Tests for Self-Consistency reasoner."""

    @pytest.mark.asyncio
    async def test_self_consistency_multiple_samples(self, sample_requirements, reasoning_config):
        """Test that self-consistency generates multiple samples."""
        reasoner = SelfConsistencyReasoner(reasoning_config)

        result = await reasoner.reason(sample_requirements)

        assert isinstance(result, ReasoningResult)
        assert result.metadata.get("samples") == reasoning_config.reasoning.self_consistency_samples

    @pytest.mark.asyncio
    async def test_self_consistency_high_confidence(self, sample_requirements, reasoning_config):
        """Test that self-consistency produces consistent results."""
        reasoner = SelfConsistencyReasoner(reasoning_config)

        result = await reasoner.reason(sample_requirements)

        # Self-consistency should have decent confidence
        assert result.confidence > 0.3


class TestReActReasoner:
    """Tests for ReAct (Reasoning + Acting) reasoner."""

    @pytest.mark.asyncio
    async def test_react_interleaved_reasoning(self, sample_requirements, reasoning_config):
        """Test ReAct interleaved reasoning and actions."""
        reasoner = ReActReasoner(reasoning_config)

        result = await reasoner.reason(sample_requirements)

        assert isinstance(result, ReasoningResult)
        # Should have both thoughts and actions
        steps_text = " ".join(result.reasoning_steps)
        assert "Thought" in steps_text or "Action" in steps_text

    @pytest.mark.asyncio
    async def test_react_validation(self, sample_requirements, reasoning_config):
        """Test that ReAct includes validation actions."""
        reasoner = ReActReasoner(reasoning_config)

        result = await reasoner.reason(sample_requirements)

        # Should perform validation
        assert result.metadata.get("actions_performed", 0) > 0


class TestReflexionReasoner:
    """Tests for Reflexion (Self-Reflection) reasoner."""

    @pytest.mark.asyncio
    async def test_reflexion_iterative(self, sample_requirements, reasoning_config):
        """Test that reflexion iterates and improves."""
        reasoner = ReflexionReasoner(reasoning_config)

        result = await reasoner.reason(sample_requirements)

        assert isinstance(result, ReasoningResult)
        assert result.metadata.get("iterations", 0) > 0

    @pytest.mark.asyncio
    async def test_reflexion_learns_from_mistakes(self, sample_requirements, reasoning_config):
        """Test that reflexion identifies and fixes issues."""
        # Create requirements with deliberate issues
        incomplete_reqs = sample_requirements.copy()
        incomplete_reqs["fields"][0].pop("type", None)  # Remove type

        reasoner = ReflexionReasoner(reasoning_config)
        result = await reasoner.reason(incomplete_reqs)

        # Should have fixed the missing type
        enhanced_fields = result.enhanced_requirements.get("fields", [])
        if enhanced_fields:
            assert "type" in enhanced_fields[0]


class TestBestFirstSearchReasoner:
    """Tests for Best-First Search reasoner."""

    @pytest.mark.asyncio
    async def test_best_first_timeseries(self, timeseries_requirements, reasoning_config):
        """Test Best-First on time-series data."""
        reasoner = BestFirstSearchReasoner(reasoning_config)

        result = await reasoner.reason(timeseries_requirements)

        assert isinstance(result, ReasoningResult)
        assert result.metadata.get("nodes_explored", 0) > 0

    @pytest.mark.asyncio
    async def test_best_first_prioritizes(self, timeseries_requirements, reasoning_config):
        """Test that best-first prioritizes promising paths."""
        reasoner = BestFirstSearchReasoner(reasoning_config)

        result = await reasoner.reason(timeseries_requirements)

        # Should have explored multiple nodes
        assert result.metadata.get("nodes_explored", 0) > 1


class TestAStarReasoner:
    """Tests for A* Search reasoner."""

    @pytest.mark.asyncio
    async def test_astar_optimization(self, sample_requirements, reasoning_config):
        """Test A* for optimization scenarios."""
        reasoner = AStarReasoner(reasoning_config)

        result = await reasoner.reason(sample_requirements)

        assert isinstance(result, ReasoningResult)
        assert "final_f_score" in result.metadata

    @pytest.mark.asyncio
    async def test_astar_heuristic(self, sample_requirements, reasoning_config):
        """Test that A* uses heuristic effectively."""
        reasoner = AStarReasoner(reasoning_config)

        result = await reasoner.reason(sample_requirements)

        # Should reach goal or get close
        assert result.confidence > 0.3


class TestMetaPromptingReasoner:
    """Tests for Meta-Prompting reasoner."""

    @pytest.mark.asyncio
    async def test_meta_prompting_adapts(self, financial_requirements, reasoning_config):
        """Test that meta-prompting adapts to domain."""
        reasoner = MetaPromptingReasoner(reasoning_config)

        result = await reasoner.reason(financial_requirements)

        assert isinstance(result, ReasoningResult)
        assert "strategy_used" in result.metadata

    @pytest.mark.asyncio
    async def test_meta_prompting_detects_domain(self, healthcare_requirements, reasoning_config):
        """Test domain detection in meta-prompting."""
        reasoner = MetaPromptingReasoner(reasoning_config)

        result = await reasoner.reason(healthcare_requirements)

        # Should detect healthcare domain
        domain = result.metadata.get("domain", "")
        assert domain in ["healthcare", "general"]


class TestIterativeRefinementReasoner:
    """Tests for Iterative Refinement reasoner."""

    @pytest.mark.asyncio
    async def test_iterative_refinement_multiple_passes(self, sample_requirements, reasoning_config):
        """Test that iterative refinement makes multiple passes."""
        reasoner = IterativeRefinementReasoner(reasoning_config)

        result = await reasoner.reason(sample_requirements)

        assert isinstance(result, ReasoningResult)
        assert result.metadata.get("refinement_passes", 0) > 0

    @pytest.mark.asyncio
    async def test_iterative_refinement_improves_quality(self, sample_requirements, reasoning_config):
        """Test that quality improves over iterations."""
        reasoner = IterativeRefinementReasoner(reasoning_config)

        result = await reasoner.reason(sample_requirements)

        # Should have quality progression
        quality_scores = result.metadata.get("quality_progression", [])
        if len(quality_scores) > 1:
            # Later scores should be >= earlier scores (monotonic improvement)
            assert quality_scores[-1] >= quality_scores[0]


class TestGraphOfThoughtsReasoner:
    """Tests for Graph of Thoughts reasoner."""

    @pytest.mark.asyncio
    async def test_got_network_data(self, network_requirements, reasoning_config):
        """Test GoT on network/graph data."""
        reasoner = GraphOfThoughtsReasoner(reasoning_config)

        result = await reasoner.reason(network_requirements)

        assert isinstance(result, ReasoningResult)
        assert result.metadata.get("graph_nodes", 0) > 0

    @pytest.mark.asyncio
    async def test_got_identifies_connections(self, network_requirements, reasoning_config):
        """Test that GoT identifies graph connections."""
        reasoner = GraphOfThoughtsReasoner(reasoning_config)

        result = await reasoner.reason(network_requirements)

        # Should analyze graph structure
        assert "connected_components" in result.metadata
        assert "avg_connections" in result.metadata


class TestReasoningModuleCommonBehavior:
    """Tests for common behavior across all reasoning modules."""

    @pytest.fixture(params=[
        MCTSReasoner,
        BeamSearchReasoner,
        ChainOfThoughtReasoner,
        TreeOfThoughtsReasoner,
        SelfConsistencyReasoner,
        ReActReasoner,
        ReflexionReasoner,
        BestFirstSearchReasoner,
        AStarReasoner,
        MetaPromptingReasoner,
        IterativeRefinementReasoner,
        GraphOfThoughtsReasoner,
    ])
    def reasoner_class(self, request):
        """Parametrize over all reasoner classes."""
        return request.param

    @pytest.mark.asyncio
    async def test_all_reasoners_return_valid_result(
        self, reasoner_class, sample_requirements, reasoning_config
    ):
        """Test that all reasoners return valid ReasoningResult."""
        reasoner = reasoner_class(reasoning_config)

        result = await reasoner.reason(sample_requirements)

        assert isinstance(result, ReasoningResult)
        assert result.enhanced_requirements is not None
        assert isinstance(result.reasoning_steps, list)
        assert isinstance(result.confidence, float)
        assert 0.0 <= result.confidence <= 1.0
        assert isinstance(result.metadata, dict)

    @pytest.mark.asyncio
    async def test_all_reasoners_have_metadata(self, reasoner_class, reasoning_config):
        """Test that all reasoners provide metadata."""
        reasoner = reasoner_class(reasoning_config)

        metadata = reasoner.get_metadata()

        assert "name" in metadata
        assert "description" in metadata
        assert "use_cases" in metadata
        assert isinstance(metadata["use_cases"], list)

    @pytest.mark.asyncio
    async def test_all_reasoners_handle_empty_requirements(
        self, reasoner_class, reasoning_config
    ):
        """Test that all reasoners handle empty requirements gracefully."""
        reasoner = reasoner_class(reasoning_config)

        # Should not crash, even with empty requirements
        result = await reasoner.reason({})

        assert isinstance(result, ReasoningResult)

    @pytest.mark.asyncio
    async def test_all_reasoners_execution_time(
        self, reasoner_class, sample_requirements, reasoning_config
    ):
        """Test that all reasoners track execution time."""
        reasoner = reasoner_class(reasoning_config)

        result = await reasoner.reason(sample_requirements)

        assert result.execution_time >= 0.0
