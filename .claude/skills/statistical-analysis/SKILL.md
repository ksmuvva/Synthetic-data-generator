# Statistical Analysis Skill

## Description
Deep statistical pattern recognition and analysis for synthetic data generation. Provides advanced statistical methods for pattern detection, distribution matching, and correlation analysis.

## Purpose
This custom skill enhances the synthetic data generator with:
- Advanced statistical pattern detection
- Distribution analysis and matching
- Correlation and dependency analysis
- Time-series pattern recognition
- Multivariate statistical analysis

## When to Use
Use this skill when:
- Analyzing complex data patterns
- Detecting distributions and correlations
- Matching statistical properties of source data
- Identifying hidden patterns and relationships
- Performing deep statistical validation

## Capabilities

### 1. Distribution Analysis
- **Univariate Distributions**: Identify normal, exponential, uniform, Poisson, etc.
- **Goodness of Fit**: Chi-square, Kolmogorov-Smirnov tests
- **Parameter Estimation**: ML and Bayesian parameter estimation
- **Distribution Comparison**: Compare synthetic vs source distributions
- **Mixture Models**: Detect and model mixture distributions

### 2. Correlation Analysis
- **Pearson Correlation**: Linear relationships between variables
- **Spearman Correlation**: Monotonic relationships
- **Kendall's Tau**: Rank correlations
- **Partial Correlation**: Control for confounding variables
- **Canonical Correlation**: Relationships between sets of variables

### 3. Time-Series Analysis
- **Trend Detection**: Identify linear and non-linear trends
- **Seasonality**: Detect seasonal patterns
- **Autocorrelation**: ACF and PACF analysis
- **Stationarity Tests**: ADF and KPSS tests
- **Forecasting Models**: ARIMA, exponential smoothing

### 4. Multivariate Analysis
- **Principal Component Analysis (PCA)**: Dimensionality reduction
- **Factor Analysis**: Identify latent factors
- **Cluster Analysis**: Detect natural groupings
- **Discriminant Analysis**: Classification patterns
- **MANOVA**: Multivariate analysis of variance

### 5. Pattern Detection
- **Outlier Detection**: Statistical outliers (Z-score, IQR, isolation forest)
- **Anomaly Detection**: Unusual patterns and behaviors
- **Dependency Detection**: Functional dependencies between fields
- **Constraint Inference**: Infer implicit constraints
- **Rule Mining**: Extract association rules

## Usage Instructions

### Step 1: Perform Statistical Analysis
```python
# Use with deep_analyze_pattern or analyze_pattern tools
analysis_result = await deep_analyze_pattern_tool({
    "file_path": "pattern_data.csv",
    "analysis_depth": "comprehensive",
    "enable_statistical_analysis": True  # Activates this skill
})
```

### Step 2: Access Statistical Insights
```python
statistics = analysis_result["statistics"]

# Distribution information
distributions = statistics["distributions"]
for field, dist_info in distributions.items():
    print(f"{field}: {dist_info['type']} "
          f"(params: {dist_info['parameters']})")

# Correlation matrix
correlations = statistics["correlations"]
print(f"Strong correlations: {correlations['strong_pairs']}")

# Time-series patterns
if statistics.get("temporal_patterns"):
    temporal = statistics["temporal_patterns"]
    print(f"Trend: {temporal['trend']}")
    print(f"Seasonality: {temporal['seasonality']}")
```

### Step 3: Use for Generation
```python
# Statistical patterns automatically guide generation
generated_data = await generate_with_modes_tool({
    "requirements": requirements,
    "num_rows": 10000,
    "pattern_blueprint": pattern_blueprint,  # Contains statistical analysis
    "mode": "exact_match"  # Uses statistical patterns for matching
})
```

## Statistical Methods

### Distribution Identification
```python
# Algorithm for distribution detection:
1. Calculate descriptive statistics (mean, std, skew, kurtosis)
2. Plot histogram and Q-Q plots
3. Test against common distributions:
   - Normal: Shapiro-Wilk test
   - Exponential: Kolmogorov-Smirnov test
   - Uniform: Chi-square test
   - Poisson: Dispersion test
4. Estimate parameters using Maximum Likelihood
5. Select best-fit distribution (lowest AIC/BIC)
```

### Correlation Detection
```python
# Multi-method correlation analysis:
1. Compute Pearson correlation matrix
2. Compute Spearman rank correlation
3. Test significance (p-value < 0.05)
4. Identify strong correlations (|r| > 0.7)
5. Detect non-linear relationships (mutual information)
6. Build correlation graph for dependencies
```

### Time-Series Pattern Recognition
```python
# Time-series decomposition:
1. Detect time column (datetime fields)
2. Decompose: Trend + Seasonal + Residual
3. Test for stationarity (ADF test)
4. Calculate autocorrelation (ACF/PACF)
5. Identify seasonality period
6. Fit appropriate model (ARIMA, SARIMA)
```

## Statistical Outputs

### Distribution Report
```json
{
  "field": "age",
  "distribution": {
    "type": "normal",
    "parameters": {
      "mean": 35.6,
      "std": 12.3
    },
    "goodness_of_fit": {
      "test": "shapiro-wilk",
      "statistic": 0.987,
      "p_value": 0.142,
      "conclusion": "Cannot reject normality"
    },
    "confidence_interval_95": [33.8, 37.4]
  }
}
```

### Correlation Report
```json
{
  "correlations": {
    "strong_pairs": [
      {
        "field1": "years_experience",
        "field2": "salary",
        "pearson": 0.85,
        "spearman": 0.82,
        "p_value": 0.0001,
        "significance": "highly_significant"
      }
    ],
    "weak_pairs": [...],
    "non_linear": [...]
  },
  "dependency_graph": {
    "nodes": ["field1", "field2", ...],
    "edges": [{"source": "field1", "target": "field2", "weight": 0.85}]
  }
}
```

### Time-Series Report
```json
{
  "temporal_analysis": {
    "trend": {
      "type": "linear",
      "direction": "increasing",
      "slope": 2.3,
      "r_squared": 0.87
    },
    "seasonality": {
      "detected": true,
      "period": "monthly",
      "strength": 0.65
    },
    "stationarity": {
      "adf_test": {
        "statistic": -3.45,
        "p_value": 0.009,
        "conclusion": "stationary"
      }
    },
    "autocorrelation": {
      "lag_1": 0.72,
      "lag_12": 0.45,
      "significant_lags": [1, 2, 12, 24]
    }
  }
}
```

## Integration with Generation

### Exact Distribution Matching
```python
# When mode='exact_match', the generator:
1. Uses detected distribution type and parameters
2. Generates values from the exact distribution
3. Preserves correlations using Copula methods
4. Maintains statistical properties within 1% variance
```

### Realistic Variants
```python
# When mode='realistic_variant', the generator:
1. Uses similar distribution family
2. Adjusts parameters slightly (±20%)
3. Introduces natural variation
4. Preserves key correlations (>0.7)
```

### Statistical Validation
```python
# After generation, validates:
1. Distribution similarity (KS test)
2. Correlation preservation (correlation matrix comparison)
3. Statistical moments (mean, std, skew, kurtosis)
4. Time-series properties (if temporal data)
```

## Advanced Features

### 1. Mixture Model Detection
```python
# Automatically detects mixture distributions:
- Gaussian Mixture Models (GMM)
- Mixture of exponentials
- Multi-modal distributions
- Generates from appropriate mixture
```

### 2. Copula-based Generation
```python
# Preserves complex dependencies:
- Gaussian copula for linear dependencies
- T-copula for heavy-tailed dependencies
- Archimedean copulas for asymmetric dependencies
- Maintains marginal distributions and correlations
```

### 3. Conditional Distribution Modeling
```python
# Models conditional relationships:
- P(Y|X) conditional distributions
- Regression-based generation
- Decision tree-based generation
- Neural network-based generation (for complex patterns)
```

## Performance Optimization

- **Sampling**: Large datasets sampled for analysis (max 100K rows)
- **Caching**: Statistical results cached per session
- **Parallel**: Independent analyses run in parallel
- **Progressive**: Can analyze incrementally for large files
- **GPU Acceleration**: For complex statistical computations (optional)

## Configuration

### Settings
```yaml
statistical_analysis:
  distribution_tests:
    - normal
    - exponential
    - uniform
    - poisson
    - gamma
    - beta
  significance_level: 0.05
  correlation_threshold: 0.7
  outlier_method: "isolation_forest"
  max_sample_size: 100000
  enable_time_series: true
  enable_multivariate: true
```

### Thresholds
```yaml
thresholds:
  strong_correlation: 0.7
  moderate_correlation: 0.5
  weak_correlation: 0.3
  goodness_of_fit_alpha: 0.05
  outlier_zscore: 3.0
```

## Best Practices

1. **Sample Size**: Use at least 100 samples for reliable statistics
2. **Outlier Handling**: Remove outliers before distribution fitting
3. **Correlation Interpretation**: Check for spurious correlations
4. **Time-Series**: Ensure sufficient temporal data points
5. **Validation**: Always validate statistical properties after generation
6. **Domain Knowledge**: Combine statistical analysis with domain expertise
7. **Iterative Refinement**: Iterate on generation based on validation

## Common Patterns Detected

### 1. E-commerce Data
- **Purchase Amount**: Log-normal distribution
- **Customer Age**: Normal distribution (25-65)
- **Purchase Frequency**: Poisson distribution
- **Correlation**: Age vs Purchase Amount (0.3-0.5)

### 2. Financial Data
- **Stock Returns**: Student-t distribution
- **Trading Volume**: Log-normal distribution
- **Time-Series**: GARCH effects, autocorrelation
- **Correlation**: Multi-asset correlations (0.4-0.8)

### 3. Healthcare Data
- **Patient Age**: Mixture of normal distributions
- **Lab Values**: Normal with outliers
- **Treatment Duration**: Exponential distribution
- **Correlation**: Comorbidities (complex network)

## Error Handling

- **Insufficient Data**: Warn if sample size < 30
- **Non-numeric Data**: Skip categorical fields
- **Missing Values**: Report missing data percentage
- **Distribution Fit Failure**: Fall back to empirical distribution
- **Correlation Issues**: Handle multicollinearity

## References

- **Statistical Tests**: scipy.stats library
- **Distribution Fitting**: distfit, fitter packages
- **Time-Series**: statsmodels library
- **Multivariate**: scikit-learn library
- **Theory**: "Statistical Data Analysis" by G. Cowan

## Support

For statistical analysis issues:
1. Check sample size is sufficient
2. Verify data quality (no missing/invalid values)
3. Review statistical test assumptions
4. Consult documentation for interpretation
5. Consider domain-specific patterns
