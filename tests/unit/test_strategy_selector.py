"""
Unit tests for StrategySelector.
"""

import pytest
from synth_agent.reasoning.strategy_selector import StrategySelector, REASONING_MAP, DOMAIN_KEYWORDS

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "fixtures"))
from reasoning_fixtures import *


class TestStrategySelector:
    """Tests for strategy selection logic."""

    @pytest.mark.asyncio
    async def test_auto_detect_financial_domain(self, financial_requirements, reasoning_config):
        """Test auto-detection of financial domain."""
        selector = StrategySelector(reasoning_config)

        result = await selector.auto_detect(financial_requirements)

        assert result["recommended"] == "mcts"
        assert result["detected_domain"] in ["financial", "general"]
        assert 0.0 <= result["confidence"] <= 1.0

    @pytest.mark.asyncio
    async def test_auto_detect_healthcare_domain(self, healthcare_requirements, reasoning_config):
        """Test auto-detection of healthcare domain."""
        selector = StrategySelector(reasoning_config)

        result = await selector.auto_detect(healthcare_requirements)

        assert result["recommended"] == "chain_of_thought"
        assert "healthcare" in result["detected_domain"].lower() or result["detected_domain"] == "general"

    @pytest.mark.asyncio
    async def test_auto_detect_ecommerce_domain(self, ecommerce_requirements, reasoning_config):
        """Test auto-detection of e-commerce domain."""
        selector = StrategySelector(reasoning_config)

        result = await selector.auto_detect(ecommerce_requirements)

        assert result["recommended"] == "beam_search"

    @pytest.mark.asyncio
    async def test_auto_detect_network_domain(self, network_requirements, reasoning_config):
        """Test auto-detection of network domain."""
        selector = StrategySelector(reasoning_config)

        result = await selector.auto_detect(network_requirements)

        assert result["recommended"] == "graph_of_thoughts"

    @pytest.mark.asyncio
    async def test_auto_detect_timeseries_domain(self, timeseries_requirements, reasoning_config):
        """Test auto-detection of time-series domain."""
        selector = StrategySelector(reasoning_config)

        result = await selector.auto_detect(timeseries_requirements)

        assert result["recommended"] == "best_first_search"

    @pytest.mark.asyncio
    async def test_auto_detect_relational_domain(self, relational_requirements, reasoning_config):
        """Test auto-detection of relational domain."""
        selector = StrategySelector(reasoning_config)

        result = await selector.auto_detect(relational_requirements)

        # Could be ToT or other relational-focused methods
        assert result["recommended"] in ["tree_of_thoughts", "iterative_refinement", "meta_prompting"]

    @pytest.mark.asyncio
    async def test_auto_detect_provides_alternatives(self, sample_requirements, reasoning_config):
        """Test that auto-detect provides alternative methods."""
        selector = StrategySelector(reasoning_config)

        result = await selector.auto_detect(sample_requirements)

        assert "alternatives" in result
        assert isinstance(result["alternatives"], list)
        assert len(result["alternatives"]) > 0

    @pytest.mark.asyncio
    async def test_auto_detect_provides_explanation(self, financial_requirements, reasoning_config):
        """Test that auto-detect provides explanation."""
        selector = StrategySelector(reasoning_config)

        result = await selector.auto_detect(financial_requirements)

        assert "reason" in result
        assert len(result["reason"]) > 0
        assert isinstance(result["reason"], str)

    @pytest.mark.asyncio
    async def test_explicit_domain_override(self, sample_requirements, reasoning_config):
        """Test that explicit domain in requirements overrides detection."""
        selector = StrategySelector(reasoning_config)

        # Add explicit domain
        reqs_with_domain = sample_requirements.copy()
        reqs_with_domain["domain"] = "financial"

        result = await selector.auto_detect(reqs_with_domain)

        assert result["recommended"] == "mcts"
        assert result["confidence"] == 1.0  # Should be 100% confident with explicit domain

    @pytest.mark.asyncio
    async def test_confidence_threshold(self, reasoning_config):
        """Test confidence threshold configuration."""
        selector = StrategySelector(reasoning_config)

        assert selector.confidence_threshold == reasoning_config.reasoning.confidence_threshold

    @pytest.mark.asyncio
    async def test_fallback_to_default(self, reasoning_config):
        """Test fallback to default method for unknown domains."""
        selector = StrategySelector(reasoning_config)

        # Completely generic requirements
        generic_reqs = {"fields": [{"name": "field1", "type": "string"}]}

        result = await selector.auto_detect(generic_reqs)

        # Should fallback to default
        assert result["recommended"] in ["iterative_refinement", "meta_prompting"]

    def test_get_all_methods(self, reasoning_config):
        """Test getting all available methods."""
        selector = StrategySelector(reasoning_config)

        methods = selector.get_all_methods()

        assert len(methods) == 12
        assert all("method" in m for m in methods)
        assert all("name" in m for m in methods)
        assert all("domains" in m for m in methods)

    def test_domain_keywords_coverage(self):
        """Test that all domains have keywords defined."""
        # All domains in REASONING_MAP should be in DOMAIN_KEYWORDS or mappable
        unique_domains = set()
        for domain in REASONING_MAP.keys():
            # Extract base domain
            base_domain = domain.split("_")[0]
            unique_domains.add(base_domain)

        # Check that major domains have keywords
        major_domains = ["financial", "healthcare", "ecommerce", "network", "compliance", "timeseries"]
        for domain in major_domains:
            assert domain in DOMAIN_KEYWORDS, f"Domain {domain} should have keywords"

    @pytest.mark.asyncio
    async def test_keyword_matching_case_insensitive(self, reasoning_config):
        """Test that keyword matching is case-insensitive."""
        selector = StrategySelector(reasoning_config)

        # Use uppercase in data_type
        reqs = {
            "data_type": "FINANCIAL TRANSACTIONS",
            "fields": []
        }

        result = await selector.auto_detect(reqs)

        # Should still detect financial domain
        assert "financial" in result["detected_domain"].lower() or result["recommended"] == "mcts"

    @pytest.mark.asyncio
    async def test_multiple_domain_signals(self, reasoning_config):
        """Test behavior when multiple domains are signaled."""
        selector = StrategySelector(reasoning_config)

        # Requirements with mixed signals
        mixed_reqs = {
            "data_type": "financial healthcare data",
            "fields": [
                {"name": "transaction_id", "type": "string"},
                {"name": "patient_id", "type": "string"},
            ]
        }

        result = await selector.auto_detect(mixed_reqs)

        # Should pick one and provide alternatives
        assert result["recommended"] in ["mcts", "chain_of_thought"]
        assert len(result["alternatives"]) > 0

    @pytest.mark.asyncio
    async def test_confidence_scoring_with_many_keywords(self, reasoning_config):
        """Test that more keyword matches increase confidence."""
        selector = StrategySelector(reasoning_config)

        # Requirements with many financial keywords
        strong_financial_reqs = {
            "data_type": "financial banking trading transaction payment",
            "fields": [
                {"name": "account", "description": "bank account for trading"},
                {"name": "balance", "description": "account balance"},
                {"name": "transaction", "description": "financial transaction"},
            ]
        }

        result = await selector.auto_detect(strong_financial_reqs)

        # Should have higher confidence
        assert result["confidence"] > 0.5
        assert result["recommended"] == "mcts"


class TestStrategyMapping:
    """Tests for strategy mapping logic."""

    def test_all_reasoning_methods_covered(self):
        """Test that all 12 reasoning methods are in the mapping."""
        expected_methods = {
            "mcts", "beam_search", "chain_of_thought", "tree_of_thoughts",
            "self_consistency", "react", "reflexion", "best_first_search",
            "astar", "meta_prompting", "iterative_refinement", "graph_of_thoughts"
        }

        methods_in_map = set(REASONING_MAP.values())

        assert expected_methods.issubset(methods_in_map)

    def test_domain_to_method_consistency(self):
        """Test that domain mappings are consistent."""
        # Financial domains should all map to MCTS
        financial_domains = ["financial", "banking", "trading"]
        for domain in financial_domains:
            if domain in REASONING_MAP:
                assert REASONING_MAP[domain] == "mcts"

        # Healthcare/legal should map to CoT
        complex_domains = ["healthcare", "medical", "legal"]
        for domain in complex_domains:
            if domain in REASONING_MAP:
                assert REASONING_MAP[domain] == "chain_of_thought"


class TestStrategyExplanations:
    """Tests for explanation generation."""

    @pytest.mark.asyncio
    async def test_explanation_mentions_domain(self, financial_requirements, reasoning_config):
        """Test that explanation mentions detected domain."""
        selector = StrategySelector(reasoning_config)

        result = await selector.auto_detect(financial_requirements)

        explanation = result["reason"].lower()
        # Should mention the domain or method characteristics
        assert "financial" in explanation or "mcts" in explanation or "monte carlo" in explanation

    @pytest.mark.asyncio
    async def test_explanation_explains_choice(self, healthcare_requirements, reasoning_config):
        """Test that explanation explains why method was chosen."""
        selector = StrategySelector(reasoning_config)

        result = await selector.auto_detect(healthcare_requirements)

        explanation = result["reason"]
        # Should have substantial explanation
        assert len(explanation) > 50
        assert "healthcare" in explanation.lower() or "constraint" in explanation.lower()
