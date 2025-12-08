#!/bin/bash

# Exit on error
set -e

# Configuration
VENV_DIR=".venv"
INGESTION_SCRIPT="../ingestion/load_books.py"
DEFAULT_LIMIT=50

# Parse arguments
LIMIT=${1:-$DEFAULT_LIMIT}

echo "Starting ingestion process..."

# 1. Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# 2. Activate virtual environment
source "$VENV_DIR/bin/activate"

# 3. Install dependencies
echo "Installing dependencies..."
pip install requests psycopg2-binary networkx nltk

# 4. Run ingestion script
# 4. Run ingestion script
if [[ "$1" =~ ^[0-9]+$ ]]; then
    # Backward compatibility: if first arg is a number, treat as limit
    echo "Running ingestion script with limit: $1"
    python load_books.py --num-texts "$1"
elif [ -z "$1" ]; then
    # No arguments: use default limit
    echo "Running ingestion script with default limit: $DEFAULT_LIMIT"
    python load_books.py --num-texts "$DEFAULT_LIMIT"
else
    # Arguments provided: pass them directly to the script
    echo "Running ingestion script with args: $@"
    python load_books.py "$@"
fi

echo "Ingestion complete!"
