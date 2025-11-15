#!/usr/bin/env python3
"""
Main migration script for Oracle to PostgreSQL migration.
"""

import argparse
import logging
import sys
import yaml
from pathlib import Path
from dotenv import load_dotenv
import os

from db_connector import OracleConnector, PostgreSQLConnector
from schema_converter import SchemaConverter
from data_migrator import DataMigrator

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        logger.error(f"Failed to load config file: {e}")
        raise


def get_db_connections(config: dict) -> tuple:
    """Create Oracle and PostgreSQL connections from config."""
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
        port=pg_config.get('port') or int(os.getenv('PG_PORT', 5432)),
        database=pg_config.get('database') or os.getenv('PG_DATABASE'),
        username=pg_config.get('username') or os.getenv('PG_USERNAME'),
        password=pg_config.get('password') or os.getenv('PG_PASSWORD'),
        schema=pg_config.get('schema') or os.getenv('PG_SCHEMA', 'public')
    )
    
    return oracle_conn, pg_conn


def main():
    """Main migration function."""
    parser = argparse.ArgumentParser(
        description='Migrate database from Oracle to PostgreSQL'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    parser.add_argument(
        '--schema-only',
        action='store_true',
        help='Only migrate schema, skip data'
    )
    parser.add_argument(
        '--data-only',
        action='store_true',
        help='Only migrate data, skip schema (assumes schema already exists)'
    )
    parser.add_argument(
        '--tables',
        type=str,
        help='Comma-separated list of specific tables to migrate'
    )
    parser.add_argument(
        '--truncate',
        action='store_true',
        help='Truncate target tables before data migration'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=1000,
        help='Batch size for data migration (default: 1000)'
    )
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        logger.info(f"Loading configuration from {args.config}")
        config = load_config(args.config)
        
        # Get database connections
        logger.info("Establishing database connections...")
        oracle_conn, pg_conn = get_db_connections(config)
        
        # Connect to databases
        oracle_conn.connect()
        pg_conn.connect()
        
        try:
            # Determine tables to migrate
            table_filter = None
            if args.tables:
                table_filter = [t.strip() for t in args.tables.split(',')]
                logger.info(f"Migrating specific tables: {table_filter}")
            
            # Schema migration
            if not args.data_only:
                logger.info("Starting schema migration...")
                schema_converter = SchemaConverter(oracle_conn, pg_conn)
                schema_results = schema_converter.convert_all_tables(table_filter)
                
                failed_schemas = [t for t, success in schema_results.items() if not success]
                if failed_schemas:
                    logger.warning(f"Schema migration failed for: {failed_schemas}")
                    if args.schema_only:
                        return 1
            
            # Data migration
            if not args.schema_only:
                logger.info("Starting data migration...")
                data_migrator = DataMigrator(
                    oracle_conn, 
                    pg_conn, 
                    batch_size=args.batch_size
                )
                data_results = data_migrator.migrate_all_tables(
                    table_filter, 
                    truncate=args.truncate
                )
                
                failed_data = [t for t, success in data_results.items() if not success]
                if failed_data:
                    logger.warning(f"Data migration failed for: {failed_data}")
                    return 1
            
            logger.info("Migration completed successfully!")
            return 0
            
        finally:
            # Disconnect from databases
            oracle_conn.disconnect()
            pg_conn.disconnect()
            
    except KeyboardInterrupt:
        logger.info("Migration interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())

