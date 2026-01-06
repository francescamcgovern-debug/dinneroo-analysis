"""
Script: 01_generate_priority_list_v2.py
Phase: 3 - Synthesis
Purpose: Generate Priority 100+ Dishes combining Track A, Track B, and Smart Discovery

This script combines:
- Track A: Performance scores (proven performers)
- Track B: Opportunity scores (demand signals)
- Smart Discovery: LLM-identified dishes partners could make

Output is the final Priority 100+ list with clear evidence flags.

Inputs:
    - DATA/3_ANALYSIS/dish_performance_scores.csv (Track A)
    - DATA/3_ANALYSIS/dish_opportunity_scores.csv (Track B)
    - DATA/3_ANALYSIS/smart_discovery_dishes.csv (Discovery)

Outputs:
    - DATA/3_ANALYSIS/priority_100_final.csv
    - DATA/3_ANALYSIS/priority_100_final.json
    - docs/data/priority_dishes.json (for dashboard)
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


def load_all_scores():
    """Load all scoring data from the three sources."""
    data = {}
    
    # Track A: Performance scores
    track_a_path = ANALYSIS_DIR / "dish_performance_scores.csv"
    if track_a_path.exists():
        data['track_a'] = pd.read_csv(track_a_path)
        logger.info(f"Loaded Track A: {len(data['track_a'])} dishes")
    else:
        data['track_a'] = pd.DataFrame()
        logger.warning("Track A not found")
    
    # Track B: Opportunity scores
    track_b_path = ANALYSIS_DIR / "dish_opportunity_scores.csv"
    if track_b_path.exists():
        data['track_b'] = pd.read_csv(track_b_path)
        logger.info(f"Loaded Track B: {len(data['track_b'])} dishes")
    else:
        data['track_b'] = pd.DataFrame()
        logger.warning("Track B not found")
    
    # Smart Discovery
    discovery_path = ANALYSIS_DIR / "smart_discovery_dishes.csv"
    if discovery_path.exists():
        data['discovery'] = pd.read_csv(discovery_path)
        logger.info(f"Loaded Discovery: {len(data['discovery'])} dishes")
    else:
        data['discovery'] = pd.DataFrame()
        logger.warning("Smart Discovery not found")
    
    return data


def normalize_dish_name(name: str) -> str:
    """Normalize dish name for deduplication."""
    if pd.isna(name):
        return ""
    return str(name).lower().strip()


def merge_and_deduplicate(data: dict) -> pd.DataFrame:
    """Merge all sources and deduplicate, keeping best score for each dish."""
    all_dishes = []
    seen_dishes = {}  # Track seen dishes by normalized name
    
    # Process Track A dishes (highest priority - proven performers)
    if len(data['track_a']) > 0:
        for _, row in data['track_a'].iterrows():
            dish_name = str(row['dish_type'])
            normalized = normalize_dish_name(dish_name)
            
            # Skip if already seen (keep first occurrence which has higher priority)
            if normalized in seen_dishes:
                continue
            
            dish = {
                'dish_type': dish_name,
                'track_a_score': row.get('track_a_score'),
                'track_b_score': None,  # Will be filled from Track B
                'discovery_score': None,
                'order_volume': row.get('order_volume', 0),
                'avg_rating': row.get('avg_rating'),
                'repeat_rate': row.get('repeat_rate'),
                'adult_satisfaction': row.get('adult_satisfaction'),
                'kids_happy': row.get('kids_happy'),
                'survey_n': row.get('survey_n', 0),
                'evidence_type': 'Measured',
                'source': 'Track A',
            }
            all_dishes.append(dish)
            seen_dishes[normalized] = len(all_dishes) - 1  # Store index
    
    # Process Track B dishes
    if len(data['track_b']) > 0:
        for _, row in data['track_b'].iterrows():
            dish_name = str(row['dish_type'])
            normalized = normalize_dish_name(dish_name)
            
            # Update existing dish with Track B score
            if normalized in seen_dishes:
                idx = seen_dishes[normalized]
                all_dishes[idx]['track_b_score'] = row.get('track_b_score')
                all_dishes[idx]['latent_demand_mentions'] = row.get('latent_demand_mentions', 0)
                # Only update cuisine if not already set
                if not all_dishes[idx].get('cuisine') or pd.isna(all_dishes[idx].get('cuisine')):
                    all_dishes[idx]['cuisine'] = row.get('cuisine')
                all_dishes[idx]['gap_type'] = row.get('gap_type')
                all_dishes[idx]['potential_partners'] = row.get('potential_partners')
            else:
                # Add new dish if not in Track A
                dish = {
                    'dish_type': dish_name,
                    'track_a_score': None,
                    'track_b_score': row.get('track_b_score'),
                    'discovery_score': None,
                    'order_volume': row.get('order_volume', 0),
                    'avg_rating': None,
                    'repeat_rate': None,
                    'adult_satisfaction': None,
                    'kids_happy': None,
                    'survey_n': 0,
                    'latent_demand_mentions': row.get('latent_demand_mentions', 0),
                    'cuisine': row.get('cuisine'),
                    'gap_type': row.get('gap_type'),
                    'potential_partners': row.get('potential_partners'),
                    'evidence_type': 'Opportunity',
                    'source': 'Track B',
                }
                all_dishes.append(dish)
                seen_dishes[normalized] = len(all_dishes) - 1
    
    # Process Discovery dishes
    if len(data['discovery']) > 0:
        for _, row in data['discovery'].iterrows():
            dish_name = str(row['dish_type'])
            normalized = normalize_dish_name(dish_name)
            
            # Update existing dish with discovery info
            if normalized in seen_dishes:
                idx = seen_dishes[normalized]
                all_dishes[idx]['discovery_score'] = row.get('discovery_score')
                all_dishes[idx]['discovery_reason'] = row.get('reason')
                all_dishes[idx]['discovery_partner'] = row.get('partner')
                # Update cuisine if not set
                if not all_dishes[idx].get('cuisine') or pd.isna(all_dishes[idx].get('cuisine')):
                    all_dishes[idx]['cuisine'] = row.get('cuisine')
            else:
                # Add new discovery dish
                dish = {
                    'dish_type': dish_name,
                    'track_a_score': None,
                    'track_b_score': None,
                    'discovery_score': row.get('discovery_score'),
                    'order_volume': 0,
                    'avg_rating': None,
                    'repeat_rate': None,
                    'adult_satisfaction': None,
                    'kids_happy': None,
                    'survey_n': 0,
                    'latent_demand_mentions': 0,
                    'cuisine': row.get('cuisine'),
                    'gap_type': None,
                    'potential_partners': row.get('partner'),
                    'discovery_reason': row.get('reason'),
                    'evidence_type': 'Discovery',
                    'source': 'Smart Discovery',
                }
                all_dishes.append(dish)
                seen_dishes[normalized] = len(all_dishes) - 1
    
    # Final deduplication pass and data cleanup
    df = pd.DataFrame(all_dishes)
    
    # Drop exact duplicates by dish_type (case-insensitive), keeping first (highest priority)
    df['_normalized'] = df['dish_type'].apply(normalize_dish_name)
    df = df.drop_duplicates(subset=['_normalized'], keep='first')
    df = df.drop(columns=['_normalized'])
    
    logger.info(f"After deduplication: {len(df)} unique dishes")
    
    return df


def calculate_final_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate final priority scores and categories."""
    
    def calculate_priority_score(row):
        """Calculate combined priority score."""
        track_a = row.get('track_a_score')
        track_b = row.get('track_b_score')
        discovery = row.get('discovery_score')
        
        # If has Track A (proven performer), weight it heavily
        if pd.notna(track_a):
            if pd.notna(track_b):
                # Both tracks: 60% A, 40% B
                return round(track_a * 0.6 + track_b * 0.4, 2)
            else:
                return round(track_a, 2)
        
        # If only Track B
        if pd.notna(track_b):
            return round(track_b, 2)
        
        # If only Discovery
        if pd.notna(discovery):
            return round(discovery, 2)
        
        return 0.0
    
    def categorize(row):
        """Assign category based on scores and evidence."""
        has_track_a = pd.notna(row.get('track_a_score'))
        track_a = row.get('track_a_score', 0) or 0
        track_b = row.get('track_b_score', 0) or 0
        has_discovery = pd.notna(row.get('discovery_score'))
        order_volume = row.get('order_volume', 0) or 0
        survey_n = row.get('survey_n', 0) or 0
        
        # Only mark as "Fix" if we have STRONG evidence of underperformance
        # (high volume + low scores, or survey data showing issues)
        if has_track_a:
            if track_a >= 4.0:
                return 'Expand'  # Proven winner, expand to more zones
            elif track_a >= 3.0 and track_b >= 3.0:
                return 'Investigate'  # Mixed signals, investigate
            elif order_volume >= 500 or survey_n >= 20:
                # Only "Fix" if we have enough data to be confident it's underperforming
                return 'Fix'  # Underperforming with strong evidence
            else:
                return 'Monitor'  # Not enough data to confidently say it needs fixing
        elif track_b >= 3.5:
            return 'Recruit'  # High opportunity, recruit partners
        elif has_discovery:
            return 'Discover'  # LLM-identified opportunity
        else:
            return 'Monitor'  # Low priority, monitor
    
    def get_action(row):
        """Get recommended action for each dish."""
        category = row['category']
        dish = row['dish_type']
        partners = row.get('potential_partners', '')
        
        actions = {
            'Expand': f"Roll out {dish} to more zones - proven performer",
            'Recruit': f"Recruit partners to offer {dish}" + (f" (try: {partners})" if partners else ""),
            'Investigate': f"Investigate why {dish} has demand but lower performance",
            'Fix': f"Improve {dish} quality or deprioritize",
            'Discover': f"Test {dish} with {partners}" if partners else f"Find partner for {dish}",
            'Monitor': f"Monitor {dish} for changes in demand",
        }
        return actions.get(category, "Review")
    
    df['priority_score'] = df.apply(calculate_priority_score, axis=1)
    df['category'] = df.apply(categorize, axis=1)
    df['recommended_action'] = df.apply(get_action, axis=1)
    
    # Sort by priority score
    df = df.sort_values('priority_score', ascending=False)
    df['rank'] = range(1, len(df) + 1)
    
    return df


def format_evidence_flag(row) -> str:
    """Create human-readable evidence flag."""
    flags = []
    
    if pd.notna(row.get('track_a_score')):
        flags.append(f"Performance: {row['track_a_score']:.1f}/5")
    
    if pd.notna(row.get('track_b_score')):
        flags.append(f"Opportunity: {row['track_b_score']:.1f}/5")
    
    if pd.notna(row.get('discovery_score')):
        flags.append(f"Discovery: {row['discovery_score']:.1f}/5")
    
    if row.get('survey_n', 0) > 0:
        flags.append(f"Survey n={int(row['survey_n'])}")
    
    if row.get('order_volume', 0) > 0:
        flags.append(f"Orders: {int(row['order_volume'])}")
    
    return " | ".join(flags) if flags else "No data"


def main():
    """Main function to generate Priority 100+ list."""
    logger.info("=" * 60)
    logger.info("GENERATING PRIORITY 100+ DISHES")
    logger.info("=" * 60)
    
    # Ensure output directories exist
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load all scores
    data = load_all_scores()
    
    # Merge and deduplicate
    combined = merge_and_deduplicate(data)
    logger.info(f"Combined {len(combined)} unique dishes")
    
    # Calculate final scores and categories
    final = calculate_final_scores(combined)
    
    # Add evidence flags
    final['evidence_flag'] = final.apply(format_evidence_flag, axis=1)
    
    # Fix NaN cuisines - assign sensible defaults
    def fix_cuisine(row):
        cuisine = row.get('cuisine')
        if pd.isna(cuisine) or str(cuisine).lower() in ['nan', 'none', '']:
            dish_lower = str(row['dish_type']).lower()
            # Infer cuisine from dish name
            if 'chicken' in dish_lower and ('grilled' in dish_lower or 'rotisserie' in dish_lower):
                return 'Healthy/Fresh'
            elif 'chicken' in dish_lower:
                return 'Global'
            elif 'pasta' in dish_lower or 'lasagne' in dish_lower or 'pizza' in dish_lower:
                return 'Italian'
            elif 'curry' in dish_lower or 'tikka' in dish_lower or 'biryani' in dish_lower:
                return 'Indian'
            elif 'katsu' in dish_lower or 'teriyaki' in dish_lower or 'ramen' in dish_lower:
                return 'Japanese'
            elif 'pad thai' in dish_lower or 'pho' in dish_lower:
                return 'Thai/Vietnamese'
            elif 'fajita' in dish_lower or 'burrito' in dish_lower or 'taco' in dish_lower:
                return 'Mexican'
            elif 'chow mein' in dish_lower or 'dim sum' in dish_lower or 'fried rice' in dish_lower:
                return 'Chinese'
            else:
                return 'Global'
        return cuisine
    
    final['cuisine'] = final.apply(fix_cuisine, axis=1)
    logger.info("Fixed NaN cuisines with inferred values")
    
    # Reorder columns for output
    priority_cols = [
        'rank', 'dish_type', 'priority_score', 'category', 'evidence_type',
        'track_a_score', 'track_b_score', 'discovery_score',
        'order_volume', 'avg_rating', 'repeat_rate', 'survey_n',
        'latent_demand_mentions', 'cuisine', 'gap_type', 'potential_partners',
        'recommended_action', 'evidence_flag'
    ]
    available_cols = [c for c in priority_cols if c in final.columns]
    other_cols = [c for c in final.columns if c not in available_cols]
    final = final[available_cols + other_cols]
    
    # Save CSV
    csv_path = ANALYSIS_DIR / "priority_100_final.csv"
    final.to_csv(csv_path, index=False)
    logger.info(f"Saved CSV to: {csv_path}")
    
    # Save JSON for analysis
    json_output = []
    for _, row in final.iterrows():
        # Safely get gap_type, converting NaN to None
        gap_type_val = row.get('gap_type')
        if pd.isna(gap_type_val) or str(gap_type_val).lower() in ['nan', 'none', '']:
            gap_type_val = None
        else:
            gap_type_val = str(gap_type_val)
        
        # Safely get cuisine
        cuisine_val = row.get('cuisine')
        if pd.isna(cuisine_val) or str(cuisine_val).lower() in ['nan', 'none', '']:
            cuisine_val = 'Global'  # Default fallback
        else:
            cuisine_val = str(cuisine_val)
        
        # Safely get potential_partners
        partners_val = row.get('potential_partners')
        if pd.isna(partners_val) or str(partners_val).lower() in ['nan', 'none', '']:
            partners_val = None
        else:
            partners_val = str(partners_val)
        
        dish = {
            'rank': int(row['rank']),
            'dish_type': row['dish_type'],
            'priority_score': float(row['priority_score']),
            'category': row['category'],
            'evidence_type': row['evidence_type'],
            'track_a_score': float(row['track_a_score']) if pd.notna(row.get('track_a_score')) else None,
            'track_b_score': float(row['track_b_score']) if pd.notna(row.get('track_b_score')) else None,
            'discovery_score': float(row['discovery_score']) if pd.notna(row.get('discovery_score')) else None,
            'order_volume': int(row.get('order_volume', 0) or 0),
            'avg_rating': float(row['avg_rating']) if pd.notna(row.get('avg_rating')) else None,
            'cuisine': cuisine_val,
            'gap_type': gap_type_val,
            'potential_partners': partners_val,
            'recommended_action': row.get('recommended_action'),
            'evidence_flag': row.get('evidence_flag'),
        }
        json_output.append(dish)
    
    json_path = ANALYSIS_DIR / "priority_100_final.json"
    with open(json_path, 'w') as f:
        json.dump(json_output, f, indent=2)
    logger.info(f"Saved JSON to: {json_path}")
    
    # Save for dashboard
    docs_json_path = DOCS_DIR / "priority_dishes.json"
    with open(docs_json_path, 'w') as f:
        json.dump(json_output, f, indent=2)
    logger.info(f"Saved dashboard JSON to: {docs_json_path}")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("PRIORITY LIST COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Total dishes: {len(final)}")
    logger.info(f"\nBy category:")
    logger.info(final['category'].value_counts().to_string())
    logger.info(f"\nBy evidence type:")
    logger.info(final['evidence_type'].value_counts().to_string())
    logger.info(f"\nTop 20 Priority Dishes:")
    display_cols = ['rank', 'dish_type', 'priority_score', 'category', 'evidence_type', 'evidence_flag']
    display_cols = [c for c in display_cols if c in final.columns]
    logger.info(final[display_cols].head(20).to_string())
    
    # Category breakdown with examples
    logger.info("\n" + "=" * 60)
    logger.info("CATEGORY BREAKDOWN")
    logger.info("=" * 60)
    
    for category in ['Expand', 'Recruit', 'Investigate', 'Discover', 'Fix', 'Monitor']:
        cat_dishes = final[final['category'] == category]
        if len(cat_dishes) > 0:
            logger.info(f"\n{category.upper()} ({len(cat_dishes)} dishes):")
            for _, row in cat_dishes.head(5).iterrows():
                logger.info(f"  - {row['dish_type']} (score: {row['priority_score']:.2f})")
    
    return final


if __name__ == "__main__":
    main()

