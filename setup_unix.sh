#!/usr/bin/env bash
set -euo pipefail
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
npm install
test -f .env || cp .env.example .env
echo "Setup complete. Add your API key to .env, activate .venv, then run: python start.py"
