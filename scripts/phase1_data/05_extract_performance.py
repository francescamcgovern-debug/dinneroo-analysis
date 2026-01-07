"""
Script: 05_extract_performance.py
Phase: 1 - Data Preparation
Purpose: Extract actual performance metrics from orders, ratings, and surveys

This script extracts MEASURED performance data (not estimates) for:
1. Partner-level metrics (satisfaction, kids happy, portions, reorder intent)
2. Dish-level metrics (by normalizing dish descriptions)
3. Cuisine-level metrics

These metrics are then used to score dishes based on actual performance,
not LLM estimates.

Outputs:
    - DATA/3_ANALYSIS/partner_performance.csv
    - DATA/3_ANALYSIS/dish_performance.csv
    - DATA/3_ANALYSIS/cuisine_performance.csv
"""

import logging
import json
import pandas as pd
import numpy as np
import re
from pathlib import Path
from collections import defaultdict

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


# Dish type normalization mapping
DISH_TYPE_PATTERNS = {
    'Katsu Curry': [r'katsu.*curry', r'chicken katsu', r'katsu chicken', r'yasai katsu'],
    'Katsu': [r'\bkatsu\b(?!.*curry)'],
    'Curry (General)': [r'\bcurry\b(?!.*katsu)', r'tikka masala', r'korma', r'butter chicken', r'ruby.*chicken', r'chicken.*ruby'],
    'Pho': [r'\bpho\b', r'pho noodle'],
    'Pad Thai': [r'pad thai'],
    'Sushi': [r'\bsushi\b', r'sushi platter'],
    'Rice Bowl': [r'rice bowl', r'teriyaki.*bowl', r'poke bowl'],
    'Noodles': [r'\bnoodle', r'chow mein', r'lo mein', r'ramen'],
    'Pizza': [r'\bpizza\b', r'margherita'],
    'Pasta': [r'\bpasta\b', r'lasagna', r'lasagne', r'spaghetti', r'penne', r'alfredo', r'bolognese', r'carbonara'],
    'Fajitas': [r'fajita'],
    'Burrito': [r'burrito', r'burrito bowl'],
    'Tacos': [r'\btaco'],
    'Shawarma': [r'shawarma', r'chicken shawarma'],
    'Fried Rice': [r'fried rice', r'egg fried rice'],
    'Stir Fry': [r'stir fry', r'stir-fry'],
    'Wings': [r'\bwings?\b'],
    'Chicken (General)': [r'\bchicken\b(?!.*katsu)(?!.*ruby)(?!.*shawarma)(?!.*wings?)'],
    'Mac & Cheese': [r'mac.*cheese', r'macaroni'],
    'Shepherd\'s Pie': [r'shepherd', r'cottage pie'],
    'Fish & Chips': [r'fish.*chip'],
    'Roast Dinner': [r'roast dinner', r'sunday roast'],
}


def normalize_dish_type(dish_description: str) -> str:
    """
    Normalize a dish description to a standard dish type.
    Returns the dish type or 'Other' if no match.
    """
    if pd.isna(dish_description):
        return 'Unknown'
    
    dish_lower = str(dish_description).lower().strip()
    
    for dish_type, patterns in DISH_TYPE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, dish_lower):
                return dish_type
    
    return 'Other'


def extract_partner_performance():
    """
    Extract partner-level performance metrics from post-order survey.
    
    Metrics:
    - satisfaction_rate: % "Loved it" or "Liked it"
    - kids_happy_rate: % kids "full and happy"
    - portion_adequate_rate: % "Agree" or "Strongly agree" on portions
    - reorder_rate: % "Agree" or "Strongly agree" on reorder intent
    - overall_satisfaction_rate: % "Very Satisfied" or "Satisfied"
    """
    logger.info("Extracting partner performance metrics...")
    
    survey_path = SOURCE_DIR / "surveys" / "POST_ORDER_SURVEY-CONSOLIDATED.csv"
    if not survey_path.exists():
        logger.error(f"Survey file not found: {survey_path}")
        return pd.DataFrame()
    
    df = pd.read_csv(survey_path)
    logger.info(f"Loaded {len(df)} survey responses")
    
    # Find the restaurant column
    restaurant_col = None
    for col in df.columns:
        if 'restaurant' in col.lower() and 'order' in col.lower():
            restaurant_col = col
            break
    
    if not restaurant_col:
        # Try alternative
        for col in df.columns:
            if 'Which restaurant did you order from?' in col:
                restaurant_col = col
                break
    
    if not restaurant_col:
        logger.error("Could not find restaurant column")
        return pd.DataFrame()
    
    logger.info(f"Using restaurant column: {restaurant_col}")
    
    # Find key metric columns
    dish_col = None
    for col in df.columns:
        if 'dish' in col.lower() and 'order' in col.lower():
            dish_col = col
            break
    
    # Adult satisfaction column
    adult_sat_col = None
    for col in df.columns:
        if 'how did you feel about the meal' in col.lower():
            adult_sat_col = col
            break
    
    # Kids reaction columns (there may be multiple for multiple children)
    kids_cols = [col for col in df.columns if 'how did your child' in col.lower() and 'react' in col.lower()]
    
    # Portions column
    portions_col = None
    for col in df.columns:
        if 'enough food for everyone' in col.lower():
            portions_col = col
            break
    
    # Reorder intent column
    reorder_col = None
    for col in df.columns:
        if 'order the same dish again' in col.lower():
            reorder_col = col
            break
    
    # Overall satisfaction column
    overall_col = None
    for col in df.columns:
        if 'overall' in col.lower() and 'rate' in col.lower() and 'dinneroo' in col.lower():
            overall_col = col
            break
    
    # Who ordering column (to identify family orders)
    who_col = None
    for col in df.columns:
        if 'who did you order for' in col.lower():
            who_col = col
            break
    
    logger.info(f"Found columns:")
    logger.info(f"  Restaurant: {restaurant_col}")
    logger.info(f"  Dish: {dish_col}")
    logger.info(f"  Adult satisfaction: {adult_sat_col}")
    logger.info(f"  Kids reaction: {len(kids_cols)} columns")
    logger.info(f"  Portions: {portions_col}")
    logger.info(f"  Reorder: {reorder_col}")
    logger.info(f"  Overall: {overall_col}")
    logger.info(f"  Who ordering: {who_col}")
    
    # Calculate metrics by partner
    partner_metrics = []
    
    for partner in df[restaurant_col].dropna().unique():
        partner_df = df[df[restaurant_col] == partner]
        n = len(partner_df)
        
        if n < 5:  # Minimum sample size
            continue
        
        metrics = {
            'partner': partner,
            'n': n
        }
        
        # Adult satisfaction rate
        if adult_sat_col:
            sat_values = partner_df[adult_sat_col].dropna()
            if len(sat_values) > 0:
                positive = sat_values.isin(['Loved it', 'Liked it']).sum()
                metrics['adult_satisfaction_rate'] = positive / len(sat_values)
                metrics['adult_satisfaction_n'] = len(sat_values)
        
        # Kids happy rate (combine all kids columns)
        if kids_cols:
            kids_responses = []
            for col in kids_cols:
                kids_responses.extend(partner_df[col].dropna().tolist())
            
            if kids_responses:
                happy_responses = [r for r in kids_responses if 'full and happy' in str(r).lower()]
                metrics['kids_happy_rate'] = len(happy_responses) / len(kids_responses)
                metrics['kids_happy_n'] = len(kids_responses)
        
        # Portions adequate rate
        if portions_col:
            portion_values = partner_df[portions_col].dropna()
            if len(portion_values) > 0:
                adequate = portion_values.isin(['Strongly agree', 'Agree']).sum()
                metrics['portions_adequate_rate'] = adequate / len(portion_values)
                metrics['portions_n'] = len(portion_values)
        
        # Reorder intent rate
        if reorder_col:
            reorder_values = partner_df[reorder_col].dropna()
            if len(reorder_values) > 0:
                would_reorder = reorder_values.isin(['Strongly agree', 'Agree']).sum()
                metrics['reorder_rate'] = would_reorder / len(reorder_values)
                metrics['reorder_n'] = len(reorder_values)
        
        # Overall satisfaction rate
        if overall_col:
            overall_values = partner_df[overall_col].dropna()
            if len(overall_values) > 0:
                satisfied = overall_values.isin(['Very Satisfied', 'Satisfied']).sum()
                metrics['overall_satisfaction_rate'] = satisfied / len(overall_values)
                metrics['overall_n'] = len(overall_values)
        
        # Family order percentage
        if who_col:
            who_values = partner_df[who_col].dropna()
            if len(who_values) > 0:
                family = who_values.str.contains('family', case=False, na=False).sum()
                metrics['family_order_pct'] = family / len(who_values)
        
        partner_metrics.append(metrics)
    
    partner_df = pd.DataFrame(partner_metrics)
    
    # Sort by sample size
    partner_df = partner_df.sort_values('n', ascending=False)
    
    logger.info(f"Extracted metrics for {len(partner_df)} partners")
    
    return partner_df


def extract_dish_performance():
    """
    Extract dish-level performance metrics by normalizing dish descriptions.
    """
    logger.info("Extracting dish performance metrics...")
    
    survey_path = SOURCE_DIR / "surveys" / "POST_ORDER_SURVEY-CONSOLIDATED.csv"
    if not survey_path.exists():
        logger.error(f"Survey file not found: {survey_path}")
        return pd.DataFrame()
    
    df = pd.read_csv(survey_path)
    
    # Find dish column
    dish_col = None
    for col in df.columns:
        if 'dish' in col.lower() and 'order' in col.lower():
            dish_col = col
            break
    
    if not dish_col:
        logger.error("Could not find dish column")
        return pd.DataFrame()
    
    # Normalize dish types
    df['dish_type'] = df[dish_col].apply(normalize_dish_type)
    
    # Find metric columns (same as partner extraction)
    adult_sat_col = None
    for col in df.columns:
        if 'how did you feel about the meal' in col.lower():
            adult_sat_col = col
            break
    
    kids_cols = [col for col in df.columns if 'how did your child' in col.lower() and 'react' in col.lower()]
    
    portions_col = None
    for col in df.columns:
        if 'enough food for everyone' in col.lower():
            portions_col = col
            break
    
    reorder_col = None
    for col in df.columns:
        if 'order the same dish again' in col.lower():
            reorder_col = col
            break
    
    # Calculate metrics by dish type
    dish_metrics = []
    
    for dish_type in df['dish_type'].unique():
        if dish_type in ['Unknown', 'Other']:
            continue
            
        dish_df = df[df['dish_type'] == dish_type]
        n = len(dish_df)
        
        if n < 3:  # Lower threshold for dishes
            continue
        
        metrics = {
            'dish_type': dish_type,
            'n': n
        }
        
        # Adult satisfaction
        if adult_sat_col:
            sat_values = dish_df[adult_sat_col].dropna()
            if len(sat_values) > 0:
                positive = sat_values.isin(['Loved it', 'Liked it']).sum()
                metrics['adult_satisfaction_rate'] = positive / len(sat_values)
                metrics['adult_satisfaction_n'] = len(sat_values)
        
        # Kids happy rate
        if kids_cols:
            kids_responses = []
            for col in kids_cols:
                kids_responses.extend(dish_df[col].dropna().tolist())
            
            if kids_responses:
                happy_responses = [r for r in kids_responses if 'full and happy' in str(r).lower()]
                metrics['kids_happy_rate'] = len(happy_responses) / len(kids_responses)
                metrics['kids_happy_n'] = len(kids_responses)
        
        # Portions
        if portions_col:
            portion_values = dish_df[portions_col].dropna()
            if len(portion_values) > 0:
                adequate = portion_values.isin(['Strongly agree', 'Agree']).sum()
                metrics['portions_adequate_rate'] = adequate / len(portion_values)
                metrics['portions_n'] = len(portion_values)
        
        # Reorder
        if reorder_col:
            reorder_values = dish_df[reorder_col].dropna()
            if len(reorder_values) > 0:
                would_reorder = reorder_values.isin(['Strongly agree', 'Agree']).sum()
                metrics['reorder_rate'] = would_reorder / len(reorder_values)
                metrics['reorder_n'] = len(reorder_values)
        
        dish_metrics.append(metrics)
    
    dish_df = pd.DataFrame(dish_metrics)
    dish_df = dish_df.sort_values('n', ascending=False)
    
    logger.info(f"Extracted metrics for {len(dish_df)} dish types")
    
    return dish_df


def extract_cuisine_performance():
    """
    Extract cuisine-level performance from orders and ratings.
    """
    logger.info("Extracting cuisine performance metrics...")
    
    orders_path = SOURCE_DIR / "snowflake" / "ALL_DINNEROO_ORDERS.csv"
    ratings_path = SOURCE_DIR / "snowflake" / "DINNEROO_RATINGS.csv"
    
    if not orders_path.exists():
        logger.error(f"Orders file not found: {orders_path}")
        return pd.DataFrame()
    
    orders_df = pd.read_csv(orders_path)
    logger.info(f"Loaded {len(orders_df)} orders")
    
    # Find cuisine column
    cuisine_col = None
    for col in orders_df.columns:
        if 'cuisine' in col.lower():
            cuisine_col = col
            break
    
    if not cuisine_col:
        logger.error("Could not find cuisine column")
        return pd.DataFrame()
    
    # Calculate order metrics by cuisine
    cuisine_metrics = orders_df.groupby(cuisine_col).agg({
        'ORDER_ID': 'count',
        'CUSTOMER_ID': 'nunique'
    }).reset_index()
    cuisine_metrics.columns = [cuisine_col, 'order_count', 'unique_customers']
    
    # Calculate repeat rate by cuisine
    customer_orders = orders_df.groupby([cuisine_col, 'CUSTOMER_ID']).size().reset_index(name='orders_per_customer')
    repeat_customers = customer_orders[customer_orders['orders_per_customer'] > 1].groupby(cuisine_col)['CUSTOMER_ID'].count()
    total_customers = customer_orders.groupby(cuisine_col)['CUSTOMER_ID'].count()
    repeat_rate = (repeat_customers / total_customers).reset_index()
    repeat_rate.columns = [cuisine_col, 'repeat_rate']
    
    cuisine_metrics = cuisine_metrics.merge(repeat_rate, on=cuisine_col, how='left')
    
    # Add ratings if available
    if ratings_path.exists():
        ratings_df = pd.read_csv(ratings_path)
        
        # Join with orders to get cuisine
        if 'ORDER_ID' in ratings_df.columns and 'ORDER_ID' in orders_df.columns:
            ratings_with_cuisine = ratings_df.merge(
                orders_df[[cuisine_col, 'ORDER_ID']].drop_duplicates(),
                on='ORDER_ID',
                how='left'
            )
            
            if 'RATING_STARS' in ratings_with_cuisine.columns:
                avg_rating = ratings_with_cuisine.groupby(cuisine_col)['RATING_STARS'].agg(['mean', 'count']).reset_index()
                avg_rating.columns = [cuisine_col, 'avg_rating', 'rating_count']
                cuisine_metrics = cuisine_metrics.merge(avg_rating, on=cuisine_col, how='left')
    
    cuisine_metrics = cuisine_metrics.sort_values('order_count', ascending=False)
    
    logger.info(f"Extracted metrics for {len(cuisine_metrics)} cuisines")
    
    return cuisine_metrics


def main():
    """Main function to extract all performance metrics."""
    logger.info("=" * 60)
    logger.info("EXTRACTING PERFORMANCE METRICS")
    logger.info("=" * 60)
    
    # Ensure output directory exists
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Extract partner performance
    partner_df = extract_partner_performance()
    if len(partner_df) > 0:
        output_path = ANALYSIS_DIR / "partner_performance.csv"
        partner_df.to_csv(output_path, index=False)
        logger.info(f"Saved partner performance to: {output_path}")
        
        # Show top partners
        logger.info("\nTop 10 partners by sample size:")
        cols_to_show = ['partner', 'n', 'adult_satisfaction_rate', 'kids_happy_rate', 'portions_adequate_rate']
        cols_available = [c for c in cols_to_show if c in partner_df.columns]
        logger.info(partner_df[cols_available].head(10).to_string())
    
    # Extract dish performance
    dish_df = extract_dish_performance()
    if len(dish_df) > 0:
        output_path = ANALYSIS_DIR / "dish_performance.csv"
        dish_df.to_csv(output_path, index=False)
        logger.info(f"\nSaved dish performance to: {output_path}")
        
        # Show top dishes
        logger.info("\nTop dish types by sample size:")
        cols_to_show = ['dish_type', 'n', 'adult_satisfaction_rate', 'kids_happy_rate']
        cols_available = [c for c in cols_to_show if c in dish_df.columns]
        logger.info(dish_df[cols_available].head(15).to_string())
    
    # Extract cuisine performance
    cuisine_df = extract_cuisine_performance()
    if len(cuisine_df) > 0:
        output_path = ANALYSIS_DIR / "cuisine_performance.csv"
        cuisine_df.to_csv(output_path, index=False)
        logger.info(f"\nSaved cuisine performance to: {output_path}")
        
        # Show top cuisines
        logger.info("\nTop cuisines by order count:")
        logger.info(cuisine_df.head(10).to_string())
    
    logger.info("\n" + "=" * 60)
    logger.info("EXTRACTION COMPLETE")
    logger.info("=" * 60)
    
    return {
        'partner': partner_df,
        'dish': dish_df,
        'cuisine': cuisine_df
    }


if __name__ == "__main__":
    main()



