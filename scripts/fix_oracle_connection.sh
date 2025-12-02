#!/bin/bash

# Quick fix script for Oracle connection issues

echo "=== Fixing Oracle Connection ==="
echo ""

# Load environment variables
if [ -f .env ]; then
    source .env
fi

ORACLE_PORT=${ORACLE_PORT:-1521}
ORACLE_PASSWORD=${ORACLE_PASSWORD:-testpass}
ORACLE_USERNAME=${ORACLE_USERNAME:-testuser}

# Check if container exists
if docker ps -a --format "{{.Names}}" | grep -q "^oracle-test$"; then
    echo "Found existing container 'oracle-test'"
    
    # Check if it's running
    if docker ps --format "{{.Names}}" | grep -q "^oracle-test$"; then
        echo "Container is running. Checking port mapping..."
        
        # Check port mapping
        PORT_MAP=$(docker port oracle-test 2>/dev/null | grep 1521 || echo "")
        
        if [ -z "$PORT_MAP" ]; then
            echo "⚠️  Port 1521 is not properly mapped!"
            echo "Stopping and recreating container with correct port mapping..."
            docker stop oracle-test
            docker rm oracle-test
            
            echo "Creating new container with port mapping..."
            docker run -d \
              --name oracle-test \
              -p ${ORACLE_PORT}:1521 \
              -e ORACLE_PASSWORD=${ORACLE_PASSWORD} \
              -e APP_USER=${ORACLE_USERNAME} \
              -e APP_USER_PASSWORD=${ORACLE_PASSWORD} \
              gvenzl/oracle-xe:21-slim
            
            echo "⏳ Waiting 60 seconds for Oracle to start..."
            sleep 60
        else
            echo "✓ Port mapping looks correct: $PORT_MAP"
            echo "Container is running. If connection still fails, Oracle may still be starting."
            echo ""
            echo "Checking if Oracle is ready..."
            sleep 5
            if docker logs oracle-test 2>&1 | grep -q "DATABASE IS READY"; then
                echo "✓ Oracle database is ready!"
            else
                echo "⏳ Oracle is still starting. This can take 1-2 minutes."
                echo "   Monitor progress with: docker logs -f oracle-test"
            fi
        fi
    else
        echo "Container exists but is not running. Starting it..."
        docker start oracle-test
        echo "⏳ Waiting 60 seconds for Oracle to start..."
        sleep 60
    fi
else
    echo "No container found. Creating new Oracle container..."
    docker run -d \
      --name oracle-test \
      -p ${ORACLE_PORT}:1521 \
      -e ORACLE_PASSWORD=${ORACLE_PASSWORD} \
      -e APP_USER=${ORACLE_USERNAME} \
      -e APP_USER_PASSWORD=${ORACLE_PASSWORD} \
      gvenzl/oracle-xe:21-slim
    
    echo "⏳ Waiting 90 seconds for Oracle to fully start (first time takes longer)..."
    sleep 90
fi

echo ""
echo "=== Connection Test ==="
echo "Testing connection..."

# Wait a bit more and check logs
sleep 10
READY=$(docker logs oracle-test 2>&1 | grep -c "DATABASE IS READY" || echo "0")

if [ "$READY" -gt 0 ]; then
    echo "✓ Oracle database is ready!"
    echo ""
    echo "Connection details:"
    echo "  Host: localhost"
    echo "  Port: ${ORACLE_PORT}"
    echo "  Service Name: ${ORACLE_SERVICE_NAME:-XEPDB1}"
    echo "  Username: ${ORACLE_USERNAME}"
    echo "  Password: ${ORACLE_PASSWORD}"
    echo ""
    echo "Test connection with:"
    echo "  sqlplus ${ORACLE_USERNAME}/${ORACLE_PASSWORD}@localhost:${ORACLE_PORT}/${ORACLE_SERVICE_NAME:-XEPDB1}"
else
    echo "⏳ Oracle is still starting..."
    echo ""
    echo "This is normal - Oracle can take 1-2 minutes to fully start."
    echo "Monitor progress: docker logs -f oracle-test"
    echo ""
    echo "Once you see 'DATABASE IS READY' in the logs, try connecting again."
fi

echo ""
echo "=== Troubleshooting ==="
echo "If connection still fails:"
echo "1. Wait 1-2 minutes after container starts"
echo "2. Check logs: docker logs -f oracle-test"
echo "3. Verify port: docker port oracle-test"
echo "4. Test with: ./scripts/check_oracle_connection.sh"

