#!/bin/bash

# Oracle Connection Diagnostic and Fix Script

echo "=== Oracle Connection Diagnostic ==="
echo ""

# Check if Docker is running
if ! docker ps &> /dev/null; then
    echo "❌ Docker is not running!"
    echo "Please start Docker Desktop and try again."
    exit 1
fi

echo "✓ Docker is running"
echo ""

# Check Oracle containers
echo "Checking Oracle containers..."
ORACLE_CONTAINER=$(docker ps -a --filter "name=oracle" --format "{{.Names}}" | head -1)

if [ -z "$ORACLE_CONTAINER" ]; then
    echo "❌ No Oracle container found!"
    echo ""
    echo "To create an Oracle container, run:"
    echo "  ./scripts/setup_oracle_docker.sh"
    exit 1
fi

echo "Found container: $ORACLE_CONTAINER"
echo ""

# Check if container is running
if ! docker ps --format "{{.Names}}" | grep -q "$ORACLE_CONTAINER"; then
    echo "⚠️  Container '$ORACLE_CONTAINER' is not running"
    echo ""
    echo "Starting container..."
    docker start "$ORACLE_CONTAINER"
    echo "⏳ Waiting 30 seconds for Oracle to start..."
    sleep 30
    echo ""
fi

# Check container status
CONTAINER_STATUS=$(docker inspect --format='{{.State.Status}}' "$ORACLE_CONTAINER" 2>/dev/null)
echo "Container status: $CONTAINER_STATUS"

if [ "$CONTAINER_STATUS" != "running" ]; then
    echo "❌ Container is not running!"
    echo "Attempting to start..."
    docker start "$ORACLE_CONTAINER"
    sleep 10
fi

# Check if port 1521 is exposed
echo ""
echo "Checking port 1521..."
PORT_CHECK=$(docker port "$ORACLE_CONTAINER" 2>/dev/null | grep 1521 || echo "")

if [ -z "$PORT_CHECK" ]; then
    echo "⚠️  Port 1521 is not exposed!"
    echo ""
    echo "The container may need to be recreated with port mapping."
    echo "Current container ports:"
    docker port "$ORACLE_CONTAINER" 2>/dev/null || echo "  (none exposed)"
    echo ""
    echo "To fix, stop and remove the container, then run:"
    echo "  ./scripts/setup_oracle_docker.sh"
else
    echo "✓ Port mapping found: $PORT_CHECK"
fi

# Check Oracle logs for readiness
echo ""
echo "Checking Oracle database status..."
LATEST_LOG=$(docker logs --tail 20 "$ORACLE_CONTAINER" 2>&1)

if echo "$LATEST_LOG" | grep -q "DATABASE IS READY"; then
    echo "✓ Oracle database is ready!"
elif echo "$LATEST_LOG" | grep -q "Starting Oracle"; then
    echo "⏳ Oracle is still starting... (this can take 1-2 minutes)"
    echo "   Run 'docker logs -f $ORACLE_CONTAINER' to monitor progress"
else
    echo "⚠️  Oracle status unclear. Recent logs:"
    echo "$LATEST_LOG" | tail -5
fi

# Test connection if sqlplus is available
echo ""
if command -v sqlplus &> /dev/null; then
    echo "Testing connection with sqlplus..."
    # Load env vars if .env exists
    if [ -f .env ]; then
        source .env
    fi
    
    ORACLE_HOST=${ORACLE_HOST:-localhost}
    ORACLE_PORT=${ORACLE_PORT:-1521}
    ORACLE_SERVICE_NAME=${ORACLE_SERVICE_NAME:-XEPDB1}
    ORACLE_USERNAME=${ORACLE_USERNAME:-testuser}
    ORACLE_PASSWORD=${ORACLE_PASSWORD:-testpass}
    
    CONN_STRING="${ORACLE_USERNAME}/${ORACLE_PASSWORD}@${ORACLE_HOST}:${ORACLE_PORT}/${ORACLE_SERVICE_NAME}"
    
    echo "Attempting: sqlplus $ORACLE_USERNAME/***@${ORACLE_HOST}:${ORACLE_PORT}/${ORACLE_SERVICE_NAME}"
    
    # Try connection (timeout after 5 seconds)
    timeout 5 sqlplus -S "$CONN_STRING" <<EOF 2>&1 | head -5
SELECT 'Connection successful!' FROM DUAL;
EXIT;
EOF
    
    if [ $? -eq 0 ]; then
        echo "✓ Connection successful!"
    else
        echo "❌ Connection failed"
        echo ""
        echo "Troubleshooting steps:"
        echo "1. Wait 1-2 minutes after starting container"
        echo "2. Check logs: docker logs $ORACLE_CONTAINER"
        echo "3. Verify port mapping: docker port $ORACLE_CONTAINER"
        echo "4. Check .env file has correct connection details"
    fi
else
    echo "ℹ️  sqlplus not found (optional - not required for Python connections)"
fi

echo ""
echo "=== Summary ==="
echo "Container: $ORACLE_CONTAINER"
echo "Status: $CONTAINER_STATUS"
if [ -n "$PORT_CHECK" ]; then
    echo "Port: $PORT_CHECK"
fi
echo ""
echo "If connection still fails:"
echo "1. Wait 1-2 minutes for Oracle to fully start"
echo "2. Check logs: docker logs -f $ORACLE_CONTAINER"
echo "3. Verify your .env or config.yaml has correct connection details"
echo "4. For Docker containers, ensure port 1521 is mapped: -p 1521:1521"

