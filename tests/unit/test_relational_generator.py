"""Unit tests for relational data generator."""

import pytest
import pandas as pd
import numpy as np

from synth_agent.core.exceptions import DataGenerationError
from synth_agent.generation.relational import RelationalDataGenerator


class TestRelationalDataGenerator:
    """Test relational data generator."""

    def test_simple_one_to_many(self):
        """Test simple one-to-many relationship."""
        generator = RelationalDataGenerator()

        # Define schemas
        table_schemas = {
            "customers": {
                "fields": [
                    {"name": "id", "type": "integer"},
                    {"name": "name", "type": "string"}
                ]
            },
            "orders": {
                "fields": [
                    {"name": "id", "type": "integer"},
                    {"name": "customer_id", "type": "integer"},
                    {"name": "amount", "type": "float"}
                ]
            }
        }

        # Define relationship
        relationships = [
            {
                "from_table": "orders",
                "from_column": "customer_id",
                "to_table": "customers",
                "to_column": "id",
                "relationship_type": "many_to_one"
            }
        ]

        # Generate
        row_counts = {"customers": 10, "orders": 50}
        tables = generator.generate_relational_dataset(
            table_schemas, relationships, row_counts
        )

        # Verify
        assert "customers" in tables
        assert "orders" in tables
        assert len(tables["customers"]) == 10
        assert len(tables["orders"]) == 50

        # Verify foreign key integrity
        customer_ids = set(tables["customers"]["id"])
        order_customer_ids = set(tables["orders"]["customer_id"])
        assert order_customer_ids.issubset(customer_ids)

    def test_generation_order(self):
        """Test tables are generated in correct dependency order."""
        generator = RelationalDataGenerator()

        # Define three-level hierarchy
        table_schemas = {
            "countries": {
                "fields": [{"name": "id", "type": "integer"}]
            },
            "cities": {
                "fields": [
                    {"name": "id", "type": "integer"},
                    {"name": "country_id", "type": "integer"}
                ]
            },
            "stores": {
                "fields": [
                    {"name": "id", "type": "integer"},
                    {"name": "city_id", "type": "integer"}
                ]
            }
        }

        relationships = [
            {
                "from_table": "cities",
                "from_column": "country_id",
                "to_table": "countries",
                "to_column": "id",
                "relationship_type": "many_to_one"
            },
            {
                "from_table": "stores",
                "from_column": "city_id",
                "to_table": "cities",
                "to_column": "id",
                "relationship_type": "many_to_one"
            }
        ]

        # Get generation order
        order = generator._get_generation_order(table_schemas, relationships)

        # Verify countries -> cities -> stores
        assert order.index("countries") < order.index("cities")
        assert order.index("cities") < order.index("stores")

    def test_circular_dependency_detection(self):
        """Test detection of circular dependencies."""
        generator = RelationalDataGenerator()

        table_schemas = {
            "table_a": {"fields": [{"name": "id", "type": "integer"}]},
            "table_b": {"fields": [{"name": "id", "type": "integer"}]}
        }

        # Create circular dependency
        relationships = [
            {
                "from_table": "table_a",
                "from_column": "b_id",
                "to_table": "table_b",
                "to_column": "id",
                "relationship_type": "many_to_one"
            },
            {
                "from_table": "table_b",
                "from_column": "a_id",
                "to_table": "table_a",
                "to_column": "id",
                "relationship_type": "many_to_one"
            }
        ]

        with pytest.raises(DataGenerationError, match="Circular dependency"):
            generator._get_generation_order(table_schemas, relationships)

    def test_one_to_one_relationship(self):
        """Test one-to-one relationship."""
        generator = RelationalDataGenerator()

        table_schemas = {
            "users": {
                "fields": [{"name": "id", "type": "integer"}]
            },
            "profiles": {
                "fields": [
                    {"name": "id", "type": "integer"},
                    {"name": "user_id", "type": "integer"}
                ]
            }
        }

        relationships = [
            {
                "from_table": "profiles",
                "from_column": "user_id",
                "to_table": "users",
                "to_column": "id",
                "relationship_type": "one_to_one"
            }
        ]

        row_counts = {"users": 10, "profiles": 10}
        tables = generator.generate_relational_dataset(
            table_schemas, relationships, row_counts
        )

        # Verify one-to-one (all user_ids should be unique)
        assert len(tables["profiles"]["user_id"].unique()) == len(tables["profiles"])

    def test_junction_table_creation(self):
        """Test many-to-many junction table creation."""
        generator = RelationalDataGenerator()

        # First create base tables
        table_schemas = {
            "students": {
                "fields": [{"name": "id", "type": "integer"}]
            },
            "courses": {
                "fields": [{"name": "id", "type": "integer"}]
            }
        }

        row_counts = {"students": 20, "courses": 10}
        tables = generator.generate_relational_dataset(
            table_schemas, [], row_counts
        )

        # Create junction table
        junction = generator.add_junction_table(
            table_name="enrollments",
            left_table="students",
            left_column="id",
            right_table="courses",
            right_column="id",
            num_relationships=50
        )

        # Verify junction table
        assert len(junction) <= 50  # May be less due to duplicate removal
        assert "students_id" in junction.columns
        assert "courses_id" in junction.columns

        # Verify referential integrity
        student_ids = set(tables["students"]["id"])
        course_ids = set(tables["courses"]["id"])
        assert set(junction["students_id"]).issubset(student_ids)
        assert set(junction["courses_id"]).issubset(course_ids)

    def test_missing_relationship_fields(self):
        """Test validation of relationship definitions."""
        generator = RelationalDataGenerator()

        table_schemas = {"table_a": {"fields": []}, "table_b": {"fields": []}}

        # Missing required field
        relationships = [
            {
                "from_table": "table_a",
                "from_column": "id",
                # Missing to_table and to_column
            }
        ]

        with pytest.raises(DataGenerationError, match="missing required field"):
            generator._validate_relationships(table_schemas, relationships)

    def test_nonexistent_table_in_relationship(self):
        """Test validation fails for nonexistent tables."""
        generator = RelationalDataGenerator()

        table_schemas = {"table_a": {"fields": []}}

        relationships = [
            {
                "from_table": "table_a",
                "from_column": "id",
                "to_table": "nonexistent_table",
                "to_column": "id"
            }
        ]

        with pytest.raises(DataGenerationError, match="not found"):
            generator._validate_relationships(table_schemas, relationships)
