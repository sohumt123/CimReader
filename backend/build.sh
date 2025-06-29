#!/bin/bash
set -e

echo "Python version:"
python --version

echo "Installing Python packages..."
pip install --upgrade pip

# Install packages with specific Python 3.11 compatibility
pip install -r requirements.txt

echo "Installing Playwright browsers..."
playwright install chromium

echo "Build complete!" 