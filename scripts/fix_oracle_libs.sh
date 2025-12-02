#!/bin/bash

# Script to fix Oracle Instant Client library path issues

echo "=== Fixing Oracle Instant Client Library Paths ==="

# Set the Instant Client directory
INSTANT_CLIENT_DIR="/opt/oracle/instantclient_21_12"

# Check if the directory exists
if [ ! -d "$INSTANT_CLIENT_DIR" ]; then
    echo "❌ Oracle Instant Client directory not found at $INSTANT_CLIENT_DIR"
    echo "Please ensure Oracle Instant Client is installed first."
    exit 1
fi

echo "✓ Found Instant Client at $INSTANT_CLIENT_DIR"

# Configure ldconfig
echo "📝 Configuring system library paths..."
echo "$INSTANT_CLIENT_DIR" | sudo tee /etc/ld.so.conf.d/oracle-instantclient.conf > /dev/null

# Run ldconfig to update the cache
echo "🔄 Updating library cache..."
sudo ldconfig

# Verify the libraries are found
echo ""
echo "🔍 Verifying library configuration..."
if ldconfig -p | grep -q libclntsh.so; then
    echo "✓ libclntsh.so is registered"
else
    echo "⚠️  libclntsh.so not found in library cache"
fi

if ldconfig -p | grep -q libnnz21.so; then
    echo "✓ libnnz21.so is registered"
else
    echo "⚠️  libnnz21.so not found in library cache"
fi

echo ""
echo "=== Library Path Configuration Complete ==="
echo "You can now run your migration script."
