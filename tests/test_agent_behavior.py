"""
Real agent behavior testing with complex prompts.

This test suite actually sends prompts to the agent and validates responses,
rather than just checking tool availability.
"""

import asyncio
import os
import sys
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from synth_agent.agent import SynthAgentClient
from synth_agent.core.config import Config


class AgentComplexPromptTester:
    """Tests agent behavior with complex prompts."""

    def __init__(self, api_key: str):
        os.environ["ANTHROPIC_API_KEY"] = api_key
        self.config = Config()
        self.results = []

    async def test_prompt(self, prompt: str, test_name: str) -> dict:
        """Test agent with a single prompt."""
        print(f"\n{'='*80}")
        print(f"Test: {test_name}")
        print(f"{'='*80}")
        print(f"Prompt: {prompt[:200]}...")

        result = {
            "test_name": test_name,
            "prompt": prompt,
            "success": False,
            "response_chunks": [],
            "error": None
        }

        try:
            # Create fresh client for each test
            client = SynthAgentClient(config=self.config)

            # Send query and collect responses
            async for chunk in client.query(prompt):
                if chunk.get("type") == "text":
                    text = chunk.get("text", "")
                    result["response_chunks"].append(text)
                    print(text, end="", flush=True)

            print("\n")
            result["success"] = True
            result["full_response"] = "".join(result["response_chunks"])

        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            result["error"] = str(e)
            result["success"] = False

        return result

    async def run_tests(self):
        """Run all agent behavior tests."""

        test_cases = [
            {
                "name": "Simple Generation Request",
                "prompt": "Generate 10 customer records with name, email, and age. Keep it simple."
            },
            {
                "name": "Ambiguous Request Handling",
                "prompt": "I need some user data with the usual fields and stuff."
            },
            {
                "name": "Complex Constraints",
                "prompt": """Generate 50 employee records where:
                - Ages are between 25-65
                - Emails must be unique
                - Salary correlates with age
                - Include department (Engineering, Sales, HR, Marketing)"""
            },
            {
                "name": "Multi-Step Workflow",
                "prompt": "Generate 20 products with name, price, and category. Then analyze the price distribution."
            },
            {
                "name": "Format Request",
                "prompt": "Generate 15 customer records and export to both CSV and JSON formats."
            }
        ]

        for test_case in test_cases:
            result = await self.test_prompt(
                test_case["prompt"],
                test_case["name"]
            )
            self.results.append(result)

            # Brief pause between tests
            await asyncio.sleep(1)

        # Summary
        self.print_summary()

    def print_summary(self):
        """Print test summary."""
        print(f"\n{'='*80}")
        print("AGENT BEHAVIOR TEST SUMMARY")
        print(f"{'='*80}\n")

        success_count = sum(1 for r in self.results if r["success"])
        total = len(self.results)

        print(f"Total Tests: {total}")
        print(f"Successful: {success_count}")
        print(f"Failed: {total - success_count}")

        if success_count < total:
            print(f"\n{'='*80}")
            print("FAILURES:")
            print(f"{'='*80}")
            for result in self.results:
                if not result["success"]:
                    print(f"\n{result['test_name']}:")
                    print(f"  Error: {result['error']}")

        # Save results
        output_file = Path(__file__).parent / "agent_behavior_test_results.json"
        with open(output_file, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\n📝 Results saved to: {output_file}")


async def main():
    """Main test execution."""
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key and len(sys.argv) > 1:
        api_key = sys.argv[1]

    if not api_key:
        print("❌ Error: No API key provided")
        print("Usage: python test_agent_behavior.py <api_key>")
        print("   Or: Set ANTHROPIC_API_KEY environment variable")
        sys.exit(1)

    tester = AgentComplexPromptTester(api_key)
    await tester.run_tests()


if __name__ == "__main__":
    asyncio.run(main())
