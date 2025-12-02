"""
Interactive migration planner for collecting user inputs and generating migration plans.
"""

import logging
import getpass
from typing import Dict, Any, List, Optional, Tuple
from tabulate import tabulate

logger = logging.getLogger(__name__)


class InteractivePlanner:
    """Handles interactive user input collection and migration planning."""
    
    def __init__(self):
        self.oracle_config = {}
        self.pg_config = {}
        self.selected_tables = []
        self.migration_plan = {}
    
    def collect_connection_details(self) -> Dict[str, Any]:
        """
        Collect database connection details from user interactively.
        
        Returns:
            Configuration dictionary with oracle and postgresql sections
        """
        print("\n" + "="*70)
        print("  Oracle to PostgreSQL Migration - Interactive Mode")
        print("="*70)
        print("\nThis wizard will guide you through the migration process.")
        print("You'll be asked to provide connection details for both databases.\n")
        
        # Collect Oracle connection details
        print("\n--- Oracle Database Connection ---")
        self.oracle_config = {
            'host': input("Oracle Host [localhost]: ").strip() or 'localhost',
            'port': int(input("Oracle Port [1521]: ").strip() or '1521'),
            'service_name': input("Oracle Service Name [XEPDB1]: ").strip() or 'XEPDB1',
            'username': input("Oracle Username [testuser]: ").strip() or 'testuser',
            'password': getpass.getpass("Oracle Password: "),
            'schema': input("Oracle Schema (leave empty to use username): ").strip()
        }
        
        # Use username as schema if not provided
        if not self.oracle_config['schema']:
            self.oracle_config['schema'] = self.oracle_config['username'].upper()
        
        # Collect PostgreSQL connection details
        print("\n--- PostgreSQL Database Connection ---")
        self.pg_config = {
            'host': input("PostgreSQL Host [localhost]: ").strip() or 'localhost',
            'port': int(input("PostgreSQL Port [5432]: ").strip() or '5432'),
            'database': input("PostgreSQL Database [migration_test]: ").strip() or 'migration_test',
            'username': input("PostgreSQL Username [postgres]: ").strip() or 'postgres',
            'password': getpass.getpass("PostgreSQL Password: "),
            'schema': input("PostgreSQL Schema [public]: ").strip() or 'public'
        }
        
        # Build configuration dictionary
        config = {
            'oracle': self.oracle_config,
            'postgresql': self.pg_config
        }
        
        return config
    
    def validate_connections(self, config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate database connections.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Tuple of (success, error_message)
        """
        from src.utils.config_loader import get_db_connections
        
        print("\n--- Validating Connections ---")
        
        try:
            oracle_conn, pg_conn = get_db_connections(config)
            
            # Test Oracle connection
            print("Testing Oracle connection...", end=" ")
            oracle_conn.connect()
            print("✓ Connected")
            
            # Test PostgreSQL connection
            print("Testing PostgreSQL connection...", end=" ")
            pg_conn.connect()
            print("✓ Connected")
            
            # Disconnect
            oracle_conn.disconnect()
            pg_conn.disconnect()
            
            print("\n✓ All connections validated successfully!")
            return True, None
            
        except Exception as e:
            error_msg = f"Connection validation failed: {str(e)}"
            print(f"\n✗ {error_msg}")
            return False, error_msg
    
    def discover_schema(self, config: Dict[str, Any]) -> List[str]:
        """
        Discover available tables in Oracle schema.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            List of table names
        """
        from src.utils.config_loader import get_db_connections
        
        print("\n--- Discovering Schema ---")
        
        try:
            oracle_conn, _ = get_db_connections(config)
            oracle_conn.connect()
            
            try:
                tables = oracle_conn.get_tables()
                print(f"\nFound {len(tables)} tables in schema '{oracle_conn.schema}':")
                
                # Display tables in columns
                if tables:
                    # Split into columns for better display
                    cols = 3
                    rows = [tables[i:i+cols] for i in range(0, len(tables), cols)]
                    for row in rows:
                        print("  " + "".join(f"{t:<25}" for t in row))
                
                return tables
            finally:
                oracle_conn.disconnect()
                
        except Exception as e:
            logger.error(f"Schema discovery failed: {e}")
            print(f"\n✗ Failed to discover schema: {e}")
            return []
    
    def select_tables(self, available_tables: List[str]) -> List[str]:
        """
        Allow user to select specific tables or all tables.
        
        Args:
            available_tables: List of available table names
            
        Returns:
            List of selected table names
        """
        if not available_tables:
            print("\n✗ No tables found in the schema.")
            return []
        
        print("\n--- Table Selection ---")
        print("Options:")
        print("  1. Migrate all tables")
        print("  2. Select specific tables")
        
        choice = input("\nEnter your choice [1]: ").strip() or '1'
        
        if choice == '1':
            print(f"\n✓ Selected all {len(available_tables)} tables for migration")
            return available_tables
        elif choice == '2':
            print("\nEnter table names separated by commas:")
            print("(or press Enter to cancel and migrate all)")
            table_input = input("> ").strip()
            
            if not table_input:
                print(f"\n✓ Selected all {len(available_tables)} tables for migration")
                return available_tables
            
            selected = [t.strip().upper() for t in table_input.split(',')]
            # Validate table names
            valid_tables = [t for t in selected if t in available_tables]
            invalid_tables = [t for t in selected if t not in available_tables]
            
            if invalid_tables:
                print(f"\n⚠ Warning: The following tables were not found: {', '.join(invalid_tables)}")
            
            if valid_tables:
                print(f"\n✓ Selected {len(valid_tables)} tables for migration")
                return valid_tables
            else:
                print("\n✗ No valid tables selected. Migrating all tables.")
                return available_tables
        else:
            print("\n✗ Invalid choice. Migrating all tables.")
            return available_tables
    
    def generate_migration_plan(self, config: Dict[str, Any], tables: List[str]) -> Dict[str, Any]:
        """
        Generate detailed migration plan.
        
        Args:
            config: Configuration dictionary
            tables: List of tables to migrate
            
        Returns:
            Migration plan dictionary
        """
        from src.utils.config_loader import get_db_connections
        from agents.schema_agent import SchemaAgent
        
        print("\n--- Generating Migration Plan ---")
        print("Analyzing schema and estimating migration complexity...\n")
        
        try:
            oracle_conn, pg_conn = get_db_connections(config)
            oracle_conn.connect()
            
            try:
                plan = {
                    'source': {
                        'type': 'Oracle',
                        'host': config['oracle']['host'],
                        'schema': config['oracle']['schema']
                    },
                    'target': {
                        'type': 'PostgreSQL',
                        'host': config['postgresql']['host'],
                        'database': config['postgresql']['database'],
                        'schema': config['postgresql']['schema']
                    },
                    'tables': [],
                    'summary': {
                        'total_tables': len(tables),
                        'total_rows': 0,
                        'estimated_complexity': 'Medium'
                    },
                    'warnings': []
                }
                
                # Analyze each table
                for table in tables:
                    try:
                        # Get row count
                        count_query = f"SELECT COUNT(*) FROM {table}"
                        result = oracle_conn.execute_query(count_query)
                        row_count = result[0][0] if result else 0
                        
                        # Get column info
                        columns_query = f"""
                            SELECT column_name, data_type, data_length, nullable
                            FROM all_tab_columns
                            WHERE table_name = :1 AND owner = :2
                            ORDER BY column_id
                        """
                        columns = oracle_conn.execute_query(
                            columns_query, 
                            (table, oracle_conn.schema)
                        )
                        
                        table_info = {
                            'name': table,
                            'row_count': row_count,
                            'column_count': len(columns) if columns else 0,
                            'columns': columns[:5] if columns else []  # Sample first 5 columns
                        }
                        
                        plan['tables'].append(table_info)
                        plan['summary']['total_rows'] += row_count
                        
                    except Exception as e:
                        logger.warning(f"Could not analyze table {table}: {e}")
                        plan['warnings'].append(f"Could not fully analyze table {table}")
                
                # Estimate complexity
                if plan['summary']['total_rows'] > 1000000:
                    plan['summary']['estimated_complexity'] = 'High'
                elif plan['summary']['total_rows'] > 100000:
                    plan['summary']['estimated_complexity'] = 'Medium'
                else:
                    plan['summary']['estimated_complexity'] = 'Low'
                
                # Use LLM for additional insights if available
                schema_agent = SchemaAgent()
                if schema_agent.llm_client:
                    try:
                        llm_analysis = schema_agent.call_llm(
                            f"""Analyze this Oracle to PostgreSQL migration:
                            - Tables: {len(tables)}
                            - Total rows: {plan['summary']['total_rows']:,}
                            - Sample tables: {', '.join(tables[:5])}
                            
                            Provide brief insights on potential challenges and recommendations (2-3 sentences).""",
                            system_prompt="You are a database migration expert.",
                            max_tokens=200
                        )
                        plan['llm_insights'] = llm_analysis
                    except Exception as e:
                        logger.debug(f"LLM analysis not available: {e}")
                
                self.migration_plan = plan
                return plan
                
            finally:
                oracle_conn.disconnect()
                
        except Exception as e:
            logger.error(f"Failed to generate migration plan: {e}")
            raise
    
    def display_plan(self, plan: Dict[str, Any]) -> None:
        """
        Display migration plan to user.
        
        Args:
            plan: Migration plan dictionary
        """
        print("\n" + "="*70)
        print("  MIGRATION PLAN")
        print("="*70)
        
        # Source and Target
        print("\n--- Source Database ---")
        print(f"  Type:   {plan['source']['type']}")
        print(f"  Host:   {plan['source']['host']}")
        print(f"  Schema: {plan['source']['schema']}")
        
        print("\n--- Target Database ---")
        print(f"  Type:     {plan['target']['type']}")
        print(f"  Host:     {plan['target']['host']}")
        print(f"  Database: {plan['target']['database']}")
        print(f"  Schema:   {plan['target']['schema']}")
        
        # Summary
        print("\n--- Migration Summary ---")
        print(f"  Tables to migrate:     {plan['summary']['total_tables']}")
        print(f"  Total rows (approx):   {plan['summary']['total_rows']:,}")
        print(f"  Estimated complexity:  {plan['summary']['estimated_complexity']}")
        
        # Tables
        print("\n--- Tables ---")
        table_data = [
            [i+1, t['name'], f"{t['row_count']:,}", t['column_count']]
            for i, t in enumerate(plan['tables'])
        ]
        print(tabulate(
            table_data,
            headers=['#', 'Table Name', 'Rows', 'Columns'],
            tablefmt='simple'
        ))
        
        # Warnings
        if plan.get('warnings'):
            print("\n--- Warnings ---")
            for warning in plan['warnings']:
                print(f"  ⚠ {warning}")
        
        # LLM Insights
        if plan.get('llm_insights'):
            print("\n--- AI Insights ---")
            print(f"  {plan['llm_insights']}")
        
        print("\n" + "="*70)
    
    def get_user_approval(self) -> bool:
        """
        Get user approval to proceed with migration.
        
        Returns:
            True if user approves, False otherwise
        """
        print("\n--- Approval Required ---")
        print("Review the migration plan above carefully.")
        print("\n⚠ WARNING: This will modify the target PostgreSQL database.")
        print("  - Schema objects will be created")
        print("  - Data will be migrated from Oracle to PostgreSQL")
        
        while True:
            response = input("\nDo you want to proceed with this migration? (yes/no): ").strip().lower()
            
            if response in ['yes', 'y']:
                print("\n✓ Migration approved. Starting migration process...\n")
                return True
            elif response in ['no', 'n']:
                print("\n✗ Migration cancelled by user.")
                return False
            else:
                print("Please enter 'yes' or 'no'")
    
    def run_interactive_mode(self) -> Tuple[Optional[Dict[str, Any]], Optional[List[str]]]:
        """
        Run the complete interactive workflow.
        
        Returns:
            Tuple of (config, selected_tables) if approved, (None, None) if cancelled
        """
        try:
            # Step 1: Collect connection details
            config = self.collect_connection_details()
            
            # Step 2: Validate connections
            success, error = self.validate_connections(config)
            if not success:
                print("\n✗ Cannot proceed without valid database connections.")
                return None, None
            
            # Step 3: Discover schema
            available_tables = self.discover_schema(config)
            if not available_tables:
                print("\n✗ No tables found to migrate.")
                return None, None
            
            # Step 4: Select tables
            selected_tables = self.select_tables(available_tables)
            if not selected_tables:
                print("\n✗ No tables selected for migration.")
                return None, None
            
            # Step 5: Generate migration plan
            plan = self.generate_migration_plan(config, selected_tables)
            
            # Step 6: Display plan
            self.display_plan(plan)
            
            # Step 7: Get approval
            if self.get_user_approval():
                return config, selected_tables
            else:
                return None, None
                
        except KeyboardInterrupt:
            print("\n\n✗ Interactive mode cancelled by user.")
            return None, None
        except Exception as e:
            logger.error(f"Interactive mode failed: {e}", exc_info=True)
            print(f"\n✗ Interactive mode failed: {e}")
            return None, None


def run_interactive_mode() -> Tuple[Optional[Dict[str, Any]], Optional[List[str]]]:
    """
    Convenience function to run interactive mode.
    
    Returns:
        Tuple of (config, selected_tables) if approved, (None, None) if cancelled
    """
    planner = InteractivePlanner()
    return planner.run_interactive_mode()
