#!/usr/bin/env python3
"""
Test PostgreSQL connection and display database information.
"""

import psycopg2
import sys

def test_connection():
    """Test PostgreSQL connection."""
    
    import os

    connection_params = {
        'host': os.getenv('PG_HOST', 'localhost'),
        'port': int(os.getenv('PG_PORT', 5432)),
        'database': os.getenv('PG_DATABASE', 'migration_test'),
        'user': os.getenv('PG_USER', 'testuser'),
        'password': os.getenv('PG_PASSWORD', 'testpass')
    }
    
    print("Testing PostgreSQL connection...")
    print(f"  Host: {connection_params['host']}")
    print(f"  Port: {connection_params['port']}")
    print(f"  Database: {connection_params['database']}")
    print(f"  User: {connection_params['user']}")
    print()
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**connection_params)
        cursor = conn.cursor()
        
        print("✓ Connected successfully!")
        print()
        
        # Get PostgreSQL version
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"PostgreSQL Version:")
        print(f"  {version.split(',')[0]}")
        print()
        
        # Get database size
        cursor.execute("""
            SELECT pg_size_pretty(pg_database_size(current_database())) AS size;
        """)
        size = cursor.fetchone()[0]
        print(f"Database Size: {size}")
        print()
        
        # List existing tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        if tables:
            print(f"Existing Tables ({len(tables)}):")
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]};")
                count = cursor.fetchone()[0]
                print(f"  - {table[0]:30} ({count} rows)")
        else:
            print("No tables found (database is empty - ready for migration!)")
        
        print()
        print("✓ PostgreSQL is ready for migration!")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Connection failed: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Make sure PostgreSQL is running: brew services list")
        print("  2. Start PostgreSQL: brew services start postgresql@14")
        print("  3. Run setup script: ./scripts/setup_postgres.sh")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    success = test_connection()
    sys.exit(0 if success else 1)
