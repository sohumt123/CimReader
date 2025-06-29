#!/bin/bash
set -e

echo "Python version:"
python --version

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing Python packages..."
pip install --prefer-binary -r requirements.txt

echo "Installing Playwright browsers..."
# Set environment for Playwright installation
export PLAYWRIGHT_BROWSERS_PATH="/opt/render/.cache/ms-playwright"

# Install Playwright browsers with all dependencies
playwright install --with-deps chromium

# Verify installation
echo "Verifying Playwright installation..."
python -c "
import sys
from playwright.sync_api import sync_playwright
try:
    with sync_playwright() as p:
        browser_path = p.chromium.executable_path
        print(f'Chromium executable found at: {browser_path}')
        print('Playwright installation successful!')
except Exception as e:
    print(f'Playwright verification failed: {e}')
    sys.exit(1)
"

echo "Build complete!" 