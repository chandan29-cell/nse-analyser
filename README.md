# NSE Analyser
[![CI](https://github.com/chandan29-cell/nse-analyser/actions/workflows/ci.yml/badge.svg)](https://github.com/chandan29-cell/nse-analyser/actions/workflows/ci.yml)

This repository scaffolds a production-minded NSE stock screener and recommendation engine.

Quick start (backend only):

1. Create a virtual environment and install requirements:

```bash
python -m venv .venv
source .venv/bin/activate  # on Windows use .venv\Scripts\activate
pip install -r requirements.txt
```

2. Run the backend API:

```bash
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

3. Create desktop shortcut (Windows PowerShell):

```powershell
cd "path\to\repo"
.\scripts\create_shortcut.ps1
```

Notes:
- The system is intentional about data: if any external data is unavailable it returns "Data unavailable" and does not fabricate values.
- Frontend skeleton is under `frontend/` and is a minimal React + Tailwind starter.

Data providers
-
The scaffold supports two kinds of providers:

- Price/time-series: `yfinance` (already used for historical prices).
- Fundamentals/earnings: `Finnhub` (recommended stable provider).

To enable Finnhub for real fundamentals and earnings, add your API key to `.env` as `FINNHUB_API_KEY` (see `.env.example`). When the key is missing, the system will safely mark fundamentals as unavailable.
