#!/usr/bin/env bash
# exit on error
set -o errexit

echo "--- Installing dependencies ---"
python -m pip install -r requirements.txt

echo "--- Installing Playwright browsers ---"
# Set a predictable, shared path for Playwright browsers.
# This ensures they are downloaded to a location that will persist
# from the build step to the runtime step.
export PLAYWRIGHT_BROWSERS_PATH=/opt/render/project/src/.playwright_cache
python -m playwright install chromium

echo "--- Build finished successfully ---" 