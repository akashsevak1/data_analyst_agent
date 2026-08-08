#!/bin/bash
# ============================================
#  Data Analyst Agent - Mac/Linux launcher
#  Double-click this file to start the app
# ============================================

clear
echo "============================================"
echo "  Data Analyst Agent - Starting..."
echo "============================================"
echo ""

# Move to the script's directory
cd "$(dirname "$0")"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed!"
    echo ""
    echo "Please install Python from https://python.org"
    echo "Or on Mac:   brew install python"
    echo "Or on Ubuntu: sudo apt install python3 python3-pip"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo "[1/3] Python found: $(python3 --version)"
echo ""

# Install dependencies
echo "[2/3] Checking/installing required libraries..."
python3 -m pip install -r requirements.txt --quiet
echo "Done."
echo ""

# Run the app
echo "[3/3] Launching Data Analyst Agent..."
echo "Your browser will open automatically at http://localhost:8501"
echo ""
echo "To STOP the app, close this window or press Ctrl+C"
echo "============================================"
echo ""

python3 -m streamlit run app.py
