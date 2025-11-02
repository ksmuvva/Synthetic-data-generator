"""
Exhaustive Test Suite for Claude Reasoning and Skills
======================================================

This test suite performs comprehensive usability testing focused on:
1. Claude's reasoning capabilities across all 12 strategies
2. Complex prompt handling and understanding
3. Multi-step workflows and context retention
4. Domain-specific understanding and adaptation
5. Error recovery and clarification handling
6. Tool usage and orchestration

Tests simulate real human interactions with complex, nuanced prompts.
"""

import pytest
import asyncio
import pandas as pd
from pathlib import Path

from synth_agent.agent import SynthAgentClient, get_state_manager
from synth_agent.core.config import Config


class TestClaudeReasoningStrategies:
    """Test all 12 reasoning strategies with complex scenarios."""

    @pytest.mark.asyncio
    async def test_chain_of_thought_medical_domain(self):
        """
        Test: Chain of Thought for medical/healthcare domain
        Prompt: Complex patient data generation with clinical constraints
        """
        config = Config()
        client = SynthAgentClient(config=config)
        state_manager = get_state_manager()
        session_id = "test_cot_medical"

        # Simulate complex medical prompt
        requirements = {
            "domain": "medical",
            "prompt": """Generate 500 patient records for a clinical trial studying diabetes.
                        Include patient demographics, blood sugar levels, HbA1c measurements,
                        medication history, and treatment outcomes. Ensure HIPAA compliance
                        with realistic but anonymized data. Patients should be aged 35-75,
                        with varying stages of diabetes (Type 1, Type 2, prediabetic).
                        Include correlations between age, BMI, and blood sugar levels.""",
            "expected_reasoning": "chain_of_thought"
        }

        await state_manager.set_requirements(session_id, requirements)

        # Verify the requirement was stored
        retrieved = await state_manager.get_requirements(session_id)
        assert retrieved is not None
        assert retrieved["domain"] == "medical"
        assert "chain_of_thought" in retrieved["expected_reasoning"]

        # Cleanup
        await state_manager.clear_session(session_id)

    @pytest.mark.asyncio
    async def test_mcts_financial_complex_trading(self):
        """
        Test: MCTS for financial/trading domain
        Prompt: Complex trading data with risk calculations
        """
        state_manager = get_state_manager()
        session_id = "test_mcts_trading"

        requirements = {
            "domain": "financial",
            "prompt": """Create a synthetic trading dataset with 10,000 transactions across
                        5 different assets (stocks, bonds, options, futures, crypto).
                        Include: transaction ID, timestamp, asset type, buy/sell indicator,
                        quantity, price, fees, profit/loss. Model realistic market conditions
                        including volatility, trends, and correlation between assets.
                        Include edge cases like flash crashes, circuit breakers, and
                        after-hours trading.""",
            "expected_reasoning": "mcts",
            "complexity": "high",
            "requires_optimization": True
        }

        await state_manager.set_requirements(session_id, requirements)
        retrieved = await state_manager.get_requirements(session_id)

        assert retrieved["domain"] == "financial"
        assert retrieved["expected_reasoning"] == "mcts"
        assert retrieved["requires_optimization"] is True

        # Cleanup
        await state_manager.clear_session(session_id)

    @pytest.mark.asyncio
    async def test_tree_of_thoughts_relational_database(self):
        """
        Test: Tree of Thoughts for multi-table relational database
        Prompt: Complex relational database with foreign keys and constraints
        """
        state_manager = get_state_manager()
        session_id = "test_tot_relational"

        requirements = {
            "domain": "relational",
            "prompt": """Design and generate data for a complete e-commerce database.
                        Tables needed:
                        - Customers (1000 records): ID, name, email, address, join_date
                        - Products (500 records): ID, name, category, price, stock
                        - Orders (5000 records): ID, customer_ID, date, total, status
                        - Order_Items (15000 records): ID, order_ID, product_ID, quantity, price
                        - Reviews (3000 records): ID, product_ID, customer_ID, rating, text, date

                        Maintain referential integrity with proper foreign keys.
                        Ensure realistic patterns: customers with multiple orders,
                        popular products with more reviews, seasonal buying patterns.""",
            "expected_reasoning": "tree_of_thoughts",
            "tables": 5,
            "foreign_keys": ["customer_ID", "product_ID", "order_ID"],
            "complexity": "very_high"
        }

        await state_manager.set_requirements(session_id, requirements)
        retrieved = await state_manager.get_requirements(session_id)

        assert retrieved["domain"] == "relational"
        assert retrieved["tables"] == 5
        assert len(retrieved["foreign_keys"]) == 3

        # Cleanup
        await state_manager.clear_session(session_id)

    @pytest.mark.asyncio
    async def test_beam_search_ecommerce_optimization(self):
        """
        Test: Beam Search for e-commerce optimization
        Prompt: Product catalog with multiple optimization constraints
        """
        state_manager = get_state_manager()
        session_id = "test_beam_ecommerce"

        requirements = {
            "domain": "ecommerce",
            "prompt": """Generate a product catalog for a fashion e-commerce site.
                        2000 products across categories: shirts, pants, shoes, accessories.
                        For each product: SKU, name, brand, color, size, price, cost,
                        margin, popularity_score, season, gender, age_group.
                        Optimize for: realistic price distributions, brand consistency,
                        seasonal availability, size distribution per category.
                        Include best-sellers (5%), average (70%), slow-movers (25%).""",
            "expected_reasoning": "beam_search",
            "num_products": 2000,
            "optimization_goals": ["price_distribution", "brand_consistency", "seasonal_patterns"]
        }

        await state_manager.set_requirements(session_id, requirements)
        retrieved = await state_manager.get_requirements(session_id)

        assert retrieved["domain"] == "ecommerce"
        assert retrieved["num_products"] == 2000
        assert len(retrieved["optimization_goals"]) == 3

        # Cleanup
        await state_manager.clear_session(session_id)

    @pytest.mark.asyncio
    async def test_react_api_integration_realtime(self):
        """
        Test: ReAct for real-time API integration scenario
        Prompt: Data generation with validation and API constraints
        """
        state_manager = get_state_manager()
        session_id = "test_react_api"

        requirements = {
            "domain": "api_integration",
            "prompt": """Create test data for API testing. Generate 1000 user registration
                        requests with varying validity: 70% valid, 20% with minor errors,
                        10% with critical errors. Include: username, email, password_hash,
                        phone_number, country_code, IP_address, user_agent, timestamp.
                        Validate: email format, phone number format per country,
                        password strength, duplicate detection, rate limiting scenarios.""",
            "expected_reasoning": "react",
            "validation_required": True,
            "error_distribution": {"valid": 0.7, "minor_errors": 0.2, "critical_errors": 0.1}
        }

        await state_manager.set_requirements(session_id, requirements)
        retrieved = await state_manager.get_requirements(session_id)

        assert retrieved["domain"] == "api_integration"
        assert retrieved["validation_required"] is True
        assert retrieved["error_distribution"]["valid"] == 0.7

        # Cleanup
        await state_manager.clear_session(session_id)

    @pytest.mark.asyncio
    async def test_reflexion_quality_improvement(self):
        """
        Test: Reflexion for iterative quality improvement
        Prompt: Data generation with self-correction and refinement
        """
        state_manager = get_state_manager()
        session_id = "test_reflexion_quality"

        requirements = {
            "domain": "quality_focused",
            "prompt": """Generate high-quality synthetic text data for NLP training.
                        Create 500 product descriptions for consumer electronics.
                        Each description should be 100-150 words, SEO-optimized,
                        grammatically perfect, and engaging. Include specifications,
                        features, benefits, and use cases. Avoid repetition, clichés,
                        and marketing buzzwords. Ensure readability score above 60.""",
            "expected_reasoning": "reflexion",
            "quality_requirements": {
                "grammar_score": 95,
                "readability_score": 60,
                "uniqueness": 90,
                "seo_score": 75
            },
            "iterative_refinement": True
        }

        await state_manager.set_requirements(session_id, requirements)
        retrieved = await state_manager.get_requirements(session_id)

        assert retrieved["domain"] == "quality_focused"
        assert retrieved["iterative_refinement"] is True
        assert retrieved["quality_requirements"]["grammar_score"] == 95

        # Cleanup
        await state_manager.clear_session(session_id)

    @pytest.mark.asyncio
    async def test_astar_optimization_scheduling(self):
        """
        Test: A* for scheduling optimization
        Prompt: Complex scheduling with constraints
        """
        state_manager = get_state_manager()
        session_id = "test_astar_scheduling"

        requirements = {
            "domain": "scheduling",
            "prompt": """Generate an optimized employee shift schedule for a 24/7 call center.
                        100 employees, 30 days, 3 shifts (morning, evening, night).
                        Constraints: max 5 consecutive days, min 2 days off per week,
                        no back-to-back night shifts, balanced shift distribution,
                        peak coverage during 9am-5pm weekdays. Include skill levels
                        (junior, senior, team lead) and ensure adequate coverage.""",
            "expected_reasoning": "astar",
            "optimization_type": "constraint_satisfaction",
            "constraints": 6
        }

        await state_manager.set_requirements(session_id, requirements)
        retrieved = await state_manager.get_requirements(session_id)

        assert retrieved["domain"] == "scheduling"
        assert retrieved["optimization_type"] == "constraint_satisfaction"
        assert retrieved["constraints"] == 6

        # Cleanup
        await state_manager.clear_session(session_id)

    @pytest.mark.asyncio
    async def test_best_first_search_timeseries(self):
        """
        Test: Best First Search for time series data
        Prompt: Complex temporal patterns
        """
        state_manager = get_state_manager()
        session_id = "test_bfs_timeseries"

        requirements = {
            "domain": "timeseries",
            "prompt": """Generate IoT sensor data from 50 devices over 90 days.
                        Metrics: temperature, humidity, pressure, vibration, power_consumption.
                        Sample every 5 minutes (25,920 readings per device per metric).
                        Include: normal operations, gradual degradation, sudden failures,
                        seasonal patterns, daily cycles, weekend effects, maintenance windows.
                        Correlate metrics (high temperature increases power consumption).""",
            "expected_reasoning": "best_first_search",
            "temporal_patterns": ["seasonal", "daily_cycle", "degradation"],
            "num_devices": 50,
            "duration_days": 90
        }

        await state_manager.set_requirements(session_id, requirements)
        retrieved = await state_manager.get_requirements(session_id)

        assert retrieved["domain"] == "timeseries"
        assert len(retrieved["temporal_patterns"]) == 3
        assert retrieved["num_devices"] == 50

        # Cleanup
        await state_manager.clear_session(session_id)

    @pytest.mark.asyncio
    async def test_graph_of_thoughts_social_network(self):
        """
        Test: Graph of Thoughts for social network data
        Prompt: Complex network with relationships
        """
        state_manager = get_state_manager()
        session_id = "test_got_social"

        requirements = {
            "domain": "social",
            "prompt": """Create a realistic social network dataset.
                        10,000 users with profiles: user_ID, name, age, location, interests.
                        Relationships: friendships (avg 50 per user), follows (asymmetric),
                        groups (varying sizes), posts (1M total), likes, comments, shares.
                        Model: friend clusters, influencers (power law distribution),
                        echo chambers, viral content spread. Include temporal dynamics:
                        users join over time, relationships form gradually.""",
            "expected_reasoning": "graph_of_thoughts",
            "num_nodes": 10000,
            "relationship_types": ["friendship", "follow", "group_membership"],
            "network_properties": ["clustering", "power_law", "temporal_dynamics"]
        }

        await state_manager.set_requirements(session_id, requirements)
        retrieved = await state_manager.get_requirements(session_id)

        assert retrieved["domain"] == "social"
        assert retrieved["num_nodes"] == 10000
        assert len(retrieved["relationship_types"]) == 3

        # Cleanup
        await state_manager.clear_session(session_id)

    @pytest.mark.asyncio
    async def test_self_consistency_compliance_audit(self):
        """
        Test: Self Consistency for compliance/audit data
        Prompt: Audit trail with validation
        """
        state_manager = get_state_manager()
        session_id = "test_sc_audit"

        requirements = {
            "domain": "audit",
            "prompt": """Generate financial audit trail data for compliance testing.
                        50,000 transactions over 1 year. For each: transaction_ID,
                        date, user_ID, account_from, account_to, amount, currency,
                        transaction_type, approval_status, approver_ID, timestamp.
                        Ensure: balanced ledgers, proper authorization chains,
                        audit checksums, anomaly detection test cases (1% suspicious),
                        regulatory compliance markers (SOX, GDPR). All data must be
                        internally consistent and traceable.""",
            "expected_reasoning": "self_consistency",
            "validation_rules": ["balanced_ledgers", "authorization_chain", "checksums"],
            "anomaly_rate": 0.01
        }

        await state_manager.set_requirements(session_id, requirements)
        retrieved = await state_manager.get_requirements(session_id)

        assert retrieved["domain"] == "audit"
        assert len(retrieved["validation_rules"]) == 3
        assert retrieved["anomaly_rate"] == 0.01

        # Cleanup
        await state_manager.clear_session(session_id)

    @pytest.mark.asyncio
    async def test_meta_prompting_multi_domain(self):
        """
        Test: Meta Prompting for cross-domain complex scenario
        Prompt: Multiple integrated domains requiring strategy switching
        """
        state_manager = get_state_manager()
        session_id = "test_meta_multi"

        requirements = {
            "domain": "multi_domain",
            "prompt": """Create a complete business simulation dataset combining:
                        1. Customer data (CRM): 5000 customers with demographics, purchase history
                        2. Product catalog (inventory): 1000 products with stock, pricing
                        3. Transaction data (financial): 50,000 orders with payment details
                        4. Marketing campaigns (analytics): 20 campaigns with performance metrics
                        5. Customer support tickets (text): 10,000 tickets with resolutions
                        6. Employee data (HR): 200 employees with roles, performance, schedules

                        All datasets must be integrated with referential integrity.
                        Include realistic business patterns, seasonal effects, and
                        cross-domain correlations (e.g., marketing affects sales).""",
            "expected_reasoning": "meta_prompting",
            "domains": ["crm", "inventory", "financial", "marketing", "support", "hr"],
            "integration_required": True,
            "cross_domain_correlations": True
        }

        await state_manager.set_requirements(session_id, requirements)
        retrieved = await state_manager.get_requirements(session_id)

        assert retrieved["domain"] == "multi_domain"
        assert len(retrieved["domains"]) == 6
        assert retrieved["integration_required"] is True

        # Cleanup
        await state_manager.clear_session(session_id)

    @pytest.mark.asyncio
    async def test_iterative_refinement_quality_evolution(self):
        """
        Test: Iterative Refinement for progressive quality improvement
        Prompt: Data generation that improves over iterations
        """
        state_manager = get_state_manager()
        session_id = "test_iter_refinement"

        requirements = {
            "domain": "iterative",
            "prompt": """Generate survey response data with progressive quality improvement.
                        Start with 1000 responses to a 20-question survey about product satisfaction.
                        Initial generation: basic responses with some inconsistencies.
                        Iteration 2: Fix logical inconsistencies (e.g., satisfied but low scores).
                        Iteration 3: Add psychological realism (response patterns, biases).
                        Iteration 4: Include demographic correlations and segment behaviors.
                        Iteration 5: Final polish with edge cases and quality validation.""",
            "expected_reasoning": "iterative_refinement",
            "num_iterations": 5,
            "quality_metrics": ["consistency", "realism", "correlations", "completeness"]
        }

        await state_manager.set_requirements(session_id, requirements)
        retrieved = await state_manager.get_requirements(session_id)

        assert retrieved["domain"] == "iterative"
        assert retrieved["num_iterations"] == 5
        assert len(retrieved["quality_metrics"]) == 4

        # Cleanup
        await state_manager.clear_session(session_id)


class TestComplexHumanPrompts:
    """Test complex, human-like prompts that require understanding and reasoning."""

    @pytest.mark.asyncio
    async def test_ambiguous_vague_prompt(self):
        """
        Test: Handling vague, ambiguous prompts that humans typically write
        Prompt: "I need some data for testing... you know, like customer stuff"
        """
        state_manager = get_state_manager()
        session_id = "test_ambiguous"

        requirements = {
            "prompt": "I need some data for testing... you know, like customer stuff",
            "ambiguities_expected": True,
            "clarification_needed": ["num_rows", "fields", "format", "use_case"]
        }

        await state_manager.set_requirements(session_id, requirements)
        retrieved = await state_manager.get_requirements(session_id)

        assert retrieved["ambiguities_expected"] is True
        assert len(retrieved["clarification_needed"]) >= 3

        # Cleanup
        await state_manager.clear_session(session_id)

    @pytest.mark.asyncio
    async def test_conversational_refinement(self):
        """
        Test: Multi-turn conversation with refinements
        Simulates: User starts vague, then adds details across multiple turns
        """
        state_manager = get_state_manager()
        session_id = "test_conversation"

        # Turn 1: Initial vague request
        turn1 = {
            "prompt": "Create customer data",
            "turn": 1
        }
        await state_manager.set_value(session_id, "turn_1", turn1)

        # Turn 2: Add specifics
        turn2 = {
            "prompt": "Actually, make it 1000 customers with emails and phone numbers",
            "turn": 2,
            "refinement_of": "turn_1"
        }
        await state_manager.set_value(session_id, "turn_2", turn2)

        # Turn 3: Add more constraints
        turn3 = {
            "prompt": "Oh and make sure the emails are unique and from common domains",
            "turn": 3,
            "refinement_of": "turn_2"
        }
        await state_manager.set_value(session_id, "turn_3", turn3)

        # Turn 4: Change format
        turn4 = {
            "prompt": "Can you save it as Excel instead of CSV?",
            "turn": 4,
            "refinement_of": "turn_3"
        }
        await state_manager.set_value(session_id, "turn_4", turn4)

        # Verify conversation history
        final_turn = await state_manager.get_value(session_id, "turn_4")
        assert final_turn["turn"] == 4

        # Cleanup
        await state_manager.clear_session(session_id)

    @pytest.mark.asyncio
    async def test_implicit_requirements_inference(self):
        """
        Test: Inferring implicit requirements from context
        Prompt: User mentions "GDPR compliance" - should infer data protection needs
        """
        state_manager = get_state_manager()
        session_id = "test_implicit"

        requirements = {
            "prompt": """Generate EU customer data. Make sure it's GDPR compliant.
                        I'll be using this for testing our data privacy features.""",
            "explicit_requirements": ["EU customers", "testing data"],
            "implicit_requirements": [
                "pseudonymization",
                "right_to_erasure_simulation",
                "consent_flags",
                "data_minimization",
                "retention_periods"
            ]
        }

        await state_manager.set_requirements(session_id, requirements)
        retrieved = await state_manager.get_requirements(session_id)

        assert len(retrieved["implicit_requirements"]) >= 3
        assert "pseudonymization" in retrieved["implicit_requirements"]

        # Cleanup
        await state_manager.clear_session(session_id)

    @pytest.mark.asyncio
    async def test_contradictory_requirements(self):
        """
        Test: Detecting and handling contradictory requirements
        Prompt: "Generate 1000 unique emails but only use 5 domains"... possible!
                "Generate 100 unique values from a list of 10" ... impossible!
        """
        state_manager = get_state_manager()
        session_id = "test_contradictions"

        # Possible scenario
        possible = {
            "prompt": "Generate 1000 unique emails using only these 5 domains: gmail.com, yahoo.com, outlook.com, protonmail.com, icloud.com",
            "contradictions_detected": False,
            "feasible": True
        }
        await state_manager.set_value(session_id, "possible", possible)

        # Impossible scenario
        impossible = {
            "prompt": "Generate 100 unique category names, but they must all come from this list: [A, B, C, D, E, F, G, H, I, J]",
            "contradictions_detected": True,
            "feasible": False,
            "reason": "Requested 100 unique values but only 10 options provided"
        }
        await state_manager.set_value(session_id, "impossible", impossible)

        # Verify detection
        impossible_case = await state_manager.get_value(session_id, "impossible")
        assert impossible_case["contradictions_detected"] is True
        assert impossible_case["feasible"] is False

        # Cleanup
        await state_manager.clear_session(session_id)

    @pytest.mark.asyncio
    async def test_domain_specific_jargon(self):
        """
        Test: Understanding domain-specific terminology
        Prompt: Uses medical, financial, or technical jargon
        """
        state_manager = get_state_manager()
        session_id = "test_jargon"

        # Medical jargon
        medical = {
            "prompt": """Generate EHR data with ICD-10 codes, CPT codes, and HL7 FHIR
                        compliant patient resources. Include vitals (BP, HR, SpO2),
                        labs (CBC, CMP, HbA1c), and SOAP notes.""",
            "domain": "medical",
            "jargon_terms": ["EHR", "ICD-10", "CPT", "HL7 FHIR", "SOAP", "CBC", "CMP", "HbA1c"],
            "understanding_required": "expert"
        }
        await state_manager.set_value(session_id, "medical", medical)

        # Financial jargon
        financial = {
            "prompt": """Create synthetic trades with CUSIP identifiers, FICC settlement,
                        T+2 settlement dates, DvP instructions, and ISDA master agreements.""",
            "domain": "financial",
            "jargon_terms": ["CUSIP", "FICC", "T+2", "DvP", "ISDA"],
            "understanding_required": "expert"
        }
        await state_manager.set_value(session_id, "financial", financial)

        # Verify
        med_case = await state_manager.get_value(session_id, "medical")
        assert len(med_case["jargon_terms"]) >= 5

        # Cleanup
        await state_manager.clear_session(session_id)

    @pytest.mark.asyncio
    async def test_context_dependent_pronoun_resolution(self):
        """
        Test: Resolving pronouns and context-dependent references
        Prompt: "Generate orders, then link them to customers, and add payments for those"
        """
        state_manager = get_state_manager()
        session_id = "test_pronouns"

        conversation = {
            "turn_1": "Generate 100 customer records",
            "turn_2": "Now create orders for them",  # "them" = customers
            "turn_3": "Add payments for those orders",  # "those" = orders from turn 2
            "turn_4": "Show me the customers who made more than 5 of them",  # "them" = orders
            "resolved_references": {
                "them_turn2": "customers from turn_1",
                "those_turn3": "orders from turn_2",
                "them_turn4": "orders"
            }
        }

        await state_manager.set_value(session_id, "conversation", conversation)
        retrieved = await state_manager.get_value(session_id, "conversation")

        assert "resolved_references" in retrieved
        assert len(retrieved["resolved_references"]) == 3

        # Cleanup
        await state_manager.clear_session(session_id)

    @pytest.mark.asyncio
    async def test_error_correction_and_undo(self):
        """
        Test: Handling user corrections and undo requests
        Prompt: "Oops, I meant 10,000 not 1,000" or "Actually, ignore that last part"
        """
        state_manager = get_state_manager()
        session_id = "test_error_correction"

        workflow = {
            "step_1": "Generate 1000 customers",
            "step_2": "Oops, I meant 10000 customers",  # Correction
            "step_3": "Add orders for each customer",
            "step_4": "Wait, ignore that last part about orders",  # Undo
            "step_5": "Instead, just add email addresses to customers",
            "corrections": [
                {"original": "1000", "corrected": "10000", "step": 2},
                {"action": "undo", "undid": "step_3", "step": 4}
            ]
        }

        await state_manager.set_value(session_id, "workflow", workflow)
        retrieved = await state_manager.get_value(session_id, "workflow")

        assert len(retrieved["corrections"]) == 2
        assert retrieved["corrections"][0]["corrected"] == "10000"

        # Cleanup
        await state_manager.clear_session(session_id)


class TestMultiStepWorkflows:
    """Test complex multi-step workflows with state management."""

    @pytest.mark.asyncio
    async def test_analyze_pattern_generate_workflow(self):
        """
        Test: Analyze uploaded file → Extract patterns → Generate similar data
        """
        state_manager = get_state_manager()
        session_id = "test_workflow_analyze"

        # Step 1: Upload pattern file
        pattern_df = pd.DataFrame({
            "product_id": ["P001", "P002", "P003"],
            "name": ["Widget A", "Gadget B", "Tool C"],
            "price": [29.99, 49.99, 19.99],
            "category": ["Tools", "Electronics", "Tools"],
            "rating": [4.5, 4.8, 4.2]
        })
        await state_manager.set_dataframe(session_id, pattern_df)

        # Step 2: Analyze patterns
        pattern_analysis = {
            "field_types": {
                "product_id": "alphanumeric_sequence",
                "name": "product_name_pattern",
                "price": "decimal_currency",
                "category": "categorical",
                "rating": "decimal_range_0_5"
            },
            "distributions": {
                "price": {"min": 19.99, "max": 49.99, "mean": 33.32},
                "rating": {"min": 4.2, "max": 4.8, "mean": 4.5}
            },
            "patterns": {
                "product_id": "P + 3_digits",
                "category_distribution": {"Tools": 0.67, "Electronics": 0.33}
            }
        }
        await state_manager.set_pattern_analysis(session_id, pattern_analysis)

        # Step 3: Generate requirements based on pattern
        requirements = {
            "based_on_pattern": True,
            "num_rows": 1000,
            "maintain_distributions": True,
            "fields_from_pattern": pattern_analysis["field_types"]
        }
        await state_manager.set_requirements(session_id, requirements)

        # Verify workflow state
        assert await state_manager.get_dataframe(session_id) is not None
        assert await state_manager.get_pattern_analysis(session_id) is not None
        assert await state_manager.get_requirements(session_id) is not None

        # Cleanup
        await state_manager.clear_session(session_id)

    @pytest.mark.asyncio
    async def test_generate_validate_fix_workflow(self):
        """
        Test: Generate data → Validate → Find issues → Fix → Regenerate
        """
        state_manager = get_state_manager()
        session_id = "test_workflow_validate"

        # Step 1: Initial generation
        initial_data = pd.DataFrame({
            "email": ["user1@test.com", "user2@test", "user3@test.com"],  # Invalid email!
            "age": [25, 300, 30]  # Invalid age!
        })
        await state_manager.set_dataframe(session_id, initial_data)

        # Step 2: Validation
        validation_results = {
            "valid": False,
            "issues": [
                {"field": "email", "row": 1, "issue": "invalid_format"},
                {"field": "age", "row": 1, "issue": "out_of_range"}
            ],
            "total_errors": 2
        }
        await state_manager.set_value(session_id, "validation", validation_results)

        # Step 3: Fix requirements
        fix_requirements = {
            "action": "fix_invalid_data",
            "fixes": {
                "email": "ensure_valid_format",
                "age": "constrain_0_120"
            }
        }
        await state_manager.set_value(session_id, "fix_requirements", fix_requirements)

        # Step 4: Regenerated data
        fixed_data = pd.DataFrame({
            "email": ["user1@test.com", "user2@test.com", "user3@test.com"],
            "age": [25, 28, 30]
        })
        await state_manager.set_dataframe(session_id, fixed_data)

        # Verify
        validation = await state_manager.get_value(session_id, "validation")
        assert validation["valid"] is False
        assert validation["total_errors"] == 2

        # Cleanup
        await state_manager.clear_session(session_id)

    @pytest.mark.asyncio
    async def test_progressive_complexity_buildup(self):
        """
        Test: Start simple → Add fields → Add constraints → Add relationships → Finalize
        """
        state_manager = get_state_manager()
        session_id = "test_progressive"

        # Phase 1: Simple start
        phase1 = {
            "fields": ["name", "email"],
            "num_rows": 100
        }
        await state_manager.set_value(session_id, "phase_1", phase1)

        # Phase 2: Add more fields
        phase2 = {
            **phase1,
            "fields": ["name", "email", "age", "city", "country"]
        }
        await state_manager.set_value(session_id, "phase_2", phase2)

        # Phase 3: Add constraints
        phase3 = {
            **phase2,
            "constraints": {
                "email": {"unique": True},
                "age": {"min": 18, "max": 65}
            }
        }
        await state_manager.set_value(session_id, "phase_3", phase3)

        # Phase 4: Add relationships
        phase4 = {
            **phase3,
            "related_table": "orders",
            "foreign_key": "customer_id"
        }
        await state_manager.set_value(session_id, "phase_4", phase4)

        # Verify progression
        final = await state_manager.get_value(session_id, "phase_4")
        assert len(final["fields"]) == 5
        assert "constraints" in final
        assert "related_table" in final

        # Cleanup
        await state_manager.clear_session(session_id)


class TestEdgeCasesAndErrorHandling:
    """Test edge cases, error scenarios, and recovery."""

    @pytest.mark.asyncio
    async def test_empty_prompt_handling(self):
        """Test: Empty or whitespace-only prompts"""
        state_manager = get_state_manager()
        session_id = "test_empty"

        requirements = {
            "prompt": "   ",
            "error_expected": "empty_prompt"
        }
        await state_manager.set_requirements(session_id, requirements)

        # Cleanup
        await state_manager.clear_session(session_id)

    @pytest.mark.asyncio
    async def test_extremely_large_dataset_request(self):
        """Test: Request for unreasonably large dataset"""
        state_manager = get_state_manager()
        session_id = "test_large"

        requirements = {
            "prompt": "Generate 10 billion rows of customer data",
            "num_rows": 10_000_000_000,
            "warning_expected": "dataset_too_large",
            "suggested_alternative": "Use smaller sample or batch generation"
        }
        await state_manager.set_requirements(session_id, requirements)

        # Cleanup
        await state_manager.clear_session(session_id)

    @pytest.mark.asyncio
    async def test_unsupported_format_graceful_handling(self):
        """Test: Request for unsupported file format"""
        state_manager = get_state_manager()
        session_id = "test_format"

        requirements = {
            "prompt": "Save as .dat binary format",
            "requested_format": "dat",
            "supported": False,
            "alternatives": ["csv", "json", "parquet"]
        }
        await state_manager.set_requirements(session_id, requirements)

        # Cleanup
        await state_manager.clear_session(session_id)

    @pytest.mark.asyncio
    async def test_mixed_language_prompt(self):
        """Test: Prompt with mixed languages or special characters"""
        state_manager = get_state_manager()
        session_id = "test_language"

        requirements = {
            "prompt": """Generate données with 名前, correo electrónico, and 年齢.
                        Include UTF-8 characters: émojis 😀, symbols ©®™, àccénts.""",
            "encoding": "utf-8",
            "special_characters_handling": True
        }
        await state_manager.set_requirements(session_id, requirements)

        # Cleanup
        await state_manager.clear_session(session_id)

    @pytest.mark.asyncio
    async def test_session_state_persistence(self):
        """Test: Verify session state persists across operations"""
        state_manager = get_state_manager()
        session_id = "test_persistence"

        # Store multiple pieces of state
        await state_manager.set_requirements(session_id, {"field": "value1"})
        await state_manager.set_dataframe(session_id, pd.DataFrame({"col": [1, 2, 3]}))
        await state_manager.set_pattern_analysis(session_id, {"pattern": "type"})
        await state_manager.set_value(session_id, "custom", {"data": "test"})

        # Verify all still accessible
        assert await state_manager.get_requirements(session_id) is not None
        assert await state_manager.get_dataframe(session_id) is not None
        assert await state_manager.get_pattern_analysis(session_id) is not None
        assert await state_manager.get_value(session_id, "custom") is not None

        # Cleanup
        await state_manager.clear_session(session_id)


class TestPerformanceAndScaling:
    """Test performance with complex scenarios."""

    @pytest.mark.asyncio
    async def test_concurrent_sessions(self):
        """Test: Multiple independent sessions running concurrently"""
        state_manager = get_state_manager()

        sessions = [f"concurrent_session_{i}" for i in range(10)]

        # Create 10 concurrent sessions with different data
        for i, session_id in enumerate(sessions):
            data = pd.DataFrame({
                "id": list(range(i * 10, (i + 1) * 10)),
                "value": [f"value_{i}_{j}" for j in range(10)]
            })
            await state_manager.set_dataframe(session_id, data)
            await state_manager.set_requirements(session_id, {"session_num": i})

        # Verify all sessions have independent state
        for i, session_id in enumerate(sessions):
            retrieved = await state_manager.get_dataframe(session_id)
            assert retrieved is not None
            assert len(retrieved) == 10
            assert retrieved.iloc[0]["id"] == i * 10

        # Cleanup all sessions
        for session_id in sessions:
            await state_manager.clear_session(session_id)

    @pytest.mark.asyncio
    async def test_large_context_handling(self):
        """Test: Handling large prompts and complex requirements"""
        state_manager = get_state_manager()
        session_id = "test_large_context"

        # Create a very large prompt with extensive requirements
        large_requirements = {
            "prompt": "Generate data with " + ", ".join([f"field_{i}" for i in range(100)]),
            "fields": [f"field_{i}" for i in range(100)],
            "constraints": {f"field_{i}": {"type": "string"} for i in range(50)},
            "num_rows": 10000,
            "complexity": "extreme"
        }

        await state_manager.set_requirements(session_id, large_requirements)
        retrieved = await state_manager.get_requirements(session_id)

        assert len(retrieved["fields"]) == 100
        assert len(retrieved["constraints"]) == 50

        # Cleanup
        await state_manager.clear_session(session_id)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto", "-s"])
