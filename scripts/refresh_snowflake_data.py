#!/usr/bin/env python3
"""
Refresh Snowflake Data Script

Pulls fresh data from Snowflake using browser SSO authentication
and saves to DATA/1_SOURCE/snowflake/
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from integrations.snowflake_connector import SnowflakeConnector
import pandas as pd

# Output directory
OUTPUT_DIR = project_root / "DATA" / "1_SOURCE" / "snowflake"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    print("=" * 60)
    print("SNOWFLAKE DATA REFRESH")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    # Initialize connector with browser SSO
    print("Initializing Snowflake connector (browser SSO)...")
    print("A browser window will open for authentication.")
    print()
    
    connector = SnowflakeConnector(auth_method='browser')
    
    # Test connection first
    print("Testing connection...")
    if not connector.test_connection():
        print("ERROR: Connection test failed!")
        sys.exit(1)
    print()
    
    # 1. Pull all Dinneroo orders
    print("-" * 40)
    print("1. Pulling ALL_DINNEROO_ORDERS...")
    orders = connector.get_all_dinneroo_orders()
    orders_path = OUTPUT_DIR / "ALL_DINNEROO_ORDERS.csv"
    orders.to_csv(orders_path, index=False)
    print(f"   Saved {len(orders):,} orders to {orders_path.name}")
    print(f"   Date range: {orders['ORDER_TIMESTAMP'].min()} to {orders['ORDER_TIMESTAMP'].max()}")
    print()
    
    # 2. Pull customer metrics
    print("-" * 40)
    print("2. Pulling ALL_DINNEROO_CUSTOMERS...")
    customers = connector.get_customer_metrics()
    customers_path = OUTPUT_DIR / "ALL_DINNEROO_CUSTOMERS.csv"
    customers.to_csv(customers_path, index=False)
    print(f"   Saved {len(customers):,} customers to {customers_path.name}")
    print()
    
    # 3. Pull ratings (from orders table - ratings may be embedded)
    print("-" * 40)
    print("3. Pulling DINNEROO_RATINGS...")
    # Try to get ratings from a different source - check if there's rating data in orders
    ratings_query = """
    SELECT 
        o.ID AS ORDER_ID,
        o.USER_ID AS CUSTOMER_ID,
        u.EMAIL AS CUSTOMER_EMAIL,
        o.RESTAURANT_NAME AS PARTNER_NAME,
        o.MENU_CATEGORY AS CUISINE,
        o.ZONE_NAME,
        o.CREATED_AT AS ORDER_TIMESTAMP,
        o.ORDER_RATING AS RATING_STARS,
        o.ORDER_RATING_COMMENT AS RATING_COMMENT
    FROM production.denormalised.orders o
    LEFT JOIN production.orderweb.users u ON o.USER_ID = u.ID
    WHERE o.IS_FAMILY_TIME_ORDER = TRUE
      AND o.STATUS = 'DELIVERED'
      AND o.ORDER_RATING IS NOT NULL
    ORDER BY o.CREATED_AT DESC
    """
    try:
        ratings = connector.execute_query(ratings_query)
        ratings_path = OUTPUT_DIR / "DINNEROO_RATINGS.csv"
        ratings.to_csv(ratings_path, index=False)
        print(f"   Saved {len(ratings):,} ratings to {ratings_path.name}")
    except Exception as e:
        print(f"   WARNING: Could not pull ratings - {str(e)[:100]}")
        print("   Skipping ratings pull...")
    print()
    
    # 4. Pull zone performance
    print("-" * 40)
    print("4. Pulling zone performance...")
    zones = connector.get_zone_performance()
    zones_path = OUTPUT_DIR / "DINNEROO_PARTNER_CATALOG_BY_ZONE.csv"
    zones.to_csv(zones_path, index=False)
    print(f"   Saved {len(zones):,} zones to {zones_path.name}")
    print()
    
    # 5. Pull partner performance
    print("-" * 40)
    print("5. Pulling partner performance...")
    partners = connector.get_partner_performance()
    partners_path = OUTPUT_DIR / "DINNEROO_PARTNER_PERFORMANCE.csv"
    partners.to_csv(partners_path, index=False)
    print(f"   Saved {len(partners):,} partner-zone combinations to {partners_path.name}")
    print()
    
    # 6. Pull menu catalog (custom query)
    print("-" * 40)
    print("6. Pulling DINNEROO_MENU_CATALOG...")
    menu_query = """
    SELECT DISTINCT
        o.RESTAURANT_NAME AS PARTNER_NAME,
        o.RESTAURANT_ID AS PARTNER_ID,
        o.MENU_CATEGORY AS CUISINE,
        o.ZONE_NAME,
        mi.value::STRING AS MENU_ITEM
    FROM production.denormalised.orders o,
    LATERAL FLATTEN(input => SPLIT(o.MENU_ITEM_LIST, ',')) mi
    WHERE o.IS_FAMILY_TIME_ORDER = TRUE
      AND o.STATUS = 'DELIVERED'
      AND o.MENU_ITEM_LIST IS NOT NULL
    ORDER BY o.RESTAURANT_NAME, mi.value::STRING
    """
    menu = connector.execute_query(menu_query)
    menu_path = OUTPUT_DIR / "DINNEROO_MENU_CATALOG.csv"
    menu.to_csv(menu_path, index=False)
    print(f"   Saved {len(menu):,} menu items to {menu_path.name}")
    print()
    
    # 7. Pull non-Dinneroo orders from Dinneroo customers (for cannibalization analysis)
    print("-" * 40)
    print("7. Pulling FULL_ORDER_HISTORY (non-Dinneroo orders from Dinneroo customers)...")
    non_dinneroo_query = """
    WITH dinneroo_customers AS (
        SELECT DISTINCT USER_ID
        FROM production.denormalised.orders
        WHERE IS_FAMILY_TIME_ORDER = TRUE
          AND STATUS = 'DELIVERED'
    )
    SELECT 
        o.ID AS ORDER_ID,
        o.USER_ID AS CUSTOMER_ID,
        o.RESTAURANT_NAME AS PARTNER_NAME,
        o.MENU_CATEGORY AS CUISINE,
        o.CREATED_AT AS ORDER_TIMESTAMP,
        DAYOFWEEK(o.CREATED_AT) AS DAY_OF_WEEK,
        o.TOTAL_VALUE_EXCL_TIP_AND_DONATIONS AS ORDER_VALUE,
        o.IS_FAMILY_TIME_ORDER AS IS_DINNEROO,
        o.DELIVEROO_PLUS_ORDER AS IS_PLUS,
        o.ZONE_NAME
    FROM production.denormalised.orders o
    INNER JOIN dinneroo_customers dc ON o.USER_ID = dc.USER_ID
    WHERE o.STATUS = 'DELIVERED'
      AND o.CREATED_AT >= DATEADD('day', -90, CURRENT_DATE())
    ORDER BY o.CREATED_AT DESC
    """
    full_history = connector.execute_query(non_dinneroo_query)
    full_history_path = OUTPUT_DIR / "FULL_ORDER_HISTORY.csv"
    full_history.to_csv(full_history_path, index=False)
    print(f"   Saved {len(full_history):,} orders to {full_history_path.name}")
    print()
    
    # Close connection
    connector.disconnect()
    
    # Summary
    print("=" * 60)
    print("REFRESH COMPLETE")
    print("=" * 60)
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("Files created:")
    for f in OUTPUT_DIR.glob("*.csv"):
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"  - {f.name} ({size_mb:.1f} MB)")
    print()
    
    # Zone summary for verification
    print("-" * 40)
    print("ZONE SUMMARY (for FTT zone verification):")
    zone_partners = partners.groupby('ZONE_NAME')['PARTNER_NAME'].nunique().reset_index()
    zone_partners.columns = ['ZONE_NAME', 'PARTNER_COUNT']
    
    zones_3plus = zone_partners[zone_partners['PARTNER_COUNT'] >= 3]
    zones_5plus = zone_partners[zone_partners['PARTNER_COUNT'] >= 5]
    
    print(f"  Total zones in data: {len(zone_partners)}")
    print(f"  Zones with 3+ partners: {len(zones_3plus)}")
    print(f"  Zones with 5+ partners (MVP threshold): {len(zones_5plus)}")
    print()
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

