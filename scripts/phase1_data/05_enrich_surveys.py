"""
Script: 05_enrich_surveys.py
Phase: 1 - Data Preparation
Purpose: Enrich survey data by joining with Snowflake order/customer data

This script:
1. Loads consolidated survey files
2. Joins with Snowflake data (orders, ratings, customers) using email-based linkage
3. Adds derived metrics (Is_Family, Is_Satisfied, etc.)
4. Outputs enriched files for analysis

Linkage Strategy (per 02_DATA_SOURCES.md):
1. Best: Match on ORDER_ID (highest confidence) - if available in survey
2. Fallback: Match on email + date ±1 day (medium confidence)
3. Last resort: Match on email only (lowest confidence)
4. Final fallback: Match on brand name + date (using SF_GLOBAL_BRAND)

Usage:
    python scripts/phase1_data/05_enrich_surveys.py --all
    python scripts/phase1_data/05_enrich_surveys.py --post-order
    python scripts/phase1_data/05_enrich_surveys.py --dropoff
"""

import argparse
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
SOURCE_DIR = PROJECT_ROOT / "DATA" / "1_SOURCE"
SURVEYS_DIR = SOURCE_DIR / "surveys"
SNOWFLAKE_DIR = SOURCE_DIR / "snowflake"
ENRICHED_DIR = PROJECT_ROOT / "DATA" / "2_ENRICHED"


def load_snowflake_data():
    """Load all Snowflake data needed for enrichment."""
    logger.info("Loading Snowflake data...")
    
    data = {}
    
    # Load orders
    orders_path = SNOWFLAKE_DIR / "ALL_DINNEROO_ORDERS.csv"
    if orders_path.exists():
        data['orders'] = pd.read_csv(orders_path)
        logger.info(f"  Orders: {len(data['orders'])} rows")
        
        # Check if CUSTOMER_EMAIL column exists
        if 'CUSTOMER_EMAIL' in data['orders'].columns:
            email_count = data['orders']['CUSTOMER_EMAIL'].notna().sum()
            logger.info(f"  Orders with email: {email_count}")
        else:
            logger.warning("  WARNING: CUSTOMER_EMAIL column not found in orders!")
    else:
        logger.warning(f"  Orders file not found: {orders_path}")
        data['orders'] = pd.DataFrame()
    
    # Load ratings
    ratings_path = SNOWFLAKE_DIR / "DINNEROO_RATINGS.csv"
    if ratings_path.exists():
        data['ratings'] = pd.read_csv(ratings_path)
        logger.info(f"  Ratings: {len(data['ratings'])} rows")
    else:
        logger.warning(f"  Ratings file not found: {ratings_path}")
        data['ratings'] = pd.DataFrame()
    
    # Load full order history (for customer linkage)
    history_path = SNOWFLAKE_DIR / "FULL_ORDER_HISTORY.csv"
    if history_path.exists():
        data['history'] = pd.read_csv(history_path)
        logger.info(f"  Full history: {len(data['history'])} rows")
    else:
        logger.warning(f"  Full history file not found: {history_path}")
        data['history'] = pd.DataFrame()
    
    # Load customers
    customers_path = SNOWFLAKE_DIR / "ALL_DINNEROO_CUSTOMERS.csv"
    if customers_path.exists():
        data['customers'] = pd.read_csv(customers_path)
        logger.info(f"  Customers: {len(data['customers'])} rows")
    else:
        logger.warning(f"  Customers file not found: {customers_path}")
        data['customers'] = pd.DataFrame()
    
    return data


def find_email_column(df):
    """Find the email column in survey data."""
    email_patterns = [
        'Please provide your Deliveroo email',
        'email address',
        'CUSTOMER_EMAIL'
    ]
    
    for col in df.columns:
        for pattern in email_patterns:
            if pattern.lower() in col.lower():
                return col
    
    return None


def normalize_email(email):
    """Normalize email for matching."""
    if pd.isna(email) or not isinstance(email, str):
        return None
    return email.lower().strip()


def normalize_brand_name(name):
    """
    Normalize restaurant/brand name for matching.
    Extracts the brand from full partner names like "Pho - Bristol" -> "pho"
    """
    if pd.isna(name) or not isinstance(name, str):
        return None
    
    # Convert to lowercase
    name = name.lower().strip()
    
    # Extract brand name (before any " - " separator)
    if ' - ' in name:
        name = name.split(' - ')[0].strip()
    
    # Remove common suffixes and prefixes
    prefixes_to_remove = ['the ', 'a ']
    for prefix in prefixes_to_remove:
        if name.startswith(prefix):
            name = name[len(prefix):]
    
    return name


def build_email_to_orders_index(orders_df):
    """
    Build an index of email -> list of orders for fast lookup.
    Returns dict: {normalized_email: [order_rows]}
    """
    if 'CUSTOMER_EMAIL' not in orders_df.columns:
        logger.warning("Cannot build email index: CUSTOMER_EMAIL column not found")
        return {}
    
    email_index = {}
    
    for idx, row in orders_df.iterrows():
        email = normalize_email(row.get('CUSTOMER_EMAIL'))
        if email:
            if email not in email_index:
                email_index[email] = []
            email_index[email].append(row)
    
    logger.info(f"Built email index with {len(email_index)} unique emails")
    return email_index


def build_brand_date_index(orders_df):
    """
    Build an index of (brand, date) -> list of orders for fallback matching.
    """
    brand_date_index = {}
    
    for idx, row in orders_df.iterrows():
        brand = normalize_brand_name(row.get('PARTNER_NAME'))
        order_date = pd.to_datetime(row.get('ORDER_TIMESTAMP'), errors='coerce')
        
        if brand and pd.notna(order_date):
            date_key = order_date.date()
            key = (brand, date_key)
            if key not in brand_date_index:
                brand_date_index[key] = []
            brand_date_index[key].append(row)
    
    logger.info(f"Built brand-date index with {len(brand_date_index)} unique combinations")
    return brand_date_index


def find_best_order_match(survey_email, survey_date, survey_brand, 
                          email_index, brand_date_index, date_tolerance_days=1):
    """
    Find the best matching order for a survey response.
    
    Returns: (order_row, linkage_method) or (None, 'unmatched')
    """
    survey_email_norm = normalize_email(survey_email)
    survey_brand_norm = normalize_brand_name(survey_brand)
    
    # Strategy 1: Email + Date match (highest confidence)
    if survey_email_norm and survey_email_norm in email_index:
        customer_orders = email_index[survey_email_norm]
        
        if survey_date:
            survey_date_ts = pd.Timestamp(survey_date)
            
            # Find orders within date_tolerance_days BEFORE the survey
            matching_orders = []
            for order in customer_orders:
                order_date = pd.to_datetime(order.get('ORDER_TIMESTAMP'), errors='coerce')
                if pd.notna(order_date):
                    # Order should be before survey and within tolerance
                    days_diff = (survey_date_ts - order_date).days
                    if 0 <= days_diff <= 7:  # Order was 0-7 days before survey
                        matching_orders.append((order, days_diff))
            
            if matching_orders:
                # Sort by date diff (prefer most recent order before survey)
                matching_orders.sort(key=lambda x: x[1])
                best_order = matching_orders[0][0]
                
                # If brand also matches, even higher confidence
                order_brand = normalize_brand_name(best_order.get('PARTNER_NAME'))
                if survey_brand_norm and order_brand == survey_brand_norm:
                    return best_order, 'email_brand_date'
                else:
                    return best_order, 'email_date'
        
        # Strategy 2: Email only (no date match, lower confidence)
        # Return most recent order for this customer
        if customer_orders:
            sorted_orders = sorted(
                customer_orders,
                key=lambda x: pd.to_datetime(x.get('ORDER_TIMESTAMP', '1900-01-01'), errors='coerce'),
                reverse=True
            )
            return sorted_orders[0], 'email_only'
    
    # Strategy 3: Brand + Date match (fallback when no email match)
    if survey_brand_norm and survey_date:
        survey_date_ts = pd.Timestamp(survey_date)
        
        # Check dates within tolerance
        for days_offset in range(8):  # 0-7 days before survey
            check_date = (survey_date_ts - pd.Timedelta(days=days_offset)).date()
            key = (survey_brand_norm, check_date)
            
            if key in brand_date_index:
                orders = brand_date_index[key]
                # Return the first matching order (could be random customer)
                return orders[0], 'brand_date'
    
    return None, 'unmatched'


def enrich_post_order_survey(snowflake_data):
    """
    Enrich post-order survey with Snowflake order data.
    
    Linkage strategy (in order of preference):
    1. email + brand + date (highest confidence)
    2. email + date (high confidence)
    3. email only (medium confidence)
    4. brand + date (low confidence - may match wrong customer)
    """
    logger.info("=" * 60)
    logger.info("ENRICHING POST-ORDER SURVEY")
    logger.info("=" * 60)
    
    # Load survey
    survey_path = SURVEYS_DIR / "POST_ORDER_SURVEY-CONSOLIDATED.csv"
    if not survey_path.exists():
        logger.error(f"Survey file not found: {survey_path}")
        return None
    
    survey_df = pd.read_csv(survey_path)
    logger.info(f"Loaded survey: {len(survey_df)} responses")
    
    # Find key columns
    email_col = find_email_column(survey_df)
    logger.info(f"Email column: {email_col}")
    
    # Find date column
    date_col = None
    for col in survey_df.columns:
        if col in ['Date Submitted', 'Time Started', 'SURVEY_DATE']:
            date_col = col
            break
    logger.info(f"Date column: {date_col}")
    
    # Find restaurant column
    restaurant_col = None
    for col in survey_df.columns:
        if 'Which restaurant did you order from?' in col:
            restaurant_col = col
            break
    logger.info(f"Restaurant column: {restaurant_col}")
    
    # Prepare survey data
    if email_col:
        survey_df['_survey_email'] = survey_df[email_col].apply(normalize_email)
        emails_present = survey_df['_survey_email'].notna().sum()
        logger.info(f"Survey responses with email: {emails_present} / {len(survey_df)}")
    else:
        survey_df['_survey_email'] = None
    
    if date_col:
        survey_df['_survey_date'] = pd.to_datetime(survey_df[date_col], errors='coerce').dt.date
    else:
        survey_df['_survey_date'] = None
    
    if restaurant_col:
        survey_df['_survey_brand'] = survey_df[restaurant_col].apply(normalize_brand_name)
    else:
        survey_df['_survey_brand'] = None
    
    # Prepare orders data
    orders_df = snowflake_data['orders'].copy()
    if len(orders_df) == 0:
        logger.error("No orders data available!")
        return None
    
    # Normalize email in orders
    if 'CUSTOMER_EMAIL' in orders_df.columns:
        orders_df['_order_email'] = orders_df['CUSTOMER_EMAIL'].apply(normalize_email)
        orders_with_email = orders_df['_order_email'].notna().sum()
        logger.info(f"Orders with email: {orders_with_email} / {len(orders_df)}")
    else:
        orders_df['_order_email'] = None
        logger.warning("No CUSTOMER_EMAIL in orders - email linkage not possible!")
    
    # Build indexes for fast lookup
    email_index = build_email_to_orders_index(orders_df)
    brand_date_index = build_brand_date_index(orders_df)
    
    # Merge ratings into orders
    ratings_df = snowflake_data['ratings'].copy()
    if len(ratings_df) > 0 and 'ORDER_ID' in orders_df.columns and 'ORDER_ID' in ratings_df.columns:
        # Get rating columns
        rating_cols = ['ORDER_ID', 'RATING_STARS', 'RATING_COMMENT', 'RATING_TAGS',
                      'RATING_ISSUE_TIME', 'RATING_ISSUE_FOOD', 'RATING_ISSUE_PACKAGING', 'RATING_ISSUE_DRIVER']
        rating_cols = [c for c in rating_cols if c in ratings_df.columns]
        
        orders_df = orders_df.merge(
            ratings_df[rating_cols],
            on='ORDER_ID',
            how='left',
            suffixes=('', '_rating')
        )
        logger.info(f"Merged ratings into orders")
    
    # Rebuild indexes after merge
    email_index = build_email_to_orders_index(orders_df)
    brand_date_index = build_brand_date_index(orders_df)
    
    # Match each survey response
    enriched_rows = []
    linkage_stats = {
        'email_brand_date': 0,
        'email_date': 0,
        'email_only': 0,
        'brand_date': 0,
        'unmatched': 0
    }
    
    logger.info("Matching survey responses to orders...")
    
    for idx, survey_row in survey_df.iterrows():
        if idx % 200 == 0:
            logger.info(f"  Processing {idx}/{len(survey_df)}...")
        
        # Find best matching order
        matched_order, linkage_method = find_best_order_match(
            survey_email=survey_row.get('_survey_email'),
            survey_date=survey_row.get('_survey_date'),
            survey_brand=survey_row.get('_survey_brand'),
            email_index=email_index,
            brand_date_index=brand_date_index
        )
        
        linkage_stats[linkage_method] += 1
        
        # Build enriched row
        enriched = survey_row.to_dict()
        
        # Remove temp columns
        for temp_col in ['_survey_email', '_survey_date', '_survey_brand']:
            enriched.pop(temp_col, None)
        
        if matched_order is not None:
            enriched['ORDER_ID'] = matched_order.get('ORDER_ID')
            enriched['LINKAGE_METHOD'] = linkage_method
            enriched['USER_ID'] = matched_order.get('CUSTOMER_ID')
            enriched['USER_EMAIL'] = matched_order.get('CUSTOMER_EMAIL')
            enriched['ORDER_DATE'] = matched_order.get('ORDER_TIMESTAMP')
            enriched['ORDER_TIMESTAMP'] = matched_order.get('ORDER_TIMESTAMP')
            enriched['PARTNER_NAME'] = matched_order.get('PARTNER_NAME')
            enriched['SF_GLOBAL_BRAND'] = matched_order.get('SF_GLOBAL_BRAND') if 'SF_GLOBAL_BRAND' in matched_order.index else None
            enriched['ORDER_VALUE'] = matched_order.get('ORDER_VALUE')
            enriched['IS_DINNEROO'] = True
            enriched['STATUS'] = 'completed'
            enriched['ZONE_NAME'] = matched_order.get('ZONE_NAME')
            enriched['MENU_ITEM_LIST'] = matched_order.get('MENU_ITEM_LIST')
            enriched['RATING_STARS'] = matched_order.get('RATING_STARS')
            enriched['RATING_COMMENT'] = matched_order.get('RATING_COMMENT')
            enriched['RATING_TAGS'] = matched_order.get('RATING_TAGS')
            enriched['RATING_ISSUE_TIME'] = matched_order.get('RATING_ISSUE_TIME')
            enriched['RATING_ISSUE_FOOD'] = matched_order.get('RATING_ISSUE_FOOD')
            enriched['RATING_ISSUE_PACKAGING'] = matched_order.get('RATING_ISSUE_PACKAGING')
            enriched['RATING_ISSUE_DRIVER'] = matched_order.get('RATING_ISSUE_DRIVER')
        else:
            enriched['ORDER_ID'] = None
            enriched['LINKAGE_METHOD'] = 'unmatched'
            enriched['USER_ID'] = None
            enriched['USER_EMAIL'] = survey_row.get('_survey_email')
            enriched['ORDER_DATE'] = None
            enriched['ORDER_TIMESTAMP'] = None
            enriched['PARTNER_NAME'] = survey_row.get(restaurant_col) if restaurant_col else None
            enriched['SF_GLOBAL_BRAND'] = None
            enriched['ORDER_VALUE'] = None
            enriched['IS_DINNEROO'] = True
            enriched['STATUS'] = 'unknown'
            enriched['ZONE_NAME'] = None
            enriched['MENU_ITEM_LIST'] = None
            enriched['RATING_STARS'] = None
            enriched['RATING_COMMENT'] = None
            enriched['RATING_TAGS'] = None
            enriched['RATING_ISSUE_TIME'] = None
            enriched['RATING_ISSUE_FOOD'] = None
            enriched['RATING_ISSUE_PACKAGING'] = None
            enriched['RATING_ISSUE_DRIVER'] = None
        
        enriched_rows.append(enriched)
    
    # Log linkage stats
    logger.info("\n" + "-" * 40)
    logger.info("LINKAGE RESULTS:")
    total_matched = sum(v for k, v in linkage_stats.items() if k != 'unmatched')
    logger.info(f"  Total matched: {total_matched} / {len(survey_df)} ({100*total_matched/len(survey_df):.1f}%)")
    for method, count in sorted(linkage_stats.items(), key=lambda x: -x[1]):
        pct = 100 * count / len(survey_df)
        logger.info(f"  - {method}: {count} ({pct:.1f}%)")
    logger.info("-" * 40)
    
    # Create enriched dataframe
    enriched_df = pd.DataFrame(enriched_rows)
    
    # Add derived metrics
    enriched_df = add_derived_metrics(enriched_df, date_col)
    
    # Save
    output_path = ENRICHED_DIR / "post_order_enriched_COMPLETE.csv"
    enriched_df.to_csv(output_path, index=False)
    logger.info(f"Saved enriched post-order survey: {output_path}")
    logger.info(f"Total rows: {len(enriched_df)}")
    
    return enriched_df


def enrich_dropoff_survey(snowflake_data):
    """
    Enrich dropoff survey with customer order history.
    
    These are people who browsed but didn't order Dinneroo, so we:
    1. Match on email to find their Deliveroo account
    2. Check if they have any Dinneroo orders (they shouldn't, but verify)
    3. Get their overall order history for context
    """
    logger.info("=" * 60)
    logger.info("ENRICHING DROPOFF SURVEY")
    logger.info("=" * 60)
    
    # Load survey
    survey_path = SURVEYS_DIR / "DROPOFF_SURVEY-CONSOLIDATED.csv"
    if not survey_path.exists():
        logger.error(f"Survey file not found: {survey_path}")
        return None
    
    survey_df = pd.read_csv(survey_path)
    logger.info(f"Loaded survey: {len(survey_df)} responses")
    
    # Find email column
    email_col = find_email_column(survey_df)
    logger.info(f"Email column: {email_col}")
    
    # Prepare survey data
    if email_col:
        survey_df['_survey_email'] = survey_df[email_col].apply(normalize_email)
        emails_present = survey_df['_survey_email'].notna().sum()
        logger.info(f"Survey responses with email: {emails_present} / {len(survey_df)}")
    else:
        survey_df['_survey_email'] = None
    
    # Load orders and build customer summary by email
    orders_df = snowflake_data.get('orders', pd.DataFrame())
    
    # Build email -> customer summary
    customer_by_email = {}
    
    if len(orders_df) > 0 and 'CUSTOMER_EMAIL' in orders_df.columns:
        orders_df['_order_email'] = orders_df['CUSTOMER_EMAIL'].apply(normalize_email)
        
        for email, group in orders_df.groupby('_order_email'):
            if email:
                customer_by_email[email] = {
                    'USER_ID': group['CUSTOMER_ID'].iloc[0] if 'CUSTOMER_ID' in group.columns else None,
                    'TOTAL_ORDERS': len(group),
                    'FIRST_ORDER_DATE': group['ORDER_TIMESTAMP'].min() if 'ORDER_TIMESTAMP' in group.columns else None,
                    'LAST_ORDER_DATE': group['ORDER_TIMESTAMP'].max() if 'ORDER_TIMESTAMP' in group.columns else None,
                    'UNIQUE_PARTNERS': group['PARTNER_NAME'].nunique() if 'PARTNER_NAME' in group.columns else 0,
                    'DINNEROO_ORDERS': len(group),  # All orders in this file are Dinneroo
                    'LAST_ORDER_ID': group.iloc[-1]['ORDER_ID'] if 'ORDER_ID' in group.columns else None,
                    'LAST_ORDER_TIMESTAMP': group['ORDER_TIMESTAMP'].max() if 'ORDER_TIMESTAMP' in group.columns else None,
                    'LAST_PARTNER': group.iloc[-1]['PARTNER_NAME'] if 'PARTNER_NAME' in group.columns else None,
                    'ZONE_NAME': group.iloc[-1]['ZONE_NAME'] if 'ZONE_NAME' in group.columns else None,
                    'PLUS_PLAN_TYPE': 'Plus' if group['DELIVEROO_PLUS_ORDER'].any() else None,
                }
        
        logger.info(f"Built customer summary for {len(customer_by_email)} unique emails")
    
    # Enrich each survey row
    enriched_rows = []
    matched_count = 0
    
    for idx, row in survey_df.iterrows():
        enriched = row.to_dict()
        survey_email = enriched.pop('_survey_email', None)
        
        # Try to find customer by email
        if survey_email and survey_email in customer_by_email:
            customer = customer_by_email[survey_email]
            matched_count += 1
            
            enriched['USER_ID'] = customer['USER_ID']
            enriched['TOTAL_ORDERS'] = customer['TOTAL_ORDERS']
            enriched['FIRST_ORDER_DATE'] = customer['FIRST_ORDER_DATE']
            enriched['LAST_ORDER_DATE'] = customer['LAST_ORDER_DATE']
            enriched['UNIQUE_PARTNERS'] = customer['UNIQUE_PARTNERS']
            enriched['DINNEROO_ORDERS'] = customer['DINNEROO_ORDERS']
            enriched['LAST_ORDER_ID'] = customer['LAST_ORDER_ID']
            enriched['LAST_ORDER_TIMESTAMP'] = customer['LAST_ORDER_TIMESTAMP']
            enriched['LAST_PARTNER'] = customer['LAST_PARTNER']
            enriched['ZONE_NAME'] = customer['ZONE_NAME']
            enriched['PLUS_PLAN_TYPE'] = customer['PLUS_PLAN_TYPE']
            enriched['ORDER_COUNT'] = customer['TOTAL_ORDERS']
        else:
            enriched['USER_ID'] = None
            enriched['TOTAL_ORDERS'] = None
            enriched['FIRST_ORDER_DATE'] = None
            enriched['LAST_ORDER_DATE'] = None
            enriched['UNIQUE_PARTNERS'] = None
            enriched['DINNEROO_ORDERS'] = None
            enriched['LAST_ORDER_ID'] = None
            enriched['LAST_ORDER_TIMESTAMP'] = None
            enriched['LAST_PARTNER'] = None
            enriched['ZONE_NAME'] = None
            enriched['PLUS_PLAN_TYPE'] = None
            enriched['ORDER_COUNT'] = None
        
        enriched_rows.append(enriched)
    
    logger.info(f"Matched {matched_count} / {len(survey_df)} dropoff respondents to Dinneroo orders")
    
    enriched_df = pd.DataFrame(enriched_rows)
    
    # Add derived metrics
    enriched_df = add_dropoff_derived_metrics(enriched_df)
    
    # Save
    output_path = ENRICHED_DIR / "DROPOFF_ENRICHED.csv"
    enriched_df.to_csv(output_path, index=False)
    logger.info(f"Saved enriched dropoff survey: {output_path}")
    logger.info(f"Total rows: {len(enriched_df)}")
    
    return enriched_df


def add_derived_metrics(df, date_col=None):
    """Add derived metrics to post-order survey."""
    logger.info("Adding derived metrics...")
    
    # Count children
    child_cols = [col for col in df.columns if 'How old are the children' in str(col)]
    if child_cols:
        df['NUM_CHILDREN_NUMERIC'] = df[child_cols].notna().sum(axis=1)
    else:
        df['NUM_CHILDREN_NUMERIC'] = 0
    
    # Is Family (has children or ordered for family)
    who_col = None
    for col in df.columns:
        if 'who did you order for' in col.lower():
            who_col = col
            break
    
    if who_col:
        df['Is_Family'] = (
            (df['NUM_CHILDREN_NUMERIC'] > 0) | 
            (df[who_col].str.contains('family', case=False, na=False))
        )
    else:
        df['Is_Family'] = df['NUM_CHILDREN_NUMERIC'] > 0
    
    # Is Satisfied
    sat_col = None
    for col in df.columns:
        if 'rate your family dinneroo experience' in col.lower():
            sat_col = col
            break
    
    if sat_col:
        df['Is_Satisfied'] = df[sat_col].isin(['Very Satisfied', 'Satisfied'])
    else:
        df['Is_Satisfied'] = None
    
    # Days to survey
    if date_col and date_col in df.columns and 'ORDER_TIMESTAMP' in df.columns:
        try:
            survey_dates = pd.to_datetime(df[date_col], errors='coerce')
            order_dates = pd.to_datetime(df['ORDER_TIMESTAMP'], errors='coerce')
            df['Days_To_Survey'] = (survey_dates - order_dates).dt.days
        except Exception as e:
            logger.warning(f"Could not calculate Days_To_Survey: {e}")
            df['Days_To_Survey'] = None
    else:
        df['Days_To_Survey'] = None
    
    # Strong Advocate (would reorder + satisfied)
    reorder_col = None
    for col in df.columns:
        if 'order the same dish again' in col.lower():
            reorder_col = col
            break
    
    if reorder_col and sat_col:
        df['Strong_Advocate'] = (
            df[reorder_col].isin(['Strongly agree', 'Agree']) &
            df['Is_Satisfied'].fillna(False)
        )
    else:
        df['Strong_Advocate'] = None
    
    return df


def add_dropoff_derived_metrics(df):
    """Add derived metrics to dropoff survey."""
    logger.info("Adding derived metrics for dropoff survey...")
    
    # Count children
    child_cols = [col for col in df.columns if 'How old are the children' in str(col)]
    if child_cols:
        df['NUM_CHILDREN_NUMERIC'] = df[child_cols].notna().sum(axis=1)
    else:
        df['NUM_CHILDREN_NUMERIC'] = 0
    
    # Is Family
    df['Is_Family'] = df['NUM_CHILDREN_NUMERIC'] > 0
    
    # Has order history
    df['Has_Order_History'] = df['TOTAL_ORDERS'].notna() & (df['TOTAL_ORDERS'] > 0)
    
    # Has Dinneroo orders
    df['Has_Dinneroo_Orders'] = df['DINNEROO_ORDERS'].notna() & (df['DINNEROO_ORDERS'] > 0)
    
    # Placed order (from dropoff survey - they explored but may not have ordered)
    df['Placed_Order'] = df['Has_Dinneroo_Orders']
    
    # Is Plus member
    df['Is_Plus_Member'] = df['PLUS_PLAN_TYPE'].notna()
    
    return df


def main():
    parser = argparse.ArgumentParser(description='Enrich survey data with Snowflake data')
    parser.add_argument('--all', action='store_true', help='Enrich all surveys')
    parser.add_argument('--post-order', action='store_true', help='Enrich post-order survey only')
    parser.add_argument('--dropoff', action='store_true', help='Enrich dropoff survey only')
    
    args = parser.parse_args()
    
    # Default to all if no specific survey selected
    if not any([args.all, args.post_order, args.dropoff]):
        args.all = True
    
    # Ensure output directory exists
    ENRICHED_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load Snowflake data once
    snowflake_data = load_snowflake_data()
    
    results = {}
    
    if args.all or args.post_order:
        results['post_order'] = enrich_post_order_survey(snowflake_data)
    
    if args.all or args.dropoff:
        results['dropoff'] = enrich_dropoff_survey(snowflake_data)
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("ENRICHMENT COMPLETE")
    logger.info("=" * 60)
    
    for survey, df in results.items():
        if df is not None:
            logger.info(f"{survey}: {len(df)} rows enriched")
            
            # Show linkage breakdown for post-order
            if survey == 'post_order' and 'LINKAGE_METHOD' in df.columns:
                logger.info("  Linkage breakdown:")
                for method, count in df['LINKAGE_METHOD'].value_counts().items():
                    pct = 100 * count / len(df)
                    logger.info(f"    - {method}: {count} ({pct:.1f}%)")
        else:
            logger.info(f"{survey}: FAILED")
    
    logger.info(f"\nOutput directory: {ENRICHED_DIR}")
    
    return results


if __name__ == "__main__":
    main()
