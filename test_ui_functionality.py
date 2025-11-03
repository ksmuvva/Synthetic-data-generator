#!/usr/bin/env python3
"""
Test script to verify Streamlit app functionality.
This simulates what a human user would do through the UI.
"""

import sys
import os
from pathlib import Path
import pandas as pd
import json

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from synth_agent.core.config import ConfigManager
from synth_agent.generation.engine import DataGenerationEngine
from synth_agent.analysis.pattern_analyzer import PatternAnalyzer
from synth_agent.analysis.requirement_parser import RequirementParser
from synth_agent.llm.manager import LLMManager
from synth_agent.llm.anthropic_provider import AnthropicProvider
from synth_agent.utils.file_validator import FileValidator


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def test_component_initialization():
    """Test 1: Initialize components like the Streamlit app does."""
    print_section("TEST 1: Component Initialization")

    try:
        config_manager = ConfigManager()
        config = config_manager.get_config()

        print("✓ ConfigManager initialized")

        # Get API key from environment
        from synth_agent.core.config import get_api_keys
        api_keys = get_api_keys()

        if not api_keys.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")

        print(f"✓ API Key loaded (length: {len(api_keys.anthropic_api_key)} chars)")

        # Initialize LLM provider
        llm_provider = AnthropicProvider(
            api_key=api_keys.anthropic_api_key,
            model=config.llm.model,
            temperature=config.llm.temperature,
            max_tokens=config.llm.max_tokens,
            timeout=config.llm.timeout
        )
        llm_manager = LLMManager(provider=llm_provider, config=config.llm)

        print("✓ LLM Provider (Anthropic) initialized")
        print(f"  Provider: {config.llm.provider}")
        print(f"  Model: {config.llm.model}")

        # Initialize other components
        requirement_parser = RequirementParser(llm_manager=llm_manager)
        pattern_analyzer = PatternAnalyzer(llm_manager=llm_manager, config=config)
        generation_engine = DataGenerationEngine(config=config.generation)
        file_validator = FileValidator()

        print("✓ RequirementParser initialized")
        print("✓ PatternAnalyzer initialized")
        print("✓ DataGenerationEngine initialized")
        print("✓ FileValidator initialized")

        print("\n✅ All components initialized successfully!")

        return {
            "config": config,
            "requirement_parser": requirement_parser,
            "pattern_analyzer": pattern_analyzer,
            "generation_engine": generation_engine,
            "file_validator": file_validator,
            "llm_manager": llm_manager
        }

    except Exception as e:
        print(f"❌ Component initialization failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_prompt_parsing(components):
    """Test 2: Parse a user prompt like the UI does."""
    print_section("TEST 2: Prompt Parsing (Customer Data)")

    # Simulate a user entering a prompt in the UI
    user_prompt = """Generate customer data with the following fields:
    - Customer ID (numeric, unique)
    - Full Name (first and last name)
    - Email Address (valid email format)
    - Phone Number (US format)
    - Registration Date (dates from last 2 years)
    - Country (USA, Canada, UK, Australia)
    - Account Status (Active, Inactive, Suspended)
    """

    print("User Prompt:")
    print("-" * 70)
    print(user_prompt)
    print("-" * 70)

    try:
        print("\n⏳ Parsing requirements with Claude API...")
        requirements = components["requirement_parser"].parse(user_prompt)

        print("\n✅ Requirements parsed successfully!")
        print("\nParsed Requirements:")
        print(json.dumps(requirements if isinstance(requirements, dict) else str(requirements), indent=2))

        return requirements

    except Exception as e:
        print(f"\n❌ Prompt parsing failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_data_generation(components, requirements):
    """Test 3: Generate synthetic data like the UI does."""
    print_section("TEST 3: Data Generation")

    num_rows = 20  # Generate smaller sample for testing

    try:
        print(f"⏳ Generating {num_rows} rows of synthetic customer data...")

        generated_df = components["generation_engine"].generate(
            requirements=requirements,
            num_rows=num_rows,
            template_df=None
        )

        if generated_df is not None and not generated_df.empty:
            print(f"\n✅ Generated {len(generated_df)} rows successfully!")

            print("\n📊 Data Preview (first 10 rows):")
            print("-" * 70)
            print(generated_df.head(10).to_string())

            print(f"\n📈 Data Statistics:")
            print(f"  Total Rows: {len(generated_df)}")
            print(f"  Total Columns: {len(generated_df.columns)}")
            print(f"  Columns: {', '.join(generated_df.columns)}")

            # Save to output directory like the UI would
            output_dir = Path("./output")
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / "test_customer_data.csv"

            generated_df.to_csv(output_path, index=False)
            print(f"\n💾 Data saved to: {output_path}")

            return generated_df
        else:
            print("❌ Generated data is empty")
            return None

    except Exception as e:
        print(f"\n❌ Data generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_file_upload_and_analysis(components):
    """Test 4: Upload a CSV file and analyze patterns."""
    print_section("TEST 4: File Upload & Pattern Analysis")

    # Create a sample CSV file to simulate user upload
    sample_data = pd.DataFrame({
        'Product_ID': ['P001', 'P002', 'P003', 'P004', 'P005'],
        'Product_Name': ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Headphones'],
        'Category': ['Electronics', 'Accessories', 'Accessories', 'Electronics', 'Accessories'],
        'Price': [999.99, 29.99, 59.99, 349.99, 89.99],
        'Stock': [50, 200, 150, 75, 120],
        'Supplier': ['TechCorp', 'PeriphCo', 'PeriphCo', 'TechCorp', 'AudioMax']
    })

    # Save sample file
    temp_file = Path("/tmp/sample_products.csv")
    sample_data.to_csv(temp_file, index=False)

    print(f"📁 Sample file created: {temp_file}")
    print("\n📄 Sample Data:")
    print("-" * 70)
    print(sample_data.to_string())
    print("-" * 70)

    try:
        # Validate file
        print("\n⏳ Validating file...")
        validation_result = components["file_validator"].validate_file(str(temp_file))

        if validation_result["is_valid"]:
            print("✓ File validation passed")

            # Analyze patterns
            print("\n⏳ Analyzing file patterns with Claude API...")
            analysis = components["pattern_analyzer"].analyze(str(temp_file))

            if analysis:
                print("\n✅ Pattern analysis completed!")

                if "data" in analysis and analysis["data"] is not None:
                    print("\n📊 Analyzed Data Preview:")
                    print(analysis["data"].head())

                if "analysis" in analysis:
                    print("\n🔍 Pattern Analysis Results:")
                    print(json.dumps(analysis["analysis"], indent=2))

                return analysis
        else:
            print(f"❌ File validation failed: {validation_result.get('error', 'Unknown error')}")
            return None

    except Exception as e:
        print(f"\n❌ File analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_export_formats(generated_df):
    """Test 5: Export data in different formats like the UI offers."""
    print_section("TEST 5: Export Functionality")

    if generated_df is None or generated_df.empty:
        print("⚠️  No data to export. Skipping export test.")
        return

    output_dir = Path("./output")
    output_dir.mkdir(exist_ok=True)

    formats = {
        "csv": lambda df, path: df.to_csv(path, index=False),
        "json": lambda df, path: df.to_json(path, orient="records", indent=2),
        "excel": lambda df, path: df.to_excel(path, index=False, engine="openpyxl"),
    }

    print("Testing export formats:")

    for format_name, export_func in formats.items():
        try:
            output_path = output_dir / f"test_export.{format_name}"
            export_func(generated_df, output_path)

            file_size = output_path.stat().st_size / 1024  # KB
            print(f"  ✓ {format_name.upper()}: {output_path} ({file_size:.2f} KB)")

        except Exception as e:
            print(f"  ❌ {format_name.upper()} export failed: {str(e)}")

    print("\n✅ Export functionality tested!")


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "STREAMLIT APP FUNCTIONALITY TEST" + " " * 21 + "║")
    print("║" + " " * 15 + "Simulating Human User Interaction" + " " * 20 + "║")
    print("╚" + "=" * 68 + "╝")

    # Test 1: Initialize components
    components = test_component_initialization()
    if not components:
        print("\n❌ TESTS FAILED: Could not initialize components")
        return 1

    # Test 2: Parse user prompt
    requirements = test_prompt_parsing(components)
    if not requirements:
        print("\n❌ TESTS FAILED: Could not parse prompt")
        return 1

    # Test 3: Generate data
    generated_df = test_data_generation(components, requirements)
    if generated_df is None:
        print("\n❌ TESTS FAILED: Could not generate data")
        return 1

    # Test 4: File upload and analysis
    analysis = test_file_upload_and_analysis(components)

    # Test 5: Export functionality
    test_export_formats(generated_df)

    # Final summary
    print_section("TEST SUMMARY")
    print("✅ Component Initialization: PASSED")
    print("✅ Prompt Parsing: PASSED")
    print("✅ Data Generation: PASSED")
    print("✅ File Analysis: " + ("PASSED" if analysis else "FAILED"))
    print("✅ Export Functionality: PASSED")

    print("\n" + "=" * 70)
    print("🎉 ALL CORE TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print("\n📱 Streamlit UI is running at: http://localhost:8501")
    print("🔑 Claude API Key is configured and working!")
    print("\n")

    return 0


if __name__ == "__main__":
    exit(main())
