#!/usr/bin/env python3
"""
Script to load sample data into Oracle Database using Python.
This is an alternative to running the SQL file directly.
"""

import cx_Oracle
import sys

def create_sample_tables():
    """Create sample tables and load data into Oracle."""
    
    # Initialize Oracle Client
    try:
        import platform
        if platform.system() == "Darwin":  # macOS
            lib_dir = "/Users/sureshrajupilli/oracle/instantclient_23_3"
            cx_Oracle.init_oracle_client(lib_dir=lib_dir)
    except Exception as e:
        print(f"Warning: Could not initialize Oracle Client: {e}")
        print("Make sure you have Oracle Instant Client installed.")

    # Connection details
    connection_params = {
        'user': os.getenv('ORACLE_USERNAME', 'testuser'),
        'password': os.getenv('ORACLE_PASSWORD', 'testpass'),
        'dsn': os.getenv('ORACLE_DSN', 'localhost:1521/XEPDB1')
    }
    
    print("Connecting to Oracle Database...")
    try:
        conn = cx_Oracle.connect(**connection_params)
        cursor = conn.cursor()
        print("✓ Connected successfully!")
        print()
        
        # Read and execute SQL file
        print("Creating tables and loading sample data...")
        with open('create_sample_tables.sql', 'r') as f:
            sql_script = f.read()
        
        # Better SQL splitting logic
        statements = []
        current_statement = []
        in_plsql = False
        
        for line in sql_script.split('\n'):
            line = line.strip()
            if not line or line.startswith('--') or line.startswith('PROMPT'):
                continue
                
            if line.upper().startswith('BEGIN'):
                in_plsql = True
            
            current_statement.append(line)
            
            if in_plsql:
                if line == '/':
                    # End of PL/SQL block
                    stmt = '\n'.join(current_statement[:-1]) # Remove the slash
                    if stmt.strip():
                        statements.append(stmt)
                    current_statement = []
                    in_plsql = False
            else:
                if line.endswith(';'):
                    # End of normal SQL statement
                    stmt = '\n'.join(current_statement)
                    stmt = stmt.rstrip(';') # Remove the semicolon
                    if stmt.strip():
                        statements.append(stmt)
                    current_statement = []
        
        # Execute statements
        for i, statement in enumerate(statements):
            try:
                # print(f"Executing statement {i+1}...")
                cursor.execute(statement)
            except cx_Oracle.DatabaseError as e:
                error, = e.args
                # Ignore "table or view does not exist" errors during drop
                if error.code != 942:
                    print(f"Warning executing statement {i+1}: {error.message}")
                    # print(f"Statement: {statement[:100]}...")
        
        conn.commit()
        
        # Verify data
        print()
        print("Verifying data...")
        print("-" * 50)
        
        tables = ['DEPARTMENTS', 'EMPLOYEES', 'CUSTOMERS', 'PRODUCTS', 'ORDERS', 'ORDER_ITEMS']
        total_rows = 0
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            total_rows += count
            print(f"  {table:20} {count:5} rows")
        
        print("-" * 50)
        print(f"  Total: {total_rows} rows across {len(tables)} tables")
        print()
        print("✓ Sample data loaded successfully!")
        
        cursor.close()
        conn.close()
        
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(f"❌ Database error: {error.message}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ create_sample_tables.sql file not found!")
        print("Make sure you're running this script from the DBMigration directory.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    create_sample_tables()
