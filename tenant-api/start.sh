#!/bin/bash

# Area X Tenant API Startup Script

set -e

echo "🚀 Area X Tenant API Startup"
echo "=============================="

# Check if running in virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: Not running in a virtual environment"
    echo "   Consider activating a venv: source venv/bin/activate"
    echo ""
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $PYTHON_VERSION"

# Check if dependencies are installed
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "⚠️  Dependencies not installed. Installing..."
    pip install -r requirements.txt
fi
echo "✓ Dependencies installed"

# Load environment variables if .env exists
if [ -f .env ]; then
    echo "✓ Loading environment from .env"
    export $(grep -v '^#' .env | xargs)
fi

# Set defaults
export PORT=${PORT:-8081}
export HOST=${HOST:-0.0.0.0}
export LOG_LEVEL=${LOG_LEVEL:-info}

echo ""
echo "📝 Configuration:"
echo "   Host: $HOST"
echo "   Port: $PORT"
echo "   Log Level: $LOG_LEVEL"
echo ""

# Start the server
echo "🌐 Starting FastAPI server..."
echo "   API Docs: http://$HOST:$PORT/docs"
echo "   Health:   http://$HOST:$PORT/health"
echo ""

exec uvicorn app.main:app \
    --host $HOST \
    --port $PORT \
    --log-level $LOG_LEVEL \
    --reload
