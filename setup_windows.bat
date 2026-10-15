@echo off
echo Setting up LegalEase...
python -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
npm install
if not exist .env copy .env.example .env
echo.
echo Setup complete. Add your API key to .env, then run:
echo .venv\Scripts\activate
echo python start.py
