"""
Script: 01_generate_priority_list.py
Phase: 3 - Synthesis
Purpose: Generate the Priority 100 Dishes list with ideal presentations
Inputs:
    - DATA/3_ANALYSIS/priority_dishes.csv
    - DATA/3_ANALYSIS/zone_analysis.csv
    - config/factor_weights.json
Outputs: 
    - DATA/3_ANALYSIS/priority_100_dishes.csv
    - DELIVERABLES/reports/priority_dishes_report.md

This script synthesizes dish scoring into the final Priority 100 list
with positioning guidance and cuisine priorities.
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


def load_priority_dishes():
    """Load scored dishes from analysis."""
    dishes_path = ANALYSIS_DIR / "priority_dishes.csv"
    if dishes_path.exists():
        return pd.read_csv(dishes_path)
    logger.warning("Priority dishes not found - run 01_score_dishes.py first")
    return pd.DataFrame()


def load_zone_analysis():
    """Load zone analysis for gap context."""
    zones_path = ANALYSIS_DIR / "zone_analysis.csv"
    if zones_path.exists():
        return pd.read_csv(zones_path)
    return pd.DataFrame()


def load_config():
    """Load factor weights configuration."""
    config_path = CONFIG_DIR / "factor_weights.json"
    with open(config_path) as f:
        return json.load(f)


def generate_ideal_presentation(dish: pd.Series) -> str:
    """
    Generate ideal presentation guidance for a £25 family meal.
    Based on dish characteristics and family meal factors.
    """
    guidance = []
    dish_name = dish['dish_name'].lower()
    
    # Portion guidance
    if dish.get('portion_flexibility', 3) < 4:
        guidance.append("Offer family-sized portion (feeds 2 adults + 2 kids)")
    
    # Customisation guidance
    if dish.get('customisation', 3) >= 4:
        guidance.append("Highlight build-your-own options with sides")
    elif 'chicken' in dish_name or 'bowl' in dish_name:
        guidance.append("Include choice of sides and protein options")
    
    # Kid-friendly guidance
    if dish.get('kid_friendly', 3) < 3:
        guidance.append("Offer mild/plain option for kids")
    
    # Balanced meal guidance
    if dish.get('balanced_guilt_free', 3) >= 4:
        guidance.append("Position as balanced midweek meal")
    elif dish.get('balanced_guilt_free', 3) < 3:
        guidance.append("Add vegetable sides or salad option")
    
    # Value guidance
    guidance.append("Target £25 price point for family of 4")
    
    # Specific dish type guidance
    if 'pizza' in dish_name:
        guidance.append("Large shareable pizza with side salad")
    elif 'curry' in dish_name or 'indian' in dish_name:
        guidance.append("Include rice, naan, and mild option")
    elif 'chinese' in dish_name or 'noodle' in dish_name:
        guidance.append("Sharing platters with variety of dishes")
    elif 'grilled' in dish_name or 'peri' in dish_name:
        guidance.append("Quarter/half chicken with customizable sides")
    elif 'pasta' in dish_name:
        guidance.append("Family-sized pasta bowl option")
    elif 'mexican' in dish_name or 'taco' in dish_name:
        guidance.append("Build-your-own taco/burrito kit")
    
    return "; ".join(guidance) if guidance else "Standard family presentation"


def calculate_cuisine_priorities(dishes_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate cuisine priorities based on dish scores and gaps."""
    
    cuisine_stats = dishes_df.groupby('cuisine').agg({
        'composite_score': ['mean', 'max', 'count'],
        'on_dinneroo_menu': 'mean',  # Average availability
        'kid_friendly': 'mean',
        'balanced_guilt_free': 'mean'
    }).round(2)
    
    cuisine_stats.columns = ['avg_score', 'max_score', 'dish_count', 
                            'avg_availability', 'avg_kid_friendly', 'avg_balanced']
    cuisine_stats = cuisine_stats.reset_index()
    
    # Calculate priority score
    # Higher score = more dishes that are good for families but less available
    cuisine_stats['priority_score'] = (
        cuisine_stats['avg_score'] * 0.4 +
        cuisine_stats['avg_kid_friendly'] / 5 * 0.2 +
        cuisine_stats['avg_balanced'] / 5 * 0.2 +
        (5 - cuisine_stats['avg_availability']) / 5 * 0.2  # Inverse availability = gap opportunity
    ).round(3)
    
    cuisine_stats = cuisine_stats.sort_values('priority_score', ascending=False)
    cuisine_stats['priority_rank'] = range(1, len(cuisine_stats) + 1)
    
    return cuisine_stats


def generate_report(dishes_df: pd.DataFrame, cuisine_priorities: pd.DataFrame) -> str:
    """Generate markdown report for Priority 100 Dishes."""
    
    report = f"""# Priority 100 Dishes Report

*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*

## Executive Summary

This report presents the Priority 100 Dishes for Dinneroo, scored using the 10-factor 
Family Meal Factors Framework. Each dish is evaluated on its suitability for balanced 
midweek family meals at the £25 price point.

### Key Findings

- **Total dishes scored:** {len(dishes_df)}
- **Evidence distribution:**
{dishes_df['evidence_type'].value_counts().to_string()}

---

## Cuisine Priorities

Based on dish scores and current availability gaps:

| Rank | Cuisine | Avg Score | Dishes | Availability | Priority |
|------|---------|-----------|--------|--------------|----------|
"""
    
    for _, row in cuisine_priorities.head(10).iterrows():
        report += f"| {row['priority_rank']} | {row['cuisine']} | {row['avg_score']:.2f} | {row['dish_count']} | {row['avg_availability']:.1f}/5 | {row['priority_score']:.3f} |\n"
    
    report += """

---

## Top 20 Priority Dishes

| Rank | Dish | Cuisine | Score | Evidence | Kid-Friendly | Balanced |
|------|------|---------|-------|----------|--------------|----------|
"""
    
    for _, row in dishes_df.head(20).iterrows():
        report += f"| {row['rank']} | {row['dish_name'][:30]} | {row['cuisine']} | {row['composite_score']:.2f} | {row['evidence_type']} | {row.get('kid_friendly', 'N/A')}/5 | {row.get('balanced_guilt_free', 'N/A')}/5 |\n"
    
    report += """

---

## Methodology

### 10-Factor Family Meal Framework

Each dish is scored on 10 factors:

1. **Kid-Friendly (15%)** - Kids will actually eat it
2. **Balanced/Guilt-Free (12%)** - Parents feel good serving it midweek
3. **Adult Appeal (8%)** - Adults enjoy it too
4. **Portion Flexibility (15%)** - Can feed 2 adults + 2 kids
5. **Fussy Eater Friendly (15%)** - Mild options, familiar flavours
6. **Customisation (10%)** - Individual preferences accommodated
7. **Value at £25 (10%)** - Worth it for family of 4
8. **Shareability (5%)** - Family sharing at table
9. **Vegetarian Option (5%)** - Good veggie alternative
10. **On Dinneroo Menu (5%)** - Current availability

### Evidence Types

- **Measured**: 3+ factors have direct survey data (n≥5 per dish)
- **Blended**: 1-2 factors have survey data, rest estimated
- **Estimated**: No matching survey data, using heuristics

---

## Ideal Presentations (£25 Family Meal)

"""
    
    for _, row in dishes_df.head(10).iterrows():
        report += f"### {row['rank']}. {row['dish_name']}\n"
        report += f"**Cuisine:** {row['cuisine']} | **Score:** {row['composite_score']:.2f}\n\n"
        report += f"**Presentation:** {row.get('ideal_presentation', row.get('positioning_guidance', 'Standard'))}\n\n"
    
    report += """
---

## Gaps & Opportunities

### High-Scoring Dishes NOT on Dinneroo

"""
    
    gaps = dishes_df[(dishes_df.get('on_dinneroo_menu', 3) <= 2) & (dishes_df['composite_score'] >= 3.5)]
    if len(gaps) > 0:
        for _, row in gaps.head(10).iterrows():
            report += f"- **{row['dish_name']}** ({row['cuisine']}) - Score: {row['composite_score']:.2f}\n"
    else:
        report += "*No significant gaps identified*\n"
    
    report += """

---

*Report generated by Dinneroo Analysis Pipeline*
"""
    
    return report


def main():
    """Main function to generate Priority 100 list."""
    logger.info("=" * 60)
    logger.info("PHASE 3: Generating Priority 100 List")
    logger.info("=" * 60)
    
    # Ensure output directories exist
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load data
    dishes_df = load_priority_dishes()
    zones_df = load_zone_analysis()
    config = load_config()
    
    if dishes_df.empty:
        logger.error("No dish data available")
        return None
    
    logger.info(f"Loaded {len(dishes_df)} scored dishes")
    
    # Generate ideal presentations
    logger.info("Generating ideal presentations...")
    dishes_df['ideal_presentation'] = dishes_df.apply(generate_ideal_presentation, axis=1)
    
    # Get top 100
    priority_100 = dishes_df.head(100).copy()
    priority_100['priority_rank'] = range(1, len(priority_100) + 1)
    
    # Calculate cuisine priorities
    logger.info("Calculating cuisine priorities...")
    cuisine_priorities = calculate_cuisine_priorities(dishes_df)
    
    # Save Priority 100
    output_path = ANALYSIS_DIR / "priority_100_dishes.csv"
    priority_100.to_csv(output_path, index=False)
    logger.info(f"Saved Priority 100 to: {output_path}")
    
    # Save cuisine priorities
    cuisine_path = ANALYSIS_DIR / "cuisine_priorities.csv"
    cuisine_priorities.to_csv(cuisine_path, index=False)
    logger.info(f"Saved cuisine priorities to: {cuisine_path}")
    
    # Generate and save report
    logger.info("Generating report...")
    report = generate_report(priority_100, cuisine_priorities)
    report_path = DELIVERABLES_DIR / "priority_dishes_report.md"
    with open(report_path, 'w') as f:
        f.write(report)
    logger.info(f"Saved report to: {report_path}")
    
    logger.info("\n" + "=" * 60)
    logger.info("PRIORITY 100 SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Priority 100 dishes generated")
    logger.info(f"\nTop 5 cuisines:")
    logger.info(cuisine_priorities[['priority_rank', 'cuisine', 'priority_score']].head(5).to_string())
    logger.info(f"\nTop 5 dishes:")
    logger.info(priority_100[['priority_rank', 'dish_name', 'composite_score']].head(5).to_string())
    
    return priority_100


if __name__ == "__main__":
    main()



