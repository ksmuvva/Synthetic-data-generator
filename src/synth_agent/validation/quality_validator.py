"""
Quality Validation for Synthetic Data.

Validates generated data against original patterns:
- Statistical similarity
- Constraint compliance
- Distribution matching
- No data leakage
- Diversity checks
"""

import json
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from scipy import stats
from scipy.spatial.distance import jensenshannon
import structlog

logger = structlog.get_logger(__name__)


class QualityValidator:
    """
    Validates quality of synthetic data against original patterns.
    """

    def __init__(self, config: Optional[Any] = None):
        """
        Initialize quality validator.

        Args:
            config: Configuration object
        """
        self.config = config

    async def validate(
        self,
        generated_df: pd.DataFrame,
        pattern_blueprint: Dict[str, Any],
        original_df: Optional[pd.DataFrame] = None,
    ) -> Dict[str, Any]:
        """
        Comprehensive quality validation of generated data.

        Args:
            generated_df: Generated synthetic data
            pattern_blueprint: Pattern blueprint from analysis
            original_df: Optional original data for comparison

        Returns:
            Validation report with scores and details
        """
        logger.info("Starting quality validation", rows=len(generated_df))

        validation_report = {
            "overall_score": 0.0,
            "passed": False,
            "validation_timestamp": pd.Timestamp.now().isoformat(),
            "checks": {
                "statistical_similarity": {},
                "constraint_compliance": {},
                "distribution_matching": {},
                "data_leakage": {},
                "diversity": {},
            },
            "recommendations": [],
        }

        # Check 1: Statistical Similarity
        logger.info("Checking statistical similarity")
        stat_check = await self._check_statistical_similarity(
            generated_df,
            pattern_blueprint.get("statistics", {}),
            variance_threshold=0.05,  # ±5%
        )
        validation_report["checks"]["statistical_similarity"] = stat_check

        # Check 2: Constraint Compliance
        logger.info("Checking constraint compliance")
        constraint_check = await self._check_constraints(
            generated_df,
            pattern_blueprint.get("constraints", {}),
        )
        validation_report["checks"]["constraint_compliance"] = constraint_check

        # Check 3: Distribution Matching
        logger.info("Checking distribution matching")
        dist_check = await self._check_distribution_matching(
            generated_df,
            pattern_blueprint.get("statistics", {}),
        )
        validation_report["checks"]["distribution_matching"] = dist_check

        # Check 4: Data Leakage Detection
        if original_df is not None:
            logger.info("Checking for data leakage")
            leakage_check = await self._check_data_leakage(generated_df, original_df)
            validation_report["checks"]["data_leakage"] = leakage_check
        else:
            validation_report["checks"]["data_leakage"] = {
                "passed": True,
                "score": 1.0,
                "message": "No original data provided for leakage check",
            }

        # Check 5: Diversity
        logger.info("Checking diversity")
        diversity_check = await self._check_diversity(generated_df)
        validation_report["checks"]["diversity"] = diversity_check

        # Calculate overall score
        scores = []
        for check_name, check_result in validation_report["checks"].items():
            if "score" in check_result:
                scores.append(check_result["score"])

        validation_report["overall_score"] = float(np.mean(scores)) if scores else 0.0
        validation_report["passed"] = validation_report["overall_score"] >= 0.85  # 85% threshold

        # Generate recommendations
        validation_report["recommendations"] = self._generate_recommendations(validation_report)

        logger.info(
            "Quality validation complete",
            score=validation_report["overall_score"],
            passed=validation_report["passed"],
        )

        return validation_report

    async def _check_statistical_similarity(
        self,
        generated_df: pd.DataFrame,
        expected_stats: Dict[str, Any],
        variance_threshold: float = 0.05,
    ) -> Dict[str, Any]:
        """
        Check if statistics match expected patterns within threshold.
        """
        result = {
            "passed": True,
            "score": 1.0,
            "field_scores": {},
            "failures": [],
        }

        field_scores = []

        for field, expected in expected_stats.items():
            if field not in generated_df.columns:
                result["failures"].append(f"Field '{field}' missing in generated data")
                continue

            generated_col = generated_df[field]
            field_score = 1.0

            # Check numeric statistics
            if "mean" in expected and expected["mean"] is not None:
                gen_mean = generated_col.mean()
                exp_mean = expected["mean"]

                if exp_mean != 0:
                    mean_diff = abs(gen_mean - exp_mean) / abs(exp_mean)
                    if mean_diff > variance_threshold:
                        field_score *= 0.8
                        result["failures"].append(
                            f"Field '{field}': Mean differs by {mean_diff:.1%} "
                            f"(expected: {exp_mean:.2f}, got: {gen_mean:.2f})"
                        )

            if "std" in expected and expected["std"] is not None:
                gen_std = generated_col.std()
                exp_std = expected["std"]

                if exp_std != 0:
                    std_diff = abs(gen_std - exp_std) / abs(exp_std)
                    if std_diff > variance_threshold * 2:  # Allow more variance in std
                        field_score *= 0.9
                        result["failures"].append(
                            f"Field '{field}': StdDev differs by {std_diff:.1%}"
                        )

            # Check range
            if "min" in expected and "max" in expected:
                gen_min = generated_col.min()
                gen_max = generated_col.max()

                if gen_min < expected["min"] or gen_max > expected["max"]:
                    field_score *= 0.7
                    result["failures"].append(
                        f"Field '{field}': Values outside expected range "
                        f"[{expected['min']}, {expected['max']}]"
                    )

            result["field_scores"][field] = field_score
            field_scores.append(field_score)

        result["score"] = float(np.mean(field_scores)) if field_scores else 0.0
        result["passed"] = result["score"] >= 0.95  # 95% threshold for stats

        return result

    async def _check_constraints(
        self,
        generated_df: pd.DataFrame,
        constraints: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Check constraint compliance (required, unique, dependencies).
        """
        result = {
            "passed": True,
            "score": 1.0,
            "violations": [],
        }

        violations = []

        # Check required fields
        for field in constraints.get("required_fields", []):
            if field not in generated_df.columns:
                violations.append(f"Required field '{field}' is missing")
                continue

            null_count = generated_df[field].isnull().sum()
            if null_count > 0:
                violations.append(
                    f"Required field '{field}' has {null_count} null values"
                )

        # Check unique fields
        for field in constraints.get("unique_fields", []):
            if field not in generated_df.columns:
                continue

            duplicates = generated_df[field].duplicated().sum()
            if duplicates > 0:
                violations.append(
                    f"Unique field '{field}' has {duplicates} duplicate values"
                )

        # Check field dependencies
        for dep in constraints.get("dependencies", []):
            independent = dep.get("independent_field")
            dependent = dep.get("dependent_field")
            relationship = dep.get("relationship")

            if independent not in generated_df.columns or dependent not in generated_df.columns:
                continue

            if relationship == "less_than":
                violations_count = (
                    generated_df[independent] >= generated_df[dependent]
                ).sum()
                if violations_count > 0:
                    violations.append(
                        f"Dependency violation: '{dependent}' should be greater than '{independent}' "
                        f"({violations_count} violations)"
                    )

        result["violations"] = violations
        result["passed"] = len(violations) == 0
        result["score"] = 1.0 if len(violations) == 0 else 0.0

        return result

    async def _check_distribution_matching(
        self,
        generated_df: pd.DataFrame,
        expected_stats: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Check if distributions match expected patterns.
        """
        result = {
            "passed": True,
            "score": 1.0,
            "field_scores": {},
            "details": [],
        }

        field_scores = []

        for field, expected in expected_stats.items():
            if field not in generated_df.columns:
                continue

            generated_col = generated_df[field]

            # For categorical data, check frequency distribution
            if "frequency_distribution" in expected:
                exp_freq = expected["frequency_distribution"]
                gen_freq = generated_col.value_counts().to_dict()

                # Convert to probability distributions
                total_gen = sum(gen_freq.values())
                gen_probs = {k: v / total_gen for k, v in gen_freq.items()}

                total_exp = sum(exp_freq.values())
                exp_probs = {k: v / total_exp for k, v in exp_freq.items()}

                # Calculate Jensen-Shannon divergence
                all_keys = set(gen_probs.keys()) | set(exp_probs.keys())
                gen_dist = [gen_probs.get(k, 0) for k in all_keys]
                exp_dist = [exp_probs.get(k, 0) for k in all_keys]

                js_div = jensenshannon(gen_dist, exp_dist)
                similarity = 1.0 - min(js_div, 1.0)

                field_scores.append(similarity)
                result["field_scores"][field] = similarity

                if similarity < 0.90:
                    result["details"].append(
                        f"Field '{field}': Distribution similarity {similarity:.2%}"
                    )

        result["score"] = float(np.mean(field_scores)) if field_scores else 1.0
        result["passed"] = result["score"] >= 0.90

        return result

    async def _check_data_leakage(
        self,
        generated_df: pd.DataFrame,
        original_df: pd.DataFrame,
    ) -> Dict[str, Any]:
        """
        Check for exact matches with original data (data leakage).
        """
        result = {
            "passed": True,
            "score": 1.0,
            "leakage_detected": False,
            "leaked_rows": 0,
            "details": [],
        }

        # Check for exact row matches
        # Convert to string representation for comparison
        gen_rows = set(generated_df.apply(lambda x: tuple(x), axis=1))
        orig_rows = set(original_df.apply(lambda x: tuple(x), axis=1))

        leaked = gen_rows.intersection(orig_rows)
        leaked_count = len(leaked)

        if leaked_count > 0:
            result["leakage_detected"] = True
            result["leaked_rows"] = leaked_count
            result["passed"] = False
            result["score"] = 0.0
            result["details"].append(
                f"Found {leaked_count} exact matches with original data (data leakage)"
            )
        else:
            result["details"].append("No exact matches found - data is synthetic")

        return result

    async def _check_diversity(
        self,
        generated_df: pd.DataFrame,
    ) -> Dict[str, Any]:
        """
        Check diversity and avoid repetitive patterns.
        """
        result = {
            "passed": True,
            "score": 1.0,
            "field_diversity": {},
            "issues": [],
        }

        field_scores = []

        for column in generated_df.columns:
            col_data = generated_df[column]

            # Calculate diversity score
            unique_ratio = col_data.nunique() / len(col_data)
            field_scores.append(unique_ratio)
            result["field_diversity"][column] = {
                "unique_ratio": float(unique_ratio),
                "unique_count": int(col_data.nunique()),
                "total_count": len(col_data),
            }

            # Check for repetitive patterns
            if pd.api.types.is_string_dtype(col_data):
                # Check for repeated values
                value_counts = col_data.value_counts()
                max_freq = value_counts.iloc[0] if len(value_counts) > 0 else 0
                max_freq_ratio = max_freq / len(col_data)

                if max_freq_ratio > 0.5:  # More than 50% same value
                    result["issues"].append(
                        f"Field '{column}': Low diversity - "
                        f"{max_freq_ratio:.1%} of values are identical"
                    )

        result["score"] = float(np.mean(field_scores)) if field_scores else 0.0
        result["passed"] = result["score"] >= 0.30 and len(result["issues"]) == 0

        return result

    def _generate_recommendations(self, validation_report: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []

        # Statistical similarity recommendations
        stat_check = validation_report["checks"]["statistical_similarity"]
        if stat_check["score"] < 0.95:
            recommendations.append(
                "Consider adjusting generation parameters to better match statistical properties"
            )

        # Constraint compliance recommendations
        constraint_check = validation_report["checks"]["constraint_compliance"]
        if not constraint_check["passed"]:
            recommendations.append(
                "Fix constraint violations before using this data in production"
            )

        # Distribution matching recommendations
        dist_check = validation_report["checks"]["distribution_matching"]
        if dist_check["score"] < 0.90:
            recommendations.append(
                "Improve distribution matching by using pattern analysis in generation"
            )

        # Data leakage recommendations
        leakage_check = validation_report["checks"]["data_leakage"]
        if leakage_check.get("leakage_detected"):
            recommendations.append(
                "CRITICAL: Remove leaked data - do not use this synthetic data"
            )

        # Diversity recommendations
        diversity_check = validation_report["checks"]["diversity"]
        if diversity_check["score"] < 0.30:
            recommendations.append(
                "Increase diversity to avoid repetitive patterns"
            )

        if not recommendations:
            recommendations.append("Data quality is excellent - ready for use")

        return recommendations
