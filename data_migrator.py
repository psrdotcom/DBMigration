"""
Data migration utilities for Oracle to PostgreSQL.
"""

import logging
from typing import List, Optional
from tqdm import tqdm
from db_connector import OracleConnector, PostgreSQLConnector

logger = logging.getLogger(__name__)


class DataMigrator:
    """Migrates data from Oracle to PostgreSQL."""
    
    def __init__(self, oracle_conn: OracleConnector, pg_conn: PostgreSQLConnector,
                 batch_size: int = 1000):
        self.oracle_conn = oracle_conn
        self.pg_conn = pg_conn
        self.batch_size = batch_size
    
    def migrate_table(self, table_name: str, truncate: bool = False) -> bool:
        """
        Migrate data from an Oracle table to PostgreSQL.
        
        Args:
            table_name: Name of the table to migrate
            truncate: If True, truncate target table before migration
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Migrating data for table: {table_name}")
            
            # Check if table exists in PostgreSQL
            if not self.pg_conn.table_exists(table_name):
                logger.error(f"Table {table_name} does not exist in PostgreSQL. Run schema migration first.")
                return False
            
            # Get row count
            total_rows = self.oracle_conn.get_row_count(table_name)
            if total_rows == 0:
                logger.info(f"Table {table_name} is empty, skipping data migration")
                return True
            
            logger.info(f"Migrating {total_rows} rows from {table_name}")
            
            # Truncate if requested
            if truncate:
                schema = self.pg_conn.schema
                self.pg_conn.execute_command(f'TRUNCATE TABLE "{schema}"."{table_name}"')
                logger.info(f"Truncated table: {table_name}")
            
            # Get column names
            columns = self.oracle_conn.get_table_columns(table_name)
            column_names = [col[0] for col in columns]
            
            # Build SELECT query
            schema = self.oracle_conn.schema
            col_list = ', '.join([f'"{col}"' for col in column_names])
            query = f'SELECT {col_list} FROM "{schema}"."{table_name}"'
            
            # Fetch and insert data in batches
            self.oracle_conn.cursor.execute(query)
            
            with tqdm(total=total_rows, desc=f"Migrating {table_name}") as pbar:
                while True:
                    batch = self.oracle_conn.cursor.fetchmany(self.batch_size)
                    if not batch:
                        break
                    
                    # Convert Oracle data types to Python types
                    converted_batch = []
                    for row in batch:
                        converted_row = []
                        for i, value in enumerate(row):
                            # Handle Oracle-specific types
                            if value is None:
                                converted_row.append(None)
                            elif hasattr(value, 'read'):  # LOB types
                                try:
                                    converted_row.append(value.read())
                                except:
                                    converted_row.append(str(value))
                            else:
                                converted_row.append(value)
                        converted_batch.append(tuple(converted_row))
                    
                    # Insert batch into PostgreSQL
                    try:
                        self.pg_conn.insert_data(table_name, column_names, converted_batch)
                        pbar.update(len(batch))
                    except Exception as e:
                        logger.error(f"Error inserting batch into {table_name}: {e}")
                        # Continue with next batch
                        pbar.update(len(batch))
            
            logger.info(f"Successfully migrated data for table: {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error migrating data for table {table_name}: {e}")
            return False
    
    def migrate_all_tables(self, table_filter: List[str] = None, 
                          truncate: bool = False) -> dict:
        """
        Migrate data from all tables.
        
        Args:
            table_filter: Optional list of table names to migrate
            truncate: If True, truncate target tables before migration
            
        Returns:
            Dictionary mapping table names to success status
        """
        results = {}
        
        # Get list of tables
        if table_filter:
            tables = [t for t in self.oracle_conn.get_tables() if t in table_filter]
        else:
            tables = self.oracle_conn.get_tables()
        
        logger.info(f"Migrating data for {len(tables)} tables...")
        
        for table_name in tables:
            results[table_name] = self.migrate_table(table_name, truncate)
        
        successful = sum(1 for v in results.values() if v)
        logger.info(f"Data migration complete: {successful}/{len(tables)} tables successful")
        
        return results

