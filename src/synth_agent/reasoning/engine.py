"""
Reasoning engine that orchestrates different reasoning strategies.

This engine manages the execution of reasoning methods and provides
a unified interface for applying reasoning to data generation.
"""

import time
from typing import Dict, Any, Optional
import structlog

from .base import BaseReasoningStrategy, ReasoningResult
from .strategy_selector import StrategySelector
from .metrics import ReasoningMetrics, get_metrics_tracker

# Import reasoning strategies (will be implemented)
from .mcts_reasoner import MCTSReasoner
from .beam_search_reasoner import BeamSearchReasoner
from .chain_of_thought import ChainOfThoughtReasoner
from .tree_of_thoughts import TreeOfThoughtsReasoner
from .self_consistency import SelfConsistencyReasoner
from .react_reasoner import ReActReasoner
from .reflexion_reasoner import ReflexionReasoner
from .best_first_search import BestFirstSearchReasoner
from .astar_reasoner import AStarReasoner
from .meta_prompting import MetaPromptingReasoner
from .iterative_refinement import IterativeRefinementReasoner
from .graph_of_thoughts import GraphOfThoughtsReasoner


logger = structlog.get_logger(__name__)


class ReasoningEngine:
    """
    Engine for applying reasoning strategies to data generation.

    This engine:
    1. Manages different reasoning strategy instances
    2. Routes requests to appropriate strategies
    3. Tracks performance metrics
    4. Handles errors and fallbacks
    """

    def __init__(self, config: Optional[Any] = None):
        """
        Initialize reasoning engine.

        Args:
            config: Configuration object with reasoning settings
        """
        self.config = config
        self.selector = StrategySelector(config)
        self.metrics_tracker = get_metrics_tracker()

        # Initialize all reasoning strategies
        self.strategies: Dict[str, BaseReasoningStrategy] = {
            "mcts": MCTSReasoner(config),
            "beam_search": BeamSearchReasoner(config),
            "chain_of_thought": ChainOfThoughtReasoner(config),
            "tree_of_thoughts": TreeOfThoughtsReasoner(config),
            "self_consistency": SelfConsistencyReasoner(config),
            "react": ReActReasoner(config),
            "reflexion": ReflexionReasoner(config),
            "best_first_search": BestFirstSearchReasoner(config),
            "astar": AStarReasoner(config),
            "meta_prompting": MetaPromptingReasoner(config),
            "iterative_refinement": IterativeRefinementReasoner(config),
            "graph_of_thoughts": GraphOfThoughtsReasoner(config),
        }

        logger.info("ReasoningEngine initialized", strategies_count=len(self.strategies))

    async def execute(
        self,
        method: str,
        requirements: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> ReasoningResult:
        """
        Execute a specific reasoning method.

        Args:
            method: Name of reasoning method to use
            requirements: Data requirements to enhance
            context: Optional context information

        Returns:
            ReasoningResult with enhanced requirements

        Raises:
            ValueError: If method is not available
        """
        if method not in self.strategies:
            available = ", ".join(self.strategies.keys())
            raise ValueError(
                f"Unknown reasoning method: {method}. Available: {available}"
            )

        strategy = self.strategies[method]
        logger.info("Executing reasoning strategy", method=method)

        start_time = time.time()
        success = True
        error_message = ""
        result = None

        try:
            # Validate requirements
            if not await strategy.validate_requirements(requirements):
                logger.warning("Requirements validation failed", method=method)
                # Continue anyway with a warning in the result

            # Execute reasoning
            result = await strategy.reason(requirements, context)
            result.method_used = method

        except Exception as e:
            success = False
            error_message = str(e)
            logger.error("Reasoning execution failed", method=method, error=str(e))

            # Return original requirements on failure
            result = ReasoningResult(
                enhanced_requirements=requirements,
                reasoning_steps=[f"Error: {error_message}"],
                confidence=0.0,
                method_used=method,
                metadata={"error": error_message},
            )

        finally:
            execution_time = time.time() - start_time
            result.execution_time = execution_time

            # Record metrics
            metrics = ReasoningMetrics(
                method_name=method,
                execution_time=execution_time,
                confidence_score=result.confidence,
                steps_count=len(result.reasoning_steps),
                success=success,
                error_message=error_message,
                metadata=result.metadata,
            )
            self.metrics_tracker.record(metrics)

        logger.info(
            "Reasoning execution completed",
            method=method,
            execution_time=execution_time,
            confidence=result.confidence,
            success=success,
        )

        return result

    async def auto_execute(
        self,
        requirements: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> tuple[ReasoningResult, Dict[str, Any]]:
        """
        Auto-detect and execute optimal reasoning strategy.

        Args:
            requirements: Data requirements
            context: Optional context information

        Returns:
            Tuple of (ReasoningResult, detection_info)
        """
        logger.info("Auto-detecting reasoning strategy")

        # Auto-detect optimal strategy
        detection = await self.selector.auto_detect(requirements, context)

        recommended = detection["recommended"]
        logger.info(
            "Strategy auto-detected",
            recommended=recommended,
            confidence=detection["confidence"],
            domain=detection["detected_domain"],
        )

        # Execute recommended strategy
        result = await self.execute(recommended, requirements, context)

        return result, detection

    def get_strategy(self, method: str) -> Optional[BaseReasoningStrategy]:
        """
        Get a specific reasoning strategy instance.

        Args:
            method: Method name

        Returns:
            Strategy instance or None
        """
        return self.strategies.get(method)

    def list_strategies(self) -> list[str]:
        """
        List all available reasoning strategies.

        Returns:
            List of strategy names
        """
        return list(self.strategies.keys())

    def get_metrics_summary(self, method: Optional[str] = None) -> Dict[str, Any]:
        """
        Get metrics summary.

        Args:
            method: Optional method name to filter by

        Returns:
            Metrics summary dictionary
        """
        return self.metrics_tracker.get_summary(method)
