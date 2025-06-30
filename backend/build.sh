#!/usr/bin/env bash
# exit on error
set -o errexit

# --- Start of Python version check ---
echo "--- Verifying Python version ---"
# Get the Python version in a format like "3.11"
DETECTED_VERSION=$(python --version 2>&1 | awk '{print $2}' | awk -F. '{print $1"."$2}')
EXPECTED_VERSION="3.11"

echo "Expected version: $EXPECTED_VERSION"
echo "Detected version: $DETECTED_VERSION"

if [[ "$DETECTED_VERSION" != "$EXPECTED_VERSION" ]]; then
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo "!! BUILD FAILED: Incorrect Python version detected.             !!"
  echo "!! Expected a Python 3.11.x environment, but found $DETECTED_VERSION.   !!"
  echo "!! This is the root cause of the C-extension build failures.      !!"
  echo "!!                                                              !!"
  echo "!! TO FIX: Go to your service on Render.com, click 'Manual       !!"
  echo "!! Deploy', and select 'Clear build cache & deploy'.              !!"
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  exit 1
else
  echo "--- Python version check passed. Proceeding with build. ---"
fi
# --- End of Python version check ---

echo "--- Forcing C compiler flags to use the correct Python headers ---"
PYTHON_PATH=$(which python)
VENV_ROOT=$(dirname $(dirname "$PYTHON_PATH"))
export CFLAGS="-I${VENV_ROOT}/include/python${DETECTED_VERSION}"
export CPPFLAGS="-I${VENV_ROOT}/include/python${DETECTED_VERSION}"
echo "CFLAGS and CPPFLAGS forced to: $CFLAGS"

echo "--- Installing dependencies ---"
python -m pip install -r requirements.txt

echo "--- Installing Playwright browsers ---"
# Install Playwright browsers and their dependencies
python -m playwright install --with-deps chromium

echo "--- Build finished successfully ---" 