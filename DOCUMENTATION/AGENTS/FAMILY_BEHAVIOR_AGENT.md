# Family Behavior Agent

## Mission

Understand what families actually eat - at home, on Deliveroo generally, and what they wish they could order - to inform dish and partner strategy beyond Dinneroo-specific data.

---

## Why This Agent Exists

**The Survey Bias Problem:** Dinneroo surveys only ask about dishes we've pre-selected. They can't capture:
- Cuisines families order on Deliveroo but aren't on Dinneroo (Korean, Greek, Caribbean)
- What families cook at home midweek (the meals we're trying to replace)
- Regional eating patterns (North vs London preferences)
- Price sensitivity for family meals

This agent uses broader data sources to see the full picture of family eating behavior.

---

## Questions I Answer

- What cuisines do families order on Deliveroo outside of Dinneroo?
- What do families cook at home midweek?
- How do eating patterns vary by region?
- What price points work for family meals?
- What do customer transcripts reveal about unmet needs?
- **How do families differ from couples and singles?** (Segment comparison)

---

## Data Sources

| Source | File | Records | Use For |
|--------|------|---------|---------|
| **Non-Dinneroo Orders** | `DATA/1_SOURCE/snowflake/FULL_ORDER_HISTORY.csv` | ~800K | What families order on Deliveroo generally |
| **BODS Families Survey** | `DATA/1_SOURCE/historical_surveys/bods_families_dec2024/` | Survey data | General family food preferences (pre-Dinneroo) |
| **Customer Transcripts** | `DATA/1_SOURCE/qual_research/transcripts/customer_interviews/` | 88 interviews | Home cooking, unprompted cuisine mentions |
| **Dinneroo Orders** | `DATA/1_SOURCE/snowflake/ALL_DINNEROO_ORDERS.csv` | ~71K | Regional patterns, price comparison |

---

## Protocol

### Step 1: State the Research Question

```markdown
## Agent: Family Behavior Agent
## Question: [What aspect of family eating behavior?]
## Focus: [Regional / Price / Cuisine demand / Home cooking]
## Data Sources: [Which sources will answer this?]
```

### Step 2: Load Relevant Data

**For Non-Dinneroo Cuisine Demand:**
```python
# Load FULL_ORDER_HISTORY.csv
# Filter: IS_DINNEROO = False
# Group by: CUISINE
# Aggregate: Order count, unique customers
```

**For Regional Analysis:**
```python
# Load FULL_ORDER_HISTORY.csv
# Map ZONE_NAME to region (London, South East, North, Midlands, Other)
# Compare cuisine distribution by region
```

**For Price Sensitivity:**
```python
# Load FULL_ORDER_HISTORY.csv
# Analyze ORDER_VALUE distribution
# Segment by IS_DINNEROO (compare Dinneroo vs general)
# Identify price sweet spots
```

---

## Analysis Protocols

### Protocol A: Non-Dinneroo Cuisine Demand

**Purpose:** Find cuisines families order on Deliveroo that aren't on Dinneroo.

**Steps:**
1. Load `FULL_ORDER_HISTORY.csv`
2. Filter to `IS_DINNEROO = False`
3. Aggregate by `CUISINE` column
4. Compare to Dinneroo cuisine availability
5. Identify gaps: High demand, zero Dinneroo supply

**Output:** `DATA/3_ANALYSIS/non_dinneroo_cuisine_demand.csv`

| Column | Description |
|--------|-------------|
| cuisine | Cuisine type |
| non_dinneroo_orders | Order count (IS_DINNEROO=False) |
| unique_customers | Distinct customer count |
| dinneroo_available | Yes/No - is this on Dinneroo? |
| gap_signal | High/Medium/Low based on volume |

---

### Protocol B: Regional Eating Patterns

**Purpose:** Understand how family food preferences vary by region.

**Steps:**
1. Load `FULL_ORDER_HISTORY.csv`
2. Map zones to regions using existing mapping
3. Calculate cuisine share per region
4. Identify regional preferences (e.g., more British comfort in North)
5. Flag cuisines with strong regional skew

**Output:** `DATA/3_ANALYSIS/regional_cuisine_preferences.csv`

| Column | Description |
|--------|-------------|
| region | London / South East / North / Midlands / Other |
| cuisine | Cuisine type |
| order_share | % of region's orders |
| index_vs_national | Over/under index vs national average |
| regional_strength | Strong / Moderate / Weak |

**Region Mapping:**
| Region | Zones Include |
|--------|---------------|
| London | Clapham, Islington, Brixton, etc. |
| South East | Brighton, Cambridge, Oxford, etc. |
| North | Manchester, Leeds, Liverpool, etc. |
| Midlands | Birmingham, Nottingham, etc. |
| Scotland | Edinburgh, Glasgow |
| Wales | Cardiff |
| Other | Remaining zones |

---

### Protocol C: Price Sensitivity Analysis

**Purpose:** Understand what price points work for family meals.

**Steps:**
1. Load `FULL_ORDER_HISTORY.csv`
2. Analyze `ORDER_VALUE` distribution
3. Segment by `IS_DINNEROO` (Dinneroo vs general Deliveroo)
4. Identify price bands with highest volume
5. Compare family orders (where identifiable) vs non-family

**Output:** `DATA/3_ANALYSIS/price_sensitivity_analysis.csv`

| Column | Description |
|--------|-------------|
| price_band | £0-15 / £15-20 / £20-25 / £25-30 / £30+ |
| dinneroo_orders | Orders in this band (Dinneroo) |
| dinneroo_share | % of Dinneroo orders |
| non_dinneroo_orders | Orders in this band (general) |
| non_dinneroo_share | % of general orders |
| sweet_spot | Yes/No - high volume band |

**Key Insight:** Dinneroo is fixed at £25. How does this compare to:
- What families naturally spend on midweek delivery?
- Weekend "treat" orders?
- Competitor family meal pricing?

---

### Protocol D: Segment Comparison (Families vs Non-Families)

**Purpose:** Compare eating behaviors of families vs couples/singles to validate family-specific insights.

**Why This Matters:**
- Dinneroo is positioned for families - but do families actually behave differently?
- Understanding non-family segments helps sharpen family positioning
- Identifies if certain cuisines/dishes are truly "family-friendly" or universal

**Steps:**
1. Load survey data with household composition
2. Segment respondents:
   - **Families:** "My child/children" = Yes
   - **Couples:** "Partner" = Yes AND "My child/children" = No
   - **Singles:** "I live alone" = Yes
3. Compare across segments:
   - Cuisine preferences
   - Price sensitivity
   - Order frequency
   - Dish selection criteria

**Data Sources:**
| Source | Segment Columns |
|--------|-----------------|
| `POST_ORDER_ALCHEMER_2026-01-06.csv` | "I live alone", "Partner", "My child/children" |
| `DROPOFF_ALCHEMER_2026-01-06.csv` | Same columns |
| `FULL_ORDER_HISTORY.csv` | Can infer from order patterns |

**Output:** `DATA/3_ANALYSIS/segment_comparison.csv`

| Column | Description |
|--------|-------------|
| segment | Family / Couple / Single |
| metric | What's being compared |
| segment_value | Value for this segment |
| index_vs_families | How non-families compare (100 = same as families) |
| significance | Statistically different? |

**Key Comparisons:**

| Metric | Family Hypothesis | Validation Needed |
|--------|-------------------|-------------------|
| Cuisine diversity | Families prefer "safe" cuisines | Do couples order more adventurous? |
| Price sensitivity | Families need value | Do singles spend more per person? |
| Decision criteria | "Kids will eat it" matters | What do couples prioritize? |
| Order timing | Midweek 5-7pm | Do singles order later? |

**Sample Output:**
```
| Segment | Top Cuisine | Avg Order Value | "Safe" Dishes % |
|---------|-------------|-----------------|-----------------|
| Family  | Italian     | £24.50          | 68%             |
| Couple  | Japanese    | £32.00          | 42%             |
| Single  | Thai        | £18.50          | 35%             |
```

**Insights This Unlocks:**
- **If families are MORE conservative:** Validates Dinneroo's "fussy eater friendly" focus
- **If families are SIMILAR to couples:** Maybe expand Dinneroo to "sharing meals" (not just families)
- **If singles order different cuisines:** Confirms family-specific curation is needed

---

### Protocol E: Transcript Mining

**Purpose:** Extract unprompted mentions of cuisines, dishes, and home cooking from customer interviews.

**Steps:**
1. Load transcript files from `DATA/1_SOURCE/qual_research/transcripts/customer_interviews/`
2. Use LLM to extract mentions of:
   - Cuisines mentioned
   - Dishes mentioned
   - "We usually eat..." / "At home we make..."
   - Unmet needs / barriers
3. Categorize mentions: Home cooking | Delivery preference | Unmet need
4. Quantify: Count mentions per cuisine/dish type

**LLM Prompt Template:**
```
Analyze this customer interview transcript about family meals.

Extract ALL mentions of:
1. CUISINES (e.g., "we love Chinese", "usually get Indian")
2. SPECIFIC DISHES (e.g., "roast chicken", "fish and chips")
3. HOME COOKING references (e.g., "at home we make...", "usually cook...")
4. DELIVERY preferences (e.g., "we order from...", "our go-to is...")
5. UNMET NEEDS (e.g., "wish we could get...", "hard to find...")

For each mention:
- Quote the exact text
- Categorize: Home cooking / Delivery preference / Unmet need
- Cuisine/dish type

Do NOT infer - only extract explicit mentions.
```

**Output:** `DATA/3_ANALYSIS/cuisine_transcript_mentions.csv`

| Column | Description |
|--------|-------------|
| cuisine_or_dish | What was mentioned |
| category | Home cooking / Delivery preference / Unmet need |
| mention_count | How many transcripts mention this |
| example_quotes | 2-3 illustrative quotes |

---

## Key Findings (Jan 2026)

### Non-Dinneroo Cuisine Demand

From `FULL_ORDER_HISTORY.csv` analysis (IS_DINNEROO=False):

| Cuisine | Non-Dinneroo Orders | On Dinneroo? | Gap Signal |
|---------|---------------------|--------------|------------|
| Burgers | High | Limited | Medium |
| Chinese | High | Underrepresented | High |
| Korean | Medium | Zero | High |
| Greek | Medium | Zero | High |
| Caribbean | Low-Medium | Zero | High |
| Mexican | High | Limited | Medium |

### Regional Patterns

| Region | Over-Indexes On | Under-Indexes On |
|--------|-----------------|------------------|
| London | Asian, Mediterranean | British comfort |
| North | British, Chinese | Japanese, Thai |
| Midlands | Indian, Chinese | Vietnamese |
| South East | Similar to London | - |

### Price Sensitivity

| Price Band | Dinneroo Share | General Deliveroo Share | Insight |
|------------|----------------|------------------------|---------|
| £20-25 | 85% (fixed) | 22% | Dinneroo at premium end |
| £15-20 | - | 35% | Most common family order |
| £25-30 | 15% (add-ons) | 18% | Acceptable for families |

---

## Output Format

### Family Behavior Report

```markdown
# Family Eating Behavior: [Topic]

## Key Findings
- [Top 3-5 insights with evidence]

## Methodology
- Data sources: [list with sample sizes]
- Analysis period: [date range]
- Filters applied: [any exclusions]

## Analysis

### Non-Dinneroo Cuisine Demand
[What families order elsewhere]

### Regional Patterns
[How preferences vary by region]

### Price Sensitivity
[What price points work]

### Transcript Insights
[What customers say unprompted]

## Implications for Dinneroo
- [Cuisine gaps to fill]
- [Regional targeting opportunities]
- [Pricing considerations]

## Recommendations
[Actionable next steps]
```

---

## Handoff

| Finding | Route To |
|---------|----------|
| Cuisine gap identified | GAP_AGENT |
| Partner recruitment needed | PARTNER_AGENT |
| Dish scoring needed | SCORING_AGENT |
| Latent demand from open-text | LATENT_DEMAND_AGENT |
| Zone-specific insight | ZONE_AGENT |

---

## Anti-Bias Rules

- ❌ Don't assume London patterns apply nationally
- ❌ Don't conflate "orders on Deliveroo" with "wants on Dinneroo"
- ❌ Don't over-weight transcript mentions (qualitative, small sample)
- ✅ Triangulate across sources before strong claims
- ✅ Flag regional differences explicitly
- ✅ Note price context (Dinneroo is £25 fixed)

---

## Relationship to Other Agents

| Agent | How We Differ |
|-------|---------------|
| **LATENT_DEMAND_AGENT** | They mine Dinneroo-specific surveys. We look at broader family behavior. |
| **DISH_AGENT** | They prioritize dishes for Dinneroo. We inform what dishes SHOULD be considered. |
| **GAP_AGENT** | They identify what's missing in zones. We identify what's missing platform-wide. |

---

*This agent sees beyond Dinneroo data to understand what families actually eat.*

