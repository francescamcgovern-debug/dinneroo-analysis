# Evidence Standards

## Purpose

This document defines the evidence standards for all analysis in the Dinneroo project. Following these standards ensures claims are properly supported and recommendations are trustworthy.

---

## Evidence Levels

| Level | Symbol | Definition | Use For |
|-------|--------|------------|---------|
| **Single** | 🔵 | One data source only | Exploratory findings, hypothesis generation |
| **Corroborated** | 🟡 | 2 independent sources | Working hypotheses, internal analysis |
| **Validated** | 🟢 | 3+ sources OR quant+qual | Strategic recommendations, stakeholder presentations |

### When to Use Each Level

| Claim Type | Minimum Level |
|------------|---------------|
| Exploratory finding | 🔵 Single |
| Internal recommendation | 🟡 Corroborated |
| Strategic recommendation | 🟢 Validated |
| Dashboard headline | 🟢 Validated |
| External communication | 🟢 Validated |

---

## Source Independence

### CAN Triangulate (Independent Sources)

| Source A | Source B | Why Independent |
|----------|----------|-----------------|
| Post-Order Survey | Snowflake Orders | Survey vs behavioral |
| Dropoff Survey | Post-Order Survey | Different populations |
| Any Quantitative | Any Qualitative | Different methods |
| Snowflake Orders | Transcripts | Behavioral vs exploratory |

### CANNOT Triangulate (Not Independent)

| Source A | Source B | Why Not |
|----------|----------|---------|
| Two questions from same survey | Same survey | Same respondents |
| Post-Order + Dropoff (same metric) | Both surveys | Method overlap |

---

## Sample Size Requirements

### Minimum for Reporting

| Sample Size | Reliability | Action |
|-------------|-------------|--------|
| n < 20 | ❌ Unreliable | Do not report |
| n = 20-50 | ⚠️ Directional | Report with caveat |
| n = 50-100 | ✓ Moderate | Report as finding |
| n > 100 | ✓✓ Strong | Report confidently |

### Minimum for Statistical Claims

| Claim Type | Minimum n |
|------------|-----------|
| Percentage | n ≥ 30 |
| Comparison (A vs B) | n ≥ 20 per group |
| Correlation | n ≥ 50 |
| Statistical significance | n ≥ 30 per group |

### Survey-Backed Scores

| Requirement | Threshold |
|-------------|-----------|
| Minimum responses per dish | n ≥ 5 |
| Dishes with fewer responses | Use estimated scores |

---

## Statistical Standards

### Significance Threshold

- **p < 0.05** for statistical significance
- Always report the actual p-value
- Only use "significant" when you have a p-value

### Distinguish

- **"Statistically significant"** = p < 0.05, tested
- **"Meaningful difference"** = practical importance, may not be tested
- **"Notable"** = worth mentioning, not necessarily tested

---

## Citation Standards

### Every Claim Must Include

1. **Source name** - Which data source
2. **Sample size** - n=X
3. **Segment** - If subset (e.g., "families only", "Zone X only")
4. **Date/freshness** - When data was collected
5. **Caveats** - Relevant limitations

### Good Example

> "Zone A has 85% satisfaction (n=127, post-order survey, Dec 2025). Note: This represents customers who completed orders in this zone."

### Bad Example

> "Zone A has high satisfaction."

---

## Triangulation Rules

### Source-Specific Constraints

| Source | Rule | Reason | Max Weight |
|--------|------|--------|------------|
| OG Survey | MUST triangulate with Snowflake | Stated ≠ revealed preference | 30% |
| Dropoff Survey | Use for themes, not prevalence | Self-selection bias | 30% |
| Orders Data | Shows available options only | Survivorship bias | 40% |
| Ratings | ~40% coverage only | Don't use for volume | 20% |

### Never Use Alone

- OG Survey for dish recommendations
- Single survey for strategic claims
- Order data for demand (survivorship bias)

---

## Bias Warnings

### Survivorship Bias

**Applies to:** Order volume analysis

**Warning:** Top-performing dishes are top performers OF WHAT WE HAVE

**Mitigation:** Always analyze latent demand via open-text alongside order volume

### Stated vs Revealed Preference

**Applies to:** Survey data

**Warning:** What people say ≠ what they do

**Mitigation:** Triangulate with behavioral data

### Selection Bias

**Applies to:** Post-order survey

**Warning:** Only orderers respond - survivors only

**Mitigation:** Use for "what works", not barriers

### Regional Bias

**Applies to:** All data

**Warning:** London/South East over-represented (65%)

**Mitigation:** Weight by population or segment separately

---

## Recommendation Standards

### Template

```
🟢 VALIDATED: [Recommendation]

Evidence:
- Source 1: [Finding] (n=X)
- Source 2: [Finding] (n=X)
- Source 3: [Finding] (n=X)

Caveats:
- [Limitation 1]
- [Limitation 2]

Confidence: [High/Medium/Low]
```

---

## Data Quality Checks

### Before Analysis

- [ ] Check file modification dates (data <7 days old?)
- [ ] Verify sample sizes are sufficient
- [ ] Check for missing data patterns
- [ ] Verify column names match expected

### During Analysis

- [ ] Validate calculations with spot checks
- [ ] Check for outliers that might skew results
- [ ] Verify totals add up
- [ ] Cross-reference with other sources

### Before Reporting

- [ ] All claims have source citations
- [ ] All claims have sample sizes
- [ ] Statistical claims have p-values
- [ ] Caveats are noted
- [ ] Evidence level is indicated

---

## Anti-Replication Rules

**Do NOT assume from previous analysis:**
- Which dishes are "winners" or "losers"
- Which zones are "high performing" or "low performing"
- Which partners are "best" or "worst"
- Which cuisines are "essential" or "nice-to-have"
- What percentage satisfaction rates are "good" or "bad"
- What customer segments behave in what ways

**Every insight must come from fresh analysis of the current data.**

---

## Escalation Rules

### Flag for Human Review When

1. **Contradictory evidence** - Sources disagree
2. **Small samples** - Key finding based on n < 30
3. **Single source strategic claim** - Recommendation from one source
4. **Novel finding** - Not seen before, could be error
5. **High stakes** - Impacts partner relationships or product direction

### How to Flag

```
⚠️ REQUIRES REVIEW

Finding: [The finding]
Concern: [Why it needs review]
Recommendation: [What to do]
```

---

## Configuration

Evidence standards are also defined in `config/evidence_standards.json` for use by scripts.

---

*These standards ensure analysis quality. Apply them consistently.*

