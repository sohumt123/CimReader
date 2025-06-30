#!/usr/bin/env bash
# exit on error
set -o errexit

echo "--- Installing dependencies ---"
python -m pip install -r requirements.txt

echo "--- Installing Playwright browsers ---"
# We remove --with-deps because it requires sudo permissions which are not
# available in the Render build environment. We rely on the base system
# image having the necessary shared libraries for Chromium.
python -m playwright install chromium

echo "--- Build finished successfully ---" 