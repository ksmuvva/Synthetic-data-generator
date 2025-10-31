"""
Programmatic data generation example using Claude Agent SDK.

This example shows how to generate data programmatically from
structured requirements without interactive conversation.
"""

import asyncio
from pathlib import Path
from synth_agent.agent import SynthAgentClient
from synth_agent.core.config import AppConfig


async def generate_customer_data():
    """Generate customer data from structured requirements."""
    print("=" * 60)
    print("Programmatic Customer Data Generation")
    print("=" * 60)

    config = AppConfig()

    # Define structured requirements
    requirements = {
        "name": "Customer Database",
        "description": "Customer records for CRM system",
        "fields": [
            {
                "name": "customer_id",
                "type": "uuid",
                "constraints": {"unique": True, "not_null": True},
            },
            {
                "name": "first_name",
                "type": "first_name",
                "constraints": {"not_null": True},
            },
            {
                "name": "last_name",
                "type": "last_name",
                "constraints": {"not_null": True},
            },
            {
                "name": "email",
                "type": "email",
                "constraints": {"unique": True, "not_null": True},
            },
            {
                "name": "phone",
                "type": "phone_number",
                "constraints": {"format": "US"},
            },
            {
                "name": "age",
                "type": "integer",
                "constraints": {"min": 18, "max": 80},
            },
            {
                "name": "registration_date",
                "type": "date",
                "constraints": {"min": "2022-01-01", "max": "2024-12-31"},
            },
        ],
    }

    # Generate data
    async with SynthAgentClient(config=config) as client:
        print("\nGenerating customer data...")

        result = await client.generate_from_requirements(
            requirements=requirements,
            num_rows=500,
            output_format="csv",
            output_path="./output/customers.csv",
        )

        print("\n" + "=" * 60)
        print("Generation completed!")
        print("=" * 60)
        print(f"Result: {result}")


async def generate_sales_data():
    """Generate sales transaction data."""
    print("\n\n" + "=" * 60)
    print("Programmatic Sales Data Generation")
    print("=" * 60)

    config = AppConfig()

    requirements = {
        "name": "Sales Transactions",
        "description": "Sales records for analytics",
        "fields": [
            {
                "name": "transaction_id",
                "type": "uuid",
                "constraints": {"unique": True, "not_null": True},
            },
            {
                "name": "transaction_date",
                "type": "datetime",
                "constraints": {"min": "2024-01-01", "max": "2024-12-31"},
            },
            {
                "name": "product_name",
                "type": "string",
                "constraints": {"not_null": True},
            },
            {
                "name": "category",
                "type": "string",
                "constraints": {
                    "choices": ["Electronics", "Clothing", "Food", "Books", "Home"]
                },
            },
            {
                "name": "quantity",
                "type": "integer",
                "constraints": {"min": 1, "max": 10},
            },
            {
                "name": "unit_price",
                "type": "decimal",
                "constraints": {"min": 5.0, "max": 500.0, "precision": 2},
            },
            {
                "name": "total_amount",
                "type": "decimal",
                "constraints": {"precision": 2},
            },
            {
                "name": "payment_method",
                "type": "string",
                "constraints": {"choices": ["Credit Card", "Debit Card", "PayPal", "Cash"]},
            },
        ],
    }

    async with SynthAgentClient(config=config) as client:
        print("\nGenerating sales data...")

        # Generate with seed for reproducibility
        result = await client.generate_from_requirements(
            requirements=requirements,
            num_rows=1000,
            output_format="json",
            output_path="./output/sales.json",
        )

        print("\n" + "=" * 60)
        print("Generation completed!")
        print("=" * 60)
        print(f"Result: {result}")


async def generate_user_data():
    """Generate user authentication data."""
    print("\n\n" + "=" * 60)
    print("Programmatic User Data Generation")
    print("=" * 60)

    config = AppConfig()

    requirements = {
        "name": "User Authentication",
        "description": "User accounts with authentication details",
        "fields": [
            {
                "name": "user_id",
                "type": "uuid",
                "constraints": {"unique": True, "not_null": True},
            },
            {
                "name": "username",
                "type": "username",
                "constraints": {"unique": True, "not_null": True},
            },
            {
                "name": "email",
                "type": "email",
                "constraints": {"unique": True, "not_null": True},
            },
            {
                "name": "password_hash",
                "type": "string",
                "constraints": {"pattern": "^[a-f0-9]{64}$"},  # SHA256 hash pattern
            },
            {
                "name": "created_at",
                "type": "datetime",
                "constraints": {"not_null": True},
            },
            {
                "name": "last_login",
                "type": "datetime",
            },
            {
                "name": "is_active",
                "type": "boolean",
                "constraints": {"not_null": True},
            },
            {
                "name": "role",
                "type": "string",
                "constraints": {"choices": ["admin", "user", "moderator", "guest"]},
            },
        ],
    }

    async with SynthAgentClient(config=config) as client:
        print("\nGenerating user data...")

        result = await client.generate_from_requirements(
            requirements=requirements,
            num_rows=200,
            output_format="parquet",
            output_path="./output/users.parquet",
        )

        print("\n" + "=" * 60)
        print("Generation completed!")
        print("=" * 60)
        print(f"Result: {result}")


async def main():
    """Run all generation examples."""
    try:
        # Generate different datasets
        await generate_customer_data()
        await generate_sales_data()
        await generate_user_data()

        print("\n\n" + "=" * 60)
        print("All datasets generated successfully!")
        print("=" * 60)
        print("\nGenerated files:")
        print("  - ./output/customers.csv")
        print("  - ./output/sales.json")
        print("  - ./output/users.parquet")

    except Exception as e:
        print(f"\nError generating data: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Create output directory
    Path("./output").mkdir(exist_ok=True)

    # Run examples
    asyncio.run(main())
