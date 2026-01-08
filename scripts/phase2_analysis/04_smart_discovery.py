"""
Script: 04_smart_discovery.py
Phase: 2 - Analysis
Purpose: Smart Discovery Layer - Identify dishes partners COULD make

This script uses LLM-style reasoning (encoded in rules) to discover:
1. Dishes existing partners could realistically offer
2. Dishes that fill family meal factor gaps
3. Dishes that address cuisine supply/quality gaps

Unlike Track A/B scoring, this generates NEW dish ideas that aren't
currently in our data, based on partner capabilities and family needs.

Inputs:
    - DATA/1_SOURCE/snowflake/DINNEROO_MENU_CATALOG.csv
    - DATA/1_SOURCE/snowflake/ALL_DINNEROO_ORDERS.csv
    - DATA/3_ANALYSIS/cuisine_gap_summary.json
    - DATA/3_ANALYSIS/dish_opportunity_scores.csv
    - config/factor_weights.json

Outputs:
    - DATA/3_ANALYSIS/smart_discovery_dishes.csv
    - DATA/3_ANALYSIS/smart_discovery_dishes.json
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
SOURCE_DIR = PROJECT_ROOT / "DATA" / "1_SOURCE"
ANALYSIS_DIR = PROJECT_ROOT / "DATA" / "3_ANALYSIS"
CONFIG_DIR = PROJECT_ROOT / "config"


# Partner knowledge base - what each partner is capable of making
PARTNER_CAPABILITIES = {
    'Dishoom': {
        'cuisine': 'Indian',
        'current_dishes': ['Curry', 'Tikka', 'Naan', 'Rice', 'Samosa'],
        'could_make': [
            {
                'dish': 'Biryani Family Pot',
                'reason': 'Dishoom has the kitchen capability for biryani - premium rice dish fits their brand',
                'factor_fit': {'kid_friendly': 3, 'balanced': 4, 'shareability': 5, 'portion_flexibility': 5}
            },
            {
                'dish': 'Butter Chicken Family Feast',
                'reason': 'Mild, creamy curry that kids love - Dishoom quality would elevate this',
                'factor_fit': {'kid_friendly': 5, 'balanced': 3, 'shareability': 5, 'portion_flexibility': 5}
            },
            {
                'dish': 'Chicken Tikka Wrap Box',
                'reason': 'Wraps are easy to portion for families, tikka is kid-friendly',
                'factor_fit': {'kid_friendly': 4, 'balanced': 4, 'customisation': 4, 'portion_flexibility': 4}
            },
        ]
    },
    'Pho': {
        'cuisine': 'Vietnamese',
        'current_dishes': ['Pho', 'Spring Rolls', 'Rice', 'Noodles'],
        'could_make': [
            {
                'dish': 'Pho Family Sharing Bowl',
                'reason': 'Large format pho for family sharing - already popular, just needs family sizing',
                'factor_fit': {'kid_friendly': 3, 'balanced': 4, 'shareability': 5, 'portion_flexibility': 5}
            },
            {
                'dish': 'Vietnamese Rice Paper Rolls Family Pack',
                'reason': 'Healthy, fun for kids to eat, shareable - fits balanced midweek positioning',
                'factor_fit': {'kid_friendly': 4, 'balanced': 5, 'shareability': 5, 'vegetarian': 4}
            },
            {
                'dish': 'Banh Mi Family Box',
                'reason': 'Sandwiches are kid-friendly, easy to customize for fussy eaters',
                'factor_fit': {'kid_friendly': 4, 'balanced': 3, 'customisation': 5, 'fussy_eater': 4}
            },
        ]
    },
    'Wagamama': {
        'cuisine': 'Japanese/Asian',
        'current_dishes': ['Katsu', 'Ramen', 'Noodles', 'Rice', 'Gyoza'],
        'could_make': [
            {
                'dish': 'Teriyaki Salmon Family Platter',
                'reason': 'Healthy protein option, balanced with rice and veg - fits midweek positioning',
                'factor_fit': {'kid_friendly': 3, 'balanced': 5, 'adult_appeal': 5, 'portion_flexibility': 5}
            },
            {
                'dish': 'Katsu Curry Family Bundle',
                'reason': 'Already top performer - family bundle format would increase value',
                'factor_fit': {'kid_friendly': 5, 'balanced': 3, 'shareability': 4, 'value': 5}
            },
            {
                'dish': 'Kids Ramen & Adult Ramen Combo',
                'reason': 'Mild ramen for kids, spicy for adults - solves fussy eater problem',
                'factor_fit': {'kid_friendly': 4, 'fussy_eater': 5, 'adult_appeal': 5, 'customisation': 5}
            },
        ]
    },
    'Farmer J': {
        'cuisine': 'Healthy/Fresh',
        'current_dishes': ['Grain Bowl', 'Salad', 'Grilled Chicken', 'Wrap'],
        'could_make': [
            {
                'dish': 'Grilled Chicken Family Platter with Sides',
                'reason': 'Perfect fit for balanced midweek - grilled protein, customizable sides',
                'factor_fit': {'kid_friendly': 4, 'balanced': 5, 'customisation': 5, 'portion_flexibility': 5}
            },
            {
                'dish': 'Build Your Own Grain Bowl Family Pack',
                'reason': 'Healthy, customizable - each family member picks toppings',
                'factor_fit': {'kid_friendly': 3, 'balanced': 5, 'customisation': 5, 'vegetarian': 5}
            },
            {
                'dish': 'Rotisserie Chicken Family Feast',
                'reason': 'Classic family meal, balanced with veg sides, high value perception',
                'factor_fit': {'kid_friendly': 5, 'balanced': 4, 'shareability': 5, 'value': 5}
            },
        ]
    },
    'Itsu': {
        'cuisine': 'Japanese/Healthy',
        'current_dishes': ['Sushi', 'Rice', 'Noodles', 'Gyoza'],
        'could_make': [
            {
                'dish': 'Sushi Family Platter',
                'reason': 'Mix of kid-friendly (cucumber, avocado) and adult options',
                'factor_fit': {'kid_friendly': 3, 'balanced': 4, 'shareability': 5, 'adult_appeal': 5}
            },
            {
                'dish': 'Teriyaki Rice Bowl Family Bundle',
                'reason': 'Mild teriyaki is kid-friendly, rice bowls easy to portion',
                'factor_fit': {'kid_friendly': 4, 'balanced': 4, 'portion_flexibility': 5, 'value': 4}
            },
        ]
    },
    'Tortilla': {
        'cuisine': 'Mexican',
        'current_dishes': ['Burrito', 'Tacos', 'Quesadilla', 'Bowl'],
        'could_make': [
            {
                'dish': 'Fajita Family Kit',
                'reason': 'Build-your-own format perfect for families with fussy eaters',
                'factor_fit': {'kid_friendly': 4, 'customisation': 5, 'fussy_eater': 5, 'shareability': 5}
            },
            {
                'dish': 'Quesadilla Family Pack',
                'reason': 'Kid-favorite, easy to share, cheese is universally loved',
                'factor_fit': {'kid_friendly': 5, 'fussy_eater': 5, 'shareability': 4, 'value': 4}
            },
            {
                'dish': 'Veggie Burrito Bowl Family Bundle',
                'reason': 'Addresses vegetarian gap, customizable, balanced',
                'factor_fit': {'kid_friendly': 3, 'balanced': 4, 'vegetarian': 5, 'customisation': 5}
            },
        ]
    },
    'Bill\'s': {
        'cuisine': 'British',
        'current_dishes': ['Burger', 'Breakfast', 'Salad', 'Pasta'],
        'could_make': [
            {
                'dish': 'Roast Dinner Family Platter',
                'reason': 'British classic, high latent demand, balanced meal',
                'factor_fit': {'kid_friendly': 4, 'balanced': 4, 'shareability': 5, 'adult_appeal': 4}
            },
            {
                'dish': 'Fish & Chips Family Bucket',
                'reason': 'British staple, high latent demand, kid-friendly',
                'factor_fit': {'kid_friendly': 5, 'balanced': 2, 'shareability': 4, 'value': 4}
            },
            {
                'dish': 'Chicken Pie with Mash & Veg',
                'reason': 'Comfort food, balanced with veg, easy to share',
                'factor_fit': {'kid_friendly': 4, 'balanced': 4, 'shareability': 4, 'fussy_eater': 4}
            },
        ]
    },
    'Banana Tree': {
        'cuisine': 'Thai/Southeast Asian',
        'current_dishes': ['Curry', 'Noodles', 'Rice', 'Stir Fry'],
        'could_make': [
            {
                'dish': 'Pad Thai Family Bundle',
                'reason': 'Mild noodle dish, popular with kids, easy to share',
                'factor_fit': {'kid_friendly': 4, 'balanced': 3, 'shareability': 4, 'adult_appeal': 4}
            },
            {
                'dish': 'Thai Green Curry Family Pot (Mild)',
                'reason': 'Mild version for families, coconut base is kid-friendly',
                'factor_fit': {'kid_friendly': 3, 'balanced': 4, 'shareability': 5, 'customisation': 3}
            },
        ]
    },
}

# Cuisine gaps to address
CUISINE_GAPS = {
    'Chinese': {
        'gap_type': 'Supply Gap',
        'suggested_dishes': [
            {
                'dish': 'Sweet & Sour Chicken Family Meal',
                'reason': 'Classic kid-friendly Chinese, high latent demand',
                'factor_fit': {'kid_friendly': 5, 'balanced': 2, 'shareability': 4, 'fussy_eater': 4}
            },
            {
                'dish': 'Dim Sum Family Selection',
                'reason': 'Shareable, variety for different tastes, fun for families',
                'factor_fit': {'kid_friendly': 3, 'shareability': 5, 'customisation': 4, 'adult_appeal': 5}
            },
            {
                'dish': 'Chicken Chow Mein Family Bundle',
                'reason': 'Familiar noodles, mild, kid-friendly',
                'factor_fit': {'kid_friendly': 4, 'balanced': 3, 'fussy_eater': 4, 'value': 4}
            },
        ],
        'recruitment_needed': True
    },
    'Greek/Mediterranean': {
        'gap_type': 'Supply Gap',
        'suggested_dishes': [
            {
                'dish': 'Souvlaki Family Platter',
                'reason': 'Grilled protein + pitta + salad = balanced midweek meal',
                'factor_fit': {'kid_friendly': 4, 'balanced': 5, 'shareability': 5, 'adult_appeal': 4}
            },
            {
                'dish': 'Greek Mezze Family Feast',
                'reason': 'Shareable, variety, includes veggie options',
                'factor_fit': {'kid_friendly': 3, 'shareability': 5, 'vegetarian': 5, 'customisation': 4}
            },
            {
                'dish': 'Halloumi Wrap Family Box',
                'reason': 'Vegetarian protein, kid-friendly, easy to portion',
                'factor_fit': {'kid_friendly': 4, 'balanced': 4, 'vegetarian': 5, 'portion_flexibility': 5}
            },
        ],
        'recruitment_needed': True
    },
    'Middle Eastern': {
        'gap_type': 'Supply Gap',
        'suggested_dishes': [
            {
                'dish': 'Shawarma Family Platter',
                'reason': 'Grilled meat, fresh salads, balanced',
                'factor_fit': {'kid_friendly': 3, 'balanced': 4, 'shareability': 5, 'adult_appeal': 5}
            },
            {
                'dish': 'Falafel & Hummus Family Box',
                'reason': 'Vegetarian option, healthy perception, shareable',
                'factor_fit': {'kid_friendly': 3, 'balanced': 4, 'vegetarian': 5, 'shareability': 4}
            },
        ],
        'recruitment_needed': True
    },
}

# Family factor gaps to address
FACTOR_GAPS = {
    'vegetarian_main': {
        'description': 'Families with 1 vegetarian struggle to find options where everyone is happy',
        'suggested_dishes': [
            {
                'dish': 'Halloumi Wrap Family Bundle',
                'reason': 'Vegetarian protein that kids like, easy to portion',
                'factor_fit': {'kid_friendly': 4, 'vegetarian': 5, 'portion_flexibility': 5}
            },
            {
                'dish': 'Veggie Fajita Family Kit',
                'reason': 'Build-your-own with veggie protein options',
                'factor_fit': {'vegetarian': 5, 'customisation': 5, 'fussy_eater': 4}
            },
            {
                'dish': 'Paneer Tikka Family Feast',
                'reason': 'Indian vegetarian protein, shareable',
                'factor_fit': {'vegetarian': 5, 'shareability': 5, 'adult_appeal': 4}
            },
        ]
    },
    'fussy_eater_options': {
        'description': 'Families with very fussy eaters need mild, plain options',
        'suggested_dishes': [
            {
                'dish': 'Plain Pasta with Sides Family Bundle',
                'reason': 'Ultra-plain option for fussiest eaters, sides for everyone else',
                'factor_fit': {'fussy_eater': 5, 'kid_friendly': 5, 'customisation': 4}
            },
            {
                'dish': 'Chicken & Rice Plain Family Meal',
                'reason': 'Simple, mild, universally acceptable',
                'factor_fit': {'fussy_eater': 5, 'kid_friendly': 5, 'balanced': 3}
            },
        ]
    },
    'balanced_midweek': {
        'description': 'Parents want balanced meals they feel good about serving on a Tuesday',
        'suggested_dishes': [
            {
                'dish': 'Grilled Chicken with Customizable Sides',
                'reason': 'Protein + veg + carbs, customizable for each family member',
                'factor_fit': {'balanced': 5, 'customisation': 5, 'kid_friendly': 4}
            },
            {
                'dish': 'Salmon Teriyaki Family Platter',
                'reason': 'Healthy protein, balanced with rice and veg',
                'factor_fit': {'balanced': 5, 'adult_appeal': 5, 'portion_flexibility': 5}
            },
        ]
    },
}


def load_existing_data():
    """Load existing analysis data."""
    data = {}
    
    # Opportunity scores (to avoid duplicates)
    opp_path = ANALYSIS_DIR / "dish_opportunity_scores.csv"
    if opp_path.exists():
        data['opportunity'] = pd.read_csv(opp_path)
        logger.info(f"Loaded {len(data['opportunity'])} opportunity-scored dishes")
    
    # Cuisine gaps
    gap_path = ANALYSIS_DIR / "cuisine_gap_summary.json"
    if gap_path.exists():
        with open(gap_path) as f:
            data['cuisine_gaps'] = json.load(f)
    
    # Orders (to check what's currently available)
    orders_path = SOURCE_DIR / "snowflake" / "ALL_DINNEROO_ORDERS.csv"
    if orders_path.exists():
        data['orders'] = pd.read_csv(orders_path)
    
    return data


def generate_partner_discoveries(existing_dishes: set) -> list:
    """Generate discovery dishes from partner capabilities."""
    discoveries = []
    
    for partner, info in PARTNER_CAPABILITIES.items():
        for dish_idea in info['could_make']:
            dish_name = dish_idea['dish']
            
            # Skip if already in our scoring
            if dish_name.lower() in [d.lower() for d in existing_dishes]:
                continue
            
            discovery = {
                'dish_type': dish_name,
                'source': 'Partner Capability',
                'partner': partner,
                'cuisine': info['cuisine'],
                'reason': dish_idea['reason'],
                'factor_fit': dish_idea['factor_fit'],
                'recruitment_needed': False,
                'evidence_type': 'Discovery',
            }
            
            # Calculate opportunity score based on factor fit
            factors = dish_idea['factor_fit']
            factor_avg = sum(factors.values()) / len(factors) if factors else 3
            discovery['framework_score'] = round(factor_avg, 2)
            
            discoveries.append(discovery)
    
    return discoveries


def generate_gap_discoveries(existing_dishes: set) -> list:
    """Generate discovery dishes from cuisine gaps."""
    discoveries = []
    
    for cuisine, info in CUISINE_GAPS.items():
        for dish_idea in info['suggested_dishes']:
            dish_name = dish_idea['dish']
            
            # Skip if already in our scoring
            if dish_name.lower() in [d.lower() for d in existing_dishes]:
                continue
            
            discovery = {
                'dish_type': dish_name,
                'source': 'Cuisine Gap',
                'partner': 'New recruitment needed',
                'cuisine': cuisine,
                'reason': dish_idea['reason'],
                'factor_fit': dish_idea['factor_fit'],
                'recruitment_needed': info['recruitment_needed'],
                'gap_type': info['gap_type'],
                'evidence_type': 'Discovery',
            }
            
            # Calculate opportunity score
            factors = dish_idea['factor_fit']
            factor_avg = sum(factors.values()) / len(factors) if factors else 3
            # Boost for being in a gap cuisine
            gap_boost = 0.5 if info['gap_type'] == 'Supply Gap' else 0.3
            discovery['framework_score'] = round(factor_avg + gap_boost, 2)
            
            discoveries.append(discovery)
    
    return discoveries


def generate_factor_gap_discoveries(existing_dishes: set) -> list:
    """Generate discovery dishes from family factor gaps."""
    discoveries = []
    
    for gap_type, info in FACTOR_GAPS.items():
        for dish_idea in info['suggested_dishes']:
            dish_name = dish_idea['dish']
            
            # Skip if already in our scoring
            if dish_name.lower() in [d.lower() for d in existing_dishes]:
                continue
            
            discovery = {
                'dish_type': dish_name,
                'source': 'Factor Gap',
                'partner': 'TBD - based on cuisine',
                'cuisine': 'Various',
                'reason': dish_idea['reason'],
                'factor_fit': dish_idea['factor_fit'],
                'factor_gap_addressed': gap_type,
                'gap_description': info['description'],
                'recruitment_needed': False,
                'evidence_type': 'Discovery',
            }
            
            # Calculate opportunity score
            factors = dish_idea['factor_fit']
            factor_avg = sum(factors.values()) / len(factors) if factors else 3
            discovery['framework_score'] = round(factor_avg, 2)
            
            discoveries.append(discovery)
    
    return discoveries


def score_discoveries(discoveries: list) -> pd.DataFrame:
    """Score and rank discovery dishes."""
    for d in discoveries:
        # Base score from framework
        base_score = d.get('framework_score', 3.0)
        
        # Adjustments
        adjustments = 0
        
        # Boost for addressing supply gaps
        if d.get('gap_type') == 'Supply Gap':
            adjustments += 0.3
        
        # Boost for partner capability (easier to implement)
        if d.get('source') == 'Partner Capability':
            adjustments += 0.2
        
        # Boost for addressing factor gaps
        if d.get('source') == 'Factor Gap':
            adjustments += 0.2
        
        # Penalty for needing recruitment
        if d.get('recruitment_needed'):
            adjustments -= 0.2
        
        d['discovery_score'] = round(base_score + adjustments, 2)
    
    # Convert to DataFrame
    df = pd.DataFrame(discoveries)
    
    # Sort by discovery score
    df = df.sort_values('discovery_score', ascending=False)
    df['discovery_rank'] = range(1, len(df) + 1)
    
    return df


def main():
    """Main function to generate smart discovery dishes."""
    logger.info("=" * 60)
    logger.info("SMART DISCOVERY: Dishes Partners Could Make")
    logger.info("=" * 60)
    
    # Load existing data
    data = load_existing_data()
    
    # Get existing dishes to avoid duplicates
    existing_dishes = set()
    if 'opportunity' in data:
        existing_dishes.update(data['opportunity']['dish_type'].tolist())
    
    logger.info(f"Found {len(existing_dishes)} existing dishes to avoid duplicates")
    
    # Generate discoveries from each source
    partner_discoveries = generate_partner_discoveries(existing_dishes)
    logger.info(f"Generated {len(partner_discoveries)} partner capability discoveries")
    
    gap_discoveries = generate_gap_discoveries(existing_dishes)
    logger.info(f"Generated {len(gap_discoveries)} cuisine gap discoveries")
    
    factor_discoveries = generate_factor_gap_discoveries(existing_dishes)
    logger.info(f"Generated {len(factor_discoveries)} factor gap discoveries")
    
    # Combine all discoveries
    all_discoveries = partner_discoveries + gap_discoveries + factor_discoveries
    
    # Remove duplicates (same dish from different sources)
    seen_dishes = set()
    unique_discoveries = []
    for d in all_discoveries:
        dish_lower = d['dish_type'].lower()
        if dish_lower not in seen_dishes:
            seen_dishes.add(dish_lower)
            unique_discoveries.append(d)
    
    logger.info(f"Total unique discoveries: {len(unique_discoveries)}")
    
    # Score and rank
    discoveries_df = score_discoveries(unique_discoveries)
    
    # Save CSV
    csv_path = ANALYSIS_DIR / "smart_discovery_dishes.csv"
    discoveries_df.to_csv(csv_path, index=False)
    logger.info(f"Saved to: {csv_path}")
    
    # Save JSON
    json_output = []
    for _, row in discoveries_df.iterrows():
        dish = {
            'rank': int(row['discovery_rank']),
            'dish_type': row['dish_type'],
            'discovery_score': float(row['discovery_score']),
            'source': row['source'],
            'partner': row['partner'],
            'cuisine': row['cuisine'],
            'reason': row['reason'],
            'recruitment_needed': bool(row['recruitment_needed']),
            'evidence_type': 'Discovery',
        }
        json_output.append(dish)
    
    json_path = ANALYSIS_DIR / "smart_discovery_dishes.json"
    with open(json_path, 'w') as f:
        json.dump(json_output, f, indent=2)
    logger.info(f"Saved JSON to: {json_path}")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("DISCOVERY SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total discoveries: {len(discoveries_df)}")
    logger.info(f"\nBy source:")
    logger.info(discoveries_df['source'].value_counts().to_string())
    logger.info(f"\nTop 15 Discovery Dishes:")
    display_cols = ['discovery_rank', 'dish_type', 'discovery_score', 'source', 'partner', 'reason']
    available_cols = [c for c in display_cols if c in discoveries_df.columns]
    logger.info(discoveries_df[available_cols].head(15).to_string())
    
    return discoveries_df


if __name__ == "__main__":
    main()




