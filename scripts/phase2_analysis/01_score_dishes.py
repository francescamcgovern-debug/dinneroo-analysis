"""
Script: 01_score_dishes.py
Phase: 2 - Analysis
Purpose: Score dishes on 10 family meal factors
Inputs: 
    - DATA/3_ANALYSIS/survey_backed_scores.csv
    - DATA/1_SOURCE/snowflake/DINNEROO_MENU_CATALOG.csv
    - DATA/1_SOURCE/snowflake/DINNEROO_ORDERS.csv
    - config/factor_weights.json
Outputs: DATA/3_ANALYSIS/priority_dishes.csv

This script implements the Family Meal Factors Framework to score dishes
on 10 factors and generate a prioritized list.
"""

import logging
import json
import pandas as pd
import numpy as np
import re
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


def load_config():
    """Load factor weights configuration."""
    config_path = CONFIG_DIR / "factor_weights.json"
    with open(config_path) as f:
        return json.load(f)


def load_survey_scores():
    """Load pre-extracted survey scores."""
    scores_path = ANALYSIS_DIR / "survey_backed_scores.csv"
    if scores_path.exists():
        return pd.read_csv(scores_path)
    logger.warning("Survey scores not found - run 02_extract_survey_scores.py first")
    return pd.DataFrame()


def load_menu_catalog():
    """Load Dinneroo menu catalog."""
    menu_path = SOURCE_DIR / "snowflake" / "DINNEROO_MENU_CATALOG.csv"
    if menu_path.exists():
        return pd.read_csv(menu_path)
    logger.warning("Menu catalog not found")
    return pd.DataFrame()


def load_orders():
    """Load orders data for volume metrics."""
    orders_path = SOURCE_DIR / "snowflake" / "DINNEROO_ORDERS.csv"
    if orders_path.exists():
        return pd.read_csv(orders_path)
    logger.warning("Orders data not found")
    return pd.DataFrame()


def get_menu_availability(dish_name: str, menu_df: pd.DataFrame) -> int:
    """
    Check menu availability and return score 1-5.
    5 = 50+ menu items
    4 = 20-49 menu items
    3 = 5-19 menu items
    2 = 1-4 menu items
    1 = Not on menu
    """
    if menu_df.empty:
        return 3  # Default if no menu data
    
    dish_col = None
    for col in ['dish_name', 'item_name', 'menu_item', 'name']:
        if col in menu_df.columns:
            dish_col = col
            break
    
    if not dish_col:
        return 3
    
    # Escape special regex characters in dish name
    escaped_dish = re.escape(dish_name.lower())
    matches = menu_df[menu_df[dish_col].str.lower().str.contains(escaped_dish, na=False, regex=True)]
    count = len(matches)
    
    if count >= 50:
        return 5
    elif count >= 20:
        return 4
    elif count >= 5:
        return 3
    elif count >= 1:
        return 2
    else:
        return 1


def estimate_factor_score(dish_name: str, factor: str) -> int:
    """
    Estimate factor score based on dish characteristics when survey data unavailable.
    This uses heuristics based on dish type knowledge.
    """
    dish_lower = dish_name.lower()
    
    # Kid-friendly estimation
    if factor == 'kid_friendly':
        kid_friendly_terms = ['pizza', 'pasta', 'chicken nugget', 'fish finger', 'burger', 
                             'mac and cheese', 'sausage', 'chips', 'rice', 'noodle']
        not_kid_friendly = ['spicy', 'curry', 'chilli', 'wasabi', 'kimchi']
        
        if any(term in dish_lower for term in kid_friendly_terms):
            return 4
        elif any(term in dish_lower for term in not_kid_friendly):
            return 2
        return 3
    
    # Balanced/guilt-free estimation
    if factor == 'balanced_guilt_free':
        healthy_terms = ['grilled', 'salad', 'steamed', 'baked', 'vegetable', 'lean', 'protein']
        unhealthy_terms = ['fried', 'deep fried', 'crispy', 'battered', 'cream', 'cheese']
        
        if any(term in dish_lower for term in healthy_terms):
            return 4
        elif any(term in dish_lower for term in unhealthy_terms):
            return 2
        return 3
    
    # Adult appeal estimation
    if factor == 'adult_appeal':
        premium_terms = ['wagyu', 'truffle', 'lobster', 'premium', 'signature', 'chef']
        basic_terms = ['nugget', 'finger', 'kids', 'mini']
        
        if any(term in dish_lower for term in premium_terms):
            return 5
        elif any(term in dish_lower for term in basic_terms):
            return 2
        return 3
    
    # Fussy eater friendly estimation
    if factor == 'fussy_eater_friendly':
        safe_terms = ['plain', 'mild', 'cheese', 'chicken', 'pasta', 'rice']
        risky_terms = ['spicy', 'exotic', 'unusual', 'fusion']
        
        if any(term in dish_lower for term in safe_terms):
            return 4
        elif any(term in dish_lower for term in risky_terms):
            return 2
        return 3
    
    # Customisation estimation
    if factor == 'customisation':
        customisable_terms = ['build your own', 'choose', 'pick', 'sides', 'bowl']
        fixed_terms = ['set meal', 'combo', 'fixed']
        
        if any(term in dish_lower for term in customisable_terms):
            return 5
        elif any(term in dish_lower for term in fixed_terms):
            return 2
        return 3
    
    # Value estimation
    if factor == 'value_at_25':
        # Most dishes default to middle
        return 3
    
    # Shareability estimation
    if factor == 'shareability':
        shareable_terms = ['platter', 'sharing', 'family', 'large', 'feast']
        individual_terms = ['single', 'personal', 'individual']
        
        if any(term in dish_lower for term in shareable_terms):
            return 5
        elif any(term in dish_lower for term in individual_terms):
            return 2
        return 3
    
    # Vegetarian option estimation
    if factor == 'vegetarian_option':
        veg_terms = ['vegetarian', 'vegan', 'veggie', 'plant-based']
        meat_only = ['steak', 'lamb', 'pork', 'beef', 'chicken', 'fish']
        
        if any(term in dish_lower for term in veg_terms):
            return 5
        elif any(term in dish_lower for term in meat_only):
            return 2
        return 3
    
    # Portion flexibility estimation
    if factor == 'portion_flexibility':
        family_terms = ['family', 'sharing', 'for 4', 'large']
        single_terms = ['single', 'individual', 'personal']
        
        if any(term in dish_lower for term in family_terms):
            return 5
        elif any(term in dish_lower for term in single_terms):
            return 2
        return 3
    
    return 3  # Default middle score


def get_dish_candidates(orders_df: pd.DataFrame, menu_df: pd.DataFrame) -> list:
    """
    Generate list of candidate dishes from orders and menu.
    Also includes smart discovery dishes based on family meal factors.
    """
    dishes = set()
    
    # From orders
    if not orders_df.empty:
        dish_col = None
        for col in ['dish_name', 'item_name', 'menu_item']:
            if col in orders_df.columns:
                dish_col = col
                break
        if dish_col:
            dishes.update(orders_df[dish_col].dropna().unique())
    
    # From menu
    if not menu_df.empty:
        dish_col = None
        for col in ['dish_name', 'item_name', 'menu_item', 'name']:
            if col in menu_df.columns:
                dish_col = col
                break
        if dish_col:
            dishes.update(menu_df[dish_col].dropna().unique())
    
    # Smart discovery: Add dish types that score well on family meal factors
    # These are dishes that may not be in current data but fit the framework
    smart_discovery_dishes = [
        # Grilled chicken (Nando's-style) - high on balanced, customisable
        "Grilled Chicken with Sides",
        "Peri-Peri Chicken Family Platter",
        "Flame-Grilled Chicken Quarter",
        # Mediterranean - high on balanced, adult appeal
        "Greek Mezze Sharing Platter",
        "Grilled Halloumi Wrap",
        "Mediterranean Family Feast",
        # Fresh pasta - high on adult appeal, shareability
        "Fresh Pasta Family Bowl",
        "Carbonara for Sharing",
        # Healthy bowls - high on balanced, customisation
        "Build Your Own Poke Bowl",
        "Protein Bowl with Grains",
        # British comfort - high on kid-friendly, value
        "Fish and Chips Family Meal",
        "Shepherd's Pie for 4",
        "Sunday Roast Family Platter"
    ]
    
    dishes.update(smart_discovery_dishes)
    
    return list(dishes)


def score_dish(dish_name: str, survey_scores: pd.DataFrame, menu_df: pd.DataFrame, config: dict) -> dict:
    """
    Score a single dish on all 10 factors.
    Uses survey data where available, estimates otherwise.
    """
    factors = config['factors']
    scores = {'dish_name': dish_name}
    measured_factors = 0
    
    # Get survey scores if available
    survey_row = None
    if not survey_scores.empty and 'dish_name' in survey_scores.columns:
        matches = survey_scores[survey_scores['dish_name'].str.lower() == dish_name.lower()]
        if len(matches) > 0:
            survey_row = matches.iloc[0]
    
    # Score each factor
    for factor_name, factor_info in factors.items():
        survey_col = f"{factor_name}_score"
        n_col = f"{factor_name.replace('_score', '')}_n"
        
        # Check for survey data
        if survey_row is not None and survey_col in survey_row.index:
            score = survey_row.get(survey_col)
            n = survey_row.get(n_col, 0) if n_col in survey_row.index else 0
            if pd.notna(score) and n >= 5:
                scores[factor_name] = int(score)
                scores[f"{factor_name}_source"] = "measured"
                measured_factors += 1
                continue
        
        # Special handling for menu availability
        if factor_name == 'on_dinneroo_menu':
            scores[factor_name] = get_menu_availability(dish_name, menu_df)
            scores[f"{factor_name}_source"] = "catalog"
            continue
        
        # Estimate score
        scores[factor_name] = estimate_factor_score(dish_name, factor_name)
        scores[f"{factor_name}_source"] = "estimated"
    
    # Determine evidence type
    if measured_factors >= 3:
        scores['evidence_type'] = "Measured"
    elif measured_factors >= 1:
        scores['evidence_type'] = "Blended"
    else:
        scores['evidence_type'] = "Estimated"
    
    scores['measured_factor_count'] = measured_factors
    
    return scores


def calculate_composite_score(scores: dict, config: dict) -> float:
    """Calculate weighted composite score."""
    factors = config['factors']
    total_score = 0
    total_weight = 0
    
    for factor_name, factor_info in factors.items():
        weight = factor_info['weight']
        score = scores.get(factor_name, 3)  # Default to 3 if missing
        total_score += score * weight
        total_weight += weight
    
    return round(total_score / total_weight if total_weight > 0 else 0, 2)


def determine_cuisine(dish_name: str) -> str:
    """Determine cuisine type from dish name."""
    dish_lower = dish_name.lower()
    
    cuisine_keywords = {
        'Italian': ['pizza', 'pasta', 'risotto', 'lasagna', 'carbonara', 'bolognese'],
        'Chinese': ['noodle', 'rice', 'dim sum', 'sweet and sour', 'kung pao', 'chow mein'],
        'Indian': ['curry', 'tikka', 'masala', 'biryani', 'korma', 'naan', 'tandoori'],
        'Mexican': ['taco', 'burrito', 'quesadilla', 'nachos', 'enchilada'],
        'Japanese': ['sushi', 'ramen', 'teriyaki', 'tempura', 'katsu'],
        'Thai': ['pad thai', 'green curry', 'red curry', 'tom yum'],
        'Mediterranean': ['greek', 'halloumi', 'mezze', 'falafel', 'hummus'],
        'American': ['burger', 'wings', 'bbq', 'ribs'],
        'British': ['fish and chips', 'pie', 'roast', 'shepherd'],
        'Grilled Chicken': ['peri-peri', 'grilled chicken', 'flame-grilled'],
        'Healthy': ['poke', 'bowl', 'salad', 'protein']
    }
    
    for cuisine, keywords in cuisine_keywords.items():
        if any(kw in dish_lower for kw in keywords):
            return cuisine
    
    return 'Other'


def generate_positioning_guidance(scores: dict) -> str:
    """Generate positioning guidance based on scores."""
    guidance = []
    
    # Check balanced/guilt-free score
    if scores.get('balanced_guilt_free', 3) >= 4:
        guidance.append("Position as balanced midweek meal")
    elif scores.get('balanced_guilt_free', 3) <= 2:
        guidance.append("Consider healthier preparation (grilled vs fried)")
    
    # Check kid-friendly score
    if scores.get('kid_friendly', 3) <= 2:
        guidance.append("Offer mild option for kids")
    
    # Check customisation
    if scores.get('customisation', 3) >= 4:
        guidance.append("Highlight build-your-own options")
    
    # Check portion flexibility
    if scores.get('portion_flexibility', 3) <= 2:
        guidance.append("Create family-sized portion option")
    
    return "; ".join(guidance) if guidance else "Standard presentation"


def main():
    """Main function to score all dishes."""
    logger.info("=" * 60)
    logger.info("PHASE 2: Scoring Dishes")
    logger.info("=" * 60)
    
    # Ensure output directory exists
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load inputs
    config = load_config()
    survey_scores = load_survey_scores()
    menu_df = load_menu_catalog()
    orders_df = load_orders()
    
    logger.info(f"Loaded config with {len(config['factors'])} factors")
    logger.info(f"Survey scores: {len(survey_scores)} dishes")
    logger.info(f"Menu catalog: {len(menu_df)} items")
    logger.info(f"Orders: {len(orders_df)} records")
    
    # Get candidate dishes
    candidates = get_dish_candidates(orders_df, menu_df)
    logger.info(f"Total candidate dishes: {len(candidates)}")
    
    # Score each dish
    all_scores = []
    for dish in candidates:
        scores = score_dish(dish, survey_scores, menu_df, config)
        scores['composite_score'] = calculate_composite_score(scores, config)
        scores['cuisine'] = determine_cuisine(dish)
        scores['positioning_guidance'] = generate_positioning_guidance(scores)
        all_scores.append(scores)
    
    # Create dataframe and sort
    results_df = pd.DataFrame(all_scores)
    results_df = results_df.sort_values('composite_score', ascending=False)
    
    # Add rank
    results_df['rank'] = range(1, len(results_df) + 1)
    
    # Reorder columns
    priority_cols = ['rank', 'dish_name', 'cuisine', 'composite_score', 'evidence_type']
    factor_cols = [c for c in results_df.columns if c in config['factors'].keys()]
    other_cols = [c for c in results_df.columns if c not in priority_cols + factor_cols]
    results_df = results_df[priority_cols + factor_cols + other_cols]
    
    # Save
    output_path = ANALYSIS_DIR / "priority_dishes.csv"
    results_df.to_csv(output_path, index=False)
    
    logger.info("\n" + "=" * 60)
    logger.info("DISH SCORING SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total dishes scored: {len(results_df)}")
    logger.info(f"\nEvidence type distribution:")
    logger.info(results_df['evidence_type'].value_counts().to_string())
    logger.info(f"\nCuisine distribution:")
    logger.info(results_df['cuisine'].value_counts().head(10).to_string())
    logger.info(f"\nTop 10 dishes:")
    logger.info(results_df[['rank', 'dish_name', 'composite_score', 'evidence_type']].head(10).to_string())
    logger.info(f"\nSaved to: {output_path}")
    
    return results_df


if __name__ == "__main__":
    main()

