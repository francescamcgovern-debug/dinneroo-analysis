# Family Behavior Methodology

## Purpose

This document describes the methodology for understanding family eating behaviors and segmenting customers to inform dish and zone recommendations.

---

## Core Research Questions

### A. What families cook/eat at home midweek and why

**Sources:**
- Customer transcripts (88 interviews)
- OG Survey (family composition, decision-making)
- BODS Families Survey

**Key Findings:**
- Quick, familiar meals dominate midweek
- Pasta, chicken + veg, rice dishes most common
- Time constraint is primary driver
- Kids' preferences heavily influence choices

### B. What families want to eat more of but don't currently and why

**Sources:**
- Dropoff survey open-text
- Customer transcripts
- Post-order survey improvements

**Key Findings:**
- More variety (145 mentions)
- Healthier options (186 mentions)
- Better vegetarian options (87 mentions)
- More customization (125 mentions)

### C. What families order on Deliveroo normally (outside Dinneroo)

**Sources:**
- FULL_ORDER_HISTORY.csv
- Non-Dinneroo order patterns

**Key Findings:**
- Weekend orders are more "treat" focused
- Midweek orders more routine/balanced
- Nando's significant for non-Dinneroo midweek orders
- Different cuisines for different occasions

### D. What families order and enjoy on Dinneroo

**Sources:**
- DINNEROO_ORDERS.csv
- Post-order survey
- Ratings data

**Key Findings:**
- Asian cuisines dominate (Wagamama, Pho)
- High satisfaction with kid-friendly options
- Repeat orders for familiar dishes
- Price sensitivity at £25 threshold

### E. What families would benefit from having on Dinneroo

**Sources:**
- Gap analysis (latent demand)
- Open-text mining
- Behavioral patterns

**Key Findings:**
- Grilled chicken with customizable sides
- More British comfort food
- Better vegetarian family options
- Mediterranean/healthy options

---

## Customer Segmentation

### By Family Type

| Segment | Definition | Behavior |
|---------|------------|----------|
| **Young Families** | Children under 7 | Most fussy eater concerns |
| **School-Age Families** | Children 7-12 | More adventurous, value-focused |
| **Teen Families** | Children 13+ | Larger portions, adult preferences |
| **Mixed Ages** | Multiple children, different ages | Need most customization |

### By Region

| Region | Zones | Characteristics |
|--------|-------|-----------------|
| **London** | 45% of orders | Most diverse cuisine preferences |
| **South East** | 20% of orders | Similar to London |
| **North** | 15% of orders | More British comfort preferences |
| **Midlands** | 12% of orders | Mixed preferences |
| **Other** | 8% of orders | Varies significantly |

### By Subscription Status

| Status | Behavior |
|--------|----------|
| **Plus Subscribers** | Higher frequency, more experimental |
| **PAYG** | Price-sensitive, stick to known dishes |

---

## Cannibalization Analysis

### Purpose

Ensure Dinneroo creates NEW occasions rather than replacing existing Deliveroo orders.

### Key Finding

**Dinneroo is 98% midweek orders** - successfully creating new occasion.

### Day Distribution

| Day | Dinneroo % | Non-Dinneroo % |
|-----|------------|----------------|
| Monday | 18% | 8% |
| Tuesday | 22% | 9% |
| Wednesday | 25% | 10% |
| Thursday | 21% | 12% |
| Friday | 8% | 22% |
| Saturday | 4% | 24% |
| Sunday | 2% | 15% |

### Cannibalization Risk Assessment

| Risk Level | Criteria | Implication |
|------------|----------|-------------|
| **Low** | Dinneroo >70% midweek, Non-Dinneroo >50% weekend | New occasion created |
| **Medium** | Some overlap but mostly differentiated | Monitor patterns |
| **High** | Significant overlap | Review positioning |

**Current Status:** Low risk - Dinneroo successfully differentiated.

---

## Midweek vs Weekend Patterns

### Midweek (Mon-Thu) Characteristics

- **Occasion:** Routine family dinner
- **Driver:** Convenience + nutrition
- **Constraint:** Time, weeknight energy
- **Dishes:** Balanced, familiar, quick
- **Price Sensitivity:** Higher

### Weekend (Fri-Sun) Characteristics

- **Occasion:** Treat/celebration
- **Driver:** Indulgence, variety
- **Constraint:** Less time pressure
- **Dishes:** More indulgent, experimental
- **Price Sensitivity:** Lower

### Implications for Dinneroo

Dinneroo should focus on:
- ✅ Balanced meals (not treats)
- ✅ Quick/convenient options
- ✅ Familiar flavors for kids
- ✅ Good value at £25
- ❌ Not heavy indulgence
- ❌ Not experimental cuisines

---

## Evidence Sources

### Quantitative

| Source | Sample | Use For |
|--------|--------|---------|
| Dinneroo Orders | ~71,000 | Revealed preference |
| Full Order History | ~150,000 | Non-Dinneroo patterns |
| Post-Order Survey | ~1,500 | Satisfaction, feedback |
| Dropoff Survey | ~800 | Barriers, unmet demand |

### Qualitative

| Source | Sample | Use For |
|--------|--------|---------|
| Customer Transcripts | 88 interviews | Deep "why" understanding |
| Rating Comments | ~1,000 | Specific feedback |
| Open-text Responses | ~2,800 | Unprompted mentions |

---

## Implementation

### Script Location

`scripts/phase2_analysis/03_segment_customers.py`

### Outputs

- `DATA/3_ANALYSIS/customer_segments.json` - Segmentation results
- `DATA/3_ANALYSIS/regional_segments.csv` - Regional breakdown
- `DATA/3_ANALYSIS/subscription_segments.csv` - Plus vs PAYG

---

## Bias Awareness

### Regional Bias

London/South East over-represented in data (65% of orders).

**Mitigation:** Weight analysis by population or segment separately.

### Selection Bias

Survey respondents may not represent all customers.

**Mitigation:** Triangulate with behavioral data.

### Survivorship Bias

Only see behavior of customers who use Dinneroo.

**Mitigation:** Use dropoff survey for non-users.

---

*This methodology ensures customer understanding is evidence-based and segmentation is actionable.*




