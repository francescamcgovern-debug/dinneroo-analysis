"""
Script: 01_score_dishes_v3.py
Phase: 2 - Analysis
Purpose: Two-Track Dish Scoring System

This script implements the Two-Track Scoring System:
- Track A: PERFORMANCE SCORE - How well is this dish doing? (only for dishes with 50+ orders)
- Track B: OPPORTUNITY SCORE - How much do families want this? (for ALL dishes)

This addresses survivorship bias by NOT penalizing unavailable dishes for having no orders.

Inputs: 
    - DATA/3_ANALYSIS/dish_performance.csv
    - DATA/3_ANALYSIS/cuisine_performance.csv
    - DATA/1_SOURCE/snowflake/ALL_DINNEROO_ORDERS.csv
    - DATA/1_SOURCE/snowflake/DINNEROO_RATINGS.csv
    - DATA/1_SOURCE/snowflake/DINNEROO_MENU_CATALOG.csv
    - DATA/1_SOURCE/surveys/POST_ORDER_SURVEY-CONSOLIDATED.csv
    - DATA/1_SOURCE/surveys/DROPOFF_SURVEY-CONSOLIDATED.csv
    - config/factor_weights.json

Outputs: 
    - DATA/3_ANALYSIS/dish_performance_scores.csv (Track A)
    - DATA/3_ANALYSIS/dish_opportunity_scores.csv (Track B)
    - DATA/3_ANALYSIS/priority_100_dishes_v2.csv (Combined)
    - DATA/3_ANALYSIS/priority_100_dishes_v2.json
"""

import logging
import json
import pandas as pd
import numpy as np
import re
from pathlib import Path
from datetime import datetime
from collections import Counter

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

# Constants
MIN_ORDERS_FOR_TRACK_A = 50
RATING_THRESHOLD = 4.5  # Updated from 4.0 to align with Deliveroo standard
REPEAT_RATE_THRESHOLD = 0.35
SATISFACTION_THRESHOLD = 0.80
KIDS_HAPPY_THRESHOLD = 0.70


def load_all_data():
    """Load all data sources needed for both tracks."""
    data = {}
    
    # Orders
    orders_path = SOURCE_DIR / "snowflake" / "ALL_DINNEROO_ORDERS.csv"
    if orders_path.exists():
        data['orders'] = pd.read_csv(orders_path)
        logger.info(f"Loaded {len(data['orders'])} orders")
    else:
        data['orders'] = pd.DataFrame()
        logger.warning("Orders not found")
    
    # Ratings
    ratings_path = SOURCE_DIR / "snowflake" / "DINNEROO_RATINGS.csv"
    if ratings_path.exists():
        data['ratings'] = pd.read_csv(ratings_path)
        logger.info(f"Loaded {len(data['ratings'])} ratings")
    else:
        data['ratings'] = pd.DataFrame()
        logger.warning("Ratings not found")
    
    # Menu catalog
    menu_path = SOURCE_DIR / "snowflake" / "DINNEROO_MENU_CATALOG.csv"
    if menu_path.exists():
        data['menu'] = pd.read_csv(menu_path)
        logger.info(f"Loaded {len(data['menu'])} menu items")
    else:
        data['menu'] = pd.DataFrame()
        logger.warning("Menu catalog not found")
    
    # Post-order survey
    post_order_path = SOURCE_DIR / "surveys" / "POST_ORDER_SURVEY-CONSOLIDATED.csv"
    if post_order_path.exists():
        data['post_order'] = pd.read_csv(post_order_path)
        logger.info(f"Loaded {len(data['post_order'])} post-order survey responses")
    else:
        data['post_order'] = pd.DataFrame()
        logger.warning("Post-order survey not found")
    
    # Dropoff survey (for latent demand)
    dropoff_path = SOURCE_DIR / "surveys" / "DROPOFF_SURVEY-CONSOLIDATED.csv"
    if dropoff_path.exists():
        data['dropoff'] = pd.read_csv(dropoff_path)
        logger.info(f"Loaded {len(data['dropoff'])} dropoff survey responses")
    else:
        data['dropoff'] = pd.DataFrame()
        logger.warning("Dropoff survey not found")
    
    # Dish performance (from previous extraction)
    dish_perf_path = ANALYSIS_DIR / "dish_performance.csv"
    if dish_perf_path.exists():
        data['dish_performance'] = pd.read_csv(dish_perf_path)
        logger.info(f"Loaded {len(data['dish_performance'])} dish performance records")
    else:
        data['dish_performance'] = pd.DataFrame()
        logger.warning("Dish performance not found - run 05_extract_performance.py first")
    
    # Cuisine gap analysis
    cuisine_gap_path = ANALYSIS_DIR / "cuisine_gap_summary.json"
    if cuisine_gap_path.exists():
        with open(cuisine_gap_path) as f:
            data['cuisine_gaps'] = json.load(f)
        logger.info("Loaded cuisine gap analysis")
    else:
        data['cuisine_gaps'] = {}
        logger.warning("Cuisine gap analysis not found")
    
    return data


def load_config():
    """Load factor weights configuration."""
    config_path = CONFIG_DIR / "factor_weights.json"
    with open(config_path) as f:
        return json.load(f)


def normalize_dish_type(text: str, check_primary: bool = True) -> str:
    """
    Normalize dish description to a standard dish type.
    
    Args:
        text: Menu item text to analyze
        check_primary: If True, only return dish type if it appears to be the PRIMARY item
                      (not a side dish). Uses position in text as a heuristic.
    """
    if pd.isna(text):
        return None
    
    text = str(text).lower().strip()
    
    # Side dishes that should NOT be counted as primary dish types
    # These are typically add-ons, not the main meal
    side_dish_patterns = [
        r'\bwing',  # Wings are typically sides at Pizza Express, etc.
        r'\bgarlic bread\b',
        r'\bdip\b',
        r'\bside\b',
        r'\bstarter\b',
        r'\bdessert\b',
    ]
    
    # Mapping patterns to dish types (ordered by specificity)
    mappings = [
        (r'\bkatsu\b', 'Katsu'),
        (r'\bpho\b', 'Pho'),
        (r'\bpad thai\b', 'Pad Thai'),
        (r'\bsushi\b', 'Sushi'),
        (r'\bramen\b', 'Ramen'),
        (r'\bcurry\b', 'Curry'),
        (r'\bnoodle', 'Noodles'),
        (r'\brice bowl\b', 'Rice Bowl'),
        (r'\bfried rice\b', 'Fried Rice'),
        (r'\bpizza\b', 'Pizza'),
        (r'\bpasta\b', 'Pasta'),
        (r'\blasagne\b|\blasagna\b', 'Lasagne'),
        (r'\bburger\b', 'Burger'),
        (r'\bfajita', 'Fajitas'),
        (r'\bburrito\b', 'Burrito'),
        (r'\btaco', 'Tacos'),
        (r'\bshawarma\b', 'Shawarma'),
        (r'\bkebab\b', 'Kebab'),
        (r'\bmac.*cheese\b|mac & cheese', 'Mac & Cheese'),
        (r'\bstir.?fry\b', 'Stir Fry'),
        (r'\bbiryani\b', 'Biryani'),
        (r'\btikka\b', 'Tikka'),
        (r'\bkorma\b', 'Korma'),
        (r'\bbutter chicken\b', 'Butter Chicken'),
        (r'\bteriyaki\b', 'Teriyaki'),
        (r'\bpoke\b', 'Poke Bowl'),
        (r'\bbowl\b', 'Bowl'),
        (r'\bwrap\b', 'Wrap'),
        (r'\bsalad\b', 'Salad'),
        (r'\bchicken\b', 'Chicken'),
    ]
    
    # For primary check, look at the FIRST item in the order (before first ~)
    if check_primary and '~' in text:
        first_item = text.split('~')[0].strip()
    else:
        first_item = text
    
    for pattern, dish_type in mappings:
        if re.search(pattern, first_item):
            return dish_type
    
    return None


def calculate_track_a_scores(data: dict) -> pd.DataFrame:
    """
    Calculate Track A: Performance Scores
    
    Only for dishes with 50+ orders.
    
    Components:
    - Repeat Rate (30%): From orders
    - Average Rating (30%): From ratings (4.5+ threshold)
    - Adult Satisfaction (15%): From post-order survey
    - Kids Happy Rate (15%): From post-order survey
    - Portions Adequate (10%): From post-order survey
    """
    logger.info("=" * 60)
    logger.info("CALCULATING TRACK A: PERFORMANCE SCORES")
    logger.info("=" * 60)
    
    results = []
    
    # Get dish performance data
    dish_perf = data.get('dish_performance', pd.DataFrame())
    orders = data.get('orders', pd.DataFrame())
    ratings = data.get('ratings', pd.DataFrame())
    
    # Calculate order volume by dish type
    dish_volumes = {}
    if len(orders) > 0 and 'MENU_ITEM_LIST' in orders.columns:
        for _, row in orders.iterrows():
            items = str(row.get('MENU_ITEM_LIST', ''))
            dish_type = normalize_dish_type(items)
            if dish_type:
                dish_volumes[dish_type] = dish_volumes.get(dish_type, 0) + 1
    
    # Calculate ratings by dish type
    dish_ratings = {}
    if len(ratings) > 0 and 'MENU_ITEM_LIST' in ratings.columns:
        for _, row in ratings.iterrows():
            items = str(row.get('MENU_ITEM_LIST', ''))
            dish_type = normalize_dish_type(items)
            rating = row.get('RATING_STARS')
            if dish_type and pd.notna(rating):
                if dish_type not in dish_ratings:
                    dish_ratings[dish_type] = []
                dish_ratings[dish_type].append(rating)
    
    # Get dishes with 50+ orders
    qualifying_dishes = [d for d, v in dish_volumes.items() if v >= MIN_ORDERS_FOR_TRACK_A]
    logger.info(f"Found {len(qualifying_dishes)} dishes with {MIN_ORDERS_FOR_TRACK_A}+ orders")
    
    for dish_type in qualifying_dishes:
        score_data = {
            'dish_type': dish_type,
            'order_volume': dish_volumes.get(dish_type, 0),
        }
        
        # Rating score
        if dish_type in dish_ratings:
            ratings_list = dish_ratings[dish_type]
            avg_rating = np.mean(ratings_list)
            score_data['avg_rating'] = round(avg_rating, 2)
            score_data['rating_n'] = len(ratings_list)
            score_data['rating_score'] = 5 if avg_rating >= 4.5 else (4 if avg_rating >= 4.0 else (3 if avg_rating >= 3.5 else 2))
            score_data['meets_rating_threshold'] = avg_rating >= RATING_THRESHOLD
        
        # Get survey data if available
        if len(dish_perf) > 0 and 'dish_type' in dish_perf.columns:
            dish_row = dish_perf[dish_perf['dish_type'] == dish_type]
            if len(dish_row) > 0:
                dish_row = dish_row.iloc[0]
                
                # Adult satisfaction
                if 'adult_satisfaction_rate' in dish_row and pd.notna(dish_row['adult_satisfaction_rate']):
                    score_data['adult_satisfaction'] = round(dish_row['adult_satisfaction_rate'], 2)
                    score_data['adult_satisfaction_n'] = dish_row.get('adult_satisfaction_n', 0)
                    score_data['satisfaction_score'] = 5 if dish_row['adult_satisfaction_rate'] >= 0.9 else (4 if dish_row['adult_satisfaction_rate'] >= 0.8 else 3)
                
                # Kids happy
                if 'kids_happy_rate' in dish_row and pd.notna(dish_row['kids_happy_rate']):
                    score_data['kids_happy'] = round(dish_row['kids_happy_rate'], 2)
                    score_data['kids_happy_n'] = dish_row.get('kids_happy_n', 0)
                    score_data['kids_score'] = 5 if dish_row['kids_happy_rate'] >= 0.85 else (4 if dish_row['kids_happy_rate'] >= 0.7 else 3)
                
                # Portions
                if 'portions_adequate_rate' in dish_row and pd.notna(dish_row['portions_adequate_rate']):
                    score_data['portions_adequate'] = round(dish_row['portions_adequate_rate'], 2)
                    score_data['portions_n'] = dish_row.get('portions_n', 0)
                    score_data['portions_score'] = 5 if dish_row['portions_adequate_rate'] >= 0.9 else (4 if dish_row['portions_adequate_rate'] >= 0.8 else 3)
                
                # Repeat rate
                if 'reorder_rate' in dish_row and pd.notna(dish_row['reorder_rate']):
                    score_data['repeat_rate'] = round(dish_row['reorder_rate'], 2)
                    score_data['repeat_score'] = 5 if dish_row['reorder_rate'] >= 0.4 else (4 if dish_row['reorder_rate'] >= 0.35 else (3 if dish_row['reorder_rate'] >= 0.25 else 2))
                
                score_data['survey_n'] = dish_row.get('n', 0)
        
        # Calculate composite Track A score
        components = []
        weights = []
        
        if 'repeat_score' in score_data:
            components.append(score_data['repeat_score'])
            weights.append(0.30)
        if 'rating_score' in score_data:
            components.append(score_data['rating_score'])
            weights.append(0.30)
        if 'satisfaction_score' in score_data:
            components.append(score_data['satisfaction_score'])
            weights.append(0.15)
        if 'kids_score' in score_data:
            components.append(score_data['kids_score'])
            weights.append(0.15)
        if 'portions_score' in score_data:
            components.append(score_data['portions_score'])
            weights.append(0.10)
        
        if components:
            # Normalize weights
            total_weight = sum(weights)
            score_data['track_a_score'] = round(sum(c * w for c, w in zip(components, weights)) / total_weight, 2)
            score_data['track_a_components'] = len(components)
        else:
            score_data['track_a_score'] = None
            score_data['track_a_components'] = 0
        
        results.append(score_data)
    
    df = pd.DataFrame(results)
    if len(df) > 0:
        df = df.sort_values('track_a_score', ascending=False)
    
    logger.info(f"Track A scored {len(df)} dishes")
    
    return df


def extract_latent_demand(data: dict) -> dict:
    """
    Extract latent demand signals from surveys and comments.
    
    Sources:
    - Dropoff survey open-text
    - Post-order survey comments
    - Rating comments
    """
    logger.info("Extracting latent demand signals...")
    
    demand_counts = Counter()
    demand_sources = {}
    
    # Dish types to look for
    dish_keywords = {
        'Grilled Chicken': ['grilled chicken', 'nando', 'peri peri', 'peri-peri'],
        'Chinese': ['chinese', 'sweet and sour', 'chow mein', 'dim sum'],
        'Roast Dinner': ['roast', 'sunday roast', 'roast dinner'],
        'Fish & Chips': ['fish and chips', 'fish & chips', 'chippy'],
        'Lasagne': ['lasagne', 'lasagna'],
        'Shepherd\'s Pie': ['shepherd', 'cottage pie'],
        'Biryani': ['biryani'],
        'Greek': ['greek', 'souvlaki', 'gyros'],
        'Halloumi': ['halloumi'],
        'Vegetarian': ['vegetarian', 'veggie', 'vegan', 'meat-free'],
        'Mild Options': ['mild', 'not spicy', 'plain', 'fussy'],
        'Mexican': ['mexican', 'taco', 'burrito', 'fajita', 'quesadilla'],
        'Sushi': ['sushi', 'sashimi'],
        'Korean': ['korean', 'bibimbap', 'bulgogi'],
        'Thai': ['thai', 'pad thai', 'green curry'],
        'Healthy': ['healthy', 'salad', 'grain bowl', 'balanced'],
    }
    
    # Search dropoff survey
    dropoff = data.get('dropoff', pd.DataFrame())
    if len(dropoff) > 0:
        text_cols = [c for c in dropoff.columns if 'comment' in c.lower() or 'other' in c.lower() or 'what' in c.lower()]
        for col in text_cols:
            for text in dropoff[col].dropna():
                text_lower = str(text).lower()
                for dish_type, keywords in dish_keywords.items():
                    if any(kw in text_lower for kw in keywords):
                        demand_counts[dish_type] += 1
                        if dish_type not in demand_sources:
                            demand_sources[dish_type] = []
                        demand_sources[dish_type].append(('dropoff', text[:100]))
    
    # Search post-order survey comments
    post_order = data.get('post_order', pd.DataFrame())
    if len(post_order) > 0:
        text_cols = [c for c in post_order.columns if 'comment' in c.lower() or 'feedback' in c.lower()]
        for col in text_cols:
            for text in post_order[col].dropna():
                text_lower = str(text).lower()
                for dish_type, keywords in dish_keywords.items():
                    if any(kw in text_lower for kw in keywords):
                        demand_counts[dish_type] += 1
                        if dish_type not in demand_sources:
                            demand_sources[dish_type] = []
                        demand_sources[dish_type].append(('post_order', text[:100]))
    
    # Search ratings comments
    ratings = data.get('ratings', pd.DataFrame())
    if len(ratings) > 0:
        text_cols = [c for c in ratings.columns if 'comment' in c.lower() or 'feedback' in c.lower()]
        for col in text_cols:
            for text in ratings[col].dropna():
                text_lower = str(text).lower()
                for dish_type, keywords in dish_keywords.items():
                    if any(kw in text_lower for kw in keywords):
                        demand_counts[dish_type] += 1
                        if dish_type not in demand_sources:
                            demand_sources[dish_type] = []
                        demand_sources[dish_type].append(('ratings', text[:100]))
    
    logger.info(f"Found latent demand for {len(demand_counts)} dish categories")
    
    return {
        'counts': dict(demand_counts),
        'sources': demand_sources
    }


def calculate_track_b_scores(data: dict, config: dict, latent_demand: dict) -> pd.DataFrame:
    """
    Calculate Track B: Opportunity Scores
    
    For ALL dish types (including unavailable).
    
    Components:
    - Latent Demand (30%): Mentions in surveys/comments
    - 10-Factor Framework Fit (30%): Weighted factor score
    - Partner Capability (20%): Could existing partners make this?
    - Cuisine Gap Priority (20%): Supply/quality gap status
    """
    logger.info("=" * 60)
    logger.info("CALCULATING TRACK B: OPPORTUNITY SCORES")
    logger.info("=" * 60)
    
    # Define all dish types to evaluate (including unavailable)
    # NOTE: Excluding side dishes/starters that don't fit "balanced midweek family meal" positioning
    # Wings, garlic bread, dips etc. are sides, not primary family meal dishes
    all_dish_types = [
        # Currently available (from data) - PRIMARY MEAL TYPES ONLY
        'Katsu', 'Pho', 'Pad Thai', 'Sushi', 'Noodles', 'Rice Bowl', 'Fried Rice',
        'Pizza', 'Pasta', 'Burger', 'Fajitas', 'Burrito', 'Shawarma',
        'Mac & Cheese', 'Stir Fry', 'Curry', 'Teriyaki', 'Wrap', 'Salad', 'Bowl',
        # Gap dishes (may not be available)
        'Grilled Chicken with Sides', 'Roast Dinner', 'Fish & Chips', 'Lasagne',
        'Shepherd\'s Pie', 'Biryani', 'Greek Mezze', 'Souvlaki', 'Halloumi Wrap',
        'Chinese Family Meal', 'Sweet & Sour Chicken', 'Dim Sum', 'Korean Fried Chicken',
        'Bibimbap', 'Grain Bowl', 'Buddha Bowl', 'Poke Bowl', 'Veggie Fajitas',
        'Butter Chicken', 'Tikka Masala', 'Korma', 'Ramen', 'Tacos', 'Quesadilla',
        'Rotisserie Chicken', 'Chicken Pie', 'Cottage Pie', 'Bangers & Mash',
    ]
    # Explicitly excluded: 'Wings' - typically a starter/side, not a balanced family meal
    
    # Remove duplicates
    all_dish_types = list(set(all_dish_types))
    
    # Get menu for availability check
    menu = data.get('menu', pd.DataFrame())
    orders = data.get('orders', pd.DataFrame())
    
    # Get cuisine gaps
    cuisine_gaps = data.get('cuisine_gaps', {})
    supply_gaps = cuisine_gaps.get('cuisines_by_gap', {}).get('SUPPLY GAP', [])
    quality_gaps = cuisine_gaps.get('cuisines_by_gap', {}).get('QUALITY GAP', [])
    
    # Factor weights from config
    factors = config.get('factors', {})
    
    results = []
    
    for dish_type in all_dish_types:
        score_data = {
            'dish_type': dish_type,
        }
        
        dish_lower = dish_type.lower()
        
        # Check availability - only count as "on Dinneroo" if it's a PRIMARY dish type
        # (not a side dish like wings at Pizza Express)
        is_available = False
        order_volume = 0
        primary_order_volume = 0
        
        if len(orders) > 0 and 'MENU_ITEM_LIST' in orders.columns:
            # Total mentions (including as side)
            matches = orders[orders['MENU_ITEM_LIST'].astype(str).str.lower().str.contains(dish_lower.split()[0], na=False)]
            order_volume = len(matches)
            
            # Primary mentions (as main dish - first item before ~)
            for _, row in matches.iterrows():
                items = str(row.get('MENU_ITEM_LIST', ''))
                first_item = items.split('~')[0].lower() if '~' in items else items.lower()
                if dish_lower.split()[0] in first_item:
                    primary_order_volume += 1
            
            # Only mark as available if it's a PRIMARY dish (>20% of mentions are primary)
            # This filters out side dishes like wings
            if order_volume > 0:
                primary_ratio = primary_order_volume / order_volume
                is_available = primary_ratio >= 0.2 or primary_order_volume >= 50
        
        score_data['on_dinneroo'] = is_available
        score_data['order_volume'] = primary_order_volume  # Use primary volume, not total
        
        # 1. LATENT DEMAND SCORE (30%)
        demand_count = 0
        for demand_key, count in latent_demand['counts'].items():
            if demand_key.lower() in dish_lower or dish_lower in demand_key.lower():
                demand_count += count
        
        # Also check for related terms
        related_terms = {
            'Grilled Chicken with Sides': ['chicken', 'grilled', 'nando'],
            'Chinese Family Meal': ['chinese', 'sweet and sour'],
            'Roast Dinner': ['roast', 'sunday'],
            'Fish & Chips': ['fish', 'chips', 'chippy'],
        }
        
        for related_dish, terms in related_terms.items():
            if related_dish == dish_type:
                for term in terms:
                    for demand_key, count in latent_demand['counts'].items():
                        if term in demand_key.lower():
                            demand_count += count
        
        score_data['latent_demand_mentions'] = demand_count
        # Score: 0 mentions = 1, 1-5 = 2, 6-15 = 3, 16-30 = 4, 31+ = 5
        if demand_count >= 31:
            score_data['latent_demand_score'] = 5
        elif demand_count >= 16:
            score_data['latent_demand_score'] = 4
        elif demand_count >= 6:
            score_data['latent_demand_score'] = 3
        elif demand_count >= 1:
            score_data['latent_demand_score'] = 2
        else:
            score_data['latent_demand_score'] = 1
        
        # 2. 10-FACTOR FRAMEWORK FIT (30%)
        factor_scores = estimate_factor_scores(dish_type, factors)
        score_data.update(factor_scores)
        
        # Calculate weighted factor score
        factor_total = 0
        factor_weight_total = 0
        for factor_key, factor_config in factors.items():
            if factor_key in factor_scores:
                weight = factor_config.get('weight', 0)
                factor_total += factor_scores[factor_key] * weight
                factor_weight_total += weight
        
        if factor_weight_total > 0:
            score_data['framework_score'] = round(factor_total / factor_weight_total, 2)
        else:
            score_data['framework_score'] = 3.0
        
        # 3. PARTNER CAPABILITY (20%)
        # Estimate based on cuisine match with existing partners
        partner_capability = estimate_partner_capability(dish_type, data)
        score_data['partner_capability'] = partner_capability['score']
        score_data['potential_partners'] = partner_capability['partners']
        
        # 4. CUISINE GAP PRIORITY (20%)
        cuisine = get_dish_cuisine(dish_type)
        score_data['cuisine'] = cuisine
        
        if cuisine in supply_gaps:
            score_data['gap_type'] = 'Supply Gap'
            score_data['gap_score'] = 5  # High priority
        elif cuisine in quality_gaps:
            score_data['gap_type'] = 'Quality Gap'
            score_data['gap_score'] = 4
        else:
            score_data['gap_type'] = 'No Gap'
            score_data['gap_score'] = 2  # Lower priority for gaps we don't have
        
        # Calculate composite Track B score
        track_b_score = (
            score_data['latent_demand_score'] * 0.30 +
            (score_data['framework_score'] / 5 * 5) * 0.30 +  # Normalize to 1-5
            score_data['partner_capability'] * 0.20 +
            score_data['gap_score'] * 0.20
        )
        score_data['track_b_score'] = round(track_b_score, 2)
        
        results.append(score_data)
    
    df = pd.DataFrame(results)
    df = df.sort_values('track_b_score', ascending=False)
    
    logger.info(f"Track B scored {len(df)} dishes")
    
    return df


def estimate_factor_scores(dish_type: str, factors: dict) -> dict:
    """Estimate 10-factor scores for a dish type."""
    scores = {}
    dish_lower = dish_type.lower()
    
    # Kid-Friendly
    if any(term in dish_lower for term in ['pizza', 'pasta', 'nugget', 'mac', 'cheese', 'chips']):
        scores['kid_friendly'] = 5
    elif any(term in dish_lower for term in ['katsu', 'chicken', 'noodle', 'rice', 'wrap']):
        scores['kid_friendly'] = 4
    elif any(term in dish_lower for term in ['curry', 'thai', 'pho']):
        scores['kid_friendly'] = 3
    elif any(term in dish_lower for term in ['spicy', 'chilli', 'korean']):
        scores['kid_friendly'] = 2
    else:
        scores['kid_friendly'] = 3
    
    # Balanced/Guilt-Free
    if any(term in dish_lower for term in ['salad', 'grain', 'buddha', 'poke', 'grilled']):
        scores['balanced_guilt_free'] = 5
    elif any(term in dish_lower for term in ['pho', 'bowl', 'chicken', 'roast']):
        scores['balanced_guilt_free'] = 4
    elif any(term in dish_lower for term in ['curry', 'noodle', 'rice']):
        scores['balanced_guilt_free'] = 3
    elif any(term in dish_lower for term in ['fried', 'pizza', 'burger', 'chips', 'wings']):
        scores['balanced_guilt_free'] = 2
    else:
        scores['balanced_guilt_free'] = 3
    
    # Adult Appeal
    if any(term in dish_lower for term in ['pho', 'curry', 'sushi', 'ramen', 'korean', 'thai']):
        scores['adult_appeal'] = 5
    elif any(term in dish_lower for term in ['katsu', 'fajita', 'shawarma', 'mezze']):
        scores['adult_appeal'] = 4
    elif any(term in dish_lower for term in ['pizza', 'pasta', 'burger']):
        scores['adult_appeal'] = 3
    else:
        scores['adult_appeal'] = 3
    
    # Portion Flexibility
    if any(term in dish_lower for term in ['sharing', 'platter', 'family', 'feast', 'meal']):
        scores['portion_flexibility'] = 5
    elif any(term in dish_lower for term in ['bowl', 'bundle', 'box']):
        scores['portion_flexibility'] = 4
    else:
        scores['portion_flexibility'] = 3
    
    # Fussy Eater Friendly
    if any(term in dish_lower for term in ['pizza', 'pasta', 'chicken', 'chips', 'mac']):
        scores['fussy_eater_friendly'] = 5
    elif any(term in dish_lower for term in ['katsu', 'noodle', 'rice', 'wrap']):
        scores['fussy_eater_friendly'] = 4
    elif any(term in dish_lower for term in ['mild', 'plain']):
        scores['fussy_eater_friendly'] = 4
    elif any(term in dish_lower for term in ['spicy', 'chilli', 'korean', 'thai']):
        scores['fussy_eater_friendly'] = 2
    else:
        scores['fussy_eater_friendly'] = 3
    
    # Customisation
    if any(term in dish_lower for term in ['fajita', 'bowl', 'wrap', 'build', 'poke']):
        scores['customisation'] = 5
    elif any(term in dish_lower for term in ['pizza', 'burrito', 'salad']):
        scores['customisation'] = 4
    else:
        scores['customisation'] = 3
    
    # Value at £25
    if any(term in dish_lower for term in ['family', 'sharing', 'feast', 'platter']):
        scores['value_at_25'] = 4
    elif any(term in dish_lower for term in ['sushi', 'steak']):
        scores['value_at_25'] = 2
    else:
        scores['value_at_25'] = 3
    
    # Shareability
    if any(term in dish_lower for term in ['sharing', 'platter', 'family', 'mezze', 'dim sum']):
        scores['shareability'] = 5
    elif any(term in dish_lower for term in ['pizza', 'curry', 'roast']):
        scores['shareability'] = 4
    else:
        scores['shareability'] = 3
    
    # Vegetarian Option
    if any(term in dish_lower for term in ['veggie', 'vegetarian', 'vegan', 'halloumi', 'falafel']):
        scores['vegetarian_option'] = 5
    elif any(term in dish_lower for term in ['pizza', 'pasta', 'curry', 'bowl']):
        scores['vegetarian_option'] = 4
    elif any(term in dish_lower for term in ['chicken', 'beef', 'pork', 'lamb', 'fish']):
        scores['vegetarian_option'] = 2
    else:
        scores['vegetarian_option'] = 3
    
    return scores


def estimate_partner_capability(dish_type: str, data: dict) -> dict:
    """
    Estimate which existing partners could make this dish.
    Returns score (1-5) and list of potential partners.
    """
    dish_lower = dish_type.lower()
    
    # Partner capabilities based on cuisine/type
    partner_capabilities = {
        'Dishoom': ['curry', 'biryani', 'indian', 'tikka', 'korma', 'butter chicken', 'naan'],
        'Pho': ['pho', 'vietnamese', 'noodle', 'rice', 'spring roll'],
        'Wagamama': ['katsu', 'ramen', 'noodle', 'rice', 'teriyaki', 'japanese', 'asian'],
        'Itsu': ['sushi', 'japanese', 'asian', 'rice', 'noodle', 'healthy'],
        'Farmer J': ['healthy', 'grain', 'bowl', 'salad', 'grilled', 'chicken'],
        'Bill\'s': ['british', 'roast', 'pie', 'burger', 'breakfast'],
        'Banana Tree': ['thai', 'vietnamese', 'asian', 'noodle', 'curry'],
        'Tortilla': ['mexican', 'burrito', 'taco', 'fajita', 'quesadilla'],
        'Franco Manca': ['pizza', 'italian'],
        'Iro Sushi': ['sushi', 'japanese'],
    }
    
    potential_partners = []
    for partner, capabilities in partner_capabilities.items():
        if any(cap in dish_lower for cap in capabilities):
            potential_partners.append(partner)
    
    # Score based on number of potential partners
    if len(potential_partners) >= 3:
        score = 5
    elif len(potential_partners) >= 2:
        score = 4
    elif len(potential_partners) >= 1:
        score = 3
    else:
        score = 2  # No current partner, but could recruit
    
    return {
        'score': score,
        'partners': ', '.join(potential_partners) if potential_partners else 'New recruitment needed'
    }


def get_dish_cuisine(dish_type: str) -> str:
    """Map dish type to cuisine category."""
    dish_lower = dish_type.lower()
    
    cuisine_mappings = {
        'Indian': ['curry', 'biryani', 'tikka', 'korma', 'butter chicken', 'naan', 'samosa'],
        'Japanese': ['sushi', 'ramen', 'katsu', 'teriyaki', 'tempura'],
        'Vietnamese': ['pho', 'banh mi', 'spring roll'],
        'Thai': ['pad thai', 'thai', 'green curry', 'massaman'],
        'Chinese': ['chinese', 'dim sum', 'sweet and sour', 'chow mein', 'fried rice'],
        'Korean': ['korean', 'bibimbap', 'bulgogi'],
        'Mexican': ['mexican', 'taco', 'burrito', 'fajita', 'quesadilla'],
        'Italian': ['pizza', 'pasta', 'lasagne', 'carbonara', 'risotto'],
        'British': ['roast', 'fish and chips', 'pie', 'bangers', 'shepherd'],
        'Middle Eastern': ['shawarma', 'kebab', 'falafel', 'hummus'],
        'Greek': ['greek', 'souvlaki', 'gyros', 'mezze'],
        'Healthy/Fresh': ['salad', 'grain', 'buddha', 'poke', 'bowl'],
        'American': ['burger', 'wings', 'mac and cheese', 'bbq'],
    }
    
    for cuisine, keywords in cuisine_mappings.items():
        if any(kw in dish_lower for kw in keywords):
            return cuisine
    
    return 'Global'


def combine_tracks_to_priority_100(track_a: pd.DataFrame, track_b: pd.DataFrame) -> pd.DataFrame:
    """
    Combine Track A and Track B into Priority 100 list.
    
    Categories:
    - Expand: High Track A, any Track B (proven winners)
    - Recruit: No Track A, High Track B (high-demand gaps)
    - Investigate: Low Track A, High Track B (demand/performance mismatch)
    - Fix: Low Track A, Low Track B (underperformers)
    """
    logger.info("=" * 60)
    logger.info("COMBINING TRACKS INTO PRIORITY 100")
    logger.info("=" * 60)
    
    # Merge tracks
    combined = track_b.copy()
    
    # Add Track A scores where available
    if len(track_a) > 0:
        track_a_subset = track_a[['dish_type', 'track_a_score', 'avg_rating', 'repeat_rate', 
                                   'adult_satisfaction', 'kids_happy', 'survey_n']].copy()
        track_a_subset.columns = ['dish_type', 'track_a_score', 'avg_rating', 'repeat_rate',
                                  'adult_satisfaction', 'kids_happy', 'survey_n']
        combined = combined.merge(track_a_subset, on='dish_type', how='left')
    else:
        combined['track_a_score'] = None
    
    # Determine category
    def categorize(row):
        has_track_a = pd.notna(row.get('track_a_score'))
        track_a = row.get('track_a_score', 0) or 0
        track_b = row.get('track_b_score', 0) or 0
        
        if has_track_a:
            if track_a >= 4.0:
                return 'Expand'
            elif track_a >= 3.0 and track_b >= 3.5:
                return 'Investigate'
            else:
                return 'Fix'
        else:
            if track_b >= 3.5:
                return 'Recruit'
            else:
                return 'Monitor'
    
    combined['category'] = combined.apply(categorize, axis=1)
    
    # Calculate combined priority score
    # For dishes with Track A: weight both tracks
    # For dishes without Track A: use Track B only
    def calculate_priority(row):
        has_track_a = pd.notna(row.get('track_a_score'))
        track_a = row.get('track_a_score', 0) or 0
        track_b = row.get('track_b_score', 0) or 0
        
        if has_track_a:
            # 60% Track A, 40% Track B for available dishes
            return round(track_a * 0.6 + track_b * 0.4, 2)
        else:
            # 100% Track B for unavailable dishes
            return round(track_b, 2)
    
    combined['priority_score'] = combined.apply(calculate_priority, axis=1)
    
    # Sort by priority score
    combined = combined.sort_values('priority_score', ascending=False)
    combined['rank'] = range(1, len(combined) + 1)
    
    # Reorder columns
    priority_cols = ['rank', 'dish_type', 'priority_score', 'category', 'track_a_score', 'track_b_score',
                     'on_dinneroo', 'order_volume', 'cuisine', 'gap_type']
    other_cols = [c for c in combined.columns if c not in priority_cols]
    combined = combined[priority_cols + other_cols]
    
    logger.info(f"Combined {len(combined)} dishes")
    logger.info(f"\nCategory distribution:")
    logger.info(combined['category'].value_counts().to_string())
    
    return combined


def main():
    """Main function to run two-track dish scoring."""
    logger.info("=" * 60)
    logger.info("TWO-TRACK DISH SCORING SYSTEM")
    logger.info("=" * 60)
    logger.info(f"Rating threshold: {RATING_THRESHOLD}")
    logger.info(f"Min orders for Track A: {MIN_ORDERS_FOR_TRACK_A}")
    
    # Ensure output directory exists
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load all data
    data = load_all_data()
    config = load_config()
    
    # Extract latent demand
    latent_demand = extract_latent_demand(data)
    
    # Calculate Track A: Performance Scores
    track_a = calculate_track_a_scores(data)
    
    # Save Track A
    track_a_path = ANALYSIS_DIR / "dish_performance_scores.csv"
    track_a.to_csv(track_a_path, index=False)
    logger.info(f"Saved Track A to: {track_a_path}")
    
    # Calculate Track B: Opportunity Scores
    track_b = calculate_track_b_scores(data, config, latent_demand)
    
    # Save Track B
    track_b_path = ANALYSIS_DIR / "dish_opportunity_scores.csv"
    track_b.to_csv(track_b_path, index=False)
    logger.info(f"Saved Track B to: {track_b_path}")
    
    # Combine into Priority 100
    priority_100 = combine_tracks_to_priority_100(track_a, track_b)
    
    # Save Priority 100 CSV
    priority_csv_path = ANALYSIS_DIR / "priority_100_dishes_v2.csv"
    priority_100.to_csv(priority_csv_path, index=False)
    logger.info(f"Saved Priority 100 to: {priority_csv_path}")
    
    # Save Priority 100 JSON
    json_output = []
    for _, row in priority_100.head(100).iterrows():
        dish = {
            'rank': int(row['rank']),
            'dish_type': row['dish_type'],
            'priority_score': float(row['priority_score']),
            'category': row['category'],
            'track_a_score': float(row['track_a_score']) if pd.notna(row.get('track_a_score')) else None,
            'track_b_score': float(row['track_b_score']) if pd.notna(row.get('track_b_score')) else None,
            'on_dinneroo': bool(row['on_dinneroo']),
            'order_volume': int(row.get('order_volume', 0)),
            'cuisine': row.get('cuisine', 'Unknown'),
            'gap_type': row.get('gap_type', 'Unknown'),
            'latent_demand_mentions': int(row.get('latent_demand_mentions', 0)),
            'potential_partners': row.get('potential_partners', ''),
        }
        json_output.append(dish)
    
    json_path = ANALYSIS_DIR / "priority_100_dishes_v2.json"
    with open(json_path, 'w') as f:
        json.dump(json_output, f, indent=2)
    logger.info(f"Saved JSON to: {json_path}")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("SCORING COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Track A (Performance): {len(track_a)} dishes scored")
    logger.info(f"Track B (Opportunity): {len(track_b)} dishes scored")
    logger.info(f"Priority 100: {len(priority_100)} dishes ranked")
    logger.info(f"\nTop 15 Priority Dishes:")
    display_cols = ['rank', 'dish_type', 'priority_score', 'category', 'track_a_score', 'track_b_score']
    logger.info(priority_100[display_cols].head(15).to_string())
    
    return priority_100


if __name__ == "__main__":
    main()

