# Dinneroo Zone Analysis — Architecture Diagram

## Purpose

This diagram shows **how raw sources flow through the pipeline scripts into analysis outputs and dashboards**, including the **single source of truth** for the master dashboard.

## End-to-end pipeline (sources → scripts → outputs)

```mermaid
flowchart TB
  %% -----------------------------
  %% Sources
  %% -----------------------------
  subgraph S["Data Sources (read-only)"]
    SF["Snowflake extracts\n`DATA/1_SOURCE/snowflake/*.csv`\n(Performance metrics)"]:::source
    ANNA["Anna supply exports\n`DATA/1_SOURCE/anna_slides/anna_*.csv`\n(Supply metrics)"]:::source
    SURV["Surveys\n`DATA/1_SOURCE/surveys/*`\n(Preference metrics)"]:::source
    QUAL["Qual research\n`DATA/1_SOURCE/qual_research/*`\n(Open-text, transcripts)"]:::source
    CFG["Config\n`config/*.json`\n(Thresholds, definitions, standards)"]:::config
  end

  %% -----------------------------
  %% Phase 1
  %% -----------------------------
  subgraph P1["Phase 1 — Data preparation (`scripts/phase1_data/`)"]
    L1["01_load_sources.py\nLoad + standardise sources"]:::proc
    L2["02_extract_survey_scores.py\nSurvey feature extraction"]:::proc
    L3["03_validate_data.py\nData QA checks"]:::proc
    L4["04_validate_config.py\nConfig ↔ data validation (fail-fast)"]:::proc
    L5["05_extract_performance.py\nPerformance features (for v3 scoring)"]:::proc
  end

  %% -----------------------------
  %% Phase 2
  %% -----------------------------
  subgraph P2["Phase 2 — Analysis (`scripts/phase2_analysis/`)"]
    A1["01_score_dishes_v3.py\nTwo-track scoring"]:::proc
    A2["02_analyze_zones.py\nZone performance + coverage"]:::proc
    A3["03_segment_customers.py\nSegmentation"]:::proc
    A4["04_smart_discovery.py\nSmart Discovery dishes"]:::proc
    A5["generate_three_lists.py\nSegment-specific rankings"]:::proc
  end

  %% -----------------------------
  %% Phase 3
  %% -----------------------------
  subgraph P3["Phase 3 — Synthesis (`scripts/phase3_synthesis/` + `scripts/`)"]
    S1["01_generate_priority_list_v2.py\nPriority list export"]:::proc
    S2["02_generate_zone_report.py\nZone report generation"]:::proc
    S3["03_export_dashboard_data.py\n(Currently empty / no-op)"]:::proc
    S4["generate_zone_dashboard_data.py\nBuild `docs/data/zone_analysis.json`"]:::proc
    S5["sync_zone_data.py\nBuild `zone_data.js` + copy dashboard to `docs/`"]:::proc
    S6["update_master_dashboard.py\nRefresh master dashboard metrics"]:::proc
  end

  %% -----------------------------
  %% Data artifacts
  %% -----------------------------
  subgraph D["Key Data Artifacts"]
    E1["`DATA/2_ENRICHED/*`\nEnriched joins + QA reports"]:::data
    O1["`DATA/3_ANALYSIS/*`\nAnalysis outputs"]:::data
    ZMVP["`docs/data/zone_mvp_status.json`\nEstablished MVP status (do not recalc)"]:::data
    ZAN["`docs/data/zone_analysis.json`\nZone dataset used by dashboards"]:::data
  end

  %% -----------------------------
  %% Deliverables
  %% -----------------------------
  subgraph OUT["Deliverables"]
    REP["`DELIVERABLES/reports/*`"]:::out
    PRES["`DELIVERABLES/presentation_data/*`"]:::out
    DASH["`DELIVERABLES/dashboards/dinneroo_master_dashboard.html`\n(SINGLE SOURCE OF TRUTH: edit here)"]:::out
    GH["`docs/`\nGitHub Pages output (auto-synced; do not edit by hand)"]:::out
  end

  %% -----------------------------
  %% Edges
  %% -----------------------------
  SF --> L1
  ANNA --> L1
  SURV --> L1
  QUAL --> L1
  CFG --> L4
  CFG --> A1

  L1 --> E1
  L2 --> E1
  L3 --> E1
  L4 --> E1
  L5 --> E1

  E1 --> A1
  E1 --> A2
  E1 --> A3
  E1 --> A4
  E1 --> A5

  A1 --> O1
  A2 --> O1
  A3 --> O1
  A4 --> O1
  A5 --> O1

  O1 --> S1
  O1 --> S2
  O1 --> S3
  O1 --> S4
  ZMVP --> S4

  S1 --> REP
  S2 --> REP
  S3 --> PRES
  S4 --> ZAN
  S4 --> ZMVP
  ZAN --> S5
  S6 --> DASH
  DASH --> S5
  S5 --> GH
  REP --> OUT
  PRES --> OUT

  %% -----------------------------
  %% Styles
  %% -----------------------------
  classDef source fill:#1f2937,stroke:#94a3b8,color:#f8fafc;
  classDef config fill:#0f766e,stroke:#5eead4,color:#f8fafc;
  classDef proc fill:#1e3a8a,stroke:#93c5fd,color:#f8fafc;
  classDef data fill:#111827,stroke:#a78bfa,color:#f8fafc;
  classDef out fill:#7c2d12,stroke:#fdba74,color:#f8fafc;
```

## Dashboard deployment flow (single source of truth)

```mermaid
flowchart LR
  MASTER["`DELIVERABLES/dashboards/dinneroo_master_dashboard.html`\nEDIT THIS FILE"]:::out
  SYNC["`scripts/sync_zone_data.py`\nCopies master dashboard + syncs data"]:::proc
  PAGES["`docs/dashboard.html`\nGitHub Pages output\nDO NOT EDIT DIRECTLY"]:::out

  MASTER --> SYNC --> PAGES

  classDef proc fill:#1e3a8a,stroke:#93c5fd,color:#f8fafc;
  classDef out fill:#7c2d12,stroke:#fdba74,color:#f8fafc;
```

## Quick “what do I run?” (common paths)

- **Update dashboard only (after editing HTML)**: `python3 scripts/sync_zone_data.py`
- **Regenerate zone dashboard data then sync**:
  - `python3 scripts/generate_zone_dashboard_data.py`
  - `python3 scripts/sync_zone_data.py`
- **Full regen (rare)**: `python3 scripts/run_pipeline.py --phase 3`

