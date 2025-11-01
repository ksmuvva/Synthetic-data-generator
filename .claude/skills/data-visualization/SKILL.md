# Data Visualization Skill

## Description
Create charts, graphs, and visual representations of data patterns, quality metrics, and generation results.

## Purpose
This custom skill enhances the synthetic data generator with:
- Visual quality reports and dashboards
- Pattern visualization and comparison
- Distribution plots and histograms
- Correlation heatmaps and networks
- Interactive dashboards

## When to Use
Use this skill when:
- Creating visual quality reports
- Comparing synthetic vs source data distributions
- Visualizing correlation patterns
- Generating dashboards for stakeholders
- Presenting validation results visually

## Capabilities

### 1. Distribution Visualization
- **Histograms**: Frequency distributions with bins
- **Density Plots**: Smooth distribution curves
- **Q-Q Plots**: Quantile-quantile plots for distribution comparison
- **Box Plots**: Distribution summaries with quartiles
- **Violin Plots**: Combination of box and density plots
- **Overlay Plots**: Compare synthetic vs source distributions

### 2. Correlation Visualization
- **Heatmaps**: Correlation matrix heatmaps
- **Scatter Matrices**: Pairwise scatter plots
- **Network Graphs**: Dependency networks
- **Chord Diagrams**: Circular correlation visualization
- **Cluster Maps**: Hierarchical clustering with heatmaps

### 3. Time-Series Visualization
- **Line Charts**: Temporal trends and patterns
- **Decomposition Plots**: Trend, seasonal, residual components
- **ACF/PACF Plots**: Autocorrelation visualization
- **Seasonality Plots**: Seasonal pattern visualization
- **Forecast Plots**: Predictions with confidence intervals

### 4. Quality Visualization
- **Quality Dashboards**: Comprehensive quality overview
- **Score Cards**: Quality metrics as cards
- **Progress Bars**: Validation check progress
- **Radar Charts**: Multi-dimensional quality metrics
- **Comparison Charts**: Side-by-side comparisons

### 5. Statistical Visualization
- **Confidence Intervals**: Error bars and ranges
- **Statistical Tests**: Visual test results
- **P-value Plots**: Significance visualization
- **Effect Size Plots**: Statistical effect visualization
- **ROC Curves**: Classification performance (if applicable)

## Usage Instructions

### Step 1: Generate Visualizations
```python
# Automatically included in validation reports
validation_result = await validate_quality_tool({
    "session_id": session_id,
    "original_data_path": "source_data.csv",
    "generate_visualizations": True  # Activates this skill
})

# Visualizations saved to output/visualizations/
```

### Step 2: Create Custom Visualizations
```python
# For custom visualization requests
viz_request = {
    "visualization_type": "distribution_comparison",
    "fields": ["age", "salary", "experience"],
    "synthetic_data": synthetic_df,
    "source_data": source_df,
    "output_path": "comparison_charts.html"
}
```

### Step 3: Generate Dashboard
```python
# Create interactive dashboard
dashboard = {
    "title": "Synthetic Data Quality Report",
    "sections": [
        {"type": "score_card", "metrics": quality_scores},
        {"type": "distribution_comparison", "fields": key_fields},
        {"type": "correlation_heatmap", "data": correlation_matrix},
        {"type": "validation_summary", "results": validation_results}
    ],
    "output_format": "html"  # or "pdf", "png"
}
```

## Visualization Types

### 1. Distribution Comparison Plot
```python
# Overlays synthetic and source distributions
- Histogram with overlaid density curves
- Different colors for synthetic vs source
- Statistical test results displayed
- KS statistic and p-value shown
```

### 2. Correlation Heatmap
```python
# Side-by-side correlation matrices
- Source data correlation (left)
- Synthetic data correlation (right)
- Difference heatmap (optional)
- Hierarchical clustering
- Annotated with correlation values
```

### 3. Quality Dashboard
```python
# Comprehensive HTML dashboard with:
- Overall quality score (gauge chart)
- Individual check scores (progress bars)
- Distribution comparisons (histograms)
- Correlation heatmaps
- Validation summary table
- Recommendations list
```

### 4. Pattern Analysis Visualization
```python
# Pattern blueprint visualization:
- Schema diagram (fields and types)
- Distribution grid (all field distributions)
- Dependency graph (field relationships)
- Constraint visualization
- Business rules flowchart
```

## Chart Specifications

### Distribution Comparison
```json
{
  "chart_type": "histogram_overlay",
  "data": {
    "synthetic": [...],
    "source": [...]
  },
  "style": {
    "synthetic_color": "#2ecc71",
    "source_color": "#3498db",
    "alpha": 0.6,
    "bins": 30
  },
  "annotations": {
    "show_mean": true,
    "show_median": true,
    "show_std": true,
    "show_ks_test": true
  }
}
```

### Correlation Heatmap
```json
{
  "chart_type": "heatmap",
  "data": "correlation_matrix",
  "style": {
    "colormap": "RdYlGn",
    "vmin": -1,
    "vmax": 1,
    "annot": true,
    "fmt": ".2f"
  },
  "clustering": {
    "method": "ward",
    "metric": "euclidean"
  }
}
```

### Quality Dashboard
```json
{
  "dashboard": {
    "layout": "grid",
    "sections": [
      {
        "position": {"row": 0, "col": 0, "colspan": 2},
        "type": "header",
        "content": "Synthetic Data Quality Report"
      },
      {
        "position": {"row": 1, "col": 0},
        "type": "gauge",
        "metric": "overall_score",
        "title": "Overall Quality"
      },
      {
        "position": {"row": 1, "col": 1},
        "type": "score_cards",
        "metrics": ["statistical_similarity", "constraint_compliance"]
      },
      {
        "position": {"row": 2, "col": 0, "colspan": 2},
        "type": "distribution_grid",
        "fields": ["all"]
      }
    ]
  }
}
```

## Output Formats

### Static Formats
- **PNG**: High-resolution images (300 DPI)
- **SVG**: Scalable vector graphics
- **PDF**: Multi-page reports
- **JPEG**: Compressed images

### Interactive Formats
- **HTML**: Interactive dashboards with Plotly
- **Jupyter Notebook**: Embedded visualizations
- **Dashboard**: Standalone dashboard app

## Integration Points

### With Validation Tool
```python
# Automatically generates visualizations during validation
- Distribution comparison plots for each field
- Correlation heatmap comparison
- Quality score dashboard
- Validation summary charts
```

### With Pattern Analysis
```python
# Visualizes pattern analysis results
- Field distribution plots
- Correlation network graph
- Business rule flowcharts
- Schema diagrams
```

### With Generation Tool
```python
# Tracks generation progress visually
- Progress indicators
- Real-time quality metrics
- Distribution convergence plots
- Constraint satisfaction tracking
```

## Customization

### Themes
```yaml
themes:
  default:
    colors: ["#2ecc71", "#3498db", "#e74c3c", "#f39c12"]
    font: "Arial"
    background: "#ffffff"
  dark:
    colors: ["#1abc9c", "#3498db", "#e74c3c", "#f39c12"]
    font: "Roboto"
    background: "#2c3e50"
  professional:
    colors: ["#34495e", "#7f8c8d", "#95a5a6", "#bdc3c7"]
    font: "Helvetica"
    background: "#ecf0f1"
```

### Chart Styles
```yaml
chart_styles:
  histogram:
    alpha: 0.6
    edgecolor: "black"
    bins: "auto"
  heatmap:
    cmap: "RdYlGn"
    annot: true
    fmt: ".2f"
  scatter:
    s: 50
    alpha: 0.5
    edgecolors: "black"
```

## Best Practices

1. **Color Accessibility**: Use colorblind-friendly palettes
2. **Clear Labels**: Always label axes and provide legends
3. **Appropriate Scale**: Choose appropriate axis scales (linear, log)
4. **Reduce Clutter**: Avoid overcrowded visualizations
5. **Tell a Story**: Organize visualizations to tell a coherent story
6. **Interactive Elements**: Use tooltips and zoom for interactivity
7. **Export Quality**: Use high DPI for print-quality outputs

## Example Outputs

### Quality Dashboard HTML
```html
<!DOCTYPE html>
<html>
<head>
    <title>Synthetic Data Quality Report</title>
    <script src="plotly.min.js"></script>
</head>
<body>
    <h1>Quality Report - Customer Data</h1>
    <div id="overall-score">Score: 94.5%</div>
    <div id="distribution-charts">...</div>
    <div id="correlation-heatmap">...</div>
    <div id="validation-summary">...</div>
</body>
</html>
```

### Distribution Comparison PNG
```
File: age_distribution_comparison.png
Size: 1920x1080 pixels, 300 DPI
Contents:
- Overlaid histograms (synthetic vs source)
- Density curves
- Statistical annotations (mean, std, KS test)
- Legend
```

### Correlation Heatmap PDF
```
File: correlation_comparison.pdf
Pages: 2
Contents:
- Page 1: Source data correlation heatmap
- Page 2: Synthetic data correlation heatmap
- Annotations: Correlation values, clustering dendrograms
```

## Configuration

```yaml
data_visualization:
  default_format: "html"
  dpi: 300
  figure_size: [12, 8]
  style: "seaborn"
  theme: "default"
  interactive: true
  save_static_copies: true
  output_directory: "output/visualizations"
```

## Performance

- **Large Datasets**: Sample for visualization (max 10K points per plot)
- **Caching**: Cache generated plots
- **Lazy Loading**: Load interactive plots on demand
- **Compression**: Compress PNG outputs
- **Progressive**: Render plots progressively for large datasets

## Libraries Used

- **Matplotlib**: Static plots and charts
- **Seaborn**: Statistical visualizations
- **Plotly**: Interactive visualizations
- **Bokeh**: Interactive dashboards
- **Altair**: Declarative visualizations
- **NetworkX**: Network graphs

## Error Handling

- **Missing Data**: Skip fields with all missing values
- **Invalid Values**: Filter outliers for better visualization
- **Memory Issues**: Sample large datasets
- **Rendering Failures**: Fall back to simpler chart types
- **Format Issues**: Warn and use default format

## Support

For visualization issues:
1. Check output directory permissions
2. Verify sufficient memory for large plots
3. Review data quality (NaN, inf values)
4. Try different output formats
5. Reduce data size for testing
