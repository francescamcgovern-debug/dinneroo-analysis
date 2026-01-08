# Changelog

All notable changes to the Dinneroo Zone Analysis project.

---

## [3.2.0] - 2026-01-08

### Added - Unified Definitions System

**Created single source of truth for all cuisine, dish, and zone definitions.**

This release eliminates inconsistencies across agents by establishing `scripts/utils/definitions.py` as the canonical source for all mappings.

#### New Files
- `scripts/utils/definitions.py` - Canonical definitions module (all agents must import from here)
- `scripts/utils/__init__.py` - Package initialization
- `scripts/validate_consistency.py` - Validates outputs use consistent definitions
- `scripts/update_dish_cuisines.py` - Updates priority_100 with Core 7 mappings

#### Key Changes

**Two-Level Cuisine Architecture:**
- Level 1: Core 7 (Asian, Italian, Indian, Healthy, Mexican, Middle Eastern, British) - for MVP
- Level 2: Sub-cuisines (Japanese, Thai, Vietnamese, etc.) - for drill-down analysis

**Tiered MVP Status:**
| Status | Cuisines | Description |
|--------|----------|-------------|
| MVP Ready | 5+ of 7 | North star target |
| Near MVP | 4 of 7 | Almost there |
| Progressing | 3 of 7 | Data inflection point |
| Developing | 1-2 of 7 | Early stage |
| Supply Only | Any | Partners but no orders |
| Not Started | 0 | No partners |

**Data Corrections:**
- British cuisine now correctly shows 137 zones (10.5%) - Bill's included
- Zone cuisine counting uses Anna's Core 7 columns, not messy Deliveroo tags
- MVP Ready zones: 70 (up from incorrect count due to sub-cuisine overcounting)

#### Updated Files
- `DATA/3_ANALYSIS/priority_100_unified.csv` - Added `core_7_cuisine`, `sub_cuisine` columns
- `docs/data/zone_mvp_status.json` - New two-level structure with Core 7 + sub-cuisines
- `docs/data/zone_analysis.json` - Updated methodology and MVP status breakdown
- `scripts/generate_zone_dashboard_data.py` - Uses canonical definitions
- `scripts/sync_zone_data.py` - Updated summary output
- `config/mvp_thresholds.json` - Added MVP status tiers
- `config/cuisine_hierarchy.json` - Added canonical definitions reference

#### Documentation Updates
- `DOCUMENTATION/SHARED/03_DEFINITIONS.md` - Added unified cuisine tables, MVP tiers
- `DOCUMENTATION/AGENTS/ZONE_AGENT.md` - Updated MVP definition with tiers
- `DOCUMENTATION/AGENTS/CUISINE_GAP_AGENT.md` - Added canonical import reference

#### Impact
All agents now produce consistent outputs:
- Zone says "MVP Ready with 7 cuisines" ✓
- Cuisine agent says "Japanese performs best within Asian" ✓
- Dish agent says "Katsu (Asian/Japanese) is Tier 2" ✓
- No more conflicting evidence between zone and proposition levels

---

## [3.1.0] - 2026-01-07

### Added - Ground Truth Data Reconciliation

**Reconciled supply data with Anna's authoritative spreadsheet.**

#### New Data Files
- `DATA/3_ANALYSIS/anna_family_dishes.csv` - 142 curated family dishes from Anna's Item Categorisation
- `DATA/3_ANALYSIS/anna_partner_coverage.csv` - 40 partners with 756 onboarded sites
- `DATA/3_ANALYSIS/anna_zone_dish_counts.csv` - 1,306 zones with dish/cuisine/brand counts

#### New Config Files
- `config/analysis_registry.json` - Registry of all analyses with ground truth markers
- `config/data_source_map.json` - Maps questions to appropriate data sources
- `config/brief_intake.json` - Maps brief types to required analysis

#### New Documentation
- `DOCUMENTATION/CONTEXT/08_GROUND_TRUTH_DATA.md` - Explains data hierarchy and when to use each source

#### Changed
- Updated `.cursorrules` to mandate using Anna's data for supply metrics
- Added anti-pattern: "Don't use order-derived counts for supply metrics"

#### Key Insight
Order-derived data significantly understated availability:
- Partners: ~25-30 (orders) vs 40 (ground truth) = +33%
- Sites: ~400 (orders) vs 756 (ground truth) = +89%
- Zones with dishes: ~200 (orders) vs 434 (ground truth) = +117%

---

## [3.0.0] - 2026-01-05

### Changed - Architecture Upgrade

**Major restructure from multi-agent to task-based pipeline following Denis Rothman's methodology.**

#### Architecture
- Replaced multi-agent routing system with sequential pipeline
- Created `scripts/` directory with three phases:
  - `phase1_data/` - Data loading, survey extraction, validation
  - `phase2_analysis/` - Dish scoring, zone analysis, customer segmentation
  - `phase3_synthesis/` - Report generation, dashboard export
- Added `run_pipeline.py` for one-command execution
- Created `config/` directory for adjustable weights and thresholds

#### Configuration
- `factor_weights.json` - 10-factor weights with documentation
- `mvp_thresholds.json` - Zone MVP criteria with justifications
- `evidence_standards.json` - Sample size requirements

#### Documentation
- Replaced `DOCUMENTATION/AGENTS/` with `DOCUMENTATION/METHODOLOGY/`
- Created comprehensive methodology docs:
  - `01_DISH_SCORING.md` - Full 10-factor methodology
  - `02_ZONE_MVP.md` - Zone evaluation methodology
  - `03_FAMILY_BEHAVIOR.md` - Customer segmentation methodology
  - `04_EVIDENCE_STANDARDS.md` - Evidence and citation standards

#### Dashboards
- Created `docs/` directory for GitHub Pages hosting
- Dashboards now load data dynamically from JSON files
- Added interactive weight sliders to Priority Dishes dashboard
- Updated Zone MVP dashboard with status distribution chart

#### Removed
- `DOCUMENTATION/AGENTS/` directory (replaced by METHODOLOGY)
- Agent routing logic in `.cursorrules`
- `00_COORDINATOR.md` (no longer needed)

---

## [2.0.0] - 2026-01-05

### Changed - 10-Factor Framework

- Split "Midweek Fit" into three explicit factors:
  - Kid-Friendly (15%)
  - Balanced/Guilt-Free (12%)
  - Adult Appeal (8%)
- Now 10 factors total (was 8)
- Added interactive weight sliders to dashboard

### Added
- Survey-backed scoring: Factor scores derived from actual survey outcomes where available
- Evidence type indicators: Measured / Blended / Estimated
- `survey_sample_size` column in priority dishes

---

## [1.1.0] - 2026-01-05

### Added
- Family Meal Factors Framework (8 factors)
- Priority 100 Dishes methodology
- Smart Discovery approach for generating candidate dishes
- Dish Types Framework (think types, not brands)
- Survivorship bias documentation
- Latent demand analysis framework

### Changed
- Updated `.cursorrules` with bias warnings
- Added strategic positioning context (balanced midweek meals)

---

## [1.0.0] - 2026-01-04

### Added
- Initial multi-agent system
- Dish Agent, Zone Agent, Customer Agent, Gap Agent, Data Agent
- Coordinator for question routing
- Data source inventory
- Quality standards documentation

---

## Versioning

This project uses semantic versioning:
- **Major** (X.0.0): Architecture changes, breaking changes
- **Minor** (0.X.0): New features, methodology updates
- **Patch** (0.0.X): Bug fixes, documentation updates


