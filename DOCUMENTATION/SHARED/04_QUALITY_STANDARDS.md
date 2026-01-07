# Quality Standards

## Evidence Rules

### Evidence Levels

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
| Post-Order + Dropoff (for same metric) | Both surveys | Method overlap |

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

---

## Statistical Standards

### Significance Threshold
- **p < 0.05** for statistical significance
- Always report the actual p-value
- Only use "significant" when you have a p-value

### Distinguish:
- **"Statistically significant"** = p < 0.05, tested
- **"Meaningful difference"** = practical importance, may not be tested
- **"Notable"** = worth mentioning, not necessarily tested

---

## Citation Standards

### Every Claim Must Include:

1. **Source name** - Which data source
2. **Sample size** - n=X
3. **Segment** - If subset (e.g., "families only", "Zone X only")
4. **Date/freshness** - When data was collected
5. **Caveats** - Relevant limitations

### Good Example:
> "Zone A has 85% satisfaction (n=127, post-order survey, Dec 2025). Note: This represents customers who completed orders in this zone."

### Bad Example:
> "Zone A has high satisfaction."

---

## Recommendation Standards

### For Any Recommendation:

1. State evidence level (🔵/🟡/🟢)
2. List all supporting sources
3. Include sample sizes
4. Note methodological caveats
5. Flag uncertainties

### Template:
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

## Anti-Replication Rules

**Do NOT assume any of these from previous analysis:**
- Which dishes are "winners" or "losers"
- Which zones are "high performing" or "low performing"
- Which partners are "best" or "worst"
- Which cuisines are "essential" or "nice-to-have"
- What percentage satisfaction rates are "good" or "bad"

**Every insight must come from fresh analysis of the current data.**

### Red Flags That Suggest Replication

- Finding matches old project conclusions exactly
- Specific percentages appear without fresh calculation
- Partner/dish names appear as "winners" without analysis
- Conclusions written before data is loaded
- Examples from briefs copied as findings

### Validation Questions

Before reporting any insight, ask:
1. Did I calculate this from the current data?
2. Can I show the code/query that produced this number?
3. Is this different from what I might have assumed?
4. Would this finding change if the data changed?

---

## Data Quality Checks

### Before Analysis:

- [ ] Check file modification dates (data <7 days old?)
- [ ] Verify sample sizes are sufficient
- [ ] Check for missing data patterns
- [ ] Verify column names match expected

### During Analysis:

- [ ] Validate calculations with spot checks
- [ ] Check for outliers that might skew results
- [ ] Verify totals add up (e.g., segments sum to total)
- [ ] Cross-reference with other sources where possible

### Before Reporting:

- [ ] All claims have source citations
- [ ] All claims have sample sizes
- [ ] Statistical claims have p-values
- [ ] Caveats are noted
- [ ] Evidence level is indicated

---

## Escalation Rules

### Flag for Human Review When:

1. **Contradictory evidence** - Sources disagree
2. **Small samples** - Key finding based on n < 30
3. **Single source strategic claim** - Recommendation from one source
4. **Novel finding** - Not seen before, could be error
5. **High stakes** - Impacts partner relationships or product direction

### How to Flag:
```
⚠️ REQUIRES REVIEW

Finding: [The finding]
Concern: [Why it needs review]
Recommendation: [What to do]
```

---

## Avoiding Common Errors

### Data Errors

| Error | Prevention |
|-------|------------|
| Wrong deduplication | Use ORDER_ID, not RESPONSE_ID |
| Survey bias in targeting | Use Snowflake customer data |
| Mixing dropoff segments | Analyze "Tried Before" and "Never Tried" separately |
| Wrong file for volume | Use ALL_DINNEROO_ORDERS (100%), not RATINGS (40%) |
| Order-derived supply counts | Use Anna's ground truth data |

### Analysis Errors

| Error | Prevention |
|-------|------------|
| Unsupported "significant" | Only use with p-value |
| Small sample claims | Check n ≥ 20 before reporting |
| Single-source recommendations | Triangulate for strategic claims |
| Correlation as causation | Use causal language carefully |

### Reporting Errors

| Error | Prevention |
|-------|------------|
| Missing source | Always cite data source |
| Missing sample size | Always include n=X |
| Missing caveats | Note limitations |
| Overstating confidence | Match language to evidence level |

---

*These standards ensure analysis quality. Apply them consistently.*


