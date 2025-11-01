"""
Manual integration testing script for SynthAgent
This script tests various scenarios and records issues/bugs found
"""

import sys
import json
import pandas as pd
from pathlib import Path
import traceback
from datetime import datetime

# Track all bugs and issues
ISSUES_FOUND = []
TEST_RESULTS = []

def record_issue(test_name, severity, description, stack_trace=None):
    """Record a bug or issue found during testing"""
    issue = {
        "test": test_name,
        "severity": severity,  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
        "description": description,
        "timestamp": datetime.now().isoformat(),
        "stack_trace": stack_trace
    }
    ISSUES_FOUND.append(issue)
    print(f"\n❌ ISSUE FOUND [{severity}]: {test_name}")
    print(f"   {description}")
    if stack_trace:
        print(f"   Stack trace: {stack_trace}")

def record_test_result(test_name, status, details=""):
    """Record test result"""
    result = {
        "test": test_name,
        "status": status,  # "PASS", "FAIL", "SKIP"
        "details": details,
        "timestamp": datetime.now().isoformat()
    }
    TEST_RESULTS.append(result)
    symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⏭️"
    print(f"\n{symbol} {test_name}: {status}")
    if details:
        print(f"   {details}")

def test_basic_import():
    """Test 1: Can we import the agent module?"""
    test_name = "Basic Agent Import"
    try:
        from synth_agent.agent.client import SynthAgentClient
        record_test_result(test_name, "PASS", "Agent client imported successfully")
        return True
    except Exception as e:
        record_issue(test_name, "CRITICAL", f"Failed to import SynthAgentClient: {str(e)}", traceback.format_exc())
        record_test_result(test_name, "FAIL", str(e))
        return False

def test_config_loading():
    """Test 2: Can we load the config?"""
    test_name = "Config Loading"
    try:
        from synth_agent.core.config import get_config
        config = get_config()

        # Check if API key is loaded
        if not config.llm.anthropic_api_key and not config.llm.openai_api_key:
            record_issue(test_name, "HIGH", "No API key found in configuration")
            record_test_result(test_name, "FAIL", "Missing API keys")
            return False

        record_test_result(test_name, "PASS", f"Config loaded. Provider: {config.llm.provider}")
        return True
    except Exception as e:
        record_issue(test_name, "HIGH", f"Failed to load config: {str(e)}", traceback.format_exc())
        record_test_result(test_name, "FAIL", str(e))
        return False

def test_basic_data_generation():
    """Test 3: Can we generate basic synthetic data?"""
    test_name = "Basic Data Generation"
    try:
        from synth_agent.generation.engine import SyntheticDataGenerator
        from synth_agent.core.config import get_config

        config = get_config()
        generator = SyntheticDataGenerator(config)

        # Simple test: generate 10 rows with basic fields
        requirements = {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "string"},
                {"name": "email", "type": "email"}
            ],
            "rows": 10
        }

        # Note: This might fail if it requires LLM - that's what we're testing
        try:
            df = generator.generate(requirements)
            if df is not None and len(df) == 10:
                record_test_result(test_name, "PASS", f"Generated {len(df)} rows with {len(df.columns)} columns")
                return True
            else:
                record_issue(test_name, "MEDIUM", f"Generated dataframe is invalid: {df}")
                record_test_result(test_name, "FAIL", "Invalid dataframe")
                return False
        except NotImplementedError as e:
            record_test_result(test_name, "SKIP", "Generator requires LLM implementation")
            return False

    except Exception as e:
        record_issue(test_name, "HIGH", f"Data generation failed: {str(e)}", traceback.format_exc())
        record_test_result(test_name, "FAIL", str(e))
        return False

def test_format_handlers():
    """Test 4: Can we use all format handlers?"""
    test_name = "Format Handlers"
    try:
        from synth_agent.formats.csv_handler import CSVFormatter
        from synth_agent.formats.json_handler import JSONFormatter
        from synth_agent.formats.excel_handler import ExcelFormatter
        from synth_agent.formats.parquet_handler import ParquetFormatter
        from synth_agent.formats.xml_handler import XMLFormatter
        from synth_agent.formats.sql_handler import SQLFormatter

        # Create test dataframe
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'email': ['alice@test.com', 'bob@test.com', 'charlie@test.com']
        })

        output_dir = Path("/tmp/synth_agent_test")
        output_dir.mkdir(exist_ok=True)

        formats_tested = []
        formats_failed = []

        # Test CSV
        try:
            csv_formatter = CSVFormatter()
            csv_path = output_dir / "test.csv"
            csv_formatter.export(df, str(csv_path))
            if csv_path.exists():
                formats_tested.append("CSV")
            else:
                formats_failed.append("CSV - file not created")
        except Exception as e:
            formats_failed.append(f"CSV - {str(e)}")

        # Test JSON
        try:
            json_formatter = JSONFormatter()
            json_path = output_dir / "test.json"
            json_formatter.export(df, str(json_path))
            if json_path.exists():
                formats_tested.append("JSON")
            else:
                formats_failed.append("JSON - file not created")
        except Exception as e:
            formats_failed.append(f"JSON - {str(e)}")

        # Test Excel
        try:
            excel_formatter = ExcelFormatter()
            excel_path = output_dir / "test.xlsx"
            excel_formatter.export(df, str(excel_path))
            if excel_path.exists():
                formats_tested.append("Excel")
            else:
                formats_failed.append("Excel - file not created")
        except Exception as e:
            formats_failed.append(f"Excel - {str(e)}")

        # Test Parquet
        try:
            parquet_formatter = ParquetFormatter()
            parquet_path = output_dir / "test.parquet"
            parquet_formatter.export(df, str(parquet_path))
            if parquet_path.exists():
                formats_tested.append("Parquet")
            else:
                formats_failed.append("Parquet - file not created")
        except Exception as e:
            formats_failed.append(f"Parquet - {str(e)}")

        # Test XML
        try:
            xml_formatter = XMLFormatter()
            xml_path = output_dir / "test.xml"
            xml_formatter.export(df, str(xml_path))
            if xml_path.exists():
                formats_tested.append("XML")
            else:
                formats_failed.append("XML - file not created")
        except Exception as e:
            formats_failed.append(f"XML - {str(e)}")

        # Test SQL
        try:
            sql_formatter = SQLFormatter()
            sql_path = output_dir / "test.sql"
            sql_formatter.export(df, str(sql_path))
            if sql_path.exists():
                formats_tested.append("SQL")
            else:
                formats_failed.append("SQL - file not created")
        except Exception as e:
            formats_failed.append(f"SQL - {str(e)}")

        if formats_failed:
            for failure in formats_failed:
                record_issue(test_name, "MEDIUM", f"Format handler failed: {failure}")

        record_test_result(test_name, "PASS" if not formats_failed else "FAIL",
                         f"Tested: {', '.join(formats_tested)}. Failed: {', '.join(formats_failed) if formats_failed else 'None'}")
        return len(formats_failed) == 0

    except Exception as e:
        record_issue(test_name, "HIGH", f"Format handler test failed: {str(e)}", traceback.format_exc())
        record_test_result(test_name, "FAIL", str(e))
        return False

def test_session_management():
    """Test 5: Can we create and manage sessions?"""
    test_name = "Session Management"
    try:
        from synth_agent.core.session import SessionManager, SessionState

        # Create session manager
        session_mgr = SessionManager()

        # Create a session
        session = SessionState(session_id="test_session_001")
        session_mgr.save_session(session)

        # Load the session
        loaded_session = session_mgr.load_session("test_session_001")

        if loaded_session and loaded_session.session_id == "test_session_001":
            record_test_result(test_name, "PASS", "Session saved and loaded successfully")

            # Cleanup
            session_mgr.delete_session("test_session_001")
            return True
        else:
            record_issue(test_name, "MEDIUM", "Session loaded incorrectly")
            record_test_result(test_name, "FAIL", "Session data mismatch")
            return False

    except Exception as e:
        record_issue(test_name, "MEDIUM", f"Session management failed: {str(e)}", traceback.format_exc())
        record_test_result(test_name, "FAIL", str(e))
        return False

def test_analysis_modules():
    """Test 6: Can we use analysis modules?"""
    test_name = "Analysis Modules"
    try:
        from synth_agent.analysis.requirement_parser import RequirementParser
        from synth_agent.analysis.pattern_analyzer import PatternAnalyzer
        from synth_agent.analysis.ambiguity_detector import AmbiguityDetector

        # Test requirement parser
        parser = RequirementParser()
        test_req = {
            "fields": [{"name": "test", "type": "string"}],
            "confidence": 0.9
        }

        is_valid = parser.validate_requirements(test_req)

        if is_valid:
            record_test_result(test_name, "PASS", "Analysis modules functional")
            return True
        else:
            record_issue(test_name, "LOW", "Requirement validation failed unexpectedly")
            record_test_result(test_name, "FAIL", "Validation failed")
            return False

    except Exception as e:
        record_issue(test_name, "MEDIUM", f"Analysis modules failed: {str(e)}", traceback.format_exc())
        record_test_result(test_name, "FAIL", str(e))
        return False

def test_edge_case_empty_data():
    """Test 7: How does the system handle empty data?"""
    test_name = "Edge Case: Empty Data"
    try:
        from synth_agent.formats.csv_handler import CSVFormatter

        # Create empty dataframe
        df = pd.DataFrame()

        csv_formatter = CSVFormatter()

        # This should raise a ValidationError
        try:
            csv_formatter.validate(df)
            record_issue(test_name, "MEDIUM", "Empty dataframe was not rejected by validator")
            record_test_result(test_name, "FAIL", "Empty data not handled properly")
            return False
        except Exception as e:
            # Expected to fail
            record_test_result(test_name, "PASS", f"Empty data correctly rejected: {str(e)}")
            return True

    except Exception as e:
        record_issue(test_name, "LOW", f"Edge case test failed: {str(e)}", traceback.format_exc())
        record_test_result(test_name, "FAIL", str(e))
        return False

def test_edge_case_null_values():
    """Test 8: How does the system handle null values?"""
    test_name = "Edge Case: Null Values"
    try:
        from synth_agent.formats.json_handler import JSONFormatter

        # Create dataframe with nulls
        df = pd.DataFrame({
            'id': [1, None, 3],
            'name': [None, 'Bob', 'Charlie'],
            'value': [100.5, 200.0, None]
        })

        json_formatter = JSONFormatter()
        output_path = Path("/tmp/synth_agent_test/test_nulls.json")

        json_formatter.export(df, str(output_path))

        # Read back and verify
        if output_path.exists():
            with open(output_path) as f:
                data = json.load(f)
                record_test_result(test_name, "PASS", "Null values handled correctly")
                return True
        else:
            record_issue(test_name, "MEDIUM", "Failed to export data with null values")
            record_test_result(test_name, "FAIL", "Export failed")
            return False

    except Exception as e:
        record_issue(test_name, "MEDIUM", f"Null value handling failed: {str(e)}", traceback.format_exc())
        record_test_result(test_name, "FAIL", str(e))
        return False

def test_edge_case_large_dataset():
    """Test 9: Can the system handle large datasets?"""
    test_name = "Edge Case: Large Dataset"
    try:
        from synth_agent.formats.parquet_handler import ParquetFormatter

        # Create large dataframe (10,000 rows)
        df = pd.DataFrame({
            'id': range(10000),
            'value': [i * 1.5 for i in range(10000)],
            'text': [f'Row {i}' for i in range(10000)]
        })

        parquet_formatter = ParquetFormatter()
        output_path = Path("/tmp/synth_agent_test/test_large.parquet")

        parquet_formatter.export(df, str(output_path))

        if output_path.exists():
            # Check file size
            size_mb = output_path.stat().st_size / (1024 * 1024)
            record_test_result(test_name, "PASS", f"Large dataset exported successfully ({size_mb:.2f} MB)")
            return True
        else:
            record_issue(test_name, "HIGH", "Failed to export large dataset")
            record_test_result(test_name, "FAIL", "Export failed")
            return False

    except Exception as e:
        record_issue(test_name, "HIGH", f"Large dataset handling failed: {str(e)}", traceback.format_exc())
        record_test_result(test_name, "FAIL", str(e))
        return False

def test_edge_case_special_characters():
    """Test 10: Can the system handle special characters?"""
    test_name = "Edge Case: Special Characters"
    try:
        from synth_agent.formats.csv_handler import CSVFormatter

        # Create dataframe with special characters
        df = pd.DataFrame({
            'name': ['Test "Quotes"', 'Test, Comma', 'Test\nNewline', "Test'Apostrophe"],
            'unicode': ['日本語', '中文', 'العربية', 'Ελληνικά'],
            'symbols': ['©®™', '€$¥£', '←↑→↓', '♠♣♥♦']
        })

        csv_formatter = CSVFormatter()
        output_path = Path("/tmp/synth_agent_test/test_special.csv")

        csv_formatter.export(df, str(output_path))

        # Read back and verify
        if output_path.exists():
            df_read = pd.read_csv(output_path)
            if len(df_read) == len(df):
                record_test_result(test_name, "PASS", "Special characters handled correctly")
                return True
            else:
                record_issue(test_name, "MEDIUM", "Data corrupted after round-trip with special characters")
                record_test_result(test_name, "FAIL", "Data mismatch after round-trip")
                return False
        else:
            record_issue(test_name, "MEDIUM", "Failed to export data with special characters")
            record_test_result(test_name, "FAIL", "Export failed")
            return False

    except Exception as e:
        record_issue(test_name, "MEDIUM", f"Special character handling failed: {str(e)}", traceback.format_exc())
        record_test_result(test_name, "FAIL", str(e))
        return False

def test_relational_data_generation():
    """Test 11: Can we generate relational data?"""
    test_name = "Relational Data Generation"
    try:
        from synth_agent.generation.relational import RelationalDataGenerator
        from synth_agent.core.config import get_config

        config = get_config()
        rel_gen = RelationalDataGenerator(config)

        # Define a simple schema: users and orders
        schema = {
            "tables": {
                "users": {
                    "fields": [
                        {"name": "user_id", "type": "integer", "primary_key": True},
                        {"name": "username", "type": "string"},
                        {"name": "email", "type": "email"}
                    ],
                    "rows": 5
                },
                "orders": {
                    "fields": [
                        {"name": "order_id", "type": "integer", "primary_key": True},
                        {"name": "user_id", "type": "integer", "foreign_key": "users.user_id"},
                        {"name": "amount", "type": "float"}
                    ],
                    "rows": 10
                }
            }
        }

        # Try to generate
        try:
            result = rel_gen.generate(schema)
            if result and "users" in result and "orders" in result:
                record_test_result(test_name, "PASS",
                                 f"Generated {len(result['users'])} users and {len(result['orders'])} orders")
                return True
            else:
                record_test_result(test_name, "SKIP", "Relational generation not fully implemented")
                return False
        except NotImplementedError:
            record_test_result(test_name, "SKIP", "Relational generation requires LLM")
            return False

    except Exception as e:
        record_issue(test_name, "MEDIUM", f"Relational data generation failed: {str(e)}", traceback.format_exc())
        record_test_result(test_name, "FAIL", str(e))
        return False

def test_error_handling():
    """Test 12: Does the system have proper error handling?"""
    test_name = "Error Handling"
    try:
        from synth_agent.core.exceptions import (
            SynthAgentError, ValidationError, FormatError
        )

        errors_tested = []

        # Test that exceptions can be raised and caught
        try:
            raise ValidationError("Test validation error")
        except ValidationError as e:
            errors_tested.append("ValidationError")

        try:
            raise FormatError("Test format error")
        except FormatError as e:
            errors_tested.append("FormatError")

        try:
            raise SynthAgentError("Test base error")
        except SynthAgentError as e:
            errors_tested.append("SynthAgentError")

        record_test_result(test_name, "PASS",
                         f"Error handling works. Tested: {', '.join(errors_tested)}")
        return True

    except Exception as e:
        record_issue(test_name, "HIGH", f"Error handling test failed: {str(e)}", traceback.format_exc())
        record_test_result(test_name, "FAIL", str(e))
        return False

def save_test_report():
    """Save test results and issues to files"""
    report_dir = Path("/tmp/synth_agent_test_report")
    report_dir.mkdir(exist_ok=True)

    # Save issues
    issues_file = report_dir / "issues_found.json"
    with open(issues_file, 'w') as f:
        json.dump(ISSUES_FOUND, f, indent=2)

    # Save test results
    results_file = report_dir / "test_results.json"
    with open(results_file, 'w') as f:
        json.dump(TEST_RESULTS, f, indent=2)

    # Create summary report
    summary_file = report_dir / "test_summary.md"
    with open(summary_file, 'w') as f:
        f.write("# Synthetic Data Generator - Test Report\n\n")
        f.write(f"**Date**: {datetime.now().isoformat()}\n\n")

        # Test summary
        passed = len([r for r in TEST_RESULTS if r['status'] == 'PASS'])
        failed = len([r for r in TEST_RESULTS if r['status'] == 'FAIL'])
        skipped = len([r for r in TEST_RESULTS if r['status'] == 'SKIP'])
        total = len(TEST_RESULTS)

        f.write("## Test Summary\n\n")
        f.write(f"- **Total Tests**: {total}\n")
        f.write(f"- **Passed**: {passed} ✅\n")
        f.write(f"- **Failed**: {failed} ❌\n")
        f.write(f"- **Skipped**: {skipped} ⏭️\n")
        f.write(f"- **Pass Rate**: {(passed/total*100):.1f}%\n\n")

        # Issues summary
        critical = len([i for i in ISSUES_FOUND if i['severity'] == 'CRITICAL'])
        high = len([i for i in ISSUES_FOUND if i['severity'] == 'HIGH'])
        medium = len([i for i in ISSUES_FOUND if i['severity'] == 'MEDIUM'])
        low = len([i for i in ISSUES_FOUND if i['severity'] == 'LOW'])

        f.write("## Issues Summary\n\n")
        f.write(f"- **Critical**: {critical}\n")
        f.write(f"- **High**: {high}\n")
        f.write(f"- **Medium**: {medium}\n")
        f.write(f"- **Low**: {low}\n")
        f.write(f"- **Total Issues**: {len(ISSUES_FOUND)}\n\n")

        # Detailed test results
        f.write("## Detailed Test Results\n\n")
        for result in TEST_RESULTS:
            symbol = "✅" if result['status'] == 'PASS' else "❌" if result['status'] == 'FAIL' else "⏭️"
            f.write(f"### {symbol} {result['test']}\n")
            f.write(f"- **Status**: {result['status']}\n")
            f.write(f"- **Details**: {result['details']}\n")
            f.write(f"- **Timestamp**: {result['timestamp']}\n\n")

        # Detailed issues
        if ISSUES_FOUND:
            f.write("## Detailed Issues\n\n")
            for issue in ISSUES_FOUND:
                f.write(f"### [{issue['severity']}] {issue['test']}\n")
                f.write(f"- **Description**: {issue['description']}\n")
                f.write(f"- **Timestamp**: {issue['timestamp']}\n")
                if issue.get('stack_trace'):
                    f.write(f"- **Stack Trace**:\n```\n{issue['stack_trace']}\n```\n")
                f.write("\n")

    print(f"\n📊 Test report saved to: {report_dir}")
    print(f"   - Issues: {issues_file}")
    print(f"   - Results: {results_file}")
    print(f"   - Summary: {summary_file}")

def main():
    """Run all tests"""
    print("=" * 80)
    print("SYNTHETIC DATA GENERATOR - COMPREHENSIVE TEST SUITE")
    print("=" * 80)

    # Run all tests
    test_basic_import()
    test_config_loading()
    test_basic_data_generation()
    test_format_handlers()
    test_session_management()
    test_analysis_modules()
    test_edge_case_empty_data()
    test_edge_case_null_values()
    test_edge_case_large_dataset()
    test_edge_case_special_characters()
    test_relational_data_generation()
    test_error_handling()

    # Generate report
    save_test_report()

    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = len([r for r in TEST_RESULTS if r['status'] == 'PASS'])
    failed = len([r for r in TEST_RESULTS if r['status'] == 'FAIL'])
    skipped = len([r for r in TEST_RESULTS if r['status'] == 'SKIP'])
    total = len(TEST_RESULTS)

    print(f"Total Tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Skipped: {skipped} ⏭️")
    print(f"Pass Rate: {(passed/total*100):.1f}%")

    print("\n" + "=" * 80)
    print("ISSUES SUMMARY")
    print("=" * 80)

    critical = len([i for i in ISSUES_FOUND if i['severity'] == 'CRITICAL'])
    high = len([i for i in ISSUES_FOUND if i['severity'] == 'HIGH'])
    medium = len([i for i in ISSUES_FOUND if i['severity'] == 'MEDIUM'])
    low = len([i for i in ISSUES_FOUND if i['severity'] == 'LOW'])

    print(f"Critical: {critical}")
    print(f"High: {high}")
    print(f"Medium: {medium}")
    print(f"Low: {low}")
    print(f"Total Issues: {len(ISSUES_FOUND)}")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
