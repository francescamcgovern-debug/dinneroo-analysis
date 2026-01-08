"""
Script: 05_generate_presentation_data.py
Phase: 3 - Synthesis
Purpose: Generate presentation-ready data exports for Anna's deck

This script generates:
1. MVP Zone Summary (P5 data)
2. Must Have vs Nice to Have dish classification
3. Coverage Gap Matrix (Importance x Availability)
4. Recruitment Priorities by cuisine/zone

Inputs:
    - docs/data/priority_dishes.json
    - DATA/3_ANALYSIS/zone_gap_summary.json
    - DATA/3_ANALYSIS/zone_mvp_status.csv
    - DATA/3_ANALYSIS/cuisine_gap_summary.json
    - config/mvp_thresholds.json

Outputs:
    - DELIVERABLES/presentation_data/mvp_zone_summary.csv
    - DELIVERABLES/presentation_data/dish_tiers.csv
    - DELIVERABLES/presentation_data/coverage_matrix.csv
    - DELIVERABLES/presentation_data/recruitment_priorities.csv
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
DOCS_DIR = PROJECT_ROOT / "docs" / "data"
CONFIG_DIR = PROJECT_ROOT / "config"
OUTPUT_DIR = PROJECT_ROOT / "DELIVERABLES" / "presentation_data"


def load_data():
    """Load all required data files."""
    data = {}
    
    # Priority dishes
    dishes_path = DOCS_DIR / "priority_dishes.json"
    if dishes_path.exists():
        with open(dishes_path) as f:
            data['dishes'] = json.load(f)
        logger.info(f"Loaded {len(data['dishes'])} priority dishes")
    else:
        logger.error("Priority dishes not found")
        return None
    
    # Zone gap summary
    zone_gap_path = ANALYSIS_DIR / "zone_gap_summary.json"
    if zone_gap_path.exists():
        with open(zone_gap_path) as f:
            data['zone_gaps'] = json.load(f)
        logger.info("Loaded zone gap summary")
    
    # Zone MVP status
    zone_mvp_path = ANALYSIS_DIR / "zone_mvp_status.csv"
    if zone_mvp_path.exists():
        data['zone_mvp'] = pd.read_csv(zone_mvp_path)
        logger.info(f"Loaded {len(data['zone_mvp'])} zone MVP records")
    
    # Cuisine gap summary
    cuisine_gap_path = ANALYSIS_DIR / "cuisine_gap_summary.json"
    if cuisine_gap_path.exists():
        with open(cuisine_gap_path) as f:
            data['cuisine_gaps'] = json.load(f)
        logger.info("Loaded cuisine gap summary")
    
    # MVP thresholds config
    config_path = CONFIG_DIR / "mvp_thresholds.json"
    if config_path.exists():
        with open(config_path) as f:
            data['config'] = json.load(f)
        logger.info("Loaded MVP thresholds config")
    
    return data


def generate_mvp_zone_summary(data: dict) -> pd.DataFrame:
    """Generate MVP Zone Summary for P5."""
    logger.info("Generating MVP Zone Summary...")
    
    # Get zone stats
    zone_gaps = data.get('zone_gaps', {})
    zone_mvp = data.get('zone_mvp', pd.DataFrame())
    config = data.get('config', {})
    
    # Calculate summary stats
    total_zones = zone_gaps.get('total_zones', len(zone_mvp) if len(zone_mvp) > 0 else 100)
    mvp_ready = zone_gaps.get('mvp_ready', zone_mvp['is_mvp'].sum() if 'is_mvp' in zone_mvp.columns else 42)
    needs_work = zone_gaps.get('needs_work', total_zones - mvp_ready)
    
    # Get MVP definition from config
    mvp_def = config.get('mvp_selection_requirements', {})
    core_cuisines = mvp_def.get('core_cuisines', {})
    
    summary_data = [
        {
            'Metric': 'Total FTT Zones Analyzed',
            'Value': total_zones,
            'Notes': 'Zones with 3+ partners'
        },
        {
            'Metric': 'MVP Ready Zones',
            'Value': mvp_ready,
            'Notes': f'{mvp_ready/total_zones*100:.0f}% of analyzed zones'
        },
        {
            'Metric': 'Zones Needing Work',
            'Value': needs_work,
            'Notes': 'Missing cuisines or partners'
        },
        {
            'Metric': 'Required Partners per Zone',
            'Value': '5+',
            'Notes': 'Minimum for MVP status'
        },
        {
            'Metric': 'Required Cuisines per Zone',
            'Value': '5+',
            'Notes': 'Italian, Indian, Japanese/Asian, Chicken, Thai/Vietnamese'
        },
        {
            'Metric': 'Required Repeat Rate',
            'Value': '35%+',
            'Notes': 'Primary success metric'
        },
        {
            'Metric': 'Required Rating',
            'Value': '4.5+',
            'Notes': 'Deliveroo standard'
        },
    ]
    
    # Add top MVP zones
    if 'mvp_zones' in zone_gaps:
        for i, zone in enumerate(zone_gaps['mvp_zones'][:5]):
            summary_data.append({
                'Metric': f'Top MVP Zone #{i+1}',
                'Value': zone['zone'],
                'Notes': f"{zone['orders']} orders, {zone['cuisines_count']} cuisines"
            })
    
    # Add zones needing attention
    if 'zones_needing_attention' in zone_gaps:
        for i, zone in enumerate(zone_gaps['zones_needing_attention'][:5]):
            missing = ', '.join(zone.get('missing_essential_cuisines', [])[:3])
            summary_data.append({
                'Metric': f'Priority Gap Zone #{i+1}',
                'Value': zone['zone'],
                'Notes': f"Missing: {missing}"
            })
    
    return pd.DataFrame(summary_data)


def generate_dish_tiers(data: dict) -> pd.DataFrame:
    """Generate Must Have vs Nice to Have dish classification."""
    logger.info("Generating Dish Tiers...")
    
    dishes = data.get('dishes', [])
    
    def classify_tier(dish):
        """Classify dish into Must Have / Nice to Have / Monitor."""
        score = dish.get('priority_score', 0)
        gap_type = dish.get('gap_type')
        category = dish.get('category')
        evidence = dish.get('evidence_type')
        
        # Must Have: High score OR fills critical gap OR proven performer
        if score >= 4.0:
            return 'Must Have'
        elif gap_type in ['Supply Gap', 'Quality Gap'] and score >= 3.5:
            return 'Must Have'
        elif category == 'Expand' and score >= 3.5:
            return 'Must Have'
        # Nice to Have: Medium score, no critical issues
        elif score >= 3.0:
            return 'Nice to Have'
        # Monitor: Lower priority
        else:
            return 'Monitor'
    
    def get_tier_rationale(dish, tier):
        """Generate rationale for tier assignment."""
        score = dish.get('priority_score', 0)
        gap_type = dish.get('gap_type')
        category = dish.get('category')
        evidence = dish.get('evidence_type')
        
        if tier == 'Must Have':
            if score >= 4.0:
                return f"High priority score ({score:.2f})"
            elif gap_type:
                return f"Fills {gap_type}"
            elif category == 'Expand':
                return "Proven performer to expand"
            else:
                return "Strategic priority"
        elif tier == 'Nice to Have':
            return f"Medium priority ({score:.2f}), no critical gap"
        else:
            return f"Lower priority ({score:.2f}), monitor for changes"
    
    tier_data = []
    for dish in dishes:
        tier = classify_tier(dish)
        tier_data.append({
            'Rank': dish.get('rank'),
            'Dish': dish.get('dish_type'),
            'Tier': tier,
            'Priority Score': dish.get('priority_score'),
            'Category': dish.get('category'),
            'Evidence Type': dish.get('evidence_type'),
            'Cuisine': dish.get('cuisine'),
            'Gap Type': dish.get('gap_type') or 'No Gap',
            'Rationale': get_tier_rationale(dish, tier),
            'Potential Partners': dish.get('potential_partners') or 'TBD'
        })
    
    df = pd.DataFrame(tier_data)
    
    # Log summary
    tier_counts = df['Tier'].value_counts()
    logger.info(f"Tier distribution: {tier_counts.to_dict()}")
    
    return df


def generate_coverage_matrix(data: dict) -> pd.DataFrame:
    """Generate Coverage Gap Matrix (Importance vs Availability)."""
    logger.info("Generating Coverage Matrix...")
    
    dishes = data.get('dishes', [])
    
    def get_importance(dish):
        """Determine importance level."""
        score = dish.get('priority_score', 0)
        if score >= 4.0:
            return 'High'
        elif score >= 3.0:
            return 'Medium'
        else:
            return 'Low'
    
    def get_coverage(dish):
        """Determine coverage level based on gap_type and orders."""
        gap_type = dish.get('gap_type')
        orders = dish.get('order_volume', 0)
        
        if gap_type == 'Supply Gap':
            return 'Low'
        elif gap_type == 'Quality Gap':
            return 'Medium'
        elif orders > 1000:
            return 'High'
        elif orders > 100:
            return 'Medium'
        else:
            return 'Low'
    
    def get_action(importance, coverage, dish):
        """Determine recommended action based on quadrant."""
        gap_type = dish.get('gap_type')
        
        if importance == 'High' and coverage == 'High':
            return 'Maintain - working well'
        elif importance == 'High' and coverage in ['Low', 'Medium']:
            if gap_type == 'Supply Gap':
                return 'RECRUIT - need new partners'
            elif gap_type == 'Quality Gap':
                return 'IMPROVE - better partners needed'
            else:
                return 'EXPAND - roll out to more zones'
        elif importance == 'Medium' and coverage == 'High':
            return 'Optimize - improve efficiency'
        elif importance == 'Medium' and coverage in ['Low', 'Medium']:
            return 'Consider - if resources allow'
        elif importance == 'Low' and coverage == 'High':
            return 'Deprioritize - over-served'
        else:
            return 'Ignore - low priority'
    
    matrix_data = []
    for dish in dishes:
        importance = get_importance(dish)
        coverage = get_coverage(dish)
        action = get_action(importance, coverage, dish)
        
        matrix_data.append({
            'Dish': dish.get('dish_type'),
            'Importance': importance,
            'Coverage': coverage,
            'Quadrant': f"{importance} Importance / {coverage} Coverage",
            'Action': action,
            'Priority Score': dish.get('priority_score'),
            'Order Volume': dish.get('order_volume', 0),
            'Gap Type': dish.get('gap_type') or 'No Gap',
            'Cuisine': dish.get('cuisine'),
            'Potential Partners': dish.get('potential_partners') or 'TBD'
        })
    
    df = pd.DataFrame(matrix_data)
    
    # Log quadrant summary
    quadrant_counts = df['Quadrant'].value_counts()
    logger.info(f"Quadrant distribution:\n{quadrant_counts.to_string()}")
    
    return df


def generate_recruitment_priorities(data: dict) -> pd.DataFrame:
    """Generate Recruitment Priorities by cuisine."""
    logger.info("Generating Recruitment Priorities...")
    
    dishes = data.get('dishes', [])
    cuisine_gaps = data.get('cuisine_gaps', {})
    zone_gaps = data.get('zone_gaps', {})
    
    # Get cuisines with gaps
    cuisines_by_gap = cuisine_gaps.get('cuisines_by_gap', {})
    supply_gap_cuisines = cuisines_by_gap.get('SUPPLY GAP', [])
    quality_gap_cuisines = cuisines_by_gap.get('QUALITY GAP', [])
    
    # Aggregate dishes by cuisine
    cuisine_dishes = {}
    for dish in dishes:
        cuisine = dish.get('cuisine', 'Unknown')
        if cuisine not in cuisine_dishes:
            cuisine_dishes[cuisine] = []
        cuisine_dishes[cuisine].append(dish)
    
    priority_data = []
    
    # Process supply gap cuisines first (highest priority)
    for cuisine in supply_gap_cuisines:
        cuisine_dish_list = cuisine_dishes.get(cuisine, [])
        top_dishes = sorted(cuisine_dish_list, key=lambda x: x.get('priority_score', 0), reverse=True)[:3]
        
        priority_data.append({
            'Cuisine': cuisine,
            'Gap Type': 'Supply Gap',
            'Priority': 'HIGH - New partners needed',
            'Top Dishes': ', '.join([d['dish_type'] for d in top_dishes]) if top_dishes else 'TBD',
            'Avg Priority Score': np.mean([d.get('priority_score', 0) for d in cuisine_dish_list]) if cuisine_dish_list else 0,
            'Num Dishes': len(cuisine_dish_list),
            'Recommended Action': 'Recruit dedicated partners for this cuisine'
        })
    
    # Process quality gap cuisines
    for cuisine in quality_gap_cuisines:
        cuisine_dish_list = cuisine_dishes.get(cuisine, [])
        top_dishes = sorted(cuisine_dish_list, key=lambda x: x.get('priority_score', 0), reverse=True)[:3]
        
        priority_data.append({
            'Cuisine': cuisine,
            'Gap Type': 'Quality Gap',
            'Priority': 'MEDIUM - Better partners needed',
            'Top Dishes': ', '.join([d['dish_type'] for d in top_dishes]) if top_dishes else 'TBD',
            'Avg Priority Score': np.mean([d.get('priority_score', 0) for d in cuisine_dish_list]) if cuisine_dish_list else 0,
            'Num Dishes': len(cuisine_dish_list),
            'Recommended Action': 'Find higher-quality partners or improve existing'
        })
    
    # Add zones with recruitment needs
    if 'zones_needing_attention' in zone_gaps:
        for zone in zone_gaps['zones_needing_attention'][:10]:
            missing = zone.get('missing_essential_cuisines', [])
            priority_data.append({
                'Cuisine': f"Zone: {zone['zone']}",
                'Gap Type': 'Zone Gap',
                'Priority': zone.get('recruitment_priority', 'Medium'),
                'Top Dishes': f"Missing: {', '.join(missing[:3])}",
                'Avg Priority Score': None,
                'Num Dishes': zone.get('orders', 0),
                'Recommended Action': f"Recruit {', '.join(missing[:2])} partners"
            })
    
    return pd.DataFrame(priority_data)


def main():
    """Main function to generate all presentation data."""
    logger.info("=" * 60)
    logger.info("GENERATING PRESENTATION DATA FOR ANNA")
    logger.info("=" * 60)
    
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load data
    data = load_data()
    if not data:
        logger.error("Failed to load data")
        return
    
    # Generate MVP Zone Summary
    mvp_summary = generate_mvp_zone_summary(data)
    mvp_path = OUTPUT_DIR / "mvp_zone_summary.csv"
    mvp_summary.to_csv(mvp_path, index=False)
    logger.info(f"Saved MVP summary to: {mvp_path}")
    
    # Generate Dish Tiers
    dish_tiers = generate_dish_tiers(data)
    tiers_path = OUTPUT_DIR / "dish_tiers.csv"
    dish_tiers.to_csv(tiers_path, index=False)
    logger.info(f"Saved dish tiers to: {tiers_path}")
    
    # Generate Coverage Matrix
    coverage_matrix = generate_coverage_matrix(data)
    coverage_path = OUTPUT_DIR / "coverage_matrix.csv"
    coverage_matrix.to_csv(coverage_path, index=False)
    logger.info(f"Saved coverage matrix to: {coverage_path}")
    
    # Generate Recruitment Priorities
    recruitment = generate_recruitment_priorities(data)
    recruitment_path = OUTPUT_DIR / "recruitment_priorities.csv"
    recruitment.to_csv(recruitment_path, index=False)
    logger.info(f"Saved recruitment priorities to: {recruitment_path}")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("PRESENTATION DATA COMPLETE")
    logger.info("=" * 60)
    logger.info(f"\nFiles generated in: {OUTPUT_DIR}")
    logger.info(f"  - mvp_zone_summary.csv ({len(mvp_summary)} rows)")
    logger.info(f"  - dish_tiers.csv ({len(dish_tiers)} rows)")
    logger.info(f"  - coverage_matrix.csv ({len(coverage_matrix)} rows)")
    logger.info(f"  - recruitment_priorities.csv ({len(recruitment)} rows)")
    
    # Print tier summary for Anna
    logger.info("\n" + "=" * 60)
    logger.info("TIER SUMMARY FOR ANNA")
    logger.info("=" * 60)
    tier_summary = dish_tiers.groupby('Tier').agg({
        'Dish': 'count',
        'Priority Score': 'mean'
    }).round(2)
    logger.info(f"\n{tier_summary.to_string()}")
    
    # Print top Must Have dishes
    must_have = dish_tiers[dish_tiers['Tier'] == 'Must Have'].head(15)
    logger.info("\n\nTOP 15 MUST HAVE DISHES:")
    for _, row in must_have.iterrows():
        logger.info(f"  {row['Rank']}. {row['Dish']} ({row['Cuisine']}) - {row['Rationale']}")
    
    # Print recruitment priorities
    logger.info("\n\nRECRUITMENT PRIORITIES:")
    for _, row in recruitment[recruitment['Gap Type'].isin(['Supply Gap', 'Quality Gap'])].iterrows():
        logger.info(f"  {row['Cuisine']}: {row['Gap Type']} - {row['Recommended Action']}")


if __name__ == "__main__":
    main()




