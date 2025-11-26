#!/bin/bash

echo "Installing Python dependencies for DBMigration..."

# Install basic dependencies (required)
echo "Installing basic dependencies..."
pip install python-dotenv pyyaml tqdm tabulate openai anthropic

echo ""
echo "✓ Basic dependencies installed!"
echo ""
echo "Optional database drivers:"
echo "  - For PostgreSQL: brew install postgresql && pip install psycopg2-binary"
echo "  - For Oracle: Download Oracle Instant Client, then pip install cx_Oracle"
echo ""
echo "You can now run: python migrate.py --interactive"
