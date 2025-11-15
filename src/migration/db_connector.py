"""
Database connection handlers for Oracle and PostgreSQL.
"""

import cx_Oracle
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class OracleConnector:
    """Handles Oracle database connections and operations."""
    
    def __init__(self, host: str, port: int, service_name: str, 
                 username: str, password: str, schema: Optional[str] = None):
        self.host = host
        self.port = port
        self.service_name = service_name
        self.username = username
        self.password = password
        self.schema = schema or username
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Establish connection to Oracle database."""
        try:
            dsn = cx_Oracle.makedsn(self.host, self.port, service_name=self.service_name)
            self.connection = cx_Oracle.connect(
                user=self.username,
                password=self.password,
                dsn=dsn
            )
            self.cursor = self.connection.cursor()
            logger.info(f"Connected to Oracle database: {self.service_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Oracle: {e}")
            raise
    
    def disconnect(self):
        """Close Oracle database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("Disconnected from Oracle database")
    
    def execute_query(self, query: str, params: Optional[Dict] = None):
        """Execute a query and return results."""
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_tables(self) -> list:
        """Get list of all tables in the schema."""
        query = """
            SELECT table_name 
            FROM all_tables 
            WHERE owner = :schema
            ORDER BY table_name
        """
        results = self.execute_query(query, {'schema': self.schema.upper()})
        return [row[0] for row in results]
    
    def get_table_columns(self, table_name: str) -> list:
        """Get column information for a table."""
        query = """
            SELECT 
                column_name,
                data_type,
                data_length,
                data_precision,
                data_scale,
                nullable,
                data_default
            FROM all_tab_columns
            WHERE owner = :schema AND table_name = :table_name
            ORDER BY column_id
        """
        results = self.execute_query(query, {
            'schema': self.schema.upper(),
            'table_name': table_name.upper()
        })
        return results
    
    def get_primary_keys(self, table_name: str) -> list:
        """Get primary key columns for a table."""
        query = """
            SELECT acc.column_name
            FROM all_cons_columns acc
            JOIN all_constraints ac ON acc.owner = ac.owner 
                AND acc.constraint_name = ac.constraint_name
            WHERE acc.owner = :schema
            AND ac.table_name = :table_name
            AND ac.constraint_type = 'P'
            ORDER BY acc.position
        """
        results = self.execute_query(query, {
            'schema': self.schema.upper(),
            'table_name': table_name.upper()
        })
        return [row[0] for row in results] if results else []
    
    def get_foreign_keys(self, table_name: str) -> list:
        """Get foreign key constraints for a table."""
        query = """
            SELECT 
                a.constraint_name,
                a.column_name,
                c.r_owner,
                c.r_constraint_name,
                b.column_name as ref_column
            FROM all_cons_columns a
            JOIN all_constraints c ON a.owner = c.owner 
                AND a.constraint_name = c.constraint_name
            JOIN all_cons_columns b ON c.r_owner = b.owner 
                AND c.r_constraint_name = b.constraint_name
            WHERE a.owner = :schema
            AND a.table_name = :table_name
            AND c.constraint_type = 'R'
            ORDER BY a.position
        """
        return self.execute_query(query, {
            'schema': self.schema.upper(),
            'table_name': table_name.upper()
        })
    
    def get_indexes(self, table_name: str) -> list:
        """Get indexes for a table."""
        query = """
            SELECT 
                index_name,
                column_name,
                column_position,
                uniqueness
            FROM all_ind_columns
            WHERE table_owner = :schema
            AND table_name = :table_name
            ORDER BY index_name, column_position
        """
        return self.execute_query(query, {
            'schema': self.schema.upper(),
            'table_name': table_name.upper()
        })
    
    def get_row_count(self, table_name: str) -> int:
        """Get total row count for a table."""
        query = f'SELECT COUNT(*) FROM "{self.schema}"."{table_name}"'
        result = self.execute_query(query)
        return result[0][0] if result else 0


class PostgreSQLConnector:
    """Handles PostgreSQL database connections and operations."""
    
    def __init__(self, host: str, port: int, database: str, 
                 username: str, password: str, schema: str = 'public'):
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.schema = schema
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Establish connection to PostgreSQL database."""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.username,
                password=self.password
            )
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            # Ensure schema exists
            self.cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {self.schema}")
            self.connection.commit()
            logger.info(f"Connected to PostgreSQL database: {self.database}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise
    
    def disconnect(self):
        """Close PostgreSQL database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("Disconnected from PostgreSQL database")
    
    def execute_query(self, query: str, params: Optional[tuple] = None):
        """Execute a query and return results."""
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def execute_command(self, command: str, params: Optional[tuple] = None):
        """Execute a command (INSERT, UPDATE, DELETE, DDL) without returning results."""
        if params:
            self.cursor.execute(command, params)
        else:
            self.cursor.execute(command)
        self.connection.commit()
    
    def create_table(self, table_name: str, columns: list, primary_keys: list = None):
        """Create a table in PostgreSQL."""
        schema = self.schema
        column_defs = ', '.join(columns)
        
        query = f'CREATE TABLE IF NOT EXISTS "{schema}"."{table_name}" ({column_defs}'
        
        if primary_keys:
            pk_cols = ', '.join([f'"{pk}"' for pk in primary_keys])
            query += f', PRIMARY KEY ({pk_cols})'
        
        query += ')'
        
        self.execute_command(query)
        logger.info(f"Created table: {schema}.{table_name}")
    
    def insert_data(self, table_name: str, columns: list, data: list):
        """Insert data into a table using batch insert."""
        schema = self.schema
        col_names = ', '.join([f'"{col}"' for col in columns])
        placeholders = ', '.join(['%s'] * len(columns))
        
        query = f'INSERT INTO "{schema}"."{table_name}" ({col_names}) VALUES ({placeholders})'
        
        self.cursor.executemany(query, data)
        self.connection.commit()
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists."""
        query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = %s AND table_name = %s
            )
        """
        result = self.execute_query(query, (self.schema, table_name))
        return result[0]['exists'] if result else False

