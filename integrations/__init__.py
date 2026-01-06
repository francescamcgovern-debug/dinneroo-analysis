"""
Dinneroo Analysis Integrations Layer

This module provides connectors for external services:
- Snowflake: Data warehouse for behavioral data
"""

from .snowflake_connector import SnowflakeConnector, get_connector

__all__ = [
    'SnowflakeConnector',
    'get_connector',
]
