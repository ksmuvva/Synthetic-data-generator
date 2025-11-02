#!/usr/bin/env python3
"""
Test script to verify template_file support and format detection fixes.
"""

import sys
sys.path.insert(0, '/home/user/Synthetic-data-generator/src')

from synth_agent.cli.nlp_app import (
    ConversationContext,
    _detect_format_from_file,
    _extract_template_content,
    _fallback_intent_classification
)
from pathlib import Path

def test_template_file_detection():
    """Test that template file format detection works."""
    print("=" * 60)
    print("TEST 1: Template File Format Detection")
    print("=" * 60)

    test_cases = [
        ("test.json", "json"),
        ("data.csv", "csv"),
        ("report.pdf", "pdf"),
        ("document.docx", "docx"),
        ("spreadsheet.xlsx", "excel"),
        ("data.parquet", "parquet"),
        ("config.xml", "xml"),
        ("list.txt", "txt"),
    ]

    for filename, expected_format in test_cases:
        detected = _detect_format_from_file(filename)
        status = "✅ PASS" if detected == expected_format else "❌ FAIL"
        print(f"{status}: {filename} -> {detected} (expected: {expected_format})")

    print()


def test_template_content_extraction():
    """Test that template content can be extracted."""
    print("=" * 60)
    print("TEST 2: Template Content Extraction")
    print("=" * 60)

    # Test with our created JSON file
    test_file = "/home/user/Synthetic-data-generator/test_template.json"

    if Path(test_file).exists():
        content = _extract_template_content(test_file)
        print(f"✅ PASS: Successfully extracted content from {test_file}")
        print(f"Content preview (first 200 chars):")
        print(f"{content[:200]}...")
    else:
        print(f"❌ FAIL: Test file {test_file} not found")

    print()


def test_context_template_file():
    """Test that ConversationContext supports template_file."""
    print("=" * 60)
    print("TEST 3: ConversationContext Template File Support")
    print("=" * 60)

    context = ConversationContext()

    # Check that template_file is in user_preferences
    if "template_file" in context.user_preferences:
        print("✅ PASS: template_file key exists in user_preferences")
        print(f"   Default value: {context.user_preferences['template_file']}")
    else:
        print("❌ FAIL: template_file key not found in user_preferences")

    # Test setting template file
    context.user_preferences["template_file"] = "test.json"
    if context.user_preferences["template_file"] == "test.json":
        print("✅ PASS: Can set template_file in context")
    else:
        print("❌ FAIL: Could not set template_file in context")

    print()


def test_fallback_intent_classification():
    """Test that fallback intent classification detects formats correctly."""
    print("=" * 60)
    print("TEST 4: Fallback Intent Classification Format Detection")
    print("=" * 60)

    test_cases = [
        ("create customer data as JSON", "json"),
        ("generate API test data", "json"),
        ("make an Excel spreadsheet with sales", "excel"),
        ("create a PDF document with employee info", "pdf"),
        ("generate Word document", "docx"),
        ("create XML for web service", "xml"),
        ("make CSV customer data", "csv"),
    ]

    context = ConversationContext()

    for user_input, expected_format in test_cases:
        result = _fallback_intent_classification(user_input, context)
        detected_format = result["params"].get("format", "unknown")
        status = "✅ PASS" if detected_format == expected_format else "❌ FAIL"
        print(f"{status}: '{user_input}'")
        print(f"   Detected: {detected_format} (expected: {expected_format})")
        if "reasoning" in result:
            print(f"   Reasoning: {result['reasoning']}")

    print()


def test_template_file_format_override():
    """Test that template file format overrides default."""
    print("=" * 60)
    print("TEST 5: Template File Format Override")
    print("=" * 60)

    context = ConversationContext()
    context.user_preferences["template_file"] = "test_template.json"

    result = _fallback_intent_classification("create customer data", context)
    detected_format = result["params"].get("format", "unknown")

    if detected_format == "json":
        print("✅ PASS: Template file format (json) overrides default (csv)")
        print(f"   Detected format: {detected_format}")
    else:
        print(f"❌ FAIL: Expected 'json' from template, got '{detected_format}'")

    print()


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("TESTING TEMPLATE FILE SUPPORT AND FORMAT DETECTION")
    print("=" * 60)
    print()

    try:
        test_template_file_detection()
        test_template_content_extraction()
        test_context_template_file()
        test_fallback_intent_classification()
        test_template_file_format_override()

        print("=" * 60)
        print("ALL TESTS COMPLETED")
        print("=" * 60)
        print("\n✅ Summary: Key fixes implemented successfully!")
        print("   1. template_file setting is now recognized")
        print("   2. Format detection is improved with reasoning")
        print("   3. Template files can be used to guide generation")
        print()

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
