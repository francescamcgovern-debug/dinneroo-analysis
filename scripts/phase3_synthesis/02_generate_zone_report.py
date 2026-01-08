"""
Script: 02_generate_zone_report.py
Phase: 3 - Synthesis
Purpose: Generate Zone MVP status report with actionable recommendations
Inputs:
    - DATA/3_ANALYSIS/zone_analysis.csv
    - DATA/3_ANALYSIS/priority_100_dishes.csv
    - config/mvp_thresholds.json
Outputs:
    - DELIVERABLES/reports/zone_mvp_report.md

This script synthesizes zone analysis into an actionable report for
Account Managers to evaluate and improve their zones.
"""

import logging
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
ANALYSIS_DIR = PROJECT_ROOT / "DATA" / "3_ANALYSIS"
DELIVERABLES_DIR = PROJECT_ROOT / "DELIVERABLES" / "reports"
CONFIG_DIR = PROJECT_ROOT / "config"


def load_zone_analysis():
    """Load zone analysis results."""
    zones_path = ANALYSIS_DIR / "zone_analysis.csv"
    if zones_path.exists():
        return pd.read_csv(zones_path)
    logger.warning("Zone analysis not found - run 02_analyze_zones.py first")
    return pd.DataFrame()


def load_priority_dishes():
    """Load Priority 100 dishes for recommendations."""
    dishes_path = ANALYSIS_DIR / "priority_100_dishes.csv"
    if dishes_path.exists():
        return pd.read_csv(dishes_path)
    return pd.DataFrame()


def load_mvp_config():
    """Load MVP thresholds configuration."""
    config_path = CONFIG_DIR / "mvp_thresholds.json"
    with open(config_path) as f:
        return json.load(f)


def generate_zone_recommendations(zone: pd.Series, priority_dishes: pd.DataFrame) -> list:
    """Generate specific recommendations for a zone."""
    recommendations = []
    
    # Check each MVP criterion
    if not zone.get('meets_cuisines', True):
        recommendations.append(f"🍽️ Add {5 - zone.get('cuisine_count', 0)} more cuisines to reach MVP")
    
    if not zone.get('meets_partners', True):
        recommendations.append(f"🏪 Recruit {5 - zone.get('partner_count', 0)} more partners")
    
    if not zone.get('meets_dishes', True):
        recommendations.append(f"📋 Add {21 - zone.get('dish_count', 0)} more dishes to menu")
    
    if not zone.get('meets_rating', True):
        recommendations.append(f"⭐ Improve average rating from {zone.get('avg_rating', 'N/A')} to 4.0+")
    
    # Add gap-specific recommendations
    supply_gaps = zone.get('supply_gaps_str', '')
    if supply_gaps and supply_gaps != 'None':
        recommendations.append(f"📍 Supply gaps: {supply_gaps}")
    
    return recommendations


def generate_report(zones_df: pd.DataFrame, priority_dishes: pd.DataFrame, config: dict) -> str:
    """Generate comprehensive Zone MVP report."""
    
    thresholds = config['mvp_criteria']
    
    report = f"""# Zone MVP Status Report

*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*

## Executive Summary

This report evaluates each Dinneroo zone against MVP criteria to identify where 
selection is no longer a barrier to growth.

### MVP Criteria

| Criterion | Threshold | Justification |
|-----------|-----------|---------------|
| Cuisines | ≥{thresholds['cuisines_min']['value']} | {thresholds['cuisines_min']['justification']} |
| Partners | ≥{thresholds['partners_min']['value']} | {thresholds['partners_min']['justification']} |
| Dishes | ≥{thresholds['dishes_min']['value']} | {thresholds['dishes_min']['justification']} |
| Rating | ≥{thresholds['rating_min']['value']} | {thresholds['rating_min']['justification']} |

### Status Distribution

"""
    
    status_counts = zones_df['mvp_status'].value_counts()
    total_zones = len(zones_df)
    
    for status, count in status_counts.items():
        pct = count / total_zones * 100
        report += f"- **{status}**: {count} zones ({pct:.1f}%)\n"
    
    report += f"""

---

## MVP Ready Zones

These zones have selection that supports growth - focus on other levers.

| Zone | Quality Score | Cuisines | Partners | Dishes | Rating |
|------|---------------|----------|----------|--------|--------|
"""
    
    mvp_ready = zones_df[zones_df['mvp_status'] == 'MVP Ready']
    for _, zone in mvp_ready.head(20).iterrows():
        report += f"| {zone['zone_name']} | {zone['quality_score']:.3f} | {zone['cuisine_count']} | {zone['partner_count']} | {zone['dish_count']} | {zone.get('avg_rating', 'N/A')} |\n"
    
    report += """

---

## Near MVP Zones (Quick Wins)

These zones are close to MVP - small improvements can unlock growth.

"""
    
    near_mvp = zones_df[zones_df['mvp_status'] == 'Near MVP'].head(15)
    for _, zone in near_mvp.iterrows():
        recommendations = generate_zone_recommendations(zone, priority_dishes)
        report += f"### {zone['zone_name']}\n"
        report += f"**Quality Score:** {zone['quality_score']:.3f} | **Criteria Met:** {zone['criteria_met']}/4\n\n"
        report += "**Actions Needed:**\n"
        for rec in recommendations:
            report += f"- {rec}\n"
        report += "\n"
    
    report += """

---

## Developing Zones

These zones need significant partner recruitment.

| Zone | Quality Score | Criteria Met | Primary Gap |
|------|---------------|--------------|-------------|
"""
    
    developing = zones_df[zones_df['mvp_status'] == 'Developing']
    for _, zone in developing.head(20).iterrows():
        primary_gap = zone.get('supply_gaps_str', 'Multiple gaps')[:40]
        report += f"| {zone['zone_name']} | {zone['quality_score']:.3f} | {zone['criteria_met']}/4 | {primary_gap} |\n"
    
    report += """

---

## Zone Quality Score Components

The quality score is calculated from:

| Component | Weight | Description |
|-----------|--------|-------------|
| Cuisine Coverage | 25% | Number of cuisines / 8 |
| Partner Density | 20% | Number of partners / 10 |
| Dish Variety | 20% | Number of dishes / 50 |
| Quality Score | 20% | Average rating / 5 |
| Volume | 15% | Order count / 1000 |

---

## How to Use This Report

### For Account Managers

1. Find your zone in the appropriate section
2. Review the recommendations for your zone
3. Prioritize actions that move you toward MVP status
4. Track progress using the quality score

### For Product Directors

1. Review MVP Ready zones - these can focus on non-selection growth levers
2. Identify Near MVP zones for quick wins
3. Allocate partner recruitment resources to high-potential Developing zones

---

*Report generated by Dinneroo Analysis Pipeline*
"""
    
    return report


def main():
    """Main function to generate zone report."""
    logger.info("=" * 60)
    logger.info("PHASE 3: Generating Zone MVP Report")
    logger.info("=" * 60)
    
    # Ensure output directory exists
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load data
    zones_df = load_zone_analysis()
    priority_dishes = load_priority_dishes()
    config = load_mvp_config()
    
    if zones_df.empty:
        logger.error("No zone data available")
        return None
    
    logger.info(f"Loaded {len(zones_df)} zones")
    
    # Generate report
    logger.info("Generating report...")
    report = generate_report(zones_df, priority_dishes, config)
    
    # Save report
    report_path = DELIVERABLES_DIR / "zone_mvp_report.md"
    with open(report_path, 'w') as f:
        f.write(report)
    
    logger.info(f"Saved report to: {report_path}")
    
    logger.info("\n" + "=" * 60)
    logger.info("ZONE REPORT SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total zones: {len(zones_df)}")
    logger.info(f"\nMVP Status distribution:")
    logger.info(zones_df['mvp_status'].value_counts().to_string())
    
    return report


if __name__ == "__main__":
    main()




