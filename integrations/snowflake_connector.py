"""
Snowflake Connector for Dinneroo Analysis

Supports multiple authentication methods for both interactive and automated use:
1. External Browser (SSO) - for interactive sessions
2. Key-Pair Authentication - for automated pipelines (recommended)
3. Password Authentication - for service accounts

Environment Variables:
    SNOWFLAKE_ACCOUNT: Snowflake account identifier
    SNOWFLAKE_USER: Username/email
    SNOWFLAKE_WAREHOUSE: Warehouse name
    SNOWFLAKE_DATABASE: Database name
    SNOWFLAKE_SCHEMA: Schema name
    SNOWFLAKE_AUTH_METHOD: 'browser', 'keypair', or 'password'
    SNOWFLAKE_PRIVATE_KEY_PATH: Path to private key file (for keypair auth)
    SNOWFLAKE_PRIVATE_KEY_PASSPHRASE: Passphrase for private key (optional)
    SNOWFLAKE_PASSWORD: Password (for password auth)
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, List, Any
from functools import lru_cache
from datetime import datetime

import pandas as pd

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SnowflakeConnector:
    """
    Manages Snowflake connections with support for multiple auth methods.
    
    Usage:
        # Interactive (browser SSO)
        connector = SnowflakeConnector(auth_method='browser')
        
        # Automated (key-pair)
        connector = SnowflakeConnector(auth_method='keypair')
        
        # Service account (password)
        connector = SnowflakeConnector(auth_method='password')
    """
    
    # Default configuration (can be overridden by env vars)
    DEFAULT_ACCOUNT = 'YW26239-DELIVEROO'
    DEFAULT_USER = 'francesca.mcgovern@deliveroo.co.uk'
    DEFAULT_WAREHOUSE = 'bi_development'
    DEFAULT_DATABASE = 'production'
    DEFAULT_SCHEMA = 'denormalised'
    
    def __init__(
        self,
        auth_method: Optional[str] = None,
        account: Optional[str] = None,
        user: Optional[str] = None,
        warehouse: Optional[str] = None,
        database: Optional[str] = None,
        schema: Optional[str] = None,
        private_key_path: Optional[str] = None,
        private_key_passphrase: Optional[str] = None,
        password: Optional[str] = None
    ):
        """
        Initialize Snowflake connector.
        
        Args:
            auth_method: 'browser', 'keypair', or 'password'. Defaults to env var or 'browser'
            account: Snowflake account. Defaults to env var or DEFAULT_ACCOUNT
            user: Username. Defaults to env var or DEFAULT_USER
            warehouse: Warehouse name. Defaults to env var or DEFAULT_WAREHOUSE
            database: Database name. Defaults to env var or DEFAULT_DATABASE
            schema: Schema name. Defaults to env var or DEFAULT_SCHEMA
            private_key_path: Path to private key (for keypair auth)
            private_key_passphrase: Passphrase for private key
            password: Password (for password auth)
        """
        # Load from environment or use defaults
        self.account = account or os.environ.get('SNOWFLAKE_ACCOUNT', self.DEFAULT_ACCOUNT)
        self.user = user or os.environ.get('SNOWFLAKE_USER', self.DEFAULT_USER)
        self.warehouse = warehouse or os.environ.get('SNOWFLAKE_WAREHOUSE', self.DEFAULT_WAREHOUSE)
        self.database = database or os.environ.get('SNOWFLAKE_DATABASE', self.DEFAULT_DATABASE)
        self.schema = schema or os.environ.get('SNOWFLAKE_SCHEMA', self.DEFAULT_SCHEMA)
        
        # Authentication configuration
        self.auth_method = auth_method or os.environ.get('SNOWFLAKE_AUTH_METHOD', 'browser')
        self.private_key_path = private_key_path or os.environ.get('SNOWFLAKE_PRIVATE_KEY_PATH')
        self.private_key_passphrase = private_key_passphrase or os.environ.get('SNOWFLAKE_PRIVATE_KEY_PASSPHRASE')
        self.password = password or os.environ.get('SNOWFLAKE_PASSWORD')
        
        self._connection = None
        self._cache: Dict[str, pd.DataFrame] = {}
        
        logger.info(f"SnowflakeConnector initialized with auth_method='{self.auth_method}'")
    
    def _get_private_key(self) -> bytes:
        """Load and parse private key for key-pair authentication."""
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives import serialization
        
        if not self.private_key_path:
            raise ValueError("private_key_path is required for keypair authentication")
        
        key_path = Path(self.private_key_path).expanduser()
        if not key_path.exists():
            raise FileNotFoundError(f"Private key not found: {key_path}")
        
        with open(key_path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=self.private_key_passphrase.encode() if self.private_key_passphrase else None,
                backend=default_backend()
            )
        
        # Serialize to DER format for Snowflake
        private_key_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        return private_key_bytes
    
    def connect(self):
        """
        Establish connection to Snowflake using configured auth method.
        
        Returns:
            snowflake.connector.connection.SnowflakeConnection
        """
        import snowflake.connector
        
        try:
            if self._connection is not None and not self._connection.is_closed():
                return self._connection
            
            logger.info(f"Connecting to Snowflake ({self.auth_method} auth)...")
            
            # Base connection parameters
            conn_params = {
                'account': self.account,
                'user': self.user,
                'warehouse': self.warehouse,
                'database': self.database,
                'schema': self.schema
            }
            
            # Add auth-specific parameters
            if self.auth_method == 'browser':
                conn_params['authenticator'] = 'externalbrowser'
                
            elif self.auth_method == 'keypair':
                conn_params['private_key'] = self._get_private_key()
                
            elif self.auth_method == 'password':
                if not self.password:
                    raise ValueError("password is required for password authentication")
                conn_params['password'] = self.password
                
            else:
                raise ValueError(f"Unknown auth_method: {self.auth_method}")
            
            self._connection = snowflake.connector.connect(**conn_params)
            logger.info("Connected to Snowflake successfully")
            
            return self._connection
            
        except Exception as e:
            logger.error(f"Failed to connect to Snowflake: {str(e)}")
            raise
    
    def disconnect(self):
        """Close Snowflake connection."""
        if self._connection and not self._connection.is_closed():
            self._connection.close()
            self._connection = None
            logger.info("Disconnected from Snowflake")
    
    def execute_query(
        self, 
        query: str, 
        params: Optional[Dict] = None, 
        use_cache: bool = False
    ) -> pd.DataFrame:
        """
        Execute a query and return results as pandas DataFrame.
        
        Args:
            query: SQL query string
            params: Optional parameters for parameterized queries
            use_cache: Whether to cache results
            
        Returns:
            pandas DataFrame with query results
        """
        from snowflake.connector import DictCursor
        
        # Check cache
        cache_key = f"{query}_{str(params)}"
        if use_cache and cache_key in self._cache:
            logger.info("Using cached results")
            return self._cache[cache_key].copy()
        
        try:
            conn = self.connect()
            cursor = conn.cursor(DictCursor)
            
            logger.info(f"Executing query ({len(query)} chars)...")
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            results = cursor.fetch_pandas_all()
            cursor.close()
            
            logger.info(f"Query returned {len(results)} rows, {len(results.columns)} columns")
            
            if use_cache:
                self._cache[cache_key] = results.copy()
            
            return results
            
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            logger.error(f"Query preview: {query[:200]}...")
            raise
    
    def clear_cache(self):
        """Clear query result cache."""
        self._cache = {}
        logger.info("Cache cleared")
    
    def test_connection(self) -> bool:
        """
        Test Snowflake connection.
        
        Returns:
            True if connection successful
        """
        try:
            query = "SELECT CURRENT_TIMESTAMP() AS NOW, CURRENT_USER() AS USER, CURRENT_DATABASE() AS DB"
            result = self.execute_query(query)
            logger.info(f"Connection test successful!")
            logger.info(f"  User: {result['USER'][0]}")
            logger.info(f"  Database: {result['DB'][0]}")
            logger.info(f"  Timestamp: {result['NOW'][0]}")
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False
    
    # =========================================================================
    # DINNEROO-SPECIFIC QUERY BUILDERS
    # =========================================================================
    
    def get_all_dinneroo_orders(
        self, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get all Dinneroo orders.
        
        Args:
            start_date: Optional start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)
            
        Returns:
            DataFrame with Dinneroo orders
        """
        query = """
        SELECT 
            o.ID AS ORDER_ID,
            o.USER_ID AS CUSTOMER_ID,
            u.EMAIL AS CUSTOMER_EMAIL,
            o.RESTAURANT_NAME AS PARTNER_NAME,
            o.RESTAURANT_ID AS PARTNER_ID,
            o.MENU_CATEGORY AS CUISINE,
            o.ORDER_SCHEDULE,
            o.SCHEDULED_FOR_HOURS,
            o.DELIVERY_SLOT_RANGE,
            o.CREATED_AT AS ORDER_TIMESTAMP,
            o.LOCAL_TIME_COMPLETION_TARGET AS SCHEDULED_TIME,
            o.DELIVERED_AT,
            o.TOTAL_VALUE_EXCL_TIP_AND_DONATIONS AS ORDER_VALUE,
            o.TOTAL_VALUE_AFTER_CREDITS_AND_VOUCHERS AS ORDER_VALUE_AFTER_DISCOUNTS,
            o.DELIVERY_FEE,
            o.SERVICE_FEE,
            o.TOTAL_ITEM_CNT AS BASKET_SIZE,
            o.UNIQUE_ITEM_CNT,
            o.MENU_ITEM_LIST,
            o.DELIVEROO_PLUS_ORDER,
            o.MARKETER_DISCOUNT_VALUE AS DISCOUNT_VALUE,
            o.VOUCHER_NAME,
            o.ZONE_NAME,
            o.CITY_NAME,
            o.FIRST_ORDER_DATE AS CUSTOMER_FIRST_ORDER_DATE,
            o.IS_EDITIONS,
            o.ESTIMATED_DISTANCE_DRIVER_RESTAURANT_M AS DISTANCE_METERS
        FROM production.denormalised.orders o
        LEFT JOIN production.orderweb.users u ON o.USER_ID = u.ID
        WHERE o.IS_FAMILY_TIME_ORDER = TRUE
          AND o.STATUS = 'DELIVERED'
        """
        
        if start_date:
            query += f"\n  AND o.CREATED_AT >= '{start_date}'"
        if end_date:
            query += f"\n  AND o.CREATED_AT <= '{end_date}'"
        
        query += "\nORDER BY o.CREATED_AT DESC"
        
        logger.info(f"Fetching Dinneroo orders{f' from {start_date}' if start_date else ''}{f' to {end_date}' if end_date else ''}...")
        return self.execute_query(query)
    
    def get_partner_performance(self) -> pd.DataFrame:
        """Get partner-level performance metrics."""
        query = """
        SELECT 
            o.RESTAURANT_NAME AS PARTNER_NAME,
            o.RESTAURANT_ID AS PARTNER_ID,
            o.MENU_CATEGORY AS CUISINE,
            o.ZONE_NAME,
            COUNT(DISTINCT o.ID) AS TOTAL_ORDERS,
            COUNT(DISTINCT o.USER_ID) AS UNIQUE_CUSTOMERS,
            AVG(o.TOTAL_VALUE_EXCL_TIP_AND_DONATIONS) AS AVG_ORDER_VALUE,
            AVG(o.TOTAL_ITEM_CNT) AS AVG_BASKET_SIZE,
            SUM(CASE WHEN o.ORDER_SCHEDULE = 'SCHEDULED' THEN 1 ELSE 0 END)::FLOAT / COUNT(*) AS SCHEDULING_RATE,
            SUM(CASE WHEN o.DELIVEROO_PLUS_ORDER = TRUE THEN 1 ELSE 0 END)::FLOAT / COUNT(*) AS PLUS_PENETRATION,
            MIN(o.CREATED_AT) AS FIRST_ORDER_DATE,
            MAX(o.CREATED_AT) AS LAST_ORDER_DATE
        FROM production.denormalised.orders o
        WHERE o.IS_FAMILY_TIME_ORDER = TRUE
          AND o.STATUS = 'DELIVERED'
        GROUP BY o.RESTAURANT_NAME, o.RESTAURANT_ID, o.MENU_CATEGORY, o.ZONE_NAME
        ORDER BY TOTAL_ORDERS DESC
        """
        
        logger.info("Fetching partner performance...")
        return self.execute_query(query, use_cache=True)
    
    def get_zone_performance(self) -> pd.DataFrame:
        """Get zone-level performance metrics."""
        query = """
        SELECT 
            o.ZONE_NAME,
            o.CITY_NAME,
            COUNT(DISTINCT o.ID) AS TOTAL_ORDERS,
            COUNT(DISTINCT o.RESTAURANT_ID) AS UNIQUE_PARTNERS,
            COUNT(DISTINCT o.USER_ID) AS UNIQUE_CUSTOMERS,
            AVG(o.TOTAL_VALUE_EXCL_TIP_AND_DONATIONS) AS AVG_ORDER_VALUE,
            SUM(CASE WHEN o.ORDER_SCHEDULE = 'SCHEDULED' THEN 1 ELSE 0 END)::FLOAT / COUNT(*) AS SCHEDULING_RATE,
            SUM(CASE WHEN o.DELIVEROO_PLUS_ORDER = TRUE THEN 1 ELSE 0 END)::FLOAT / COUNT(*) AS PLUS_PENETRATION
        FROM production.denormalised.orders o
        WHERE o.IS_FAMILY_TIME_ORDER = TRUE
          AND o.STATUS = 'DELIVERED'
        GROUP BY o.ZONE_NAME, o.CITY_NAME
        ORDER BY TOTAL_ORDERS DESC
        """
        
        logger.info("Fetching zone performance...")
        return self.execute_query(query, use_cache=True)
    
    def get_customer_metrics(self) -> pd.DataFrame:
        """Get customer-level metrics for segmentation."""
        query = """
        SELECT 
            o.USER_ID AS CUSTOMER_ID,
            COUNT(DISTINCT o.ID) AS TOTAL_ORDERS,
            MIN(o.CREATED_AT) AS FIRST_ORDER_DATE,
            MAX(o.CREATED_AT) AS LAST_ORDER_DATE,
            DATEDIFF('day', MIN(o.CREATED_AT), MAX(o.CREATED_AT)) AS TENURE_DAYS,
            AVG(o.TOTAL_VALUE_EXCL_TIP_AND_DONATIONS) AS AVG_ORDER_VALUE,
            SUM(o.TOTAL_VALUE_EXCL_TIP_AND_DONATIONS) AS TOTAL_GMV,
            MAX(CASE WHEN o.DELIVEROO_PLUS_ORDER = TRUE THEN 1 ELSE 0 END) AS IS_PLUS_MEMBER
        FROM production.denormalised.orders o
        WHERE o.IS_FAMILY_TIME_ORDER = TRUE
          AND o.STATUS = 'DELIVERED'
        GROUP BY o.USER_ID
        ORDER BY TOTAL_ORDERS DESC
        """
        
        logger.info("Fetching customer metrics...")
        return self.execute_query(query)
    
    def get_ratings_and_issues(self) -> pd.DataFrame:
        """Get order ratings and reported issues."""
        query = """
        SELECT 
            o.ID AS ORDER_ID,
            o.USER_ID AS CUSTOMER_ID,
            u.EMAIL AS CUSTOMER_EMAIL,
            o.RESTAURANT_NAME AS PARTNER_NAME,
            o.CREATED_AT AS ORDER_TIMESTAMP,
            r.RATING_STARS,
            r.RATING_COMMENT,
            r.CREATED_AT AS RATING_TIMESTAMP
        FROM production.denormalised.orders o
        LEFT JOIN production.orderweb.users u ON o.USER_ID = u.ID
        LEFT JOIN production.denormalised.order_ratings r ON o.ID = r.ORDER_ID
        WHERE o.IS_FAMILY_TIME_ORDER = TRUE
          AND o.STATUS = 'DELIVERED'
          AND r.RATING_STARS IS NOT NULL
        ORDER BY o.CREATED_AT DESC
        """
        
        logger.info("Fetching ratings and issues...")
        return self.execute_query(query)


# =========================================================================
# CONVENIENCE FUNCTIONS
# =========================================================================

def get_connector(auth_method: Optional[str] = None) -> SnowflakeConnector:
    """
    Get a SnowflakeConnector instance.
    
    Args:
        auth_method: Optional auth method override
        
    Returns:
        SnowflakeConnector instance
    """
    return SnowflakeConnector(auth_method=auth_method)


def quick_query(query: str, auth_method: Optional[str] = None) -> pd.DataFrame:
    """
    Execute a quick query without managing connections.
    
    Args:
        query: SQL query string
        auth_method: Optional auth method override
        
    Returns:
        pandas DataFrame with results
    """
    connector = get_connector(auth_method=auth_method)
    try:
        return connector.execute_query(query)
    finally:
        connector.disconnect()


# =========================================================================
# CLI INTERFACE
# =========================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Snowflake Connector CLI")
    parser.add_argument('--auth', choices=['browser', 'keypair', 'password'], 
                       default='browser', help='Authentication method')
    parser.add_argument('--test', action='store_true', help='Test connection')
    parser.add_argument('--query', type=str, help='Execute a query')
    
    args = parser.parse_args()
    
    connector = SnowflakeConnector(auth_method=args.auth)
    
    if args.test:
        success = connector.test_connection()
        exit(0 if success else 1)
    
    if args.query:
        result = connector.execute_query(args.query)
        print(result.to_string())
    
    connector.disconnect()


