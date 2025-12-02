#!/bin/bash
if [ -f .env ]; then
    echo "Loading environment variables from .env"
    source .env
else
    echo "⚠️ .env file not found. Skipping environment variable loading."
fi

echo "=== PostgreSQL Setup for Migration Testing ==="
echo ""

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed!"
    echo "Installing PostgreSQL via Homebrew..."
    brew install postgresql@14
fi

echo "✓ PostgreSQL is installed"
echo ""

# Start PostgreSQL service
echo "Starting PostgreSQL service..."
brew services start postgresql@14

# Wait for PostgreSQL to start
echo "Waiting for PostgreSQL to start..."
sleep 3

# Check if PostgreSQL is running
if pg_isready -q; then
    echo "✓ PostgreSQL is running"
else
    echo "⏳ PostgreSQL is starting... (waiting 5 more seconds)"
    sleep 5
fi

echo ""
echo "Creating test database and user..."

# Create database and user
psql postgres << EOF
-- Drop database if exists
DROP DATABASE IF EXISTS migration_test;

-- Drop user if exists
DROP USER IF EXISTS postgres;

-- Create user
CREATE USER postgres WITH PASSWORD 'testpass';

-- Create database
CREATE DATABASE migration_test OWNER postgres;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE migration_test TO postgres;

\c migration_test

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO postgres;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO postgres;

\q
EOF

echo ""
echo "✓ PostgreSQL setup complete!"
echo ""
echo "=========================================="
echo "PostgreSQL Connection Details:"
echo "=========================================="
echo "  Host:     ${PG_HOST}"
echo "  Port:     ${PG_PORT}"
echo "  Database: ${PG_DATABASE}"
echo "  Username: ${PG_USER}"
echo "  Password: ${PG_PASSWORD}"
echo "=========================================="
echo ""
echo "Test connection:"
echo "  psql -h ${PG_HOST} -U ${PG_USER} -d ${PG_DATABASE}"
echo ""
echo "Stop PostgreSQL:"
echo "  brew services stop postgresql@14"
echo ""
echo "Start PostgreSQL:"
echo "  brew services start postgresql@14"
echo ""
