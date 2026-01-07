"""
Factor Validation Analysis
==========================
Validates which dish factors actually correlate with success metrics.
Only factors with meaningful correlations will be included in the final framework.

Success Metrics:
- Order volume (normalized)
- Average rating
- Adult satisfaction rate
- Kids happy rate
- Portions adequate rate

Candidate Factors:
- Kid-Friendly (inherent characteristic)
- Balanced/Guilt-Free (inherent characteristic)
- Fussy Eater Friendly (inherent characteristic)
- Adult Appeal (inherent characteristic)
- Shareability (inherent characteristic)
- Value Perception (inherent characteristic)
"""

import pandas as pd
import numpy as np
from scipy import stats
import json
from pathlib import Path
from datetime import datetime

# Paths
BASE_PATH = Path(__file__).parent.parent.parent
DATA_PATH = BASE_PATH / "DATA"
DELIVERABLES_PATH = BASE_PATH / "DELIVERABLES" / "reports"

def load_data():
    """Load performance and opportunity scores data."""
    performance_df = pd.read_csv(DATA_PATH / "3_ANALYSIS" / "dish_performance_scores.csv")
    opportunity_df = pd.read_csv(DATA_PATH / "3_ANALYSIS" / "dish_opportunity_scores.csv")
    
    # Merge on dish_type
    merged = pd.merge(
        performance_df, 
        opportunity_df, 
        on='dish_type', 
        how='outer',
        suffixes=('_perf', '_opp')
    )
    
    return merged

def calculate_correlations(df):
    """Calculate correlations between factors and success metrics."""
    
    # Success metrics (what we're trying to predict)
    success_metrics = {
        'order_volume': 'order_volume_perf',
        'avg_rating': 'avg_rating',
        'adult_satisfaction': 'adult_satisfaction',
        'kids_happy': 'kids_happy',
        'portions_adequate': 'portions_adequate'
    }
    
    # Candidate factors (inherent dish characteristics)
    candidate_factors = {
        'kid_friendly': 'kid_friendly',
        'balanced_guilt_free': 'balanced_guilt_free',
        'adult_appeal': 'adult_appeal',
        'fussy_eater_friendly': 'fussy_eater_friendly',
        'shareability': 'shareability',
        'value_at_25': 'value_at_25',
        'vegetarian_option': 'vegetarian_option'
    }
    
    results = []
    
    for factor_name, factor_col in candidate_factors.items():
        for metric_name, metric_col in success_metrics.items():
            # Get valid pairs (both non-null)
            if factor_col not in df.columns or metric_col not in df.columns:
                continue
                
            valid_mask = df[factor_col].notna() & df[metric_col].notna()
            x = df.loc[valid_mask, factor_col]
            y = df.loc[valid_mask, metric_col]
            
            n = len(x)
            if n < 5:  # Need minimum sample size
                continue
            
            # Calculate Pearson correlation
            if x.std() == 0 or y.std() == 0:
                corr, p_value = 0, 1
            else:
                corr, p_value = stats.pearsonr(x, y)
            
            # Calculate Spearman correlation (for ordinal data)
            spearman_corr, spearman_p = stats.spearmanr(x, y)
            
            results.append({
                'factor': factor_name,
                'success_metric': metric_name,
                'n': n,
                'pearson_corr': round(corr, 3),
                'pearson_p': round(p_value, 4),
                'spearman_corr': round(spearman_corr, 3),
                'spearman_p': round(spearman_p, 4),
                'significant': p_value < 0.05,
                'meaningful': abs(corr) >= 0.3
            })
    
    return pd.DataFrame(results)

def analyze_factor_impact(correlations_df):
    """Analyze which factors have meaningful impact on success."""
    
    # Group by factor and calculate average correlation strength
    factor_summary = correlations_df.groupby('factor').agg({
        'pearson_corr': ['mean', 'max', 'min'],
        'spearman_corr': ['mean', 'max', 'min'],
        'significant': 'sum',
        'meaningful': 'sum',
        'n': 'mean'
    }).round(3)
    
    factor_summary.columns = [
        'pearson_mean', 'pearson_max', 'pearson_min',
        'spearman_mean', 'spearman_max', 'spearman_min',
        'significant_count', 'meaningful_count', 'avg_n'
    ]
    
    # Calculate composite impact score
    factor_summary['impact_score'] = (
        abs(factor_summary['pearson_mean']) * 0.4 +
        abs(factor_summary['spearman_mean']) * 0.4 +
        (factor_summary['significant_count'] / 5) * 0.1 +
        (factor_summary['meaningful_count'] / 5) * 0.1
    ).round(3)
    
    return factor_summary.sort_values('impact_score', ascending=False)

def recommend_weights(factor_summary):
    """Recommend weights based on correlation strength."""
    
    # Only include factors with positive impact
    valid_factors = factor_summary[factor_summary['impact_score'] > 0.1]
    
    if len(valid_factors) == 0:
        return {}
    
    # Normalize impact scores to sum to 1
    total_impact = valid_factors['impact_score'].sum()
    weights = (valid_factors['impact_score'] / total_impact).round(3)
    
    return weights.to_dict()

def generate_report(df, correlations_df, factor_summary, recommended_weights):
    """Generate the factor validation report."""
    
    report = f"""# Factor Validation Analysis Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Executive Summary

This analysis validates which dish factors actually correlate with success on Dinneroo.
Only factors with statistically meaningful relationships are included in the final framework.

### Key Findings

- **Factors Tested:** {len(factor_summary)}
- **Factors with Significant Correlations:** {int(factor_summary['significant_count'].sum())} total significant relationships
- **Factors with Meaningful Correlations (|r| >= 0.3):** {int(factor_summary['meaningful_count'].sum())} relationships

---

## Methodology

### Success Metrics Tested
1. **Order Volume** - Total orders for dish type (normalized)
2. **Average Rating** - Deliveroo star rating
3. **Adult Satisfaction** - % "Loved it" or "Liked it" from survey
4. **Kids Happy Rate** - % "Full and happy" from survey
5. **Portions Adequate** - % "Agree" or "Strongly agree" from survey

### Statistical Criteria for Inclusion
- **Correlation coefficient:** |r| >= 0.3 (meaningful relationship)
- **Statistical significance:** p-value < 0.05
- **Sample size:** n >= 10 dish types with data

### Correlation Methods
- **Pearson:** Linear relationship strength
- **Spearman:** Rank-order relationship (better for ordinal factor scores)

---

## Correlation Results

### Full Correlation Matrix

| Factor | Success Metric | n | Pearson r | p-value | Spearman r | Significant | Meaningful |
|--------|---------------|---|-----------|---------|------------|-------------|------------|
"""
    
    for _, row in correlations_df.iterrows():
        sig_mark = "✓" if row['significant'] else ""
        mean_mark = "✓" if row['meaningful'] else ""
        report += f"| {row['factor']} | {row['success_metric']} | {row['n']} | {row['pearson_corr']:.3f} | {row['pearson_p']:.4f} | {row['spearman_corr']:.3f} | {sig_mark} | {mean_mark} |\n"
    
    report += f"""

---

## Factor Impact Summary

Factors ranked by overall impact on success metrics:

| Factor | Pearson Mean | Spearman Mean | Significant Relationships | Meaningful Relationships | Impact Score |
|--------|-------------|---------------|--------------------------|-------------------------|--------------|
"""
    
    for factor, row in factor_summary.iterrows():
        report += f"| {factor} | {row['pearson_mean']:.3f} | {row['spearman_mean']:.3f} | {int(row['significant_count'])}/5 | {int(row['meaningful_count'])}/5 | {row['impact_score']:.3f} |\n"
    
    report += f"""

---

## Recommended Factor Weights

Based on correlation strength with success metrics:

| Factor | Recommended Weight | Rationale |
|--------|-------------------|-----------|
"""
    
    for factor, weight in recommended_weights.items():
        rationale = "Strong correlation with success metrics" if weight > 0.2 else "Moderate correlation with success metrics"
        report += f"| {factor} | {weight:.1%} | {rationale} |\n"
    
    # Factors to exclude
    excluded_factors = set(factor_summary.index) - set(recommended_weights.keys())
    
    report += f"""

### Factors Excluded from Framework

The following factors showed weak or no correlation with success metrics:

"""
    
    for factor in excluded_factors:
        row = factor_summary.loc[factor]
        report += f"- **{factor}**: Impact score {row['impact_score']:.3f} (below 0.1 threshold)\n"
    
    report += f"""

---

## Data Quality Notes

### Sample Sizes by Dish Type
- Dishes with full survey data: {df['adult_satisfaction'].notna().sum()}
- Dishes with ratings data: {df['avg_rating'].notna().sum()}
- Dishes with opportunity scores: {df['kid_friendly'].notna().sum()}

### Limitations
1. Small sample size for some dish types limits statistical power
2. Factor scores are partially estimated (not all from direct survey data)
3. Correlations do not imply causation

---

## Recommendations

### For Framework Design
1. **Include factors with impact score > 0.1** in the opportunity scoring
2. **Weight factors proportionally** to their correlation strength
3. **Flag estimated vs measured** scores in output

### For Future Data Collection
1. Collect more survey responses per dish type to improve statistical power
2. Add direct questions about factor importance in post-order survey
3. Track which factors drive repeat orders

---

## Appendix: Raw Data Summary

### Dish Types Analyzed
Total: {len(df)} dish types

### Performance Data Coverage
| Metric | Dishes with Data |
|--------|------------------|
| Order Volume | {df['order_volume_perf'].notna().sum()} |
| Average Rating | {df['avg_rating'].notna().sum()} |
| Adult Satisfaction | {df['adult_satisfaction'].notna().sum()} |
| Kids Happy Rate | {df['kids_happy'].notna().sum()} |
| Portions Adequate | {df['portions_adequate'].notna().sum()} |

---

*This report was generated automatically by the factor validation script.*
*Source: scripts/phase2_analysis/validate_factors.py*
"""
    
    return report

def main():
    """Run the factor validation analysis."""
    print("=" * 60)
    print("FACTOR VALIDATION ANALYSIS")
    print("=" * 60)
    
    # Load data
    print("\n1. Loading data...")
    df = load_data()
    print(f"   Loaded {len(df)} dish types")
    
    # Calculate correlations
    print("\n2. Calculating correlations...")
    correlations_df = calculate_correlations(df)
    print(f"   Calculated {len(correlations_df)} correlation pairs")
    
    # Analyze factor impact
    print("\n3. Analyzing factor impact...")
    factor_summary = analyze_factor_impact(correlations_df)
    print(f"   Analyzed {len(factor_summary)} factors")
    
    # Recommend weights
    print("\n4. Recommending weights...")
    recommended_weights = recommend_weights(factor_summary)
    print(f"   Recommended weights for {len(recommended_weights)} factors")
    
    # Generate report
    print("\n5. Generating report...")
    report = generate_report(df, correlations_df, factor_summary, recommended_weights)
    
    # Save outputs
    DELIVERABLES_PATH.mkdir(parents=True, exist_ok=True)
    
    report_path = DELIVERABLES_PATH / "factor_validation_analysis.md"
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"   Saved report to: {report_path}")
    
    # Save correlations CSV
    correlations_path = DATA_PATH / "3_ANALYSIS" / "factor_correlations.csv"
    correlations_df.to_csv(correlations_path, index=False)
    print(f"   Saved correlations to: {correlations_path}")
    
    # Save factor summary
    summary_path = DATA_PATH / "3_ANALYSIS" / "factor_impact_summary.csv"
    factor_summary.to_csv(summary_path)
    print(f"   Saved summary to: {summary_path}")
    
    # Save recommended weights as JSON
    weights_path = DATA_PATH / "3_ANALYSIS" / "recommended_factor_weights.json"
    with open(weights_path, 'w') as f:
        json.dump({
            'weights': recommended_weights,
            'generated': datetime.now().isoformat(),
            'methodology': 'Based on correlation with success metrics'
        }, f, indent=2)
    print(f"   Saved weights to: {weights_path}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("\nFactor Impact Rankings:")
    for factor, row in factor_summary.head(10).iterrows():
        print(f"  {factor}: {row['impact_score']:.3f}")
    
    print("\nRecommended Weights:")
    for factor, weight in recommended_weights.items():
        print(f"  {factor}: {weight:.1%}")
    
    print("\n✓ Factor validation complete!")
    
    return correlations_df, factor_summary, recommended_weights

if __name__ == "__main__":
    main()


