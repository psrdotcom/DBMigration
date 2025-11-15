"""Configuration loading utilities."""

import yaml
import os
from typing import Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    try:
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        logger.error(f"Failed to load config file: {e}")
        raise


def get_db_connections(config: Dict[str, Any]) -> tuple:
    """
    Create Oracle and PostgreSQL connections from config.
    
    Args:
        config: Configuration dictionary containing 'oracle' and 'postgresql' sections
        
    Returns:
        tuple: (OracleConnector, PostgreSQLConnector) instances
        
    Raises:
        KeyError: If required configuration keys are missing
        ValueError: If configuration values are invalid
    """
    from src.migration.db_connector import OracleConnector, PostgreSQLConnector
    
    # Oracle connection
    oracle_config = config.get('oracle', {})
    oracle_conn = OracleConnector(
        host=oracle_config.get('host') or os.getenv('ORACLE_HOST'),
        port=oracle_config.get('port') or int(os.getenv('ORACLE_PORT', 1521)),
        service_name=oracle_config.get('service_name') or os.getenv('ORACLE_SERVICE_NAME'),
        username=oracle_config.get('username') or os.getenv('ORACLE_USERNAME'),
        password=oracle_config.get('password') or os.getenv('ORACLE_PASSWORD'),
        schema=oracle_config.get('schema') or os.getenv('ORACLE_SCHEMA')
    )
    
    # PostgreSQL connection
    pg_config = config.get('postgresql', {})
    pg_conn = PostgreSQLConnector(
        host=pg_config.get('host') or os.getenv('PG_HOST'),
        port=int(pg_config.get('port') or os.getenv('PG_PORT') or 5432),
        database=pg_config.get('database') or os.getenv('PG_DATABASE'),
        username=pg_config.get('username') or os.getenv('PG_USERNAME'),
        password=pg_config.get('password') or os.getenv('PG_PASSWORD'),
        schema=pg_config.get('schema') or os.getenv('PG_SCHEMA', 'public')
    )
    
    return oracle_conn, pg_conn

