# Dinneroo Dashboard PRD

## Purpose

A single dashboard that answers: **"What does each zone need to succeed, and what should we do about it?"**

This dashboard serves as the unified source of truth for supply strategy, used by cross-functional teams (Product, Partner Ops, Commercial, Marketing, Strategy).

---

## Primary Audiences & Their Questions

### 1. Product Director
| Question | What They Need |
|----------|----------------|
| Who loves Dinneroo? | Segment breakdown with satisfaction scores |
| Why do they love it? | Dish choice reasons, top drivers by segment |
| Can we expand beyond families? | Non-family segment performance data |

### 2. Partner Ops
| Question | What They Need |
|----------|----------------|
| What makes a zone successful? | MVP criteria with evidence |
| Which zones need help? | Priority queue sorted by effort |
| What should I recruit for Zone X? | Specific partner recommendations per zone |

### 3. Commercial
| Question | What They Need |
|----------|----------------|
| Which partners to prioritize? | Partner coverage matrix, gap fill potential |
| Which dishes to prioritize? | Ranked lists with business rationale |
| Which cuisines are must-haves? | Core 7 with performance data |

### 4. Marketing
| Question | What They Need |
|----------|----------------|
| Who should we target? | Segment profiles with size + value |
| What message resonates? | Top dish choice drivers by segment |
| What's the positioning? | Balanced midweek meals, not indulgent treats |

### 5. Strategy / Leadership
| Question | What They Need |
|----------|----------------|
| Are we on track? | MVP progress vs target, week-over-week |
| What's the overall supply plan? | Summary view before zone details |
| Where should we invest? | Prioritized action list |

---

## Core Research Questions to Answer

### Q1: What is an MVP Zone?
**Deliverable:** Clear criteria with data evidence

| Dimension | Inflection Point | MVP Target | Evidence Required |
|-----------|------------------|------------|-------------------|
| Partners | 3+ | 5+ | Repeat rate lift |
| Cuisines | 3+ | 5 of Core 7 | Repeat rate lift |
| Dishes | TBD | Core Drivers | Kids_happy + orders |
| Rating | 4.0+ | 4.0+ | Satisfaction benchmark |
| Repeat Rate | 20%+ | 35%+ | Retention signal |

### Q2: Which dishes should we recommend?
**Deliverable:** Three ranked lists with rationale

| List | Purpose | Key Factors |
|------|---------|-------------|
| Family Performers | Best for families with kids | kids_happy (40%), fussy_eater_friendly (20%) |
| Couple Performers | Best for adults without kids | adult_satisfaction (40%), adult_appeal (15%) |
| Recruitment Priorities | What to add to platform | latent_demand (30%), gap_score (15%) |

**Must show:**
- Rank + score
- Key driver metrics
- Partners offering it
- Granular dish types (expandable)

### Q3: How should dishes be presented?
**Deliverable:** Family-friendly presentation guidelines

| Element | Guidance | Source |
|---------|----------|--------|
| Naming | Kid-friendly names work better | Post-order feedback |
| Portions | "Feeds 2 adults + 2 kids" clarity | Dropoff barriers |
| Images | Show full meal, not single items | Customer transcripts |
| Customization | Highlight mild/no-spice options | Fussy eater data |

---

## Dashboard Structure

### Tab 1: SUMMARY (Leadership Entry Point)
**Question answered:** "What's the overall supply plan?"

**Must include:**
- [x] MVP Progress bar (current vs Q2 target)
- [x] Week-over-week deltas (when available) - with guidance on enabling
- [x] Near MVP breakdown (which cuisines needed)
- [x] Segment insights (5 segments with confidence)
- [x] Key insight for VP Consumer (non-family potential)
- [x] Threshold guidance (inflection vs target)
- [x] Top action: "Recruiting X partner converts Y zones"
- [x] Why They Order panel by segment
- [x] Marketing Guidance box
- [x] Positioning Reminder (balanced midweek meals)

### Tab 2: ZONES (Partner Ops Entry Point)
**Question answered:** "What does each zone need?"

**Must include:**
- [x] Priority Queue sorted by effort-to-MVP
- [x] Zone search/filter
- [x] Zone cards with:
  - MVP status (color-coded)
  - Cuisines have/need
  - Partners have/need
  - Repeat rate (color-coded: green/amber/red)
  - Specific partner recommendation (IN ZONE vs ON PLATFORM)
- [x] Zone detail panel on click
- [x] Export: Zone checklist CSV

### Tab 3: DISHES (Commercial Entry Point)
**Question answered:** "Which dishes should we prioritize?"

**NEW STRUCTURE:**
- **Section A: Live on Dinneroo** - What's working now?
- **Section B: Recruitment Priorities** - What should we add?
- **Section C: How to Present Dishes** - Family-friendly guidelines

**Must include:**
- [x] Taxonomy explanation (Anna 24 with expandable detail)
- [x] Segment toggle (Family / Couple for live dishes)
- [x] Key differences callout (Family vs Couple rankings)
- [x] Live dish table with:
  - Rank + score
  - WHY column (3 metrics: orders, rating, kids_happy)
  - Supply column (zones available)
  - Expandable granular types + guidance
- [x] Recruitment table with:
  - Scoring formula breakdown (40/30/30)
  - Segment weight selector
  - WHY RECRUIT column (latent mentions, gap zones, family fit)
  - Maps to Anna 24
  - Potential partners
- [x] Export: Recruitment brief CSV

### Tab 4: CUISINES (renamed from GAPS)
**Question answered:** "How do cuisines perform and what should we prioritize?"

**Must include:**
- [x] Latent demand alerts (from open-text)
- [x] "Why 5 Cuisines?" rationale panel with data citation
- [x] "Why These 7?" rationale panel with triangulated evidence
- [x] Cuisine Habit-Forming Role section (repeat rate by cuisine)
- [x] Star Dishes per Core 7 cuisine
- [x] Cuisine gap matrix (zones × cuisines)
- [x] 2x2 quadrant (Performance vs Demand)
- [x] Expansion opportunities table

### Tab 5: PARTNERS (Partner Ops Entry Point)
**Question answered:** "Which partners fill which gaps?"

**Must include:**
- [x] Recruitment Quantification KPIs (67% solvable, 21 need new partners)
- [x] Partner recommendations table with WHY column
- [x] Status badges: ON PLATFORM / RECRUIT TO ZONE / NOT ON PLATFORM
- [x] Partner coverage matrix (partners × dish types)
- [x] Partner expansion potential (zones they could fill)
- [x] IN ZONE vs ON PLATFORM distinction

### Tab 6: METHODOLOGY & EVIDENCE
**Question answered:** "Where does this data come from?"

**Must include:**
- [x] Question Router - interactive links to answers
- [x] Scoring Lab (weight configuration, live recalculation)
- [x] Data sources with sample sizes
- [x] Threshold derivation methodology
- [x] Two Types of Thresholds (Inflection Points vs MVP Requirements)
- [x] Bundle Note (21 dishes = 7 partners × 3 items)
- [x] Evidence Standards with levels
- [x] How to update (pipeline instructions)

---

## Segment-Specific Requirements

### Family Segment
- Show kids_happy rate prominently
- Highlight fussy-eater-friendly dishes
- Show portion adequacy scores
- Top restaurant: Wagamama

### Couple Segment  
- Show adult_satisfaction rate
- Highlight adult_appeal scores
- Show value perception ("Good value" = 57%)
- Top restaurant: Pho

### Single/Friends/Mixed
- Show sample size warnings (Friends n=56)
- Show confidence levels
- Define "Mixed/Unspecified" clearly

---

## Positioning: Balanced Midweek Meals

The dashboard should reflect this positioning:

| Do Show | Don't Emphasize |
|---------|-----------------|
| Protein + veg + carbs dishes | Pure "treat" foods |
| Grilled/steamed options | Heavy fried foods |
| "Healthier" partners (Nando's, Pho) | Pizza/burger chains |
| Weeknight convenience | Weekend indulgence |

---

## Data Requirements

### JSON Files Needed
| File | Content | Used By |
|------|---------|---------|
| `zone_mvp_status.json` | Zone-level MVP calculations | Zones tab |
| `zone_priority_queue.json` | Effort-sorted queue | Summary, Zones |
| `segment_insights.json` | 5 segments with metrics | Summary |
| `dish_three_lists.json` | Family/Couple/Recruitment | Dishes tab |
| `latent_demand.json` | Open-text gaps | Gaps tab |
| `partner_coverage.json` | Partner × dish matrix | Partners tab |
| `weekly_deltas.json` | Week-over-week changes | Summary |

### Must Show Sample Sizes
Every metric must show n= to indicate confidence level.

### Must Show Data Source
Badge indicating: SNOWFLAKE (behavioral) vs SURVEY (attitudinal)

---

## Success Criteria

| Criterion | Measure |
|-----------|---------|
| Self-service | User can answer their question without asking analyst |
| Actionable | Every insight has a clear "so what" |
| Trustworthy | Sample sizes and sources visible |
| Up-to-date | Data freshness indicator, easy refresh |
| Exportable | Can extract data for other uses |

---

## Evaluation Checklist

For each dashboard tab, verify:

- [ ] Answers the stated question
- [ ] Shows sample sizes
- [ ] Has data source badges
- [ ] Includes "so what" / action guidance
- [ ] Works for the target audience
- [ ] Supports the balanced midweek meal positioning
- [ ] Has export functionality where needed

---

*Use this PRD to evaluate every dashboard change. If a feature doesn't serve a stated need, don't add it.*

