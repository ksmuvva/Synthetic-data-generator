"""
Strategy selector for auto-detecting optimal reasoning methods.

This module analyzes requirements and recommends the best reasoning strategy.
"""

from typing import Dict, List, Optional, Any
import structlog

logger = structlog.get_logger(__name__)


# Domain to reasoning method mapping
REASONING_MAP = {
    "financial": "mcts",
    "banking": "mcts",
    "trading": "mcts",
    "risk_management": "mcts",
    "fraud_detection": "mcts",

    "ecommerce": "beam_search",
    "retail": "beam_search",
    "marketing": "beam_search",
    "product_catalog": "beam_search",

    "healthcare": "chain_of_thought",
    "medical": "chain_of_thought",
    "legal": "chain_of_thought",
    "education": "chain_of_thought",

    "compliance": "self_consistency",
    "validation": "self_consistency",
    "audit": "self_consistency",

    "relational": "tree_of_thoughts",
    "multi_table": "tree_of_thoughts",
    "database": "tree_of_thoughts",

    "timeseries": "best_first_search",
    "sequential": "best_first_search",
    "temporal": "best_first_search",

    "network": "graph_of_thoughts",
    "social": "graph_of_thoughts",
    "graph": "graph_of_thoughts",

    "realtime": "react",
    "validation_required": "react",
    "api_integration": "react",

    "iterative": "reflexion",
    "quality_focused": "reflexion",
    "improvement": "reflexion",

    "optimization": "astar",
    "scheduling": "astar",
    "resource_allocation": "astar",

    "multi_domain": "meta_prompting",
    "adaptive": "meta_prompting",
    "cross_functional": "meta_prompting",
}

# Domain detection keywords
DOMAIN_KEYWORDS = {
    "financial": [
        "transaction", "payment", "account", "balance", "trading", "stock",
        "portfolio", "investment", "currency", "forex", "bank", "credit",
        "debit", "loan", "interest", "revenue", "expense", "profit", "loss"
    ],
    "healthcare": [
        "patient", "diagnosis", "medical", "treatment", "prescription", "doctor",
        "hospital", "clinic", "disease", "symptom", "medication", "health",
        "care", "clinical", "therapy", "surgery"
    ],
    "ecommerce": [
        "product", "order", "cart", "customer", "inventory", "sku", "price",
        "purchase", "checkout", "shipping", "catalog", "store", "retail",
        "merchant", "vendor"
    ],
    "network": [
        "node", "edge", "connection", "graph", "relationship", "link", "network",
        "social", "friend", "follower", "community", "cluster", "path"
    ],
    "compliance": [
        "compliance", "regulation", "audit", "policy", "rule", "standard",
        "certification", "validation", "verification", "legal"
    ],
    "timeseries": [
        "time", "temporal", "series", "sequence", "trend", "forecast", "historical",
        "timestamp", "date", "period", "interval"
    ],
    "optimization": [
        "optimize", "schedule", "allocation", "resource", "capacity", "planning",
        "constraint", "objective", "minimize", "maximize"
    ],
}


class StrategySelector:
    """
    Selects optimal reasoning strategy based on requirements analysis.

    Uses keyword matching, domain detection, and confidence scoring to
    recommend the best reasoning method for given requirements.
    """

    def __init__(self, config: Optional[Any] = None):
        """
        Initialize strategy selector.

        Args:
            config: Configuration object with reasoning settings
        """
        self.config = config
        self.confidence_threshold = 0.75
        if config and hasattr(config, "reasoning"):
            self.confidence_threshold = getattr(
                config.reasoning, "confidence_threshold", 0.75
            )

    async def auto_detect(
        self,
        requirements: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Auto-detect optimal reasoning strategy.

        Args:
            requirements: Data requirements to analyze
            context: Optional context information

        Returns:
            Dictionary with:
                - recommended: Recommended reasoning method
                - confidence: Confidence score (0-1)
                - reason: Explanation of why this method was chosen
                - alternatives: List of alternative methods
                - detected_domain: Detected domain/use case
        """
        logger.info("Auto-detecting reasoning strategy", requirements_keys=list(requirements.keys()))

        # Extract text content for analysis
        text_content = self._extract_text_content(requirements)

        # Detect domain
        domain_scores = self._detect_domain(text_content, requirements)
        detected_domain = max(domain_scores, key=domain_scores.get) if domain_scores else None
        confidence = domain_scores.get(detected_domain, 0.0) if detected_domain else 0.0

        logger.debug(
            "Domain detection results",
            detected_domain=detected_domain,
            confidence=confidence,
            all_scores=domain_scores,
        )

        # Map domain to reasoning method
        recommended = self._map_domain_to_reasoning(detected_domain, requirements)

        # Get alternatives
        alternatives = self._get_alternatives(detected_domain, recommended, domain_scores)

        # Generate explanation
        reason = self._generate_explanation(recommended, detected_domain, confidence, requirements)

        result = {
            "recommended": recommended,
            "confidence": confidence,
            "reason": reason,
            "alternatives": alternatives,
            "detected_domain": detected_domain or "general",
        }

        logger.info(
            "Strategy detection completed",
            recommended=recommended,
            confidence=confidence,
            detected_domain=detected_domain,
        )

        return result

    def _extract_text_content(self, requirements: Dict[str, Any]) -> str:
        """Extract all text content from requirements for analysis."""
        text_parts = []

        # Add data_type
        if "data_type" in requirements:
            text_parts.append(str(requirements["data_type"]))

        # Add field names and descriptions
        if "fields" in requirements:
            for field in requirements["fields"]:
                if isinstance(field, dict):
                    text_parts.append(field.get("name", ""))
                    text_parts.append(field.get("description", ""))
                    text_parts.append(field.get("type", ""))

        # Add constraints
        if "constraints" in requirements:
            for constraint in requirements.get("constraints", []):
                if isinstance(constraint, str):
                    text_parts.append(constraint)
                elif isinstance(constraint, dict):
                    text_parts.extend(str(v) for v in constraint.values())

        # Add relationships
        if "relationships" in requirements:
            for rel in requirements.get("relationships", []):
                if isinstance(rel, dict):
                    text_parts.extend(str(v) for v in rel.values())

        return " ".join(text_parts).lower()

    def _detect_domain(
        self,
        text_content: str,
        requirements: Dict[str, Any],
    ) -> Dict[str, float]:
        """
        Detect domain based on keyword matching.

        Returns:
            Dictionary mapping domain names to confidence scores
        """
        domain_scores = {}

        # Check explicit domain field
        if "domain" in requirements:
            explicit_domain = requirements["domain"].lower()
            if explicit_domain in REASONING_MAP:
                domain_scores[explicit_domain] = 1.0
                return domain_scores

        # Keyword-based detection
        for domain, keywords in DOMAIN_KEYWORDS.items():
            matches = sum(1 for keyword in keywords if keyword in text_content)
            if matches > 0:
                # Normalize score based on number of keywords
                score = min(1.0, matches / len(keywords) * 5)  # Scale up for better sensitivity
                domain_scores[domain] = score

        return domain_scores

    def _map_domain_to_reasoning(
        self,
        domain: Optional[str],
        requirements: Dict[str, Any],
    ) -> str:
        """Map detected domain to reasoning method."""
        # Check for explicit reasoning_method in requirements
        if "reasoning_method" in requirements:
            return requirements["reasoning_method"]

        # Use domain mapping
        if domain and domain in REASONING_MAP:
            return REASONING_MAP[domain]

        # Default fallback
        return "iterative_refinement"

    def _get_alternatives(
        self,
        detected_domain: Optional[str],
        recommended: str,
        domain_scores: Dict[str, float],
    ) -> List[str]:
        """Get alternative reasoning methods based on domain scores."""
        alternatives = []

        # Get top 3 domains (excluding the recommended one)
        sorted_domains = sorted(
            domain_scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        for domain, score in sorted_domains[:4]:  # Top 4 domains
            if domain in REASONING_MAP:
                method = REASONING_MAP[domain]
                if method != recommended and method not in alternatives:
                    alternatives.append(method)

        # Add general-purpose alternatives if list is short
        general_alternatives = ["iterative_refinement", "chain_of_thought", "reflexion"]
        for alt in general_alternatives:
            if alt != recommended and alt not in alternatives:
                alternatives.append(alt)
            if len(alternatives) >= 3:
                break

        return alternatives[:3]

    def _generate_explanation(
        self,
        recommended: str,
        detected_domain: Optional[str],
        confidence: float,
        requirements: Dict[str, Any],
    ) -> str:
        """Generate human-readable explanation for the recommendation."""
        explanations = {
            "mcts": "Monte Carlo Tree Search is ideal for financial data as it explores multiple generation paths and optimizes for realistic distributions with correlated fields.",
            "beam_search": "Beam Search maintains top candidates during generation, ensuring diverse but high-quality outputs perfect for product catalogs and e-commerce data.",
            "chain_of_thought": "Chain of Thought provides step-by-step reasoning for complex constraints, ideal for healthcare, legal, and educational data with intricate relationships.",
            "tree_of_thoughts": "Tree of Thoughts explores multiple reasoning branches simultaneously, perfect for complex relational data and multi-table database generation.",
            "self_consistency": "Self-Consistency generates multiple solutions and selects the most consistent one, ensuring high-quality validation and compliance data.",
            "react": "ReAct interleaves reasoning with actions, perfect for real-time validation and data generation that needs external API checks.",
            "reflexion": "Reflexion learns from previous generation mistakes and iteratively improves, ideal for quality-focused data generation.",
            "best_first_search": "Best-First Search prioritizes the most promising generation paths, ideal for time-series and sequential pattern data.",
            "astar": "A* Search provides optimal path finding with heuristics, perfect for scheduling, optimization, and resource allocation data.",
            "meta_prompting": "Meta-Prompting dynamically adjusts strategies based on data domain, ideal for multi-domain and cross-functional datasets.",
            "iterative_refinement": "Iterative Refinement progressively improves data quality through multiple passes, suitable for general data generation with quality requirements.",
            "graph_of_thoughts": "Graph of Thoughts reasons about data as interconnected graphs, perfect for network, social, and relationship data.",
        }

        base_explanation = explanations.get(
            recommended,
            f"{recommended.replace('_', ' ').title()} reasoning strategy",
        )

        if detected_domain:
            return f"{detected_domain.title()} domain detected. {base_explanation}"
        else:
            return f"{base_explanation} This is a general-purpose approach suitable for various data types."

    def get_all_methods(self) -> List[Dict[str, Any]]:
        """
        Get information about all available reasoning methods.

        Returns:
            List of dictionaries with method information
        """
        methods = {
            "mcts": {
                "name": "MCTS (Monte Carlo Tree Search)",
                "domains": ["financial", "banking", "trading", "risk_management"],
                "description": "Explores multiple generation paths and selects optimal distributions",
            },
            "beam_search": {
                "name": "Beam Search",
                "domains": ["ecommerce", "retail", "marketing"],
                "description": "Maintains top-k best candidates during generation",
            },
            "chain_of_thought": {
                "name": "Chain of Thought (CoT)",
                "domains": ["healthcare", "legal", "education"],
                "description": "Step-by-step reasoning for complex constraints",
            },
            "tree_of_thoughts": {
                "name": "Tree of Thoughts (ToT)",
                "domains": ["relational", "multi_table", "database"],
                "description": "Explores multiple reasoning branches simultaneously",
            },
            "self_consistency": {
                "name": "Self-Consistency",
                "domains": ["compliance", "validation", "audit"],
                "description": "Generates multiple solutions and selects most consistent",
            },
            "react": {
                "name": "ReAct (Reasoning + Acting)",
                "domains": ["realtime", "validation_required", "api_integration"],
                "description": "Interleaves reasoning with actions and external validation",
            },
            "reflexion": {
                "name": "Reflexion (Self-Reflection)",
                "domains": ["iterative", "quality_focused", "improvement"],
                "description": "Learns from mistakes and iteratively improves",
            },
            "best_first_search": {
                "name": "Best-First Search",
                "domains": ["timeseries", "sequential", "temporal"],
                "description": "Prioritizes most promising generation paths",
            },
            "astar": {
                "name": "A* Search",
                "domains": ["optimization", "scheduling", "resource_allocation"],
                "description": "Optimal path finding with heuristics",
            },
            "meta_prompting": {
                "name": "Meta-Prompting",
                "domains": ["multi_domain", "adaptive", "cross_functional"],
                "description": "Dynamically adjusts strategy based on domain",
            },
            "iterative_refinement": {
                "name": "Iterative Refinement",
                "domains": ["general", "quality_improvement"],
                "description": "Progressively improves data quality through multiple passes",
            },
            "graph_of_thoughts": {
                "name": "Graph of Thoughts (GoT)",
                "domains": ["network", "social", "graph"],
                "description": "Reasons about data as interconnected graphs",
            },
        }

        return [
            {"method": key, **value}
            for key, value in methods.items()
        ]
