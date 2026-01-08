"""
Script: 01_score_dishes_unified.py
Phase: 2 - Analysis
Purpose: Score dishes using the UNIFIED framework (Anna's Hit List + Family Fit)

This script merges:
- Anna's performance metrics (Looker behavioral data)
- Family Fit factors (Dinneroo positioning)
- Opportunity signals (latent demand)

Inputs:
    - DATA/1_SOURCE/snowflake/DINNEROO_ORDERS.csv (orders data)
    - DATA/1_SOURCE/snowflake/DINNEROO_RATINGS.csv (ratings)
    - DATA/1_SOURCE/snowflake/DINNEROO_MENU_CATALOG.csv (availability)
    - DATA/1_SOURCE/surveys/post_order_enriched_COMPLETE.csv (satisfaction)
    - DATA/3_ANALYSIS/survey_backed_scores.csv (pre-computed survey scores)
    - config/dish_scoring_unified.json (unified weights)

Outputs:
    - DATA/3_ANALYSIS/dish_scores_unified.csv
    - docs/data/priority_dishes.json (dashboard data)

Framework Reference: DOCUMENTATION/METHODOLOGY/05_UNIFIED_DISH_SCORING.md
"""

import logging
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple

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
DOCS_DATA_DIR = PROJECT_ROOT / "docs" / "data"


def load_unified_config() -> dict:
    """Load unified scoring configuration."""
    config_path = CONFIG_DIR / "dish_scoring_unified.json"
    if not config_path.exists():
        logger.error(f"Unified config not found at {config_path}")
        raise FileNotFoundError(f"Config not found: {config_path}")
    
    with open(config_path) as f:
        return json.load(f)


def load_orders_data() -> pd.DataFrame:
    """Load and aggregate orders data for performance metrics."""
    orders_path = SOURCE_DIR / "snowflake" / "DINNEROO_ORDERS.csv"
    if not orders_path.exists():
        logger.warning("Orders data not found")
        return pd.DataFrame()
    
    df = pd.read_csv(orders_path)
    logger.info(f"Loaded {len(df)} order records")
    return df


def load_ratings_data() -> pd.DataFrame:
    """Load ratings data for quality metrics."""
    ratings_path = SOURCE_DIR / "snowflake" / "DINNEROO_RATINGS.csv"
    if not ratings_path.exists():
        logger.warning("Ratings data not found")
        return pd.DataFrame()
    
    df = pd.read_csv(ratings_path)
    logger.info(f"Loaded {len(df)} rating records")
    return df


def load_survey_data() -> pd.DataFrame:
    """Load post-order survey data for satisfaction metrics."""
    survey_path = SOURCE_DIR / "surveys" / "post_order_enriched_COMPLETE.csv"
    if not survey_path.exists():
        logger.warning("Survey data not found")
        return pd.DataFrame()
    
    df = pd.read_csv(survey_path)
    logger.info(f"Loaded {len(df)} survey responses")
    return df


def load_menu_catalog() -> pd.DataFrame:
    """Load menu catalog for availability metrics."""
    catalog_path = SOURCE_DIR / "snowflake" / "DINNEROO_MENU_CATALOG.csv"
    if not catalog_path.exists():
        logger.warning("Menu catalog not found")
        return pd.DataFrame()
    
    df = pd.read_csv(catalog_path)
    logger.info(f"Loaded {len(df)} menu items")
    return df


def load_survey_backed_scores() -> pd.DataFrame:
    """Load pre-computed survey-backed scores."""
    scores_path = ANALYSIS_DIR / "survey_backed_scores.csv"
    if not scores_path.exists():
        logger.warning("Survey-backed scores not found")
        return pd.DataFrame()
    
    df = pd.read_csv(scores_path)
    logger.info(f"Loaded {len(df)} survey-backed dish scores")
    return df


# =============================================================================
# PERFORMANCE SCORING (Anna's metrics - 35%)
# =============================================================================

def calculate_normalized_sales(orders_df: pd.DataFrame, dish_name: str, 
                                zones_available: int, days_listed: int) -> float:
    """
    Calculate normalized sales score (10.5% weight).
    Formula: Total orders / (zones × days listed)
    """
    if orders_df.empty or zones_available == 0 or days_listed == 0:
        return 0.0
    
    # Find dish column
    dish_col = None
    for col in ['dish_name', 'item_name', 'menu_item', 'ITEM_NAME']:
        if col in orders_df.columns:
            dish_col = col
            break
    
    if not dish_col:
        return 0.0
    
    # Count orders for this dish
    dish_orders = len(orders_df[orders_df[dish_col].str.lower().str.contains(
        dish_name.lower(), na=False, regex=False
    )])
    
    normalized = dish_orders / (zones_available * days_listed)
    return normalized


def calculate_zone_ranking_score(dish_name: str, orders_df: pd.DataFrame) -> Tuple[float, float]:
    """
    Calculate zone ranking metrics.
    Returns: (pct_zones_rank_1, pct_zones_top_5)
    """
    if orders_df.empty:
        return 0.0, 0.0
    
    # Find zone and dish columns
    zone_col = None
    for col in ['zone_name', 'zone', 'ZONE_NAME']:
        if col in orders_df.columns:
            zone_col = col
            break
    
    dish_col = None
    for col in ['dish_name', 'item_name', 'menu_item', 'ITEM_NAME']:
        if col in orders_df.columns:
            dish_col = col
            break
    
    if not zone_col or not dish_col:
        return 0.0, 0.0
    
    # Calculate rank per zone
    zones = orders_df[zone_col].unique()
    rank_1_count = 0
    top_5_count = 0
    zones_with_dish = 0
    
    for zone in zones:
        zone_orders = orders_df[orders_df[zone_col] == zone]
        dish_counts = zone_orders[dish_col].value_counts()
        
        if dish_name.lower() in dish_counts.index.str.lower().values:
            zones_with_dish += 1
            # Get rank
            rank = (dish_counts.index.str.lower() == dish_name.lower()).argmax() + 1
            if rank == 1:
                rank_1_count += 1
            if rank <= 5:
                top_5_count += 1
    
    if zones_with_dish == 0:
        return 0.0, 0.0
    
    return rank_1_count / len(zones), top_5_count / len(zones)


def score_normalized_sales(normalized_value: float, all_normalized: list) -> int:
    """Convert normalized sales to 1-5 score based on percentile."""
    if not all_normalized or normalized_value == 0:
        return 1
    
    percentile = sum(1 for x in all_normalized if x <= normalized_value) / len(all_normalized)
    
    if percentile >= 0.90:
        return 5
    elif percentile >= 0.75:
        return 4
    elif percentile >= 0.50:
        return 3
    elif percentile >= 0.25:
        return 2
    else:
        return 1


def score_zone_ranking(pct_rank_1: float, pct_top_5: float) -> int:
    """Convert zone ranking to 1-5 score."""
    if pct_rank_1 >= 0.20 or pct_top_5 >= 0.60:
        return 5
    elif pct_rank_1 >= 0.10 or pct_top_5 >= 0.40:
        return 4
    elif pct_top_5 >= 0.20:
        return 3
    elif pct_top_5 >= 0.10:
        return 2
    else:
        return 1


def score_deliveroo_rating(avg_rating: float) -> int:
    """Convert Deliveroo rating to 1-5 score."""
    if pd.isna(avg_rating) or avg_rating == 0:
        return 3  # Default to middle if no data
    
    if avg_rating >= 4.7:
        return 5
    elif avg_rating >= 4.5:
        return 4
    elif avg_rating >= 4.3:
        return 3
    elif avg_rating >= 4.0:
        return 2
    else:
        return 1


def score_repeat_intent(pct_would_reorder: float) -> int:
    """Convert repeat intent percentage to 1-5 score."""
    if pd.isna(pct_would_reorder):
        return 3  # Default
    
    if pct_would_reorder >= 0.80:
        return 5
    elif pct_would_reorder >= 0.70:
        return 4
    elif pct_would_reorder >= 0.60:
        return 3
    elif pct_would_reorder >= 0.50:
        return 2
    else:
        return 1


# =============================================================================
# SATISFACTION SCORING (20%)
# =============================================================================

def score_meal_satisfaction(pct_satisfied: float) -> int:
    """Convert meal satisfaction to 1-5 score."""
    if pd.isna(pct_satisfied):
        return 3
    
    if pct_satisfied >= 0.90:
        return 5
    elif pct_satisfied >= 0.80:
        return 4
    elif pct_satisfied >= 0.70:
        return 3
    elif pct_satisfied >= 0.60:
        return 2
    else:
        return 1


def score_kids_happy(pct_happy: float) -> int:
    """Convert kids happy rate to 1-5 score."""
    if pd.isna(pct_happy):
        return 3
    
    if pct_happy >= 0.85:
        return 5
    elif pct_happy >= 0.75:
        return 4
    elif pct_happy >= 0.65:
        return 3
    elif pct_happy >= 0.55:
        return 2
    else:
        return 1


# =============================================================================
# FAMILY FIT SCORING (30%)
# =============================================================================

def estimate_kid_friendly(dish_name: str) -> int:
    """Estimate kid-friendly score based on dish characteristics."""
    dish_lower = dish_name.lower()
    
    # Very kid-friendly
    very_friendly = ['pizza', 'pasta', 'nugget', 'fish finger', 'mac and cheese', 
                     'chips', 'plain', 'mild', 'chicken', 'rice']
    # Not kid-friendly
    not_friendly = ['spicy', 'chilli', 'wasabi', 'kimchi', 'hot', 'jalapeño']
    
    if any(term in dish_lower for term in very_friendly):
        return 4
    elif any(term in dish_lower for term in not_friendly):
        return 2
    return 3


def estimate_fussy_eater_friendly(dish_name: str) -> int:
    """Estimate fussy eater friendliness."""
    dish_lower = dish_name.lower()
    
    safe = ['plain', 'mild', 'cheese', 'chicken', 'pasta', 'rice', 'nugget']
    risky = ['spicy', 'exotic', 'fusion', 'unusual', 'hot']
    
    if any(term in dish_lower for term in safe):
        return 4
    elif any(term in dish_lower for term in risky):
        return 2
    return 3


def estimate_balanced_guilt_free(dish_name: str) -> int:
    """Estimate balanced/guilt-free score."""
    dish_lower = dish_name.lower()
    
    healthy = ['grilled', 'salad', 'steamed', 'baked', 'vegetable', 'lean', 
               'protein', 'grain', 'bowl', 'fresh']
    unhealthy = ['fried', 'deep fried', 'crispy', 'battered', 'cream', 'loaded']
    
    if any(term in dish_lower for term in healthy):
        return 4
    elif any(term in dish_lower for term in unhealthy):
        return 2
    return 3


def estimate_portion_flexibility(dish_name: str) -> int:
    """Estimate portion flexibility score."""
    dish_lower = dish_name.lower()
    
    family = ['family', 'sharing', 'for 4', 'large', 'platter', 'feast', 'bundle']
    individual = ['single', 'individual', 'personal', 'mini']
    
    if any(term in dish_lower for term in family):
        return 5
    elif any(term in dish_lower for term in individual):
        return 2
    return 3


def estimate_customisation(dish_name: str) -> int:
    """Estimate customisation score."""
    dish_lower = dish_name.lower()
    
    customisable = ['build your own', 'choose', 'pick', 'sides', 'bowl', 'wrap', 'fajita']
    fixed = ['set meal', 'combo', 'fixed', 'platter']
    
    if any(term in dish_lower for term in customisable):
        return 5
    elif any(term in dish_lower for term in fixed):
        return 3
    return 3


# =============================================================================
# OPPORTUNITY SCORING (15%)
# =============================================================================

def score_dish_suitability(suitability_rating: float) -> int:
    """Convert dish suitability rating to 1-5 score."""
    if pd.isna(suitability_rating):
        return 3
    
    if suitability_rating >= 4.5:
        return 5
    elif suitability_rating >= 4.0:
        return 4
    elif suitability_rating >= 3.5:
        return 3
    elif suitability_rating >= 3.0:
        return 2
    else:
        return 1


def score_open_text_requests(mention_count: int) -> int:
    """Convert open-text request count to 1-5 score."""
    if mention_count >= 20:
        return 5
    elif mention_count >= 10:
        return 4
    elif mention_count >= 5:
        return 3
    elif mention_count >= 2:
        return 2
    else:
        return 1


def score_availability_gap(pct_zones_available: float) -> int:
    """
    Score availability gap (inverse - less availability = more opportunity).
    """
    if pct_zones_available < 0.20:
        return 5  # High expansion potential
    elif pct_zones_available < 0.40:
        return 4
    elif pct_zones_available < 0.60:
        return 3
    elif pct_zones_available < 0.80:
        return 2
    else:
        return 1  # Saturated


# =============================================================================
# COMPOSITE SCORING
# =============================================================================

def calculate_composite_score(scores: Dict[str, int], config: dict) -> float:
    """
    Calculate weighted composite score using unified framework.
    """
    categories = config['categories']
    total_score = 0.0
    
    # Performance (35%)
    perf = categories['performance']['factors']
    total_score += scores.get('normalized_sales', 3) * perf['normalized_sales']['effective_weight']
    total_score += scores.get('zone_ranking', 3) * perf['zone_ranking_strength']['effective_weight']
    total_score += scores.get('deliveroo_rating', 3) * perf['deliveroo_rating']['effective_weight']
    total_score += scores.get('repeat_intent', 3) * perf['repeat_intent']['effective_weight']
    
    # Satisfaction (20%)
    sat = categories['satisfaction']['factors']
    total_score += scores.get('meal_satisfaction', 3) * sat['meal_satisfaction']['effective_weight']
    total_score += scores.get('kids_happy', 3) * sat['kids_happy_rate']['effective_weight']
    
    # Family Fit (30%)
    fit = categories['family_fit']['factors']
    total_score += scores.get('kid_friendly', 3) * fit['kid_friendly']['effective_weight']
    total_score += scores.get('fussy_eater', 3) * fit['fussy_eater_friendly']['effective_weight']
    total_score += scores.get('balanced', 3) * fit['balanced_guilt_free']['effective_weight']
    total_score += scores.get('portions', 3) * fit['portion_flexibility']['effective_weight']
    total_score += scores.get('customisation', 3) * fit['customisation']['effective_weight']
    
    # Opportunity (15%)
    opp = categories['opportunity']['factors']
    total_score += scores.get('suitability', 3) * opp['dish_suitability_rating']['effective_weight']
    total_score += scores.get('open_text', 3) * opp['open_text_requests']['effective_weight']
    total_score += scores.get('availability_gap', 3) * opp['availability_gap']['effective_weight']
    
    return round(total_score, 2)


def determine_tier(composite_score: float, config: dict) -> str:
    """Determine tier classification based on composite score."""
    tiers = config['tier_classification']
    
    if composite_score >= tiers['tier_1_must_have']['threshold']:
        return "Must-Have"
    elif composite_score >= tiers['tier_2_should_have']['threshold']:
        return "Should-Have"
    elif composite_score >= tiers['tier_3_nice_to_have']['threshold']:
        return "Nice-to-Have"
    else:
        return "Monitor"


def determine_quadrant(performance_score: float, family_fit_score: float) -> str:
    """Determine quadrant based on performance vs family fit."""
    high_perf = performance_score >= 3.5
    high_fit = family_fit_score >= 3.5
    
    if high_perf and high_fit:
        return "Star"
    elif not high_perf and high_fit:
        return "Potential"
    elif high_perf and not high_fit:
        return "Cash Cow"
    else:
        return "Question Mark"


def count_factors_with_data(scores: dict) -> int:
    """Count how many factors have actual data (not estimated)."""
    data_sources = scores.get('data_sources', {})
    return sum(1 for source in data_sources.values() if source != 'estimated')


def determine_evidence_level(factors_with_data: int) -> str:
    """Determine evidence level based on data coverage."""
    if factors_with_data >= 8:
        return "Validated"
    elif factors_with_data >= 5:
        return "Corroborated"
    else:
        return "Estimated"


# =============================================================================
# MAIN SCORING FUNCTION
# =============================================================================

def score_all_dishes(orders_df: pd.DataFrame, ratings_df: pd.DataFrame,
                     survey_df: pd.DataFrame, catalog_df: pd.DataFrame,
                     survey_scores_df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """
    Score all dishes using the unified framework.
    """
    results = []
    
    # Get unique dishes from orders and catalog
    dishes = set()
    
    # From orders
    for col in ['dish_name', 'item_name', 'menu_item', 'ITEM_NAME']:
        if col in orders_df.columns:
            dishes.update(orders_df[col].dropna().unique())
            break
    
    # From catalog
    for col in ['dish_name', 'item_name', 'menu_item', 'name']:
        if col in catalog_df.columns:
            dishes.update(catalog_df[col].dropna().unique())
            break
    
    # Add discovery dishes (high family fit potential)
    discovery_dishes = [
        "Grilled Chicken Family Platter with Sides",
        "Rotisserie Chicken Family Feast",
        "Fish & Chips Family Bucket",
        "Fajita Family Kit",
        "Greek Mezze Family Feast",
        "Dim Sum Family Selection",
        "Halloumi Wrap Family Box",
        "Butter Chicken Family Feast",
        "Pad Thai Family Bundle",
        "Sushi Family Platter"
    ]
    dishes.update(discovery_dishes)
    
    logger.info(f"Scoring {len(dishes)} dishes...")
    
    # Pre-calculate normalized sales for percentile scoring
    all_normalized_sales = []
    for dish in dishes:
        norm_sales = calculate_normalized_sales(orders_df, dish, 100, 150)  # Approximate
        all_normalized_sales.append(norm_sales)
    
    for dish in dishes:
        scores = {'dish_name': dish}
        data_sources = {}
        
        # === PERFORMANCE SCORES (35%) ===
        
        # Normalized sales
        norm_sales = calculate_normalized_sales(orders_df, dish, 100, 150)
        scores['normalized_sales'] = score_normalized_sales(norm_sales, all_normalized_sales)
        data_sources['normalized_sales'] = 'looker' if norm_sales > 0 else 'estimated'
        
        # Zone ranking
        pct_rank_1, pct_top_5 = calculate_zone_ranking_score(dish, orders_df)
        scores['zone_ranking'] = score_zone_ranking(pct_rank_1, pct_top_5)
        data_sources['zone_ranking'] = 'looker' if pct_top_5 > 0 else 'estimated'
        
        # Deliveroo rating
        avg_rating = None
        if not ratings_df.empty:
            for col in ['dish_name', 'item_name', 'ITEM_NAME']:
                if col in ratings_df.columns:
                    dish_ratings = ratings_df[ratings_df[col].str.lower().str.contains(
                        dish.lower(), na=False, regex=False
                    )]
                    if len(dish_ratings) > 0:
                        for rating_col in ['rating', 'star_rating', 'RATING']:
                            if rating_col in dish_ratings.columns:
                                avg_rating = dish_ratings[rating_col].mean()
                                break
                    break
        
        scores['deliveroo_rating'] = score_deliveroo_rating(avg_rating)
        scores['avg_rating_raw'] = avg_rating
        data_sources['deliveroo_rating'] = 'looker' if avg_rating else 'estimated'
        
        # Repeat intent (from survey)
        repeat_intent = None
        if not survey_df.empty:
            # Look for repeat intent column
            for col in survey_df.columns:
                if 'repeat' in col.lower() or 'again' in col.lower():
                    dish_survey = survey_df[survey_df.apply(
                        lambda x: dish.lower() in str(x).lower(), axis=1
                    )]
                    if len(dish_survey) > 0:
                        repeat_intent = dish_survey[col].mean()
                    break
        
        scores['repeat_intent'] = score_repeat_intent(repeat_intent)
        data_sources['repeat_intent'] = 'survey' if repeat_intent else 'estimated'
        
        # === SATISFACTION SCORES (20%) ===
        
        # Meal satisfaction
        meal_sat = None
        if not survey_df.empty:
            for col in survey_df.columns:
                if 'satisfaction' in col.lower() or 'satisfied' in col.lower():
                    dish_survey = survey_df[survey_df.apply(
                        lambda x: dish.lower() in str(x).lower(), axis=1
                    )]
                    if len(dish_survey) > 0:
                        meal_sat = dish_survey[col].mean()
                    break
        
        scores['meal_satisfaction'] = score_meal_satisfaction(meal_sat)
        data_sources['meal_satisfaction'] = 'survey' if meal_sat else 'estimated'
        
        # Kids happy rate
        kids_happy = None
        if not survey_df.empty:
            for col in survey_df.columns:
                if 'child' in col.lower() or 'kid' in col.lower():
                    dish_survey = survey_df[survey_df.apply(
                        lambda x: dish.lower() in str(x).lower(), axis=1
                    )]
                    if len(dish_survey) > 0:
                        kids_happy = dish_survey[col].mean()
                    break
        
        scores['kids_happy'] = score_kids_happy(kids_happy)
        data_sources['kids_happy'] = 'survey' if kids_happy else 'estimated'
        
        # === FAMILY FIT SCORES (30%) ===
        
        # Check survey-backed scores first
        survey_row = None
        if not survey_scores_df.empty and 'dish_name' in survey_scores_df.columns:
            matches = survey_scores_df[survey_scores_df['dish_name'].str.lower() == dish.lower()]
            if len(matches) > 0:
                survey_row = matches.iloc[0]
        
        # Kid-friendly
        if survey_row is not None and 'kid_friendly_score' in survey_row.index:
            scores['kid_friendly'] = int(survey_row['kid_friendly_score'])
            data_sources['kid_friendly'] = 'survey'
        else:
            scores['kid_friendly'] = estimate_kid_friendly(dish)
            data_sources['kid_friendly'] = 'estimated'
        
        # Fussy eater friendly
        scores['fussy_eater'] = estimate_fussy_eater_friendly(dish)
        data_sources['fussy_eater'] = 'estimated'
        
        # Balanced/guilt-free
        if survey_row is not None and 'balanced_guilt_free_score' in survey_row.index:
            scores['balanced'] = int(survey_row['balanced_guilt_free_score'])
            data_sources['balanced'] = 'survey'
        else:
            scores['balanced'] = estimate_balanced_guilt_free(dish)
            data_sources['balanced'] = 'estimated'
        
        # Portion flexibility
        if survey_row is not None and 'portion_flexibility_score' in survey_row.index:
            scores['portions'] = int(survey_row['portion_flexibility_score'])
            data_sources['portions'] = 'survey'
        else:
            scores['portions'] = estimate_portion_flexibility(dish)
            data_sources['portions'] = 'estimated'
        
        # Customisation
        scores['customisation'] = estimate_customisation(dish)
        data_sources['customisation'] = 'estimated'
        
        # === OPPORTUNITY SCORES (15%) ===
        
        # Dish suitability (from R&I if available)
        scores['suitability'] = 3  # Default - would come from Anna's R&I data
        data_sources['suitability'] = 'estimated'
        
        # Open-text requests (would come from text analysis)
        scores['open_text'] = 2  # Default
        data_sources['open_text'] = 'estimated'
        
        # Availability gap
        zones_available = 0
        total_zones = 100  # Approximate
        if not catalog_df.empty:
            for col in ['dish_name', 'item_name', 'name']:
                if col in catalog_df.columns:
                    zones_available = len(catalog_df[catalog_df[col].str.lower().str.contains(
                        dish.lower(), na=False, regex=False
                    )])
                    break
        
        pct_available = zones_available / total_zones if total_zones > 0 else 0
        scores['availability_gap'] = score_availability_gap(pct_available)
        scores['zones_available'] = zones_available
        data_sources['availability_gap'] = 'catalog'
        
        # Store data sources
        scores['data_sources'] = data_sources
        
        # === CALCULATE COMPOSITE SCORES ===
        
        # Calculate sub-scores for quadrant analysis
        perf_factors = ['normalized_sales', 'zone_ranking', 'deliveroo_rating', 'repeat_intent']
        fit_factors = ['kid_friendly', 'fussy_eater', 'balanced', 'portions', 'customisation']
        
        scores['performance_subscore'] = np.mean([scores.get(f, 3) for f in perf_factors])
        scores['family_fit_subscore'] = np.mean([scores.get(f, 3) for f in fit_factors])
        
        # Calculate composite score
        scores['composite_score'] = calculate_composite_score(scores, config)
        
        # Determine tier and quadrant
        scores['tier'] = determine_tier(scores['composite_score'], config)
        scores['quadrant'] = determine_quadrant(
            scores['performance_subscore'], 
            scores['family_fit_subscore']
        )
        
        # Determine evidence level
        factors_with_data = count_factors_with_data(scores)
        scores['evidence_level'] = determine_evidence_level(factors_with_data)
        scores['factors_with_data'] = factors_with_data
        
        # Determine cuisine
        scores['cuisine'] = determine_cuisine(dish)
        
        # Get order volume
        order_count = 0
        for col in ['dish_name', 'item_name', 'menu_item', 'ITEM_NAME']:
            if col in orders_df.columns:
                order_count = len(orders_df[orders_df[col].str.lower().str.contains(
                    dish.lower(), na=False, regex=False
                )])
                break
        scores['order_volume'] = order_count
        
        results.append(scores)
    
    # Create DataFrame and sort by composite score
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('composite_score', ascending=False)
    results_df['rank'] = range(1, len(results_df) + 1)
    
    return results_df


def determine_cuisine(dish_name: str) -> str:
    """Determine cuisine type from dish name."""
    dish_lower = dish_name.lower()
    
    cuisine_keywords = {
        'Italian': ['pizza', 'pasta', 'risotto', 'lasagna', 'carbonara', 'bolognese'],
        'Chinese': ['dim sum', 'chow mein', 'sweet and sour', 'kung pao', 'fried rice'],
        'Indian': ['curry', 'tikka', 'masala', 'biryani', 'korma', 'naan', 'tandoori', 'paneer'],
        'Mexican': ['taco', 'burrito', 'quesadilla', 'nachos', 'fajita', 'enchilada'],
        'Japanese': ['sushi', 'ramen', 'teriyaki', 'tempura', 'katsu'],
        'Thai': ['pad thai', 'green curry', 'red curry', 'tom yum'],
        'Vietnamese': ['pho', 'banh mi', 'spring roll'],
        'Mediterranean': ['greek', 'halloumi', 'mezze', 'falafel', 'hummus', 'souvlaki'],
        'British': ['fish and chips', 'pie', 'roast', 'shepherd', 'bangers'],
        'Grilled Chicken': ['peri-peri', 'grilled chicken', 'flame-grilled', 'rotisserie'],
        'Healthy/Fresh': ['poke', 'bowl', 'salad', 'protein', 'grain']
    }
    
    for cuisine, keywords in cuisine_keywords.items():
        if any(kw in dish_lower for kw in keywords):
            return cuisine
    
    return 'Other'


def export_dashboard_data(results_df: pd.DataFrame, config: dict):
    """Export data for the dashboard."""
    DOCS_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Prepare dashboard data
    dashboard_data = {
        "metadata": {
            "generated": datetime.now().isoformat(),
            "framework": "Unified (Anna's Hit List + Family Fit)",
            "version": config.get('version', '1.0'),
            "total_dishes": len(results_df)
        },
        "summary": {
            "must_have_count": len(results_df[results_df['tier'] == 'Must-Have']),
            "should_have_count": len(results_df[results_df['tier'] == 'Should-Have']),
            "nice_to_have_count": len(results_df[results_df['tier'] == 'Nice-to-Have']),
            "monitor_count": len(results_df[results_df['tier'] == 'Monitor']),
            "validated_count": len(results_df[results_df['evidence_level'] == 'Validated']),
            "corroborated_count": len(results_df[results_df['evidence_level'] == 'Corroborated']),
            "estimated_count": len(results_df[results_df['evidence_level'] == 'Estimated'])
        },
        "category_weights": {
            "performance": 0.35,
            "satisfaction": 0.20,
            "family_fit": 0.30,
            "opportunity": 0.15
        },
        "dishes": []
    }
    
    # Add dish data
    for _, row in results_df.iterrows():
        dish_data = {
            "rank": int(row['rank']),
            "name": row['dish_name'],
            "cuisine": row['cuisine'],
            "composite_score": float(row['composite_score']),
            "tier": row['tier'],
            "quadrant": row['quadrant'],
            "evidence_level": row['evidence_level'],
            "order_volume": int(row.get('order_volume', 0)),
            "avg_rating": float(row['avg_rating_raw']) if pd.notna(row.get('avg_rating_raw')) else None,
            "scores": {
                "performance": {
                    "normalized_sales": int(row.get('normalized_sales', 3)),
                    "zone_ranking": int(row.get('zone_ranking', 3)),
                    "deliveroo_rating": int(row.get('deliveroo_rating', 3)),
                    "repeat_intent": int(row.get('repeat_intent', 3)),
                    "subscore": float(row.get('performance_subscore', 3))
                },
                "satisfaction": {
                    "meal_satisfaction": int(row.get('meal_satisfaction', 3)),
                    "kids_happy": int(row.get('kids_happy', 3))
                },
                "family_fit": {
                    "kid_friendly": int(row.get('kid_friendly', 3)),
                    "fussy_eater": int(row.get('fussy_eater', 3)),
                    "balanced": int(row.get('balanced', 3)),
                    "portions": int(row.get('portions', 3)),
                    "customisation": int(row.get('customisation', 3)),
                    "subscore": float(row.get('family_fit_subscore', 3))
                },
                "opportunity": {
                    "suitability": int(row.get('suitability', 3)),
                    "open_text": int(row.get('open_text', 3)),
                    "availability_gap": int(row.get('availability_gap', 3))
                }
            },
            "on_menu": row.get('zones_available', 0) > 0
        }
        dashboard_data['dishes'].append(dish_data)
    
    # Save JSON
    output_path = DOCS_DATA_DIR / "priority_dishes.json"
    with open(output_path, 'w') as f:
        json.dump(dashboard_data, f, indent=2)
    
    logger.info(f"Dashboard data exported to {output_path}")


def main():
    """Main function to run unified dish scoring."""
    logger.info("=" * 60)
    logger.info("UNIFIED DISH SCORING")
    logger.info("Framework: Anna's Hit List + Family Fit")
    logger.info("=" * 60)
    
    # Ensure output directories exist
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load config
    config = load_unified_config()
    logger.info(f"Loaded unified config v{config.get('version', '1.0')}")
    
    # Load data
    orders_df = load_orders_data()
    ratings_df = load_ratings_data()
    survey_df = load_survey_data()
    catalog_df = load_menu_catalog()
    survey_scores_df = load_survey_backed_scores()
    
    # Score all dishes
    results_df = score_all_dishes(
        orders_df, ratings_df, survey_df, catalog_df, survey_scores_df, config
    )
    
    # Save CSV
    csv_path = ANALYSIS_DIR / "dish_scores_unified.csv"
    
    # Select columns to save
    save_cols = [
        'rank', 'dish_name', 'cuisine', 'composite_score', 'tier', 'quadrant',
        'evidence_level', 'order_volume', 'avg_rating_raw',
        'performance_subscore', 'family_fit_subscore',
        'normalized_sales', 'zone_ranking', 'deliveroo_rating', 'repeat_intent',
        'meal_satisfaction', 'kids_happy',
        'kid_friendly', 'fussy_eater', 'balanced', 'portions', 'customisation',
        'suitability', 'open_text', 'availability_gap', 'zones_available'
    ]
    
    save_df = results_df[[c for c in save_cols if c in results_df.columns]]
    save_df.to_csv(csv_path, index=False)
    logger.info(f"Saved scores to {csv_path}")
    
    # Export dashboard data
    export_dashboard_data(results_df, config)
    
    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("SCORING SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total dishes scored: {len(results_df)}")
    logger.info(f"\nTier distribution:")
    logger.info(results_df['tier'].value_counts().to_string())
    logger.info(f"\nQuadrant distribution:")
    logger.info(results_df['quadrant'].value_counts().to_string())
    logger.info(f"\nEvidence level distribution:")
    logger.info(results_df['evidence_level'].value_counts().to_string())
    logger.info(f"\nTop 10 dishes:")
    logger.info(results_df[['rank', 'dish_name', 'composite_score', 'tier']].head(10).to_string())
    
    return results_df


if __name__ == "__main__":
    main()




