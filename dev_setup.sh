#!/bin/bash

# Usage: ./dev_setup.sh <python_version>

# Check if Python version argument is provided
if [ -z "$1" ]; then
  echo "Please provide the Python version as an argument."
  exit 1
fi
# Check if Python version is supported
if [ "$1" != "3.10" ] && [ "$1" != "3.11" ]; then
  echo "Unsupported Python version. Please use 3.10 or 3.11."
  exit 1
fi
# Set up and activate a Python 3.11 virtual environment
python$1 -m venv py-orca-venv-$1
source py-orca-venv-$1/bin/activate
# Upgrade pip to latest version
pip install --upgrade pip
# Install airflow with constraints
pip install -r requirements-airflow.txt
# Install py-orca
pip install -e '.[all,testing,dev]'
