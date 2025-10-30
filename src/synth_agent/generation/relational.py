"""Relational data generation with foreign key support."""

import logging
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from synth_agent.core.exceptions import DataGenerationError

logger = logging.getLogger(__name__)


class RelationalDataGenerator:
    """Generates relational datasets with foreign key constraints."""

    def __init__(self):
        """Initialize relational data generator."""
        self.tables: Dict[str, pd.DataFrame] = {}
        self.relationships: List[Dict[str, Any]] = []

    def generate_relational_dataset(
        self,
        table_schemas: Dict[str, Dict[str, Any]],
        relationships: List[Dict[str, Any]],
        row_counts: Dict[str, int]
    ) -> Dict[str, pd.DataFrame]:
        """
        Generate multiple related tables with foreign key constraints.

        Args:
            table_schemas: Dictionary mapping table names to their schemas
            relationships: List of relationship definitions
                [
                    {
                        "from_table": "orders",
                        "from_column": "customer_id",
                        "to_table": "customers",
                        "to_column": "id",
                        "relationship_type": "many_to_one"  # or "one_to_one", "many_to_many"
                    }
                ]
            row_counts: Dictionary mapping table names to desired row counts

        Returns:
            Dictionary mapping table names to generated DataFrames
        """
        logger.info(f"Generating relational dataset with {len(table_schemas)} tables")

        # Validate relationships
        self._validate_relationships(table_schemas, relationships)

        # Determine generation order (topological sort)
        generation_order = self._get_generation_order(table_schemas, relationships)

        # Generate tables in order
        self.tables = {}
        self.relationships = relationships

        for table_name in generation_order:
            logger.info(f"Generating table: {table_name}")
            schema = table_schemas[table_name]
            num_rows = row_counts.get(table_name, 100)

            # Get foreign key constraints for this table
            fk_constraints = self._get_foreign_keys(table_name, relationships)

            # Generate table data
            df = self._generate_table(table_name, schema, num_rows, fk_constraints)
            self.tables[table_name] = df

        return self.tables

    def _validate_relationships(
        self,
        table_schemas: Dict[str, Dict[str, Any]],
        relationships: List[Dict[str, Any]]
    ) -> None:
        """Validate relationship definitions."""
        for rel in relationships:
            # Check required fields
            required = ["from_table", "from_column", "to_table", "to_column"]
            for field in required:
                if field not in rel:
                    raise DataGenerationError(f"Relationship missing required field: {field}")

            # Check tables exist
            if rel["from_table"] not in table_schemas:
                raise DataGenerationError(f"From table not found: {rel['from_table']}")
            if rel["to_table"] not in table_schemas:
                raise DataGenerationError(f"To table not found: {rel['to_table']}")

    def _get_generation_order(
        self,
        table_schemas: Dict[str, Dict[str, Any]],
        relationships: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Determine table generation order based on dependencies.

        Uses topological sort to ensure parent tables are generated before children.
        """
        # Build dependency graph
        dependencies = {table: set() for table in table_schemas.keys()}

        for rel in relationships:
            # Child depends on parent
            dependencies[rel["from_table"]].add(rel["to_table"])

        # Topological sort using Kahn's algorithm
        in_degree = {table: 0 for table in table_schemas.keys()}
        for table, deps in dependencies.items():
            for dep in deps:
                in_degree[dep] += 1

        queue = [table for table, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            # Sort for deterministic ordering
            queue.sort()
            table = queue.pop(0)
            result.append(table)

            # Remove edges
            for dep in dependencies[table]:
                in_degree[dep] -= 1
                if in_degree[dep] == 0:
                    queue.append(dep)

        if len(result) != len(table_schemas):
            raise DataGenerationError("Circular dependency detected in relationships")

        # Reverse to get parent-first order
        return list(reversed(result))

    def _get_foreign_keys(
        self,
        table_name: str,
        relationships: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Get foreign key constraints for a table."""
        return [
            rel for rel in relationships
            if rel["from_table"] == table_name
        ]

    def _generate_table(
        self,
        table_name: str,
        schema: Dict[str, Any],
        num_rows: int,
        fk_constraints: List[Dict[str, Any]]
    ) -> pd.DataFrame:
        """Generate a single table with foreign key constraints."""
        # Initialize empty DataFrame
        df = pd.DataFrame()

        # Generate each field
        fields = schema.get("fields", [])

        for field in fields:
            field_name = field.get("name")

            # Check if this field is a foreign key
            fk = next(
                (fk for fk in fk_constraints if fk["from_column"] == field_name),
                None
            )

            if fk:
                # Generate foreign key values
                df[field_name] = self._generate_foreign_key_column(
                    num_rows, fk, schema
                )
            else:
                # Generate regular field (placeholder - would use main generator)
                df[field_name] = self._generate_placeholder_column(
                    num_rows, field
                )

        return df

    def _generate_foreign_key_column(
        self,
        num_rows: int,
        fk: Dict[str, Any],
        schema: Dict[str, Any]
    ) -> np.ndarray:
        """Generate foreign key column values."""
        parent_table = fk["to_table"]
        parent_column = fk["to_column"]
        relationship_type = fk.get("relationship_type", "many_to_one")

        # Get parent values
        if parent_table not in self.tables:
            raise DataGenerationError(
                f"Parent table '{parent_table}' must be generated before '{fk['from_table']}'"
            )

        parent_values = self.tables[parent_table][parent_column].values

        if len(parent_values) == 0:
            raise DataGenerationError(f"Parent table '{parent_table}' is empty")

        # Generate based on relationship type
        if relationship_type == "many_to_one":
            # Multiple child records can reference the same parent
            return np.random.choice(parent_values, size=num_rows, replace=True)

        elif relationship_type == "one_to_one":
            # Each child record references a unique parent
            if num_rows > len(parent_values):
                logger.warning(
                    f"One-to-one relationship but child has more rows ({num_rows}) than parent ({len(parent_values)}). "
                    "Reusing parent values."
                )
                return np.random.choice(parent_values, size=num_rows, replace=True)
            else:
                return np.random.choice(parent_values, size=num_rows, replace=False)

        elif relationship_type == "many_to_many":
            # Would typically need a junction table
            logger.warning(
                "Many-to-many relationships require a junction table. "
                "Treating as many-to-one for this column."
            )
            return np.random.choice(parent_values, size=num_rows, replace=True)

        else:
            raise DataGenerationError(f"Unknown relationship type: {relationship_type}")

    def _generate_placeholder_column(
        self,
        num_rows: int,
        field: Dict[str, Any]
    ) -> np.ndarray:
        """
        Generate placeholder column values.

        This is a simplified version - in production, this would use
        the main DataGenerationEngine.
        """
        field_type = field.get("type", "string")

        if field_type in ["integer", "int"]:
            return np.random.randint(1, 10000, size=num_rows)
        elif field_type in ["float", "decimal"]:
            return np.random.uniform(0, 1000, size=num_rows)
        elif field_type == "boolean":
            return np.random.choice([True, False], size=num_rows)
        else:
            # String type
            return np.array([f"value_{i}" for i in range(num_rows)])

    def add_junction_table(
        self,
        table_name: str,
        left_table: str,
        left_column: str,
        right_table: str,
        right_column: str,
        num_relationships: int
    ) -> pd.DataFrame:
        """
        Create a junction table for many-to-many relationships.

        Args:
            table_name: Name of junction table
            left_table: First table in relationship
            left_column: Column from first table
            right_table: Second table in relationship
            right_column: Column from second table
            num_relationships: Number of relationships to create

        Returns:
            Generated junction table DataFrame
        """
        if left_table not in self.tables or right_table not in self.tables:
            raise DataGenerationError("Both tables must exist before creating junction table")

        left_values = self.tables[left_table][left_column].values
        right_values = self.tables[right_table][right_column].values

        # Generate random many-to-many relationships
        left_refs = np.random.choice(left_values, size=num_relationships, replace=True)
        right_refs = np.random.choice(right_values, size=num_relationships, replace=True)

        junction_df = pd.DataFrame({
            f"{left_table}_{left_column}": left_refs,
            f"{right_table}_{right_column}": right_refs
        })

        # Remove duplicates to ensure unique relationships
        junction_df = junction_df.drop_duplicates()

        self.tables[table_name] = junction_df
        return junction_df
