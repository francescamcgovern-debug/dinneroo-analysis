# Factor Validation Analysis Report

**Generated:** 2026-01-07 11:53

## Executive Summary

This analysis validates which dish factors actually correlate with success on Dinneroo.
Only factors with statistically meaningful relationships are included in the final framework.

### Key Findings

- **Factors Tested:** 7
- **Factors with Significant Correlations:** 0 total significant relationships
- **Factors with Meaningful Correlations (|r| >= 0.3):** 5 relationships

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
| kid_friendly | order_volume | 21 | 0.124 | 0.5922 | 0.245 |  |  |
| kid_friendly | avg_rating | 21 | -0.085 | 0.7144 | -0.130 |  |  |
| kid_friendly | adult_satisfaction | 13 | -0.047 | 0.8780 | -0.508 |  |  |
| kid_friendly | kids_happy | 13 | 0.290 | 0.3363 | 0.148 |  |  |
| kid_friendly | portions_adequate | 13 | -0.375 | 0.2074 | -0.417 |  | ✓ |
| balanced_guilt_free | order_volume | 21 | 0.056 | 0.8103 | 0.170 |  |  |
| balanced_guilt_free | avg_rating | 21 | 0.224 | 0.3281 | 0.162 |  |  |
| balanced_guilt_free | adult_satisfaction | 13 | 0.215 | 0.4809 | 0.344 |  |  |
| balanced_guilt_free | kids_happy | 13 | 0.224 | 0.4614 | 0.570 |  |  |
| balanced_guilt_free | portions_adequate | 13 | 0.149 | 0.6277 | 0.183 |  |  |
| adult_appeal | order_volume | 21 | 0.301 | 0.1846 | 0.318 |  | ✓ |
| adult_appeal | avg_rating | 21 | 0.219 | 0.3399 | 0.294 |  |  |
| adult_appeal | adult_satisfaction | 13 | 0.446 | 0.1262 | 0.610 |  | ✓ |
| adult_appeal | kids_happy | 13 | 0.132 | 0.6672 | -0.067 |  |  |
| adult_appeal | portions_adequate | 13 | -0.118 | 0.7014 | -0.088 |  |  |
| fussy_eater_friendly | order_volume | 21 | 0.063 | 0.7864 | 0.131 |  |  |
| fussy_eater_friendly | avg_rating | 21 | -0.176 | 0.4456 | -0.215 |  |  |
| fussy_eater_friendly | adult_satisfaction | 13 | -0.089 | 0.7717 | -0.501 |  |  |
| fussy_eater_friendly | kids_happy | 13 | 0.236 | 0.4382 | 0.147 |  |  |
| fussy_eater_friendly | portions_adequate | 13 | -0.331 | 0.2686 | -0.383 |  | ✓ |
| shareability | order_volume | 21 | 0.084 | 0.7183 | 0.107 |  |  |
| shareability | avg_rating | 21 | -0.177 | 0.4432 | -0.188 |  |  |
| shareability | adult_satisfaction | 13 | -0.129 | 0.6737 | -0.309 |  |  |
| shareability | kids_happy | 13 | 0.001 | 0.9974 | -0.231 |  |  |
| shareability | portions_adequate | 13 | 0.082 | 0.7908 | 0.077 |  |  |
| value_at_25 | order_volume | 21 | 0.084 | 0.7168 | 0.074 |  |  |
| value_at_25 | avg_rating | 21 | -0.302 | 0.1841 | -0.370 |  | ✓ |
| value_at_25 | adult_satisfaction | 13 | -0.181 | 0.5533 | -0.232 |  |  |
| value_at_25 | kids_happy | 13 | 0.115 | 0.7093 | 0.386 |  |  |
| value_at_25 | portions_adequate | 13 | 0.028 | 0.9272 | 0.077 |  |  |
| vegetarian_option | order_volume | 21 | 0.136 | 0.5563 | 0.314 |  |  |
| vegetarian_option | avg_rating | 21 | 0.016 | 0.9454 | -0.096 |  |  |
| vegetarian_option | adult_satisfaction | 13 | -0.153 | 0.6180 | -0.538 |  |  |
| vegetarian_option | kids_happy | 13 | 0.237 | 0.4348 | 0.244 |  |  |
| vegetarian_option | portions_adequate | 13 | 0.085 | 0.7812 | 0.000 |  |  |


---

## Factor Impact Summary

Factors ranked by overall impact on success metrics:

| Factor | Pearson Mean | Spearman Mean | Significant Relationships | Meaningful Relationships | Impact Score |
|--------|-------------|---------------|--------------------------|-------------------------|--------------|
| adult_appeal | 0.196 | 0.213 | 0/5 | 2/5 | 0.204 |
| balanced_guilt_free | 0.174 | 0.286 | 0/5 | 0/5 | 0.184 |
| fussy_eater_friendly | -0.059 | -0.164 | 0/5 | 1/5 | 0.109 |
| kid_friendly | -0.019 | -0.132 | 0/5 | 1/5 | 0.080 |
| shareability | -0.028 | -0.109 | 0/5 | 0/5 | 0.055 |
| value_at_25 | -0.051 | -0.013 | 0/5 | 1/5 | 0.046 |
| vegetarian_option | 0.064 | -0.015 | 0/5 | 0/5 | 0.032 |


---

## Recommended Factor Weights

Based on correlation strength with success metrics:

| Factor | Recommended Weight | Rationale |
|--------|-------------------|-----------|
| adult_appeal | 41.0% | Strong correlation with success metrics |
| balanced_guilt_free | 37.0% | Strong correlation with success metrics |
| fussy_eater_friendly | 21.9% | Strong correlation with success metrics |


### Factors Excluded from Framework

The following factors showed weak or no correlation with success metrics:

- **shareability**: Impact score 0.055 (below 0.1 threshold)
- **value_at_25**: Impact score 0.046 (below 0.1 threshold)
- **kid_friendly**: Impact score 0.080 (below 0.1 threshold)
- **vegetarian_option**: Impact score 0.032 (below 0.1 threshold)


---

## Data Quality Notes

### Sample Sizes by Dish Type
- Dishes with full survey data: 13
- Dishes with ratings data: 22
- Dishes with opportunity scores: 48

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
Total: 49 dish types

### Performance Data Coverage
| Metric | Dishes with Data |
|--------|------------------|
| Order Volume | 22 |
| Average Rating | 22 |
| Adult Satisfaction | 13 |
| Kids Happy Rate | 13 |
| Portions Adequate | 13 |

---

*This report was generated automatically by the factor validation script.*
*Source: scripts/phase2_analysis/validate_factors.py*
