"""
Script: 01_score_dishes_v2.py
Phase: 2 - Analysis
Purpose: Score dishes using ACTUAL PERFORMANCE DATA, not LLM estimates

This is the updated dish scoring script that:
1. Uses measured performance metrics (satisfaction, kids happy, portions) from surveys
2. Uses behavioral metrics (repeat rate, volume, ratings) from Snowflake
3. Only falls back to framework estimates when no data available
4. Clearly categorizes dishes as Proven/Promising/Underperforming

Inputs: 
    - DATA/3_ANALYSIS/dish_performance.csv (from 05_extract_performance.py)
    - DATA/3_ANALYSIS/partner_performance.csv
    - DATA/3_ANALYSIS/cuisine_performance.csv
    - DATA/1_SOURCE/snowflake/ALL_DINNEROO_ORDERS.csv
    - DATA/1_SOURCE/snowflake/DINNEROO_MENU_CATALOG.csv
    - config/factor_weights.json

Outputs: 
    - DATA/3_ANALYSIS/priority_dishes.csv
    - DATA/3_ANALYSIS/priority_100_dishes.json
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


def load_performance_data():
    """Load all performance data extracted from surveys and orders."""
    data = {}
    
    # Dish performance
    dish_path = ANALYSIS_DIR / "dish_performance.csv"
    if dish_path.exists():
        data['dish'] = pd.read_csv(dish_path)
        logger.info(f"Loaded dish performance: {len(data['dish'])} dish types")
    else:
        logger.warning("Dish performance not found - run 05_extract_performance.py first")
        data['dish'] = pd.DataFrame()
    
    # Partner performance
    partner_path = ANALYSIS_DIR / "partner_performance.csv"
    if partner_path.exists():
        data['partner'] = pd.read_csv(partner_path)
        logger.info(f"Loaded partner performance: {len(data['partner'])} partners")
    else:
        data['partner'] = pd.DataFrame()
    
    # Cuisine performance
    cuisine_path = ANALYSIS_DIR / "cuisine_performance.csv"
    if cuisine_path.exists():
        data['cuisine'] = pd.read_csv(cuisine_path)
        logger.info(f"Loaded cuisine performance: {len(data['cuisine'])} cuisines")
    else:
        data['cuisine'] = pd.DataFrame()
    
    return data


def load_orders():
    """Load orders data for volume and availability."""
    orders_path = SOURCE_DIR / "snowflake" / "ALL_DINNEROO_ORDERS.csv"
    if orders_path.exists():
        df = pd.read_csv(orders_path)
        logger.info(f"Loaded {len(df)} orders")
        return df
    logger.warning("Orders not found")
    return pd.DataFrame()


def load_menu_catalog():
    """Load menu catalog for availability check."""
    menu_path = SOURCE_DIR / "snowflake" / "DINNEROO_MENU_CATALOG.csv"
    if menu_path.exists():
        df = pd.read_csv(menu_path)
        logger.info(f"Loaded {len(df)} menu items")
        return df
    logger.warning("Menu catalog not found")
    return pd.DataFrame()


def load_config():
    """Load factor weights configuration."""
    config_path = CONFIG_DIR / "factor_weights.json"
    with open(config_path) as f:
        return json.load(f)


def rate_to_score(rate: float, thresholds: list = None) -> int:
    """
    Convert a rate (0-1) to a score (1-5).
    
    Default thresholds:
    - 90%+ = 5
    - 80-89% = 4
    - 70-79% = 3
    - 60-69% = 2
    - <60% = 1
    """
    if pd.isna(rate):
        return None
    
    if thresholds is None:
        thresholds = [0.90, 0.80, 0.70, 0.60]
    
    if rate >= thresholds[0]:
        return 5
    elif rate >= thresholds[1]:
        return 4
    elif rate >= thresholds[2]:
        return 3
    elif rate >= thresholds[3]:
        return 2
    else:
        return 1


def score_dish_from_performance(dish_type: str, performance_data: dict) -> dict:
    """
    Score a dish type using actual performance data.
    Returns scores and evidence type.
    """
    scores = {'dish_type': dish_type}
    measured_count = 0
    
    dish_df = performance_data.get('dish', pd.DataFrame())
    
    if len(dish_df) > 0 and 'dish_type' in dish_df.columns:
        dish_row = dish_df[dish_df['dish_type'] == dish_type]
        
        if len(dish_row) > 0:
            dish_row = dish_row.iloc[0]
            
            # Adult satisfaction → Adult Appeal score
            if 'adult_satisfaction_rate' in dish_row and pd.notna(dish_row['adult_satisfaction_rate']):
                scores['adult_appeal'] = rate_to_score(dish_row['adult_satisfaction_rate'])
                scores['adult_appeal_measured'] = dish_row.get('adult_satisfaction_n', 0)
                measured_count += 1
            
            # Kids happy → Kid-Friendly score
            if 'kids_happy_rate' in dish_row and pd.notna(dish_row['kids_happy_rate']):
                scores['kid_friendly'] = rate_to_score(dish_row['kids_happy_rate'])
                scores['kid_friendly_measured'] = dish_row.get('kids_happy_n', 0)
                measured_count += 1
            
            # Portions adequate → Portion Flexibility score
            if 'portions_adequate_rate' in dish_row and pd.notna(dish_row['portions_adequate_rate']):
                scores['portion_flexibility'] = rate_to_score(dish_row['portions_adequate_rate'])
                scores['portion_flexibility_measured'] = dish_row.get('portions_n', 0)
                measured_count += 1
            
            # Reorder rate → Value indicator
            if 'reorder_rate' in dish_row and pd.notna(dish_row['reorder_rate']):
                scores['reorder_rate'] = dish_row['reorder_rate']
                scores['reorder_rate_measured'] = dish_row.get('reorder_n', 0)
                measured_count += 1
            
            # Sample size
            scores['survey_n'] = dish_row.get('n', 0)
    
    # Determine evidence type
    if measured_count >= 3:
        scores['evidence_type'] = 'Measured'
    elif measured_count >= 1:
        scores['evidence_type'] = 'Partial'
    else:
        scores['evidence_type'] = 'Estimated'
    
    scores['measured_factor_count'] = measured_count
    
    return scores


def estimate_missing_scores(scores: dict, dish_type: str) -> dict:
    """
    Estimate missing scores based on dish type characteristics.
    Only used when no measured data available.
    """
    dish_lower = dish_type.lower()
    
    # Kid-friendly estimation
    if 'kid_friendly' not in scores or scores['kid_friendly'] is None:
        if any(term in dish_lower for term in ['pizza', 'pasta', 'nugget', 'mac', 'cheese']):
            scores['kid_friendly'] = 4
        elif any(term in dish_lower for term in ['curry', 'katsu', 'noodle', 'rice']):
            scores['kid_friendly'] = 3
        elif any(term in dish_lower for term in ['spicy', 'chilli', 'hot']):
            scores['kid_friendly'] = 2
        else:
            scores['kid_friendly'] = 3
        scores['kid_friendly_source'] = 'estimated'
    
    # Adult appeal estimation
    if 'adult_appeal' not in scores or scores['adult_appeal'] is None:
        if any(term in dish_lower for term in ['pho', 'curry', 'katsu', 'sushi']):
            scores['adult_appeal'] = 4
        else:
            scores['adult_appeal'] = 3
        scores['adult_appeal_source'] = 'estimated'
    
    # Portion flexibility estimation
    if 'portion_flexibility' not in scores or scores['portion_flexibility'] is None:
        if any(term in dish_lower for term in ['sharing', 'platter', 'family', 'feast']):
            scores['portion_flexibility'] = 5
        elif any(term in dish_lower for term in ['bowl', 'bundle']):
            scores['portion_flexibility'] = 4
        else:
            scores['portion_flexibility'] = 3
        scores['portion_flexibility_source'] = 'estimated'
    
    # Balanced/guilt-free estimation
    if 'balanced_guilt_free' not in scores:
        if any(term in dish_lower for term in ['salad', 'grilled', 'pho', 'bowl']):
            scores['balanced_guilt_free'] = 4
        elif any(term in dish_lower for term in ['fried', 'pizza', 'burger']):
            scores['balanced_guilt_free'] = 2
        else:
            scores['balanced_guilt_free'] = 3
        scores['balanced_guilt_free_source'] = 'estimated'
    
    # Fussy eater friendly estimation
    if 'fussy_eater_friendly' not in scores:
        if any(term in dish_lower for term in ['pizza', 'pasta', 'nugget', 'plain']):
            scores['fussy_eater_friendly'] = 4
        elif any(term in dish_lower for term in ['curry', 'katsu']):
            scores['fussy_eater_friendly'] = 3
        else:
            scores['fussy_eater_friendly'] = 3
        scores['fussy_eater_friendly_source'] = 'estimated'
    
    # Customisation estimation
    if 'customisation' not in scores:
        if any(term in dish_lower for term in ['bowl', 'fajita', 'wrap', 'build']):
            scores['customisation'] = 4
        else:
            scores['customisation'] = 3
        scores['customisation_source'] = 'estimated'
    
    # Value estimation
    if 'value_at_25' not in scores:
        scores['value_at_25'] = 3
        scores['value_at_25_source'] = 'estimated'
    
    # Shareability estimation
    if 'shareability' not in scores:
        if any(term in dish_lower for term in ['sharing', 'platter', 'family']):
            scores['shareability'] = 5
        elif any(term in dish_lower for term in ['pizza', 'curry']):
            scores['shareability'] = 4
        else:
            scores['shareability'] = 3
        scores['shareability_source'] = 'estimated'
    
    # Vegetarian option estimation
    if 'vegetarian_option' not in scores:
        if any(term in dish_lower for term in ['veg', 'veggie', 'vegetarian', 'tofu', 'halloumi']):
            scores['vegetarian_option'] = 5
        elif any(term in dish_lower for term in ['chicken', 'beef', 'pork', 'lamb', 'fish']):
            scores['vegetarian_option'] = 2
        else:
            scores['vegetarian_option'] = 3
        scores['vegetarian_option_source'] = 'estimated'
    
    return scores


def calculate_composite_score(scores: dict, config: dict) -> float:
    """
    Calculate weighted composite score.
    
    New weighting prioritizes MEASURED performance:
    - If measured: Use measured scores with higher confidence
    - If estimated: Apply penalty to composite
    """
    factors = config.get('factors', {})
    
    # Map our score keys to config factor keys
    factor_mapping = {
        'kid_friendly': 'kid_friendly',
        'balanced_guilt_free': 'balanced_guilt_free',
        'adult_appeal': 'adult_appeal',
        'portion_flexibility': 'portion_flexibility',
        'fussy_eater_friendly': 'fussy_eater_friendly',
        'customisation': 'customisation',
        'value_at_25': 'value_at_25',
        'shareability': 'shareability',
        'vegetarian_option': 'vegetarian_option',
        'on_dinneroo_menu': 'on_dinneroo_menu'
    }
    
    total_score = 0
    total_weight = 0
    
    for score_key, factor_key in factor_mapping.items():
        if factor_key in factors:
            weight = factors[factor_key].get('weight', 0)
            score = scores.get(score_key, 3)  # Default to 3 if missing
            if score is None:
                score = 3
            total_score += score * weight
            total_weight += weight
    
    composite = total_score / total_weight if total_weight > 0 else 0
    
    # Apply confidence adjustment
    # Measured dishes get a small boost, estimated get a small penalty
    evidence_type = scores.get('evidence_type', 'Estimated')
    if evidence_type == 'Measured':
        composite *= 1.05  # 5% boost for measured
    elif evidence_type == 'Estimated':
        composite *= 0.95  # 5% penalty for estimated
    
    return round(composite, 2)


def categorize_dish(scores: dict, on_dinneroo: bool) -> str:
    """
    Categorize dish based on performance and availability.
    
    Categories:
    - Proven Winner: High performance + on Dinneroo
    - Promising Gap: High framework score + not on Dinneroo
    - Underperformer: On Dinneroo but low performance
    - Unvalidated: No performance data
    """
    evidence_type = scores.get('evidence_type', 'Estimated')
    composite = scores.get('composite_score', 0)
    
    # Get performance indicators
    adult_sat = scores.get('adult_appeal', 3)
    kids_happy = scores.get('kid_friendly', 3)
    
    if evidence_type == 'Measured':
        if on_dinneroo:
            if adult_sat >= 4 and kids_happy >= 4:
                return 'Proven Winner'
            elif adult_sat >= 3 and kids_happy >= 3:
                return 'Solid Performer'
            else:
                return 'Underperformer'
        else:
            return 'Validated Gap'
    elif evidence_type == 'Partial':
        if on_dinneroo:
            return 'Partial Data'
        else:
            return 'Promising Gap'
    else:
        if on_dinneroo:
            return 'Needs Validation'
        else:
            return 'Unvalidated Gap'


def get_dish_candidates(performance_data: dict, orders_df: pd.DataFrame) -> list:
    """
    Get list of dish types to score.
    Combines measured dishes with common dish types.
    """
    dishes = set()
    
    # From performance data (measured)
    if 'dish' in performance_data and len(performance_data['dish']) > 0:
        dishes.update(performance_data['dish']['dish_type'].dropna().tolist())
    
    # Add common dish types that should be evaluated
    common_dishes = [
        'Katsu Curry', 'Curry (General)', 'Pho', 'Pad Thai', 'Sushi',
        'Rice Bowl', 'Noodles', 'Pizza', 'Pasta', 'Fajitas', 'Burrito',
        'Tacos', 'Shawarma', 'Fried Rice', 'Stir Fry', 'Wings',
        'Chicken (General)', 'Mac & Cheese', 'Shepherd\'s Pie',
        'Fish & Chips', 'Roast Dinner', 'Grilled Chicken with Sides',
        'Margherita Pizza', 'Mild Curry with Rice', 'Pasta Bolognese',
        'Teriyaki Rice Bowl', 'Burrito Bowl', 'Veggie Fajita',
        'Halloumi Wrap', 'Grain Bowl', 'Buddha Bowl', 'Poke Bowl',
        'Thai Green Curry', 'Butter Chicken', 'Tikka Masala',
        'Biryani', 'Lasagne', 'Carbonara', 'Greek Mezze',
        'Chicken Souvlaki', 'Falafel Wrap', 'Hummus Platter'
    ]
    dishes.update(common_dishes)
    
    return list(dishes)


def check_dinneroo_availability(dish_type: str, menu_df: pd.DataFrame, orders_df: pd.DataFrame) -> tuple:
    """
    Check if a dish type is available on Dinneroo.
    Returns (is_available, item_count, order_volume).
    """
    dish_lower = dish_type.lower()
    
    # Check menu catalog
    menu_count = 0
    if len(menu_df) > 0:
        for col in ['MENU_ITEM_LIST', 'dish_name', 'item_name', 'name']:
            if col in menu_df.columns:
                matches = menu_df[menu_df[col].astype(str).str.lower().str.contains(dish_lower, na=False, regex=False)]
                menu_count = len(matches)
                break
    
    # Check order volume
    order_volume = 0
    if len(orders_df) > 0:
        for col in ['MENU_ITEM_LIST', 'dish_name', 'item_name']:
            if col in orders_df.columns:
                matches = orders_df[orders_df[col].astype(str).str.lower().str.contains(dish_lower, na=False, regex=False)]
                order_volume = len(matches)
                break
    
    is_available = menu_count > 0 or order_volume > 0
    
    return is_available, menu_count, order_volume


def main():
    """Main function to score dishes using performance data."""
    logger.info("=" * 60)
    logger.info("SCORING DISHES (Performance-Based)")
    logger.info("=" * 60)
    
    # Ensure output directory exists
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load data
    performance_data = load_performance_data()
    orders_df = load_orders()
    menu_df = load_menu_catalog()
    config = load_config()
    
    # Get dish candidates
    dishes = get_dish_candidates(performance_data, orders_df)
    logger.info(f"Scoring {len(dishes)} dish types")
    
    # Score each dish
    all_scores = []
    
    for dish_type in dishes:
        # Get performance-based scores
        scores = score_dish_from_performance(dish_type, performance_data)
        
        # Fill in missing scores with estimates
        scores = estimate_missing_scores(scores, dish_type)
        
        # Check availability
        is_available, menu_count, order_volume = check_dinneroo_availability(
            dish_type, menu_df, orders_df
        )
        scores['on_dinneroo'] = is_available
        scores['menu_item_count'] = menu_count
        scores['order_volume'] = order_volume
        
        # Set on_dinneroo_menu score
        if menu_count >= 50:
            scores['on_dinneroo_menu'] = 5
        elif menu_count >= 20:
            scores['on_dinneroo_menu'] = 4
        elif menu_count >= 5:
            scores['on_dinneroo_menu'] = 3
        elif menu_count >= 1:
            scores['on_dinneroo_menu'] = 2
        else:
            scores['on_dinneroo_menu'] = 1
        
        # Calculate composite score
        scores['composite_score'] = calculate_composite_score(scores, config)
        
        # Categorize
        scores['category'] = categorize_dish(scores, is_available)
        
        all_scores.append(scores)
    
    # Create dataframe
    results_df = pd.DataFrame(all_scores)
    
    # Sort by composite score
    results_df = results_df.sort_values('composite_score', ascending=False)
    results_df['rank'] = range(1, len(results_df) + 1)
    
    # Reorder columns
    priority_cols = ['rank', 'dish_type', 'composite_score', 'evidence_type', 'category', 
                     'on_dinneroo', 'order_volume', 'survey_n']
    factor_cols = ['kid_friendly', 'adult_appeal', 'portion_flexibility', 'balanced_guilt_free',
                   'fussy_eater_friendly', 'customisation', 'value_at_25', 'shareability',
                   'vegetarian_option', 'on_dinneroo_menu']
    other_cols = [c for c in results_df.columns if c not in priority_cols + factor_cols]
    
    available_priority = [c for c in priority_cols if c in results_df.columns]
    available_factor = [c for c in factor_cols if c in results_df.columns]
    available_other = [c for c in other_cols if c not in available_priority + available_factor]
    
    results_df = results_df[available_priority + available_factor + available_other]
    
    # Save CSV
    output_path = ANALYSIS_DIR / "priority_dishes.csv"
    results_df.to_csv(output_path, index=False)
    logger.info(f"Saved to: {output_path}")
    
    # Save JSON for dashboard
    json_output = []
    for _, row in results_df.head(100).iterrows():
        dish = {
            'rank': int(row['rank']),
            'dish_type': row['dish_type'],
            'composite_score': float(row['composite_score']),
            'evidence_type': row['evidence_type'],
            'category': row['category'],
            'on_dinneroo': bool(row['on_dinneroo']),
            'order_volume': int(row.get('order_volume', 0)),
            'survey_n': int(row.get('survey_n', 0)) if pd.notna(row.get('survey_n')) else 0,
            'factors': {
                'kid_friendly': int(row.get('kid_friendly', 3)),
                'adult_appeal': int(row.get('adult_appeal', 3)),
                'portion_flexibility': int(row.get('portion_flexibility', 3)),
                'balanced_guilt_free': int(row.get('balanced_guilt_free', 3)),
            }
        }
        json_output.append(dish)
    
    json_path = ANALYSIS_DIR / "priority_100_dishes.json"
    with open(json_path, 'w') as f:
        json.dump(json_output, f, indent=2)
    logger.info(f"Saved JSON to: {json_path}")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("SCORING SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total dishes scored: {len(results_df)}")
    logger.info(f"\nEvidence type distribution:")
    logger.info(results_df['evidence_type'].value_counts().to_string())
    logger.info(f"\nCategory distribution:")
    logger.info(results_df['category'].value_counts().to_string())
    logger.info(f"\nTop 15 dishes:")
    display_cols = ['rank', 'dish_type', 'composite_score', 'evidence_type', 'category', 'survey_n']
    display_cols = [c for c in display_cols if c in results_df.columns]
    logger.info(results_df[display_cols].head(15).to_string())
    
    return results_df


if __name__ == "__main__":
    main()



