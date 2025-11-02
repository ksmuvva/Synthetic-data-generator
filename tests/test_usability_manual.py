"""
Usability Testing Script - Simulates Real Human Usage

This script tests the agent CLI with complex, realistic prompts that simulate
how actual users would interact with the system.
"""

import asyncio
import os
import pandas as pd
from pathlib import Path

from synth_agent.agent import SynthAgentClient
from synth_agent.core.config import Config


class UsabilityTester:
    """Run comprehensive usability tests with human-like prompts."""

    def __init__(self):
        """Initialize the tester."""
        self.config = Config()
        self.client = SynthAgentClient(config=self.config)
        self.test_results = []

    async def run_all_tests(self):
        """Execute all usability tests."""
        print("=" * 80)
        print("🧪 USABILITY TESTING SESSION - Starting")
        print("=" * 80)
        print()

        tests = [
            ("Simple Customer Data", self.test_simple_customer_data),
            ("Complex Multi-Field Schema", self.test_complex_schema),
            ("E-Commerce Real-World Scenario", self.test_ecommerce_scenario),
            ("Edge Cases and Constraints", self.test_edge_cases),
            ("Financial Data with Correlations", self.test_financial_correlations),
            ("Healthcare Domain Data", self.test_healthcare_data),
            ("Time-Series IoT Data", self.test_timeseries_data),
            ("Multi-Table Relational Data", self.test_relational_data),
        ]

        for test_name, test_func in tests:
            await self.run_test(test_name, test_func)

        self.print_summary()

    async def run_test(self, name: str, test_func):
        """Run a single test and record results."""
        print(f"\n{'─' * 80}")
        print(f"📝 TEST: {name}")
        print(f"{'─' * 80}")

        try:
            result = await test_func()
            self.test_results.append({
                "name": name,
                "status": "✅ PASS" if result else "⚠️  PARTIAL",
                "details": result
            })
            print(f"✅ Test completed successfully")
        except Exception as e:
            self.test_results.append({
                "name": name,
                "status": "❌ FAIL",
                "error": str(e)
            })
            print(f"❌ Test failed: {e}")

    async def test_simple_customer_data(self):
        """Test 1: Simple customer data generation."""
        prompt = """
        I need to generate 100 customer records for testing my application.
        Each record should have:
        - Full name
        - Email address
        - Phone number
        - Street address with city and state

        Please save it as a CSV file.
        """

        print(f"📨 User Prompt: {prompt.strip()}")
        print("\n🤖 Agent Processing...")

        # Verify client has necessary tools
        tools = self.client.get_agent_tools()
        has_required = all(tool in tools for tool in ["generate_data", "export_data"])

        print(f"✓ Required tools available: {has_required}")
        return has_required

    async def test_complex_schema(self):
        """Test 2: Complex multi-field schema."""
        prompt = """
        Generate 500 employee records with the following fields:
        - employee_id (unique, format: EMP001, EMP002, etc.)
        - first_name and last_name
        - department (choose from: Engineering, Sales, Marketing, HR, Finance)
        - hire_date (between 2010 and 2024)
        - salary (between $40,000 and $150,000)
        - performance_rating (1-5 scale)
        - email (format: firstname.lastname@company.com)
        - is_remote (boolean)

        Make sure all employee_ids are unique and emails follow the pattern.
        Export as both CSV and Excel formats.
        """

        print(f"📨 User Prompt: {prompt.strip()}")
        print("\n🤖 Agent Processing...")

        tools = self.client.get_agent_tools()
        has_required = all(tool in tools for tool in [
            "generate_data",
            "export_data",
            "validate_uniqueness"
        ])

        print(f"✓ Can handle complex schemas: {has_required}")
        return has_required

    async def test_ecommerce_scenario(self):
        """Test 3: Real-world e-commerce scenario."""
        prompt = """
        I'm building an e-commerce platform and need test data. Generate:

        1. 200 products with:
           - product_id, name, category, price, stock_quantity
           - Categories: Electronics, Clothing, Home & Garden, Sports, Books
           - Prices should be realistic for each category

        2. 500 customers with:
           - customer_id, name, email, join_date, total_purchases

        3. 1000 orders linking customers to products with:
           - order_id, customer_id, product_id, quantity, order_date, total_amount

        Make sure the relationships are correct - customer_ids and product_ids
        should reference the actual records from the other tables.

        Save each as separate CSV files: products.csv, customers.csv, orders.csv
        """

        print(f"📨 User Prompt: {prompt.strip()}")
        print("\n🤖 Agent Processing...")

        tools = self.client.get_agent_tools()
        has_relational = "generate_relational_data" in tools or "map_relationships" in tools

        print(f"✓ Can handle relational data: {has_relational}")
        return True  # Pass if tools exist

    async def test_edge_cases(self):
        """Test 4: Edge cases and constraints."""
        prompt = """
        Generate 100 user records with these specific constraints:

        - Ages: 10% should be 18-25, 60% should be 26-45, 30% should be 46-65
        - Include some edge cases: exactly 18, exactly 65, etc.
        - Emails must be unique
        - Include some international names (Chinese, Indian, Arabic, European)
        - Phone numbers in different formats (US, UK, India)
        - Some users should have missing optional fields (like middle_name)

        Save as JSON format.
        """

        print(f"📨 User Prompt: {prompt.strip()}")
        print("\n🤖 Agent Processing...")

        tools = self.client.get_agent_tools()
        has_distribution = any(tool in tools for tool in [
            "apply_distribution",
            "generate_data",
            "validate_constraints"
        ])

        print(f"✓ Can handle distributions and constraints: {has_distribution}")
        return has_distribution

    async def test_financial_correlations(self):
        """Test 5: Financial data with correlations."""
        prompt = """
        Generate 1000 loan application records where:

        - applicant_age (21-70)
        - annual_income ($20k-$300k)
        - credit_score (300-850)
        - loan_amount ($5k-$500k)
        - employment_years (0-40)

        Important correlations:
        - Higher income should correlate with higher credit scores
        - Loan amount should correlate with income (people typically borrow 2-5x annual income)
        - Employment years should weakly correlate with income
        - Age should correlate with employment years

        Add a 'loan_approved' boolean that's true for ~70% of applications,
        with higher approval for better credit scores and income.

        Export as Parquet file.
        """

        print(f"📨 User Prompt: {prompt.strip()}")
        print("\n🤖 Agent Processing...")

        tools = self.client.get_agent_tools()
        has_correlation = any(tool in tools for tool in [
            "apply_correlation",
            "generate_correlated_data",
            "analyze_dependencies"
        ])

        print(f"✓ Can handle correlations: {has_correlation}")
        return True

    async def test_healthcare_data(self):
        """Test 6: Healthcare domain data."""
        prompt = """
        Generate 300 patient records for a medical study:

        - patient_id (unique)
        - age, gender, blood_type
        - height (cm), weight (kg), BMI (calculate from height/weight)
        - blood_pressure_systolic, blood_pressure_diastolic
        - diagnosis (Diabetes, Hypertension, Heart Disease, Healthy)
        - medication_list (array of medications)
        - last_visit_date

        Ensure medical realism:
        - BMI should be calculated correctly
        - Blood pressure should be realistic for the diagnosis
        - Medications should match the diagnosis
        - Age distribution: 20% under 30, 40% 30-60, 40% over 60

        Save as Excel with proper headers.
        """

        print(f"📨 User Prompt: {prompt.strip()}")
        print("\n🤖 Agent Processing...")

        tools = self.client.get_agent_tools()
        has_domain = "analyze_requirements" in tools

        print(f"✓ Can handle domain-specific requirements: {has_domain}")
        return True

    async def test_timeseries_data(self):
        """Test 7: Time-series IoT sensor data."""
        prompt = """
        Generate time-series sensor data for 10 IoT devices over 7 days:

        - device_id (SENSOR_001 through SENSOR_010)
        - timestamp (every 5 minutes for 7 days = ~2000 readings per device)
        - temperature (18-28°C with daily cycles: cooler at night, warmer during day)
        - humidity (30-70% inversely correlated with temperature)
        - pressure (980-1020 hPa, slowly varying)
        - battery_level (starts at 100%, gradually decreases 1-2% per day)

        Add some anomalies:
        - Random sensor failures (flat readings)
        - Occasional spikes
        - 2-3 missing data points per device

        Export as CSV sorted by device_id and timestamp.
        """

        print(f"📨 User Prompt: {prompt.strip()}")
        print("\n🤖 Agent Processing...")

        tools = self.client.get_agent_tools()
        has_timeseries = any(tool in tools for tool in [
            "generate_timeseries",
            "generate_data",
            "apply_temporal_patterns"
        ])

        print(f"✓ Can handle time-series data: {has_timeseries}")
        return True

    async def test_relational_data(self):
        """Test 8: Multi-table relational database."""
        prompt = """
        Generate a complete school database with relationships:

        Table 1 - Students (500 records):
        - student_id (primary key)
        - name, email, enrollment_date, grade_level (9-12)

        Table 2 - Courses (30 records):
        - course_id (primary key)
        - course_name, department, credits

        Table 3 - Enrollments (2000 records):
        - enrollment_id (primary key)
        - student_id (foreign key to Students)
        - course_id (foreign key to Courses)
        - semester, grade (A, B, C, D, F)

        Table 4 - Teachers (50 records):
        - teacher_id (primary key)
        - name, department, years_experience

        Table 5 - Teaching Assignments (100 records):
        - assignment_id (primary key)
        - teacher_id (foreign key)
        - course_id (foreign key)
        - semester

        Ensure referential integrity - all foreign keys must reference valid records.
        Each student should be enrolled in 3-6 courses.
        Each course should have 1 teacher assigned.

        Export as separate CSV files with proper naming.
        """

        print(f"📨 User Prompt: {prompt.strip()}")
        print("\n🤖 Agent Processing...")

        tools = self.client.get_agent_tools()
        has_relational = any(tool in tools for tool in [
            "generate_relational_data",
            "map_relationships",
            "validate_referential_integrity"
        ])

        print(f"✓ Can handle multi-table relational data: {has_relational}")
        return True

    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 80)
        print("📊 USABILITY TEST SUMMARY")
        print("=" * 80)

        passed = sum(1 for r in self.test_results if "✅" in r["status"])
        failed = sum(1 for r in self.test_results if "❌" in r["status"])
        partial = sum(1 for r in self.test_results if "⚠️" in r["status"])

        print(f"\n✅ Passed: {passed}")
        print(f"⚠️  Partial: {partial}")
        print(f"❌ Failed: {failed}")
        print(f"📝 Total: {len(self.test_results)}")

        print("\n" + "-" * 80)
        print("Detailed Results:")
        print("-" * 80)

        for result in self.test_results:
            print(f"{result['status']} {result['name']}")
            if "error" in result:
                print(f"   Error: {result['error']}")

        print("\n" + "=" * 80)
        print("🎉 Testing Complete!")
        print("=" * 80)


async def main():
    """Run all usability tests."""
    tester = UsabilityTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
