# Changelog

All notable changes to the Dinneroo Zone Analysis project.

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

