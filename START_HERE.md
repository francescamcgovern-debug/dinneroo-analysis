# Dinneroo Zone Analysis - Start Here

## Quick Start

```bash
# Run the full analysis pipeline
python scripts/run_pipeline.py --all

# Or run specific phases
python scripts/run_pipeline.py --phase 1    # Data preparation
python scripts/run_pipeline.py --phase 2    # Analysis
python scripts/run_pipeline.py --phase 3    # Synthesis

# Just update dashboards
python scripts/run_pipeline.py --dashboards
```

---

## Project Overview

This project analyzes Dinneroo zones to define MVP requirements and prioritize dishes for family midweek meals.

### Key Deliverables

1. **Priority 100 Dishes** - Ranked list of dish types families want, with ideal presentations
2. **Zone MVP Status** - Evaluation of each zone against MVP criteria
3. **Family Behavior Insights** - Understanding of family ordering patterns

### Architecture

The project uses a **task-based pipeline** following Denis Rothman's methodology:

```
CONFIG (config/)           → Adjustable weights and thresholds
    ↓
PHASE 1: DATA (scripts/phase1_data/)    → Load, extract, validate
    ↓
PHASE 2: ANALYSIS (scripts/phase2_analysis/)   → Score, analyze, segment
    ↓
PHASE 3: SYNTHESIS (scripts/phase3_synthesis/) → Generate reports, export
    ↓
DELIVERABLES (docs/, DELIVERABLES/)     → Dashboards and reports
```

For a full end-to-end view (including dashboard sync rules), see:
- `DOCUMENTATION/ARCHITECTURE_DIAGRAM.md`

---

## File Structure

```
NEW_PROJECT/
├── .cursorrules                    ← Project rules (read first)
├── config/
│   ├── factor_weights.json         ← 10-factor weights (adjustable)
│   ├── mvp_thresholds.json         ← Zone MVP criteria
│   └── evidence_standards.json     ← Sample size requirements
│
├── scripts/
│   ├── phase1_data/                ← Data loading scripts
│   │   ├── 01_load_sources.py
│   │   ├── 02_extract_survey_scores.py
│   │   └── 03_validate_data.py
│   ├── phase2_analysis/            ← Analysis scripts
│   │   ├── 01_score_dishes.py
│   │   ├── 02_analyze_zones.py
│   │   └── 03_segment_customers.py
│   ├── phase3_synthesis/           ← Report generation
│   │   ├── 01_generate_priority_list.py
│   │   ├── 02_generate_zone_report.py
│   │   └── 03_export_dashboard_data.py
│   └── run_pipeline.py             ← One-command execution
│
├── DOCUMENTATION/
│   ├── METHODOLOGY/                ← How we analyze
│   │   ├── 01_DISH_SCORING.md      ← 10-factor methodology
│   │   ├── 02_ZONE_MVP.md          ← MVP criteria methodology
│   │   ├── 03_FAMILY_BEHAVIOR.md   ← Segmentation methodology
│   │   └── 04_EVIDENCE_STANDARDS.md
│   └── CONTEXT/                    ← Background information
│
├── DATA/
│   ├── 1_SOURCE/                   ← Raw data (DO NOT MODIFY)
│   ├── 2_ENRICHED/                 ← Processed data
│   └── 3_ANALYSIS/                 ← Script outputs
│
├── docs/                           ← GitHub Pages dashboards
│   ├── index.html                  ← Landing page
│   ├── dashboards/                 ← Interactive dashboards
│   └── data/                       ← JSON data for dashboards
│
└── DELIVERABLES/
    └── reports/                    ← Markdown reports
```

---

## Key Concepts

### 10-Factor Family Meal Framework

Dishes are scored on 10 factors:

| Factor | Weight | Description |
|--------|--------|-------------|
| Kid-Friendly | 15% | Kids will actually eat it |
| Balanced/Guilt-Free | 12% | Parents feel good serving it |
| Adult Appeal | 8% | Adults enjoy it too |
| Portion Flexibility | 15% | Can feed 2 adults + 2 kids |
| Fussy Eater Friendly | 15% | Mild options available |
| Customisation | 10% | Individual preferences accommodated |
| Value at £25 | 10% | Worth it for family of 4 |
| Shareability | 5% | Family sharing at table |
| Vegetarian Option | 5% | Good veggie alternative |
| On Dinneroo Menu | 5% | Actually available |

Weights are configurable in `config/factor_weights.json`.

### Zone MVP Criteria

A zone is MVP Ready when it meets:
- ≥5 cuisines
- ≥5 partners
- ≥21 dishes
- ≥4.0 average rating

Thresholds are configurable in `config/mvp_thresholds.json`.

### Evidence Standards

- 🔵 **Single**: One source only (exploratory)
- 🟡 **Corroborated**: 2 independent sources (working hypothesis)
- 🟢 **Validated**: 3+ sources (strategic recommendation)

---

## Important Rules

### Survivorship Bias

Order volume shows what works among AVAILABLE options, not what families WANT. Always analyze latent demand via open-text.

### Dish Types, Not Brands

Think "Grilled Chicken with Sides" not "Nando's". Dish-type thinking expands options.

### Balanced Midweek Meals

Dinneroo is for balanced midweek meals, not weekend treats. Score dishes accordingly.

### Menu Gap Analysis

Check `DINNEROO_MENU_CATALOG.csv` for actual availability. Partners may serve different items on Dinneroo vs regular Deliveroo.

---

## Getting Started

1. Read `.cursorrules` for full project rules
2. Run `python scripts/run_pipeline.py --list` to see available scripts
3. Run `python scripts/run_pipeline.py --all` for full analysis
4. Open `docs/index.html` in a browser for dashboards
5. Check `DELIVERABLES/reports/` for generated reports

---

## For GitHub Pages

Push the `docs/` folder to GitHub and enable GitHub Pages to share dashboards with your team. Dashboards load data dynamically from `docs/data/` JSON files.

---

*For detailed methodology, see `DOCUMENTATION/METHODOLOGY/`*
