#!/bin/bash
set -e

echo "Python version:"
python --version

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing Python packages..."
# Try pre-compiled wheels first, then fallback to regular install
pip install --prefer-binary -r requirements.txt

echo "Installing Playwright browsers..."
playwright install chromium

echo "Build complete!" 