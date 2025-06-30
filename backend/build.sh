#!/bin/bash
set -e

echo "Python version:"
python --version
python3 --version || echo "python3 not available"
echo "Node version:"
node --version || echo "Node not available"

# Check if we're using a compatible Python version
PYTHON_VERSION=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Detected Python version: $PYTHON_VERSION"

if [[ "$PYTHON_VERSION" == "3.13" ]]; then
    echo "Warning: Python 3.13 detected. Some packages may not be compatible."
    echo "Consider using Python 3.11 or 3.12 for better compatibility."
fi

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing Python packages..."
# Install packages with explicit error handling
pip install --prefer-binary -r requirements.txt || {
    echo "Package installation failed. Trying with --force-reinstall..."
    pip install --force-reinstall --prefer-binary -r requirements.txt || {
        echo "Installation still failed. Trying individual packages..."
        pip install fastapi uvicorn python-multipart python-dotenv openai pypdf jinja2
        pip install sqlalchemy==2.0.25 greenlet==3.0.3
        pip install postgrest-py supabase httpx PyMuPDF playwright==1.38.0 requests
    }
}

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