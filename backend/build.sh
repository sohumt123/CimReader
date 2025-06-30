#!/usr/bin/env bash
# exit on error
set -o errexit

echo "--- Installing dependencies ---"
python -m pip install -r requirements.txt

echo "--- Installing Playwright browsers ---"
# Install Playwright browsers and their dependencies
python -m playwright install --with-deps chromium

echo "--- Build finished successfully ---" 