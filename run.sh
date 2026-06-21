#!/bin/bash

# Exit on error
set -e

echo "============================================="
echo "  Global Omni-Channel Expense Tracker Launcher"
echo "============================================="

# Navigate to script directory
cd "$(dirname "$0")"

# 1. Setup Virtual Environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

# 2. Install dependencies
echo "Installing/updating dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 3. Setup Env file if not exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️ Please fill in your API credentials in the .env file OR use the UI configurations on first run."
fi

# 4. Start Streamlit Application
echo "Starting Streamlit Application..."
streamlit run app/ui.py
