#!/bin/bash
#
# Sat-Sight UI Launcher
# Ensures correct conda environment and Python path
#

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "$PROJECT_ROOT")"

echo "=========================================="
echo "   Sat-Sight Web Interface"
echo "=========================================="
echo ""

# Get system IP
IP_ADDRESS=$(hostname -I | awk '{print $1}' 2>/dev/null || echo "localhost")

# Activate conda environment
echo "Activating genaienv environment..."
source ~/anaconda3/etc/profile.d/conda.sh 2>/dev/null || source ~/miniconda3/etc/profile.d/conda.sh 2>/dev/null || true
conda activate genaienv

# Check if activation worked
if [ "$CONDA_DEFAULT_ENV" != "genaienv" ]; then
    echo "ERROR: Failed to activate genaienv environment"
    echo ""
    echo "Please manually activate:"
    echo "  conda activate genaienv"
    echo "  cd $PROJECT_ROOT/ui"
    echo "  streamlit run app_enhanced.py"
    exit 1
fi

echo "Environment: $CONDA_DEFAULT_ENV"
echo ""

# Set Python path to include parent directory (GenAi_Project)
export PYTHONPATH="$PARENT_DIR:$PYTHONPATH"

# Check for .env file
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo "WARNING: .env file not found in $PROJECT_ROOT"
    echo "   API keys may not be loaded properly"
    echo ""
fi

# Change to project root (not ui directory)
cd "$PROJECT_ROOT"

# Verify the UI file exists
if [ ! -f "ui/app_enhanced.py" ]; then
    echo "ERROR: ui/app_enhanced.py not found!"
    echo "   Looking in: $PROJECT_ROOT/ui/app_enhanced.py"
    echo ""
    echo "   Available files:"
    ls -la ui/*.py 2>/dev/null || echo "   No Python files found in ui/"
    exit 1
fi

echo "Starting Streamlit server..."
echo "   Working directory: $PROJECT_ROOT"
echo ""
echo "Access URLs:"
echo "   Local:    http://localhost:8501"
echo "   Network:  http://$IP_ADDRESS:8501"
echo ""
echo "=========================================="
echo "Press Ctrl+C to stop the server"
echo "=========================================="
echo ""

# Run Streamlit with full path to app_enhanced.py
# Using 0.0.0.0 to allow network access (change to localhost for local-only)
streamlit run ui/app_enhanced.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.gatherUsageStats=false
