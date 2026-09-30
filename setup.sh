#!/usr/bin/env bash
# Creates project folders and a virtual environment, then installs dependencies.
set -e
cd "$(dirname "$0")"

mkdir -p data/raw data/processed data/plots tests src

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Setup complete. Activate with: source venv/bin/activate"
