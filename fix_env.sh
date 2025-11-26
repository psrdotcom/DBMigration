#!/bin/bash

echo "=== Python Environment Diagnostic ==="
echo ""
echo "Current Python:"
which python
python --version
echo ""
echo "Current pip:"
which pip
echo ""
echo "Python site-packages location:"
python -c "import site; print(site.getsitepackages())"
echo ""
echo "=== Installing packages using python -m pip ==="
echo "This ensures packages are installed in the active Python environment"
echo ""

# Install using python -m pip to ensure correct environment
python -m pip install python-dotenv pyyaml tqdm tabulate openai anthropic

echo ""
echo "=== Verification ==="
echo "Checking if dotenv is installed:"
python -c "import dotenv; print('✓ dotenv installed successfully')" 2>&1

echo ""
echo "Testing migrate.py:"
python migrate.py --list-agents
