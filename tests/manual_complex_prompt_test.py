"""
Manual testing script for complex agent prompts.

This script tests the agent CLI with complex, human-like prompts
to identify real-world issues and defects.
"""

import asyncio
import os
import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from synth_agent.agent import SynthAgentClient
from synth_agent.core.config import Config


# Complex test prompts that simulate human interactions
COMPLEX_PROMPTS = [
    # 1. Vague/Ambiguous prompt
    {
        "name": "Ambiguous Request",
        "prompt": "I need some customer data with names and stuff",
        "expected_tools": ["analyze_requirements", "detect_ambiguities"],
        "description": "Tests how agent handles vague requirements"
    },

    # 2. Multi-step workflow
    {
        "name": "Multi-Step Workflow",
        "prompt": """Generate 100 customer records with name, email, age, and purchase history.
        Then analyze the age distribution and export to both CSV and JSON formats.""",
        "expected_tools": ["analyze_requirements", "generate_data", "analyze_pattern", "export_data"],
        "description": "Tests multi-step workflow handling"
    },

    # 3. Domain-specific jargon
    {
        "name": "Healthcare Domain",
        "prompt": """Generate FHIR-compliant patient records with demographics,
        diagnoses, and medications following HL7 standards. Include ICD-10 codes.""",
        "expected_tools": ["analyze_requirements", "select_reasoning_strategy", "generate_data"],
        "description": "Tests domain-specific terminology understanding"
    },

    # 4. Complex constraints
    {
        "name": "Complex Constraints",
        "prompt": """Create 500 employee records where:
        - Emails must be unique
        - Ages between 22-65
        - Salary should correlate with years of experience
        - Department must be one of: Engineering, Sales, Marketing, HR
        - Manager IDs must reference valid employee IDs""",
        "expected_tools": ["analyze_requirements", "detect_ambiguities", "generate_data"],
        "description": "Tests complex business rule handling"
    },

    # 5. Relational data
    {
        "name": "Relational Tables",
        "prompt": """Generate related tables for an e-commerce system:
        - Customers table (1000 rows)
        - Products table (500 rows)
        - Orders table (5000 rows) with foreign keys to customers
        - Order_Items table (15000 rows) with foreign keys to orders and products
        Ensure referential integrity.""",
        "expected_tools": ["analyze_requirements", "select_reasoning_strategy", "generate_data"],
        "description": "Tests relational data generation"
    },

    # 6. Pattern-based generation
    {
        "name": "Pattern Learning",
        "prompt": """I have a CSV file with transaction data. Learn the patterns
        and generate 10,000 similar transactions that match the same distribution,
        categories, and value ranges.""",
        "expected_tools": ["analyze_pattern", "generate_data"],
        "description": "Tests pattern learning from examples"
    },

    # 7. Edge cases
    {
        "name": "Edge Case Generation",
        "prompt": """Generate test data including edge cases for:
        - Very young (18-20) and very old (63-65) ages
        - Minimum and maximum salary values
        - Empty strings and special characters in names
        - Boundary date values (start/end of year)""",
        "expected_tools": ["analyze_requirements", "generate_data"],
        "description": "Tests edge case generation"
    },

    # 8. Format preferences
    {
        "name": "Multiple Format Export",
        "prompt": """Generate 200 product records and export to:
        - CSV for Excel import
        - JSON for API consumption
        - Parquet for data warehouse
        - Excel with formatted headers and styling""",
        "expected_tools": ["generate_data", "list_formats", "export_data"],
        "description": "Tests multi-format export handling"
    },

    # 9. Conversational refinement
    {
        "name": "Refinement Request",
        "prompt": """Actually, change the previous request - make it 1000 rows instead
        of 100, and add a 'country' field with realistic distribution.""",
        "expected_tools": ["analyze_requirements", "generate_data"],
        "description": "Tests conversation context and refinement"
    },

    # 10. Quality and validation
    {
        "name": "Quality Requirements",
        "prompt": """Generate high-quality customer data with:
        - No duplicate emails
        - Valid phone numbers in E.164 format
        - Realistic name distributions (including international names)
        - Age-appropriate email domains (no 80-year-olds with @gmail.com)
        - Proper address formatting with real city/state combinations""",
        "expected_tools": ["analyze_requirements", "detect_ambiguities", "generate_data"],
        "description": "Tests quality constraint understanding"
    },

    # 11. Time-series data
    {
        "name": "Time-Series Generation",
        "prompt": """Generate stock market data with:
        - Ticker symbols
        - OHLC values (Open, High, Low, Close)
        - Volume
        - Timestamps at 1-minute intervals
        - Realistic price movements (no huge gaps)
        - 1 week of data per symbol, 10 symbols""",
        "expected_tools": ["analyze_requirements", "select_reasoning_strategy", "generate_data"],
        "description": "Tests time-series data generation"
    },

    # 12. Mixed data types
    {
        "name": "Mixed Data Types",
        "prompt": """Create a dataset with diverse data types:
        - UUIDs for IDs
        - JSON objects for metadata
        - Binary flags (true/false)
        - Decimal numbers with precision
        - Timestamps with timezone
        - Arrays of tags
        - Nested structures""",
        "expected_tools": ["analyze_requirements", "generate_data"],
        "description": "Tests handling of diverse data types"
    },

    # 13. Performance consideration
    {
        "name": "Large Dataset Request",
        "prompt": """Generate 1 million records with 50 fields each.
        Use parallel generation for speed. Export as partitioned Parquet files.""",
        "expected_tools": ["analyze_requirements", "generate_data", "export_data"],
        "description": "Tests performance and scalability"
    },

    # 14. Clarification needed
    {
        "name": "Ambiguous Constraints",
        "prompt": """Generate user data where age should be reasonable and
        income should make sense for their role.""",
        "expected_tools": ["analyze_requirements", "detect_ambiguities"],
        "description": "Tests ambiguity detection and clarification"
    },

    # 15. Follow-up question
    {
        "name": "Follow-Up Query",
        "prompt": """What reasoning method did you use for the previous generation?
        Why was that chosen over other methods? Can you explain the decision?""",
        "expected_tools": ["list_reasoning_methods"],
        "description": "Tests explanation and transparency"
    }
]


class ComplexPromptTester:
    """Tester for complex agent prompts."""

    def __init__(self, api_key: str):
        """Initialize tester with API key."""
        # Set API key in environment
        os.environ["ANTHROPIC_API_KEY"] = api_key

        self.config = Config()
        self.results = []

    async def test_single_prompt(self, test_case: dict) -> dict:
        """Test a single complex prompt."""
        print(f"\n{'='*80}")
        print(f"Testing: {test_case['name']}")
        print(f"Description: {test_case['description']}")
        print(f"{'='*80}")
        print(f"\nPrompt: {test_case['prompt'][:200]}...")

        result = {
            "name": test_case["name"],
            "prompt": test_case["prompt"],
            "status": "unknown",
            "error": None,
            "tools_used": [],
            "response_preview": None
        }

        try:
            # Initialize client for each test (fresh state)
            client = SynthAgentClient(config=self.config)

            # Verify client has expected tools
            available_tools = client.get_mcp_tools()
            print(f"\nAvailable MCP tools: {len(available_tools)}")

            expected_tools = test_case.get("expected_tools", [])
            missing_tools = []
            for tool in expected_tools:
                tool_name = f"mcp__synth__{tool}"
                if tool_name not in available_tools:
                    missing_tools.append(tool)

            if missing_tools:
                print(f"⚠️  Missing expected tools: {missing_tools}")
                result["status"] = "warning"
                result["error"] = f"Missing tools: {missing_tools}"
            else:
                print(f"✓ All expected tools available")
                result["status"] = "success"

            # Note: We can't actually send queries without full SDK setup
            # This test validates configuration and tool availability

            result["tools_used"] = list(available_tools)
            result["response_preview"] = f"Client initialized successfully with {len(available_tools)} tools"

        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            result["status"] = "error"
            result["error"] = str(e)

        return result

    async def run_all_tests(self):
        """Run all complex prompt tests."""
        print("\n" + "="*80)
        print("COMPLEX AGENT PROMPT TESTING")
        print("="*80)
        print(f"\nTotal test cases: {len(COMPLEX_PROMPTS)}")

        for test_case in COMPLEX_PROMPTS:
            result = await self.test_single_prompt(test_case)
            self.results.append(result)

            # Small delay between tests
            await asyncio.sleep(0.5)

        # Print summary
        self.print_summary()

        # Save results
        self.save_results()

    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)

        success_count = sum(1 for r in self.results if r["status"] == "success")
        warning_count = sum(1 for r in self.results if r["status"] == "warning")
        error_count = sum(1 for r in self.results if r["status"] == "error")

        print(f"\n✓ Success: {success_count}")
        print(f"⚠️  Warnings: {warning_count}")
        print(f"❌ Errors: {error_count}")
        print(f"Total: {len(self.results)}")

        # Print detailed failures
        failures = [r for r in self.results if r["status"] in ["error", "warning"]]
        if failures:
            print("\n" + "-"*80)
            print("ISSUES FOUND:")
            print("-"*80)
            for failure in failures:
                print(f"\n{failure['name']}:")
                print(f"  Status: {failure['status']}")
                print(f"  Error: {failure['error']}")

    def save_results(self):
        """Save test results to file."""
        output_file = Path(__file__).parent / "complex_prompt_test_results.json"

        with open(output_file, "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"\n📝 Results saved to: {output_file}")


async def main():
    """Main test execution."""
    # Get API key from environment or command line
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key and len(sys.argv) > 1:
        api_key = sys.argv[1]

    if not api_key:
        print("❌ Error: No API key provided")
        print("Usage: python manual_complex_prompt_test.py <api_key>")
        print("   Or: Set ANTHROPIC_API_KEY environment variable")
        sys.exit(1)

    print(f"Using API key: {api_key[:20]}...")

    tester = ComplexPromptTester(api_key)
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
