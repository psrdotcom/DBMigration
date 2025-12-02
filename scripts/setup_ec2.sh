#!/bin/bash

# Exit on error
set -e

echo "=== EC2 Setup for DBMigration Project ==="
echo "Target OS: Ubuntu 24.04 LTS"

# Update system
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install dependencies
echo "📦 Installing dependencies..."
sudo apt-get install -y ca-certificates curl gnupg git python3 python3-pip python3-venv libaio1 unzip

# Install Oracle Instant Client
echo "📦 Installing Oracle Instant Client..."
INSTANT_CLIENT_DIR="/opt/oracle"
sudo mkdir -p $INSTANT_CLIENT_DIR
cd $INSTANT_CLIENT_DIR

# Download Instant Client Basic (using a direct link if available, otherwise instructing user)
# Note: Oracle download links can be tricky. Using a known working link for 21.12 or similar.
# If this link fails, the user will need to download manually.
echo "Downloading Instant Client..."
if sudo wget https://download.oracle.com/otn_software/linux/instantclient/2112000/instantclient-basic-linux.x64-21.12.0.0.0dbru.zip; then
    sudo unzip -o instantclient-basic-linux.x64-21.12.0.0.0dbru.zip
    sudo rm instantclient-basic-linux.x64-21.12.0.0.0dbru.zip
    
    # Configure LD_LIBRARY_PATH
    echo "Configuring library paths..."
    echo "$INSTANT_CLIENT_DIR/instantclient_21_12" | sudo tee /etc/ld.so.conf.d/oracle-instantclient.conf > /dev/null
    sudo ldconfig
    echo "✓ Oracle Instant Client installed"
else
    echo "⚠️  Failed to download Oracle Instant Client automatically."
    echo "Please download 'instantclient-basic-linux.x64-21.12.0.0.0dbru.zip' manually from Oracle website"
    echo "and place it in $INSTANT_CLIENT_DIR, then unzip and configure ldconfig."
fi

# Go back to previous directory
cd - > /dev/null

# Install Docker
echo "📦 Installing Docker..."
# Add Docker's official GPG key:
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

# Install Docker packages
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Start Docker and add user to group
sudo service docker start
sudo usermod -aG docker $USER
echo "✓ Docker installed and started"

# Determine project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Setup Virtual Environment
echo ""
echo "🐍 Setting up Python Virtual Environment..."
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    python3 -m venv "$PROJECT_ROOT/.venv"
    echo "✓ Virtual environment created at $PROJECT_ROOT/.venv"
else
    echo "✓ Virtual environment already exists"
fi

# Activate and install requirements
source "$PROJECT_ROOT/.venv/bin/activate"
echo "📦 Installing Python requirements..."
pip install --upgrade pip
if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
    pip install -r "$PROJECT_ROOT/requirements.txt"
    echo "✓ Requirements installed"
else
    echo "⚠️  requirements.txt not found"
fi

echo ""
echo "🚀 Starting Database Containers..."
if [ -f "$PROJECT_ROOT/docker-compose.yml" ]; then
    echo "Found docker-compose.yml at "$PROJECT_ROOT""
    cd "$PROJECT_ROOT"
    
    # We need to run docker compose with sudo since the group change 
    # won't take effect for the current user until logout/login
    sudo docker compose up -d
    
    echo "✓ Oracle and PostgreSQL containers started!"
    echo "  - Oracle Port: 1521"
    echo "  - Postgres Port: 5432"
else
    echo "⚠️  docker-compose.yml not found in "$PROJECT_ROOT""
    echo "Please ensure you are running this script from within the DBMigration repository."
fi

echo ""
echo "=== Setup Complete ==="
echo "Please log out and log back in for Docker group changes to take effect."
echo "To start working:"
echo "  1. cd DBMigration"
echo "  2. source .venv/bin/activate"
echo "  3. Run migration tools"
