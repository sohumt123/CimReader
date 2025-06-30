#!/bin/bash
set -e

echo "Python version:"
python --version
echo "Node version:"
node --version || echo "Node not available"

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing Python packages..."
pip install --prefer-binary -r requirements.txt

echo "Installing Playwright system dependencies..."
# The key is to install Playwright's system dependencies properly
playwright install-deps chromium || echo "playwright install-deps failed, trying alternative..."

echo "Installing Playwright browsers with detailed logging..."
# Set environment variables for better control
export PLAYWRIGHT_BROWSERS_PATH="/opt/render/.cache/ms-playwright"

# Install browsers with maximum logging and error handling
playwright install chromium --verbose || {
    echo "Standard install failed, trying with force..."
    playwright install chromium --force || {
        echo "Force install failed, trying manual approach..."
        
        # Try to create the directory structure manually
        mkdir -p /opt/render/.cache/ms-playwright
        
        # Re-attempt installation
        PLAYWRIGHT_BROWSERS_PATH="/opt/render/.cache/ms-playwright" playwright install chromium || {
            echo "All installation attempts failed. Checking what we have..."
            ls -la /opt/render/.cache/ms-playwright/ || echo "Cache directory doesn't exist"
            find /opt/render -name "*chromium*" 2>/dev/null || echo "No chromium found"
            find /usr -name "*chromium*" 2>/dev/null || echo "No system chromium found"
        }
    }
}

echo "Verifying Playwright installation..."
python -c "
import sys
import os
from playwright.sync_api import sync_playwright

try:
    with sync_playwright() as p:
        # Try to get the executable path
        try:
            executable_path = p.chromium.executable_path
            print(f'Chromium executable found at: {executable_path}')
            
            # Check if the executable actually exists
            if os.path.exists(executable_path):
                print('✅ Executable file exists')
            else:
                print('❌ Executable file does not exist')
                
        except Exception as e:
            print(f'Could not get executable path: {e}')
        
        # Try to launch browser
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
        print('✅ Browser launch successful')
        browser.close()
        print('✅ Playwright verification complete')
        
except Exception as e:
    print(f'❌ Playwright verification failed: {e}')
    
    # Show debugging info
    print('\\nDebugging info:')
    print('Environment variables:')
    for key, value in os.environ.items():
        if 'PLAYWRIGHT' in key or 'BROWSER' in key:
            print(f'  {key}={value}')
    
    print('\\nSearching for browser installations:')
    import glob
    potential_paths = [
        '/opt/render/.cache/ms-playwright/chromium-*/chrome-linux/chrome',
        '/opt/render/.cache/ms-playwright/*/chrome-linux/chrome',
        '/usr/bin/chromium*',
        '/usr/bin/google-chrome*'
    ]
    
    for pattern in potential_paths:
        matches = glob.glob(pattern)
        if matches:
            print(f'  Found: {matches}')
    
    sys.exit(1)
"

echo "Build complete!" 