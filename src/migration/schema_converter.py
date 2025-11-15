"""
Schema conversion utilities for Oracle to PostgreSQL migration.
"""

import logging
from typing import List, Dict, Any
from .db_connector import OracleConnector, PostgreSQLConnector
from .type_mapper import TypeMapper

logger = logging.getLogger(__name__)


class SchemaConverter:
    """Converts Oracle schemas to PostgreSQL schemas."""
    
    def __init__(self, oracle_conn: OracleConnector, pg_conn: PostgreSQLConnector):
        self.oracle_conn = oracle_conn
        self.pg_conn = pg_conn
        self.type_mapper = TypeMapper()
    
    def convert_table(self, table_name: str) -> bool:
        """
        Convert a single Oracle table to PostgreSQL.
        
        Args:
            table_name: Name of the table to convert
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Converting table: {table_name}")
            
            # Get table structure from Oracle
            columns = self.oracle_conn.get_table_columns(table_name)
            primary_keys = self.oracle_conn.get_primary_keys(table_name)
            foreign_keys = self.oracle_conn.get_foreign_keys(table_name)
            indexes = self.oracle_conn.get_indexes(table_name)
            
            # Convert columns
            pg_columns = []
            for col in columns:
                col_name = col[0]
                oracle_type = col[1]
                data_length = col[2]
                data_precision = col[3]
                data_scale = col[4]
                nullable = col[5]
                default_value = col[6]
                
                # Map data type
                pg_type = self.type_mapper.map_type(
                    oracle_type, data_length, data_precision, data_scale
                )
                
                # Build column definition
                col_def = f'"{col_name}" {pg_type}'
                
                # Add NOT NULL constraint
                if nullable == 'N':
                    col_def += ' NOT NULL'
                
                # Add default value
                if default_value:
                    pg_default = self.type_mapper.convert_default_value(
                        default_value, oracle_type
                    )
                    if pg_default:
                        col_def += f' DEFAULT {pg_default}'
                
                pg_columns.append(col_def)
            
            # Create table in PostgreSQL
            self.pg_conn.create_table(table_name, pg_columns, primary_keys)
            
            # Create indexes
            self._create_indexes(table_name, indexes)
            
            # Create foreign keys
            self._create_foreign_keys(table_name, foreign_keys)
            
            logger.info(f"Successfully converted table: {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error converting table {table_name}: {e}")
            return False
    
    def _create_indexes(self, table_name: str, indexes: List[Any]):
        """Create indexes in PostgreSQL."""
        if not indexes:
            return
        
        # Group indexes by index name
        index_dict = {}
        for idx in indexes:
            idx_name = idx[0]
            col_name = idx[1]
            col_pos = idx[2]
            is_unique = idx[3] == 'UNIQUE'
            
            if idx_name not in index_dict:
                index_dict[idx_name] = {
                    'columns': [],
                    'unique': is_unique
                }
            
            # Insert column at correct position
            while len(index_dict[idx_name]['columns']) < col_pos:
                index_dict[idx_name]['columns'].append(None)
            index_dict[idx_name]['columns'][col_pos - 1] = col_name
        
        # Create indexes
        schema = self.pg_conn.schema
        for idx_name, idx_info in index_dict.items():
            try:
                # Skip if it's a primary key index (already created)
                if idx_name.upper().endswith('_PK'):
                    continue
                
                cols = [col for col in idx_info['columns'] if col]
                if not cols:
                    continue
                
                col_list = ', '.join([f'"{col}"' for col in cols])
                unique_clause = 'UNIQUE ' if idx_info['unique'] else ''
                
                # PostgreSQL index names must be unique, so prefix with table name
                pg_idx_name = f"{table_name}_{idx_name}".lower()[:63]  # Max 63 chars
                
                query = f'CREATE {unique_clause}INDEX IF NOT EXISTS "{pg_idx_name}" ' \
                       f'ON "{schema}"."{table_name}" ({col_list})'
                
                self.pg_conn.execute_command(query)
                logger.debug(f"Created index: {pg_idx_name}")
            except Exception as e:
                logger.warning(f"Failed to create index {idx_name}: {e}")
    
    def _create_foreign_keys(self, table_name: str, foreign_keys: List[Any]):
        """Create foreign key constraints in PostgreSQL."""
        if not foreign_keys:
            return
        
        # Group foreign keys by constraint name
        fk_dict = {}
        for fk in foreign_keys:
            constraint_name = fk[0]
            column_name = fk[1]
            ref_schema = fk[2]
            ref_constraint = fk[3]
            ref_column = fk[4]
            
            if constraint_name not in fk_dict:
                fk_dict[constraint_name] = {
                    'columns': [],
                    'ref_table': None,
                    'ref_columns': []
                }
            
            fk_dict[constraint_name]['columns'].append(column_name)
            fk_dict[constraint_name]['ref_columns'].append(ref_column)
        
        # Get referenced table names
        for constraint_name, fk_info in fk_dict.items():
            # Find the FK entry for this constraint to get reference info
            fk_entry = next((fk for fk in foreign_keys if fk[0] == constraint_name), None)
            if not fk_entry:
                continue
            
            ref_owner = fk_entry[2]
            ref_constraint = fk_entry[3]
            
            # Query to get referenced table
            query = """
                SELECT table_name
                FROM all_constraints
                WHERE owner = :owner
                AND constraint_name = :constraint_name
            """
            try:
                result = self.oracle_conn.execute_query(query, {
                    'owner': ref_owner,
                    'constraint_name': ref_constraint
                })
                if result:
                    fk_info['ref_table'] = result[0][0]
            except Exception as e:
                logger.warning(f"Could not determine referenced table for FK {constraint_name}: {e}")
                continue
        
        # Create foreign key constraints
        schema = self.pg_conn.schema
        for constraint_name, fk_info in fk_dict.items():
            if not fk_info['ref_table']:
                continue
            
            try:
                cols = ', '.join([f'"{col}"' for col in fk_info['columns']])
                ref_cols = ', '.join([f'"{col}"' for col in fk_info['ref_columns']])
                
                # PostgreSQL FK names must be unique
                pg_fk_name = f"{table_name}_{constraint_name}".lower()[:63]
                
                query = f'ALTER TABLE "{schema}"."{table_name}" ' \
                       f'ADD CONSTRAINT "{pg_fk_name}" ' \
                       f'FOREIGN KEY ({cols}) ' \
                       f'REFERENCES "{schema}"."{fk_info["ref_table"]}" ({ref_cols})'
                
                self.pg_conn.execute_command(query)
                logger.debug(f"Created foreign key: {pg_fk_name}")
            except Exception as e:
                logger.warning(f"Failed to create foreign key {constraint_name}: {e}")
    
    def convert_all_tables(self, table_filter: List[str] = None) -> Dict[str, bool]:
        """
        Convert all tables from Oracle to PostgreSQL.
        
        Args:
            table_filter: Optional list of table names to convert (if None, converts all)
            
        Returns:
            Dictionary mapping table names to success status
        """
        results = {}
        
        # Get list of tables
        if table_filter:
            tables = [t for t in self.oracle_conn.get_tables() if t in table_filter]
        else:
            tables = self.oracle_conn.get_tables()
        
        logger.info(f"Converting {len(tables)} tables...")
        
        for table_name in tables:
            results[table_name] = self.convert_table(table_name)
        
        successful = sum(1 for v in results.values() if v)
        logger.info(f"Schema conversion complete: {successful}/{len(tables)} tables successful")
        
        return results

