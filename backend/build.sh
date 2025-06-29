#!/bin/bash
set -e

echo "Python version:"
python --version

echo "Installing Python packages..."
pip install --upgrade pip

# Use only pre-compiled wheels to avoid compilation issues
echo "Installing packages with pre-compiled wheels only..."
pip install --only-binary=all -r requirements.txt || {
    echo "Failed with --only-binary, trying without compilation..."
    pip install --prefer-binary -r requirements.txt
}

echo "Installing Playwright browsers..."
playwright install chromium

echo "Build complete!" 