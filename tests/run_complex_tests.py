"""
Standalone test runner for complex agent prompts without conftest dependencies.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import tests from test_agent_complex_prompts
from test_agent_complex_prompts import (
    TestComplexHumanLikePrompts,
    TestComplexWorkflowScenarios,
    TestErrorHandlingComplexPrompts,
    TestReasoningStrategySelection,
    TestStateManagementComplexScenarios
)


async def run_all_tests():
    """Run all complex prompt tests."""
    test_results = {
        "passed": 0,
        "failed": 0,
        "errors": []
    }

    test_classes = [
        TestComplexHumanLikePrompts,
        TestComplexWorkflowScenarios,
        TestErrorHandlingComplexPrompts,
        TestReasoningStrategySelection,
        TestStateManagementComplexScenarios
    ]

    for test_class in test_classes:
        print(f"\n{'='*80}")
        print(f"Running: {test_class.__name__}")
        print(f"{'='*80}\n")

        # Get all test methods
        test_methods = [
            method for method in dir(test_class)
            if method.startswith("test_") and callable(getattr(test_class, method))
        ]

        for method_name in test_methods:
            try:
                print(f"  Running {method_name}...", end=" ")
                instance = test_class()
                test_method = getattr(instance, method_name)

                # Run async or sync test
                if asyncio.iscoroutinefunction(test_method):
                    await test_method()
                else:
                    test_method()

                print("✓ PASSED")
                test_results["passed"] += 1

            except Exception as e:
                print(f"✗ FAILED: {str(e)}")
                test_results["failed"] += 1
                test_results["errors"].append({
                    "test": f"{test_class.__name__}.{method_name}",
                    "error": str(e)
                })

    # Print summary
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}")
    print(f"Passed: {test_results['passed']}")
    print(f"Failed: {test_results['failed']}")
    print(f"Total: {test_results['passed'] + test_results['failed']}")

    if test_results["errors"]:
        print(f"\n{'='*80}")
        print("FAILURES:")
        print(f"{'='*80}")
        for error in test_results["errors"]:
            print(f"\n{error['test']}:")
            print(f"  {error['error']}")

    return test_results


if __name__ == "__main__":
    results = asyncio.run(run_all_tests())
    sys.exit(0 if results["failed"] == 0 else 1)
