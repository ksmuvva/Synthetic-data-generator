"""
Graph of Thoughts (GoT) reasoning for synthetic data generation.

Ideal for network data, social graphs, and scenarios where reasoning
about data as interconnected graphs is beneficial.
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
import copy

from .base import BaseReasoningStrategy, ReasoningResult


@dataclass
class GraphNode:
    """Node in the graph of thoughts."""
    id: str
    requirements: Dict[str, Any]
    connections: Set[str] = field(default_factory=set)
    score: float = 0.0


class GraphOfThoughtsReasoner(BaseReasoningStrategy):
    """
    Graph of Thoughts reasoning strategy.

    Reasons about requirements as interconnected graphs, identifying
    relationships and dependencies. Ideal for network and graph data.
    """

    def __init__(self, config: Optional[Any] = None):
        """Initialize Graph of Thoughts reasoner."""
        super().__init__(config)

    async def reason(
        self,
        requirements: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> ReasoningResult:
        """
        Apply graph of thoughts reasoning.

        Args:
            requirements: Initial requirements
            context: Optional context

        Returns:
            ReasoningResult with graph-enhanced requirements
        """
        self.logger.info("Starting Graph of Thoughts reasoning")

        reasoning_steps = [
            "Starting Graph of Thoughts reasoning",
            "Modeling requirements as interconnected graph",
        ]

        # Phase 1: Build thought graph
        reasoning_steps.append("Phase 1: Building thought graph")
        graph = self._build_thought_graph(requirements)

        reasoning_steps.append(f"  Created graph with {len(graph)} nodes")

        # Phase 2: Analyze graph structure
        reasoning_steps.append("Phase 2: Analyzing graph structure")
        analysis = self._analyze_graph(graph)

        reasoning_steps.extend([
            f"  Identified {analysis['connected_components']} connected components",
            f"  Average connections per node: {analysis['avg_connections']:.2f}",
            f"  Graph density: {analysis['density']:.3f}",
        ])

        # Phase 3: Enhance based on graph insights
        reasoning_steps.append("Phase 3: Enhancing requirements using graph insights")
        enhanced = self._enhance_from_graph(requirements, graph, analysis)

        reasoning_steps.extend([
            "  + Added graph-based relationships",
            "  + Enhanced with network properties",
            "  + Applied graph constraints",
        ])

        confidence = self._calculate_confidence(analysis, enhanced)

        reasoning_steps.append(
            f"Graph of Thoughts completed with confidence: {confidence:.2f}"
        )

        self.logger.info(
            "Graph of Thoughts completed",
            nodes=len(graph),
            confidence=confidence,
        )

        return ReasoningResult(
            enhanced_requirements=enhanced,
            reasoning_steps=reasoning_steps,
            confidence=confidence,
            metadata={
                "graph_nodes": len(graph),
                "connected_components": analysis["connected_components"],
                "avg_connections": analysis["avg_connections"],
                "density": analysis["density"],
            },
        )

    def _build_thought_graph(
        self,
        requirements: Dict[str, Any],
    ) -> Dict[str, GraphNode]:
        """Build a graph representation of thoughts."""
        graph = {}

        # Create nodes for each field
        if "fields" in requirements:
            for field in requirements["fields"]:
                if isinstance(field, dict):
                    field_name = field.get("name", "unknown")
                    node_id = f"field_{field_name}"

                    graph[node_id] = GraphNode(
                        id=node_id,
                        requirements={"field": field},
                    )

        # Add connections based on relationships
        if "relationships" in requirements:
            for rel in requirements["relationships"]:
                if isinstance(rel, dict):
                    from_field = rel.get("from", "")
                    to_field = rel.get("to", "")

                    from_id = f"field_{from_field}"
                    to_id = f"field_{to_field.split('.')[0]}"  # Handle "table.field" format

                    if from_id in graph and to_id in graph:
                        graph[from_id].connections.add(to_id)
                        graph[to_id].connections.add(from_id)

        # Infer connections from field names
        field_nodes = [n for n in graph.values() if n.id.startswith("field_")]
        for i, node1 in enumerate(field_nodes):
            for node2 in field_nodes[i + 1:]:
                # Connect if names are similar (simple heuristic)
                name1 = node1.id.replace("field_", "").lower()
                name2 = node2.id.replace("field_", "").lower()

                if self._are_related(name1, name2):
                    node1.connections.add(node2.id)
                    node2.connections.add(node1.id)

        return graph

    def _are_related(self, name1: str, name2: str) -> bool:
        """Check if two field names are semantically related."""
        # Simple heuristic: share common words
        words1 = set(name1.replace("_", " ").split())
        words2 = set(name2.replace("_", " ").split())

        common = words1 & words2
        return len(common) > 0

    def _analyze_graph(self, graph: Dict[str, GraphNode]) -> Dict[str, Any]:
        """Analyze graph structure."""
        if not graph:
            return {
                "connected_components": 0,
                "avg_connections": 0.0,
                "density": 0.0,
            }

        # Count connected components (simplified - just count isolated nodes)
        isolated = sum(1 for node in graph.values() if not node.connections)
        connected = len(graph) - isolated
        components = isolated + (1 if connected > 0 else 0)

        # Average connections
        total_connections = sum(len(node.connections) for node in graph.values())
        avg_connections = total_connections / len(graph) if graph else 0.0

        # Density
        n = len(graph)
        max_edges = n * (n - 1) / 2 if n > 1 else 1
        actual_edges = total_connections / 2  # Each edge counted twice
        density = actual_edges / max_edges if max_edges > 0 else 0.0

        return {
            "connected_components": components,
            "avg_connections": avg_connections,
            "density": density,
        }

    def _enhance_from_graph(
        self,
        requirements: Dict[str, Any],
        graph: Dict[str, GraphNode],
        analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Enhance requirements based on graph insights."""
        enhanced = copy.deepcopy(requirements)

        # Add graph properties
        if "graph_properties" not in enhanced:
            enhanced["graph_properties"] = {}

        enhanced["graph_properties"].update({
            "is_graph_data": True,
            "node_count": len(graph),
            "avg_degree": analysis["avg_connections"],
            "density": analysis["density"],
        })

        # Add network-specific constraints
        if "constraints" not in enhanced:
            enhanced["constraints"] = []

        enhanced["constraints"].extend([
            "Maintain graph connectivity",
            "Preserve degree distribution",
            "Ensure bidirectional edges",
        ])

        # Enhance quality for graph data
        if "quality_requirements" not in enhanced:
            enhanced["quality_requirements"] = {}

        enhanced["quality_requirements"]["graph_consistency"] = True

        return enhanced

    def _calculate_confidence(
        self,
        analysis: Dict[str, Any],
        requirements: Dict[str, Any],
    ) -> float:
        """Calculate confidence based on graph analysis."""
        score = 0.5  # Base confidence

        # Boost if graph properties detected
        if "graph_properties" in requirements:
            score += 0.2

        # Boost based on connectivity
        if analysis["avg_connections"] > 1:
            score += 0.15

        # Boost based on density
        if analysis["density"] > 0.1:
            score += 0.15

        return min(1.0, score)

    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about Graph of Thoughts reasoning."""
        return {
            "name": "graph_of_thoughts",
            "description": "Graph of Thoughts - Reasons about data as interconnected graphs",
            "use_cases": [
                "Network data generation",
                "Social graph generation",
                "Knowledge graph creation",
                "Relationship-heavy data",
            ],
            "parameters": {},
            "strengths": [
                "Excellent for graph data",
                "Identifies hidden relationships",
                "Maintains graph properties",
                "Good for network analysis",
            ],
            "limitations": [
                "Overhead for non-graph data",
                "Requires relationship information",
                "More complex analysis",
            ],
        }
