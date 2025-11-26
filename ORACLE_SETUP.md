# Oracle Database Setup Guide

This guide will help you set up Oracle Database with sample tables for testing the migration tool.

## Prerequisites

- Docker Desktop installed ([Download here](https://www.docker.com/products/docker-desktop))
- Oracle Instant Client installed (for cx_Oracle)

## Quick Start (Docker - Recommended)

### Step 1: Start Oracle Database

```bash
chmod +x setup_oracle_docker.sh
./setup_oracle_docker.sh
```

This will:
- Pull Oracle Database XE 21c (Express Edition) image
- Start Oracle in a Docker container
- Create a test user: `testuser` / `testpass`
- Expose Oracle on port `1521`

### Step 2: Wait for Oracle to Start

Oracle takes about 1-2 minutes to fully start. You can check the logs:

```bash
docker logs -f oracle-test
```

Wait until you see: `DATABASE IS READY TO USE!`

### Step 3: Create Sample Tables

**Option A: Using Python (Recommended)**
```bash
python load_sample_data.py
```

**Option B: Using SQL*Plus (if you have Oracle Client installed)**
```bash
sqlplus testuser/testpass@localhost:1521/XEPDB1 @create_sample_tables.sql
```

## Connection Details

Once Oracle is running, use these connection details:

```yaml
oracle:
  host: localhost
  port: 1521
  service_name: XEPDB1
  username: testuser
  password: testpass
```

## Sample Database Schema

The setup creates 6 tables with sample data:

### Tables Created:

1. **DEPARTMENTS** (5 rows)
   - department_id, department_name, location, created_date

2. **EMPLOYEES** (8 rows)
   - employee_id, first_name, last_name, email, phone_number, hire_date, salary, department_id, manager_id, is_active

3. **CUSTOMERS** (5 rows)
   - customer_id, customer_name, email, phone, address, city, state, zip_code, country, created_date

4. **PRODUCTS** (8 rows)
   - product_id, product_name, description, category, price, stock_quantity, is_active, created_date, last_updated

5. **ORDERS** (6 rows)
   - order_id, customer_id, order_date, total_amount, status, shipping_address

6. **ORDER_ITEMS** (17 rows)
   - order_item_id, order_id, product_id, quantity, unit_price, subtotal

**Total: 49 rows across 6 tables**

### Features:
- Primary keys on all tables
- Foreign key relationships
- Indexes for performance
- Various Oracle data types (NUMBER, VARCHAR2, DATE, TIMESTAMP, CLOB)
- Sample business data (e-commerce scenario)

## Testing the Migration

Once Oracle is set up with sample data, you can test the migration:

### Interactive Mode:
```bash
python migrate.py --interactive
```

When prompted, use these connection details:
- **Oracle Host**: localhost
- **Oracle Port**: 1521
- **Oracle Service Name**: XEPDB1
- **Oracle Username**: testuser
- **Oracle Password**: testpass

### With Config File:
Update `config/config.yaml` with the Oracle connection details above, then run:

```bash
# Schema only
python migrate.py --schema-only

# Full migration
python migrate.py

# Specific tables
python migrate.py --tables CUSTOMERS,ORDERS,ORDER_ITEMS
```

## Managing the Oracle Container

```bash
# Stop Oracle
docker stop oracle-test

# Start Oracle
docker start oracle-test

# View logs
docker logs oracle-test

# Connect to container
docker exec -it oracle-test bash

# Remove Oracle (deletes all data!)
docker rm -f oracle-test
```

## Troubleshooting

### Oracle won't start
- Check Docker is running: `docker ps`
- Check logs: `docker logs oracle-test`
- Ensure port 1521 is not already in use: `lsof -i :1521`

### Can't connect to Oracle
- Wait 1-2 minutes after starting the container
- Verify container is running: `docker ps | grep oracle-test`
- Check Oracle status: `docker logs oracle-test | grep "DATABASE IS READY"`

### cx_Oracle errors
- Ensure Oracle Instant Client is installed
- Set environment variables if needed:
  ```bash
  export ORACLE_HOME=/path/to/instantclient
  export LD_LIBRARY_PATH=$ORACLE_HOME:$LD_LIBRARY_PATH
  ```

## Alternative: Oracle Cloud Free Tier

If you prefer not to use Docker, you can use Oracle Cloud's Always Free tier:

1. Sign up at [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/)
2. Create an Autonomous Database (Always Free)
3. Download the wallet file
4. Update connection details in `config/config.yaml`

## Next Steps

After setting up Oracle:
1. Set up PostgreSQL (already installed via Homebrew)
2. Create a target database in PostgreSQL
3. Run the migration tool
4. Validate the migrated data

Happy migrating! 🚀
