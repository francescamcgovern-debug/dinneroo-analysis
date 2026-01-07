# Weight Rationale Document

**Generated:** 2026-01-07  
**Framework Version:** 2.0

## Executive Summary

This document explains why each weight was chosen in the Unified Dish Scoring Framework, backed by correlation analysis and data evidence.

**Key Decision:** Only factors with demonstrated impact on dish success (impact score > 0.1) are included in the framework.

---

## Framework Weight Summary

### Two-Track Structure

| Track | Weight | Rationale |
|-------|--------|-----------|
| **Performance** | 50% | Behavioral data is the strongest signal of actual demand |
| **Opportunity** | 50% | Enables scoring of dishes without performance data |

### Performance Track Components (50% total)

| Component | Effective Weight | Rationale |
|-----------|-----------------|-----------|
| Normalized Sales | 10% | Direct measure of demand |
| Zone Ranking Strength | 10% | Consistency across zones indicates universal appeal |
| Deliveroo Rating | 10% | Customer satisfaction signal |
| Repeat Intent | 5% | Forward-looking retention signal |
| Kids Full & Happy | 7.5% | Critical family success factor |
| Liked/Loved It | 7.5% | Adult satisfaction balance |

### Opportunity Track Components (50% total)

| Component | Effective Weight | Rationale |
|-----------|-----------------|-----------|
| Latent Demand | 25% | Captures unmet demand from multiple sources |
| Adult Appeal | 10.25% | Highest correlation with success (impact: 0.204) |
| Balanced/Guilt-Free | 9.25% | Strong correlation with satisfaction (impact: 0.184) |
| Fussy Eater Friendly | 5.5% | Just above threshold (impact: 0.109) |

---

## Factor Validation Evidence

### Correlation Analysis Results

We tested 7 candidate factors against 5 success metrics:
- Order volume (normalized)
- Average rating
- Adult satisfaction
- Kids happy rate
- Portions adequate

**Inclusion Criteria:**
- Impact score > 0.1
- Based on mean correlation strength + significance count

### Factors INCLUDED

#### 1. Adult Appeal
**Impact Score:** 0.204 (highest)

| Success Metric | Pearson r | Spearman r | n |
|----------------|-----------|------------|---|
| Order Volume | 0.301 | 0.318 | 21 |
| Adult Satisfaction | 0.446 | 0.610 | 13 |
| Average Rating | 0.219 | 0.294 | 21 |

**Why Included:** Strongest and most consistent correlation with success metrics. Dishes that adults genuinely enjoy perform better.

**Weight Calculation:** 0.204 / (0.204 + 0.184 + 0.109) × 25% = **10.25%**

---

#### 2. Balanced/Guilt-Free
**Impact Score:** 0.184

| Success Metric | Pearson r | Spearman r | n |
|----------------|-----------|------------|---|
| Kids Happy Rate | 0.224 | 0.570 | 13 |
| Adult Satisfaction | 0.215 | 0.344 | 13 |
| Average Rating | 0.224 | 0.162 | 21 |

**Why Included:** Strong Spearman correlation with kids happy rate (0.570) suggests balanced meals lead to happier kids. Aligns with Dinneroo's midweek positioning.

**Weight Calculation:** 0.184 / (0.204 + 0.184 + 0.109) × 25% = **9.25%**

---

#### 3. Fussy Eater Friendly
**Impact Score:** 0.109

| Success Metric | Pearson r | Spearman r | n |
|----------------|-----------|------------|---|
| Kids Happy Rate | 0.236 | 0.147 | 13 |
| Portions Adequate | -0.331 | -0.383 | 13 |
| Order Volume | 0.063 | 0.131 | 21 |

**Why Included:** Just above threshold. Supported by qualitative evidence: 1,037 mentions of fussy eaters as a barrier in dropoff survey.

**Weight Calculation:** 0.109 / (0.204 + 0.184 + 0.109) × 25% = **5.5%**

---

### Factors EXCLUDED

#### Kid-Friendly
**Impact Score:** 0.080 (below 0.1 threshold)

| Success Metric | Pearson r | Spearman r | n |
|----------------|-----------|------------|---|
| Kids Happy Rate | 0.290 | 0.148 | 13 |
| Order Volume | 0.124 | 0.245 | 21 |
| Portions Adequate | -0.375 | -0.417 | 13 |

**Why Excluded:** Surprisingly weak correlation with success metrics. The negative correlation with portions adequate suggests "kid-friendly" dishes may be perceived as smaller portions. The factor may be too generic - "fussy eater friendly" captures the more actionable signal.

---

#### Shareability
**Impact Score:** 0.055

| Success Metric | Pearson r | Spearman r | n |
|----------------|-----------|------------|---|
| All metrics | Near zero | Near zero | 21 |

**Why Excluded:** No meaningful correlation with any success metric. Shareability may be a nice-to-have but doesn't drive dish success.

---

#### Value at £25
**Impact Score:** 0.046

| Success Metric | Pearson r | Spearman r | n |
|----------------|-----------|------------|---|
| Average Rating | -0.302 | -0.370 | 21 |

**Why Excluded:** Negative correlation with rating suggests perceived "value" dishes may actually underperform on quality. This is counterintuitive but data-driven.

---

#### Vegetarian Option
**Impact Score:** 0.032

| Success Metric | Pearson r | Spearman r | n |
|----------------|-----------|------------|---|
| All metrics | Near zero or negative | Near zero | 21 |

**Why Excluded:** No meaningful correlation. While vegetarian options are important for inclusion, they don't drive overall dish success on the platform.

---

#### Portion Flexibility & Customisation
**Why Excluded:** These are **partner-level attributes**, not dish-type attributes. A "Pizza" can have good or bad portion flexibility depending on which partner serves it. Scoring at dish-type level is not meaningful.

---

## Latent Demand Weight Rationale

**Total Weight:** 25% of unified score

### Source Weights Within Latent Demand

| Source | Weight | Rationale |
|--------|--------|-----------|
| Open-text mentions | 45% | Direct expression of unmet demand |
| OG Survey wishlist | 30% | Pre-launch stated preference |
| Barrier signals | 25% | Implicit demand from dropoff reasons |

**Why 25% Total:** Latent demand captures dishes that could succeed but aren't currently available. Without this, the framework would only optimize for existing dishes (survivorship bias).

---

## Comparison to Previous Framework

### Old Framework (v1.0)
- 10 factors, heavily survey-weighted
- Performance data: 5%
- Family fit factors: 87%
- No validation of factor impact

### New Framework (v2.0)
- 3 validated factors + latent demand
- Performance data: 50%
- Opportunity factors: 50%
- All factors validated through correlation analysis

### Key Improvements
1. **Balanced behavioral + survey data** (50/50 vs 5/95)
2. **Removed factors that don't impact success** (4 excluded)
3. **Removed partner-level factors** (portion flexibility, customisation)
4. **Added comprehensive latent demand** (captures unmet demand)
5. **Evidence-based weights** (correlation-driven)

---

## Sensitivity Analysis

### What if we changed the threshold?

| Threshold | Factors Included | Impact |
|-----------|-----------------|--------|
| 0.05 | 5 factors | Would add shareability, value - but these show no correlation |
| 0.10 | 3 factors (current) | Balanced approach |
| 0.15 | 2 factors | Would lose fussy eater friendly |
| 0.20 | 1 factor | Only adult appeal - too narrow |

**Recommendation:** 0.10 threshold provides the best balance between inclusivity and signal strength.

### What if we changed track weights?

| Performance | Opportunity | Effect |
|-------------|-------------|--------|
| 30% | 70% | Favors new dishes, less proven |
| 50% | 50% | Current - balanced approach |
| 70% | 30% | Favors existing winners, survivorship bias |

**Recommendation:** 50/50 split allows both proven dishes and high-potential new dishes to score well.

---

## Data Quality Notes

### Sample Sizes
- Dishes with full survey data: 13
- Dishes with ratings data: 22
- Dishes with opportunity scores: 100
- On Dinneroo: 31
- Not on Dinneroo: 69

### Limitations
1. Small sample sizes limit statistical power
2. Some factor scores are estimated (LLM fallback)
3. Correlations do not imply causation

### Recommendations for Future
1. Collect more survey responses per dish type
2. Add direct questions about factor importance
3. Track which factors drive repeat orders

---

## Conclusion

The weights in this framework are **data-driven, not assumed**. Each factor was validated through correlation analysis, and only factors with demonstrated impact on dish success are included.

**Key Insight:** Adult appeal and balanced/guilt-free positioning are the strongest predictors of dish success on Dinneroo. Kid-friendly as a generic factor is less predictive than fussy-eater-friendly specifically.

---

*Source Data: `DATA/3_ANALYSIS/factor_correlations.csv`*  
*Validation Report: `DELIVERABLES/reports/factor_validation_analysis.md`*  
*Configuration: `config/dish_scoring_unified.json`*

