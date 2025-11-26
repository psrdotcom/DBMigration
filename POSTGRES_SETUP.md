# PostgreSQL Setup Guide

This guide will help you set up PostgreSQL for testing the Oracle to PostgreSQL migration.

## Quick Start

### Step 1: Run the Setup Script

```bash
chmod +x setup_postgres.sh
./setup_postgres.sh
```

This will:
- ✓ Check if PostgreSQL is installed (already done via Homebrew)
- ✓ Start PostgreSQL service
- ✓ Create database: `migration_test`
- ✓ Create user: `testuser` / `testpass`
- ✓ Grant all necessary privileges

### Step 2: Test the Connection

```bash
python test_postgres_connection.py
```

This will verify:
- PostgreSQL is running
- Database is accessible
- User has proper permissions
- Show current database state

## Connection Details

Use these details for the migration tool:

```yaml
postgresql:
  host: localhost
  port: 5432
  database: migration_test
  username: testuser
  password: testpass
  schema: public
```

## Manual Setup (Alternative)

If you prefer to set up manually:

```bash
# Start PostgreSQL
brew services start postgresql@14

# Connect to PostgreSQL
psql postgres

# In psql, run:
CREATE USER testuser WITH PASSWORD 'testpass';
CREATE DATABASE migration_test OWNER testuser;
GRANT ALL PRIVILEGES ON DATABASE migration_test TO testuser;
\c migration_test
GRANT ALL ON SCHEMA public TO testuser;
\q
```

## Testing the Connection

### Using psql (Command Line)

```bash
psql -h localhost -U testuser -d migration_test
```

### Using Python

```bash
python test_postgres_connection.py
```

### Using the Migration Tool

```bash
python migrate.py --interactive
```

## Managing PostgreSQL

### Start PostgreSQL
```bash
brew services start postgresql@14
```

### Stop PostgreSQL
```bash
brew services stop postgresql@14
```

### Restart PostgreSQL
```bash
brew services restart postgresql@14
```

### Check Status
```bash
brew services list | grep postgresql
# or
pg_isready
```

### View Logs
```bash
tail -f /opt/homebrew/var/log/postgresql@14.log
```

## Common Commands

### Connect to Database
```bash
psql -h localhost -U testuser -d migration_test
```

### List Databases
```bash
psql -h localhost -U testuser -l
```

### List Tables in Database
```sql
\c migration_test
\dt
```

### View Table Schema
```sql
\d table_name
```

### Drop All Tables (Clean Slate)
```sql
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO testuser;
```

## Troubleshooting

### PostgreSQL won't start
```bash
# Check if it's already running
brew services list

# Try restarting
brew services restart postgresql@14

# Check logs
tail -f /opt/homebrew/var/log/postgresql@14.log
```

### Connection refused
```bash
# Make sure PostgreSQL is running
pg_isready

# Check if port 5432 is in use
lsof -i :5432

# Restart PostgreSQL
brew services restart postgresql@14
```

### Permission denied
```bash
# Reconnect and grant permissions
psql postgres
GRANT ALL PRIVILEGES ON DATABASE migration_test TO testuser;
\c migration_test
GRANT ALL ON SCHEMA public TO testuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO testuser;
```

### Can't drop database (active connections)
```sql
-- Terminate all connections
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'migration_test'
  AND pid <> pg_backend_pid();

-- Then drop
DROP DATABASE migration_test;
```

## Verifying Migration Results

After running the migration, verify the results:

### Check Table Count
```sql
SELECT COUNT(*) FROM information_schema.tables 
WHERE table_schema = 'public';
```

### Check Row Counts
```sql
SELECT 
    schemaname,
    tablename,
    n_live_tup as row_count
FROM pg_stat_user_tables
ORDER BY tablename;
```

### Compare with Oracle
```bash
# Run this Python script to compare
python -c "
import psycopg2
conn = psycopg2.connect(
    host='localhost',
    database='migration_test',
    user='testuser',
    password='testpass'
)
cursor = conn.cursor()
cursor.execute('''
    SELECT table_name, 
           (SELECT COUNT(*) FROM information_schema.columns 
            WHERE table_name = t.table_name) as column_count
    FROM information_schema.tables t
    WHERE table_schema = 'public'
    ORDER BY table_name;
''')
for row in cursor.fetchall():
    print(f'{row[0]:30} {row[1]} columns')
"
```

## Next Steps

1. ✓ PostgreSQL is set up and running
2. ✓ Test database created
3. ✓ User with permissions created
4. → Set up Oracle with sample data (see ORACLE_SETUP.md)
5. → Run the migration tool
6. → Verify migration results

## PostgreSQL Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [psql Commands Cheat Sheet](https://www.postgresql.org/docs/current/app-psql.html)
- [PostgreSQL vs Oracle Data Types](https://wiki.postgresql.org/wiki/Oracle_to_Postgres_Conversion)

Happy migrating! 🚀
