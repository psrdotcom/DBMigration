#!/bin/bash

# Load environment variables
if [ -f .env ]; then
    source .env
fi

echo "=== Oracle Database Setup with Docker ==="
echo ""
echo "This script will set up Oracle Database XE (Express Edition) in Docker"
echo "and create sample tables for testing the migration tool."
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed!"
    echo "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

echo "✓ Docker is installed"
echo ""

# Pull Oracle Database XE image
echo "📦 Pulling Oracle Database XE 21c image (this may take a few minutes)..."
docker pull gvenzl/oracle-xe:21-slim

# Set defaults if not in .env
ORACLE_PORT=${ORACLE_PORT:-1521}
ORACLE_PASSWORD=${ORACLE_PASSWORD:-testpass}
ORACLE_USERNAME=${ORACLE_USERNAME:-testuser}

# Check if container already exists
if docker ps -a --format "{{.Names}}" | grep -q "^oracle-test$"; then
    echo "⚠️  Container 'oracle-test' already exists"
    read -p "Remove existing container? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing existing container..."
        docker rm -f oracle-test
    else
        echo "Starting existing container..."
        docker start oracle-test
        echo "⏳ Waiting for Oracle Database to start (this may take 1-2 minutes)..."
        sleep 60
        echo ""
        echo "✓ Oracle Database container started!"
        echo ""
        echo "Connection Details:"
        echo "  Host: ${ORACLE_HOST:-localhost}"
        echo "  Port: ${ORACLE_PORT}"
        echo "  Service Name: ${ORACLE_SERVICE_NAME:-XEPDB1}"
        echo "  Username: ${ORACLE_USERNAME}"
        echo "  Password: ${ORACLE_PASSWORD}"
        echo ""
        echo "To check if Oracle is ready: docker logs oracle-test | grep 'DATABASE IS READY'"
        exit 0
    fi
fi

# Start Oracle Database container
echo ""
echo "🚀 Starting Oracle Database container..."
docker run -d \
  --name oracle-test \
  -p ${ORACLE_PORT}:1521 \
  -e ORACLE_PASSWORD=${ORACLE_PASSWORD} \
  -e APP_USER=${ORACLE_USERNAME} \
  -e APP_USER_PASSWORD=${ORACLE_PASSWORD} \
  gvenzl/oracle-xe:21-slim

echo ""
echo "⏳ Waiting for Oracle Database to start (this may take 1-2 minutes)..."
sleep 60

echo ""
echo "✓ Oracle Database is starting!"
echo ""
echo "Connection Details:"
echo "  Host: ${ORACLE_HOST}"
echo "  Port: ${ORACLE_PORT}"
echo "  Service Name: ${ORACLE_SERVICE_NAME}"
echo "  Username: ${ORACLE_USERNAME}"
echo "  Password: ${ORACLE_PASSWORD}"
echo "  SYS Password: ${ORACLE_SYS_PASSWORD}"
echo ""
echo "To stop Oracle: docker stop oracle-test"
echo "To start Oracle: docker start oracle-test"
echo "To remove Oracle: docker rm -f oracle-test"
echo ""
echo "Next step: Run ./scripts/create_sample_tables.sql to create test tables"
