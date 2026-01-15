# Dinneroo Data Types Cheatsheet
> Quick reference for what data we have and how to use it

---

## 📊 The Data at a Glance

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DINNEROO DATA SOURCES                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  🔵 INTERNAL (from our systems)                                              │
│  ├── Supply/Ground Truth (Anna)     ✅ QUANT    "What we HAVE"              │
│  │   └── anna_slides/*.csv — partners, dishes, zone coverage                │
│  │                                                                           │
│  ├── Order History (Snowflake)      ✅ QUANT    "What customers DO"         │
│  │   └── 805,804 orders — repeat rate, volume, demand                       │
│  │                                                                           │
│  ├── Ratings + Comments (Snowflake) 🟣 MIXED    "How they FEEL"             │
│  │   └── 10,713 ratings — scores + open-text feedback                       │
│  │                                                                           │
│  └── Menu Catalog (Snowflake)       ✅ QUANT    "What's AVAILABLE"          │
│      └── 65,312 items — actual Dinneroo menu availability                   │
│                                                                              │
│  🟠 RESEARCH (from surveys/interviews)                                       │
│  ├── Post-order Survey              🟣 MIXED    "Are they happy?"           │
│  │   └── n=1,599 — satisfaction, kids happy, reorder intent                 │
│  │                                                                           │
│  ├── Dropoff Survey                 🟣 MIXED    "Why didn't they buy?"      │
│  │   └── n=838 — barriers, unmet demand, missing options                    │
│  │                                                                           │
│  ├── OG Survey ⚠️                    🟣 MIXED    "Pre-launch hypotheses"     │
│  │   └── n=~400 — USE WITH CAUTION, always triangulate                      │
│  │                                                                           │
│  └── Customer Transcripts           🟡 QUAL     "The WHY behind behavior"   │
│      └── n=88 interviews — unprompted mentions, motivations                 │
│                                                                              │
│  🩷 LLM-DERIVED (AI-processed)                                               │
│  └── Gemini Extraction              🩷 DERIVED  "Structured from qual"      │
│      └── transcript_mentions.json — dish/cuisine mentions with audit trail  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🏷️ Legend

| Tag | Meaning | Can you count it? |
|-----|---------|-------------------|
| ✅ **QUANT** | Numbers, metrics, counts | Yes — aggregate freely |
| 🟡 **QUAL** | Text, transcripts, context | No — rich insights, not countable |
| 🟣 **MIXED** | Has both (e.g. rating + comment) | Partially — scores yes, text no |
| 🩷 **DERIVED** | LLM turned qual → structured | Yes, but with audit trail |

| Source | What it means |
|--------|---------------|
| 🔵 **Internal** | From Deliveroo systems (reliable, refreshable) |
| 🟠 **Research** | From surveys/interviews (snapshot in time) |
| 🩷 **LLM** | AI-processed (assistive, not ground truth) |

---

## 🎯 Which Data for Which Question?

| I want to know... | Use this | Why |
|-------------------|----------|-----|
| How many partners in a zone? | **Anna supply data** | Ground truth for what exists |
| What's the repeat rate? | **Snowflake orders** | Actual behavior, not stated preference |
| Are families satisfied? | **Post-order survey** | Direct satisfaction + open-text |
| Why do people drop off? | **Dropoff survey** | Barrier questions + "what's missing" |
| What do families *really* want? | **Transcripts + LLM** | Unprompted mentions = high signal |
| Is a zone ready for MVP? | **Zone MVP status** | Pre-calculated, combines sources |
| What dishes should we recruit? | **Dish prioritization** | Weighted scoring across sources |

---

## ⚠️ Key Rules

1. **Supply ≠ Performance**
   - Anna = what EXISTS in a zone
   - Snowflake = how it PERFORMS (orders, ratings)
   - Don't mix them up!

2. **Never use OG Survey alone**
   - Pre-launch, small sample, stated preference
   - Always triangulate with behavioral data

3. **LLM outputs need audit trails**
   - Great for structuring qual data
   - But treat as *assistive*, not ground truth
   - Check `llm_extraction_log.json` for provenance

4. **Open-text is gold**
   - Surveys have quant scores AND qual insights
   - Mine the comments for latent demand

5. **Sample sizes matter**
   - Always cite n= when reporting
   - Small samples = directional only

---

## 📁 Key File Paths

```
DATA/1_SOURCE/
├── anna_slides/*.csv          ← Supply ground truth
├── snowflake/*.csv            ← Behavioral data
├── surveys/*.csv              ← Survey responses
└── qual_research/transcripts/ ← Interview transcripts

DATA/3_ANALYSIS/
├── anna_*.csv                 ← Processed supply data
├── transcript_mentions.json   ← LLM extraction output
└── zone_mvp_*.json           ← Calculated MVP status

config/
├── mvp_thresholds.json        ← Business rules
└── dish_taxonomy.csv          ← Dish classifications
```

---

## 🔄 Data Flow

```
SOURCES                    PROCESSING                 OUTPUTS
─────────────────────────────────────────────────────────────────
Anna CSVs ─────┐
               ├──► Enrichment ──► Analysis ──► Zone MVP Status
Snowflake ─────┤    & Cleaning     Scripts      Dish Priorities
               │                                 Gap Analysis
Surveys ───────┤
               │
Transcripts ───┴──► LLM Extraction ───────────► Latent Demand
                    (Gemini)                     Scores
```

---

*Questions? Check the agent briefs in `DOCUMENTATION/AGENTS/` or ask Cursor!*
