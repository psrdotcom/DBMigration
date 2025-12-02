# Quick Start Guide - Database Migration Testing

## ✅ Setup Complete!

Both databases are now ready for migration testing:

### PostgreSQL (Target Database) ✓
- **Status**: Running and ready
- **Host**: localhost
- **Port**: 5432
- **Database**: migration_test
- **Username**: testuser
- **Password**: testpass
- **State**: Empty (ready to receive migrated data)

### Oracle (Source Database) ⏳
- **Status**: Setting up via Docker (check terminal)
- **Host**: localhost
- **Port**: 1521
- **Service Name**: XEPDB1
- **Username**: testuser
- **Password**: testpass

---

## 🚀 Next Steps

### 1. Wait for Oracle to Complete Setup

Check the terminal running `./scripts/setup_oracle_docker.sh`. Wait for:
```
✓ Oracle Database is starting!
```

Then wait about 2 minutes for Oracle to fully initialize.

### 2. Load Sample Data into Oracle

```bash
# Option A: Using Python (recommended)
python scripts/load_sample_data.py

# Option B: Using SQL*Plus (if installed)
sqlplus testuser/testpass@localhost:1521/XEPDB1 @scripts/create_sample_tables.sql
```

This creates 6 tables with 49 rows of sample data.

### 3. Run the Migration

#### Interactive Mode (Recommended):
```bash
python migrate.py --interactive
```

When prompted, use the connection details above.

#### Using Config File:
```bash
# Full migration (schema + data)
python migrate.py --config config/config.yaml

# Schema only
python migrate.py --config config/config.yaml --schema-only

# Data only (assumes schema exists)
python migrate.py --config config/config.yaml --data-only

# Specific tables
python migrate.py --config config/config.yaml --tables CUSTOMERS,ORDERS,ORDER_ITEMS
```

### 4. Verify Migration Results

```bash
# Test PostgreSQL connection and view migrated data
python scripts/test_postgres_connection.py

# Or connect with psql
psql -h localhost -U testuser -d migration_test

# In psql, list tables:
\dt

# View data from a table:
SELECT * FROM customers LIMIT 10;
```

---

## 📊 Sample Database Schema

The Oracle database will contain:

| Table | Rows | Description |
|-------|------|-------------|
| DEPARTMENTS | 5 | Company departments |
| EMPLOYEES | 8 | Employee records |
| CUSTOMERS | 5 | Customer information |
| PRODUCTS | 8 | Product catalog |
| ORDERS | 6 | Customer orders |
| ORDER_ITEMS | 17 | Order line items |

**Total: 6 tables, 49 rows**

Features:
- Primary keys and foreign keys
- Indexes
- Various data types (NUMBER, VARCHAR2, DATE, TIMESTAMP, CLOB)
- Realistic relationships

---

## 🔧 Useful Commands

### PostgreSQL Management
```bash
# Start PostgreSQL
brew services start postgresql@14

# Stop PostgreSQL
brew services stop postgresql@14

# Check status
brew services list | grep postgresql

# Connect to database
psql -h localhost -U testuser -d migration_test
```

### Oracle Management (Docker)
```bash
# Check Oracle status
docker logs oracle-test

# Stop Oracle
docker stop oracle-test

# Start Oracle
docker start oracle-test

# Remove Oracle (deletes all data!)
docker rm -f oracle-test
```

### Migration Tool
```bash
# List available agents
python migrate.py --list-agents

# Interactive mode
python migrate.py --interactive

# With config file
python migrate.py --config config/config.yaml

# Schema only
python migrate.py --schema-only

# Data only
python migrate.py --data-only

# Specific tables
python migrate.py --tables TABLE1,TABLE2
```

---

## 📝 Configuration File

The `config/config.yaml` file has been updated with your test database credentials.

You can edit it to:
- Change connection details
- Configure LLM providers (optional)
- Set batch sizes
- Specify tables to migrate

---

## 🐛 Troubleshooting

### PostgreSQL Issues
```bash
# Check if running
pg_isready

# View logs
tail -f /opt/homebrew/var/log/postgresql@14.log

# Restart
brew services restart postgresql@14
```

### Oracle Issues
```bash
# Check container status
docker ps | grep oracle-test

# View logs
docker logs -f oracle-test

# Wait for: "DATABASE IS READY TO USE!"
```

### Migration Issues
- Check `migration.log` for detailed error messages
- Ensure both databases are running
- Verify connection details in `config/config.yaml`
- Test connections individually first

---

## 📚 Documentation

- `docs/POSTGRES_SETUP.md` - Detailed PostgreSQL setup guide
- `docs/ORACLE_SETUP.md` - Detailed Oracle setup guide
- `README.md` - Main project documentation
- `docs/AGENTS.md` - Agent system documentation

---

## ✨ Ready to Migrate!

Everything is set up! Once Oracle finishes starting:

1. Load sample data: `python scripts/load_sample_data.py`
2. Run migration: `python migrate.py --interactive`
3. Verify results: `python scripts/test_postgres_connection.py`

Happy migrating! 🚀
