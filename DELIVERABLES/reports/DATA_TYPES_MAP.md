# Dinneroo Data Types Map (Quant / Qual / Internal / Research / LLM)

## Purpose

This is a **single visual map** of the data types in this repo, **what they are**, **whether they’re quant/qual**, **whether they’re internal/research/LLM-derived**, and **how they flow into outputs** (analysis + dashboards + reports).

## What we have (by folder + format)

Counts below are from the current workspace:

- **Anna slides pack** (`DATA/1_SOURCE/anna_slides/`): **26 files** (**14× CSV**, **12× PDF**)  
- **Snowflake extracts** (`DATA/1_SOURCE/snowflake/`): **9× CSV**  
- **Surveys (current)** (`DATA/1_SOURCE/surveys/`): **7 files** (**5× CSV**, **2× XLSX**)  
- **Surveys (historical)** (`DATA/1_SOURCE/historical_surveys/`): **15 files** (**13× CSV**, **2× XLSX**)  
- **Qual research** (`DATA/1_SOURCE/qual_research/`): **89 files** (**88× DOCX**, **1× PDF**)  
  - **Customer interview transcripts** (`.../transcripts/customer_interviews/`): **88× DOCX**
- **External / supporting docs** (`DATA/1_SOURCE/external/`): **17 files** (mostly **11× MD**, plus spreadsheets/images)
- **Enriched layer** (`DATA/2_ENRICHED/`): **6 files** (**2× CSV**, **4× JSON**)  
- **Analysis outputs** (`DATA/3_ANALYSIS/`): **97 files** (**67× CSV**, **30× JSON**)  
- **Dashboards** (`DELIVERABLES/dashboards/`): **11 files** (incl **1× HTML**, **6× JSON**)  

## Visual: how data types flow through the system

```mermaid
flowchart LR
  %% ------------------------------------------------------------
  %% SOURCES
  %% ------------------------------------------------------------
  subgraph S1[Internal · Quant]
    A[Supply / Ground Truth (Anna)\nDATA/1_SOURCE/anna_slides/*.csv\n(+ PDFs for context)]:::internalq
    SF[Performance + Menu Catalog (Snowflake)\nDATA/1_SOURCE/snowflake/*.csv]:::internalq
  end

  subgraph S2[Research · Quant + Open-text (Mixed)]
    PO[Post-order survey\nDATA/1_SOURCE/surveys/POST_ORDER_SURVEY-CONSOLIDATED.csv\nn=1,599 responses]:::researchm
    DO[Dropoff survey\nDATA/1_SOURCE/surveys/dropoff_LATEST.csv\nn=838 responses]:::researchm
    OG[OG pre-launch survey (caution)\nDATA/1_SOURCE/historical_surveys/og_survey/*\n~n=400]:::researchm
    EXT_SURV[Other surveys (Bounce/Pulse/BODS)\nDATA/1_SOURCE/external/*.xlsx\nDATA/1_SOURCE/historical_surveys/*]:::researchm
  end

  subgraph S3[Research · Qual]
    TX[Customer interview transcripts\nDATA/1_SOURCE/qual_research/transcripts/customer_interviews/*.docx\nn=88 transcripts]:::researchq
    QR[Other qual / context\nWBRs, Pascal reports, external reports\nDATA/1_SOURCE/qual_research/*\nDATA/1_SOURCE/external/*]:::researchq
  end

  %% ------------------------------------------------------------
  %% PIPELINE
  %% ------------------------------------------------------------
  E[Enrichment / cleaning\nscripts/phase1_data/*\n→ DATA/2_ENRICHED/*]:::stage
  AN[Analysis outputs\nscripts/phase2_analysis/*\n+ scripts/phase3_synthesis/*\n→ DATA/3_ANALYSIS/*]:::stage

  %% ------------------------------------------------------------
  %% LLM DERIVED
  %% ------------------------------------------------------------
  subgraph LLM[LLM-derived]
    L1[Gemini extraction\nscripts/phase2_analysis/extract_latent_demand_llm.py]:::llm
    L2[LLM outputs\nDATA/3_ANALYSIS/transcript_mentions.json\nDATA/3_ANALYSIS/llm_extraction_log.json\nDATA/3_ANALYSIS/latent_demand_scores.csv]:::llm
  end

  %% ------------------------------------------------------------
  %% DELIVERABLES
  %% ------------------------------------------------------------
  D1[Dashboards\nDELIVERABLES/dashboards/*.html\n+ docs/data/*.json]:::deliverable
  D2[Reports & slide-ready tables\nDELIVERABLES/reports/*\nDELIVERABLES/presentation_data/*]:::deliverable

  %% ------------------------------------------------------------
  %% FLOWS
  %% ------------------------------------------------------------
  A --> E
  SF --> E
  PO --> E
  DO --> E
  OG --> E
  EXT_SURV --> E
  QR --> E
  E --> AN

  TX --> L1
  L1 --> L2
  L2 --> AN

  AN --> D1
  AN --> D2

  %% ------------------------------------------------------------
  %% STYLES
  %% ------------------------------------------------------------
  classDef internalq fill:#003b30,stroke:#00d4aa,color:#f8fafc;
  classDef researchm fill:#2b1b55,stroke:#8b5cf6,color:#f8fafc;
  classDef researchq fill:#3b2a00,stroke:#f59e0b,color:#f8fafc;
  classDef llm fill:#3b0a2a,stroke:#ec4899,color:#f8fafc;
  classDef stage fill:#111827,stroke:#64748b,color:#f8fafc;
  classDef deliverable fill:#0b1f3a,stroke:#3b82f6,color:#f8fafc;
```

## Table: what each data type is, and how we use it

| Data type | Example locations | Quant/Qual | Internal/Research/LLM | Refreshable? | What we use it for (typical) |
|---|---|---:|---|---:|---|
| **Reference configs & taxonomies** | `config/*.json`, `config/dish_taxonomy.csv`, `DOCUMENTATION/SHARED/*` | Ref | Internal | Yes | **Rules of the game**: definitions, thresholds, scoring frameworks, taxonomy mappings, evidence standards |
| **Supply / Ground truth** | `DATA/1_SOURCE/anna_slides/*.csv` → `DATA/3_ANALYSIS/anna_*.csv` | Quant | Internal | Semi (new Anna export) | **What we have**: dishes, partners, zone coverage; dish taxonomy and supply constraints |
| **Behavioral performance** | `DATA/1_SOURCE/snowflake/FULL_ORDER_HISTORY.csv` (**805,804 rows**) | Quant | Internal | Yes | **Revealed preference**: demand, repeat, volume, occasion filters; benchmarking (e.g., midweek-only comparisons) |
| **Quality / feedback at scale** | `DATA/1_SOURCE/snowflake/DINNEROO_RATINGS.csv` (**10,713 rows**) | Mixed | Internal | Yes | Ratings KPIs + **open-text** evidence (sentiment, pain points, dish mentions) |
| **Menu catalog (availability truth)** | `DATA/1_SOURCE/snowflake/DINNEROO_MENU_CATALOG.csv` (**65,312 rows**) | Quant | Internal | Yes | Check if a dish/cuisine is **actually on Dinneroo**; avoids “partner serves it elsewhere” mistakes |
| **Post-order survey** | `DATA/1_SOURCE/surveys/POST_ORDER_SURVEY-CONSOLIDATED.csv` (**n=1,599**) | Mixed | Research | No | Satisfaction, “kids happy”, reorder intent; open-text improvements (latent demand + quality issues) |
| **Dropoff survey** | `DATA/1_SOURCE/surveys/dropoff_LATEST.csv` (**n=838**) | Mixed | Research | No | Barriers, unmet demand, missing options; open-text “what do you want?” |
| **OG pre-launch survey (caution)** | `DATA/1_SOURCE/historical_surveys/og_survey/*` (~n=400) | Mixed | Research | No | Demographics/context + hypotheses **only**; must be triangulated (avoid using alone for recommendations) |
| **Qual transcripts** | `DATA/1_SOURCE/qual_research/transcripts/customer_interviews/*.docx` (**n=88**) | Qual | Research | No | “Why” context; unprompted dish/cuisine mentions (high value for discovery) |
| **Qual synth / ops notes** | `DATA/1_SOURCE/qual_research/*`, `DATA/1_SOURCE/external/WBRs/*` | Qual | Research / Internal (mixed) | No | Constraints, operational feasibility, context for interpreting metrics |
| **LLM-derived extraction** | `scripts/phase2_analysis/extract_latent_demand_llm.py` → `DATA/3_ANALYSIS/transcript_mentions.json`, `.../llm_extraction_log.json` | Derived | LLM | Yes (re-run) | Turns qual/open-text into **structured mentions + audit trail**; feeds latent demand scoring |
| **Dashboards & reports** | `DELIVERABLES/dashboards/dinneroo_master_dashboard.html`, `docs/data/*.json`, `DELIVERABLES/reports/*` | Output | n/a | Re-generated | Communicate results with provenance + sample sizes; used by Product/Commercial/Ops |

## Notes (so the labels above don’t get misused)

- **Supply ≠ performance**: supply answers “what exists in a zone”; performance answers “how it behaves” (orders/ratings).  
- **Open-text is mixed** (qual text, quant counts). We treat it as **qual input** but can quantify mentions once structured (e.g., via LLM extraction).  
- **LLM outputs are *derived***: treat as *assistive structure* (with audit trail) rather than ground truth.  

