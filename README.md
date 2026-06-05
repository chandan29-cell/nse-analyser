# NSE Analyser

[![CI](https://github.com/chandan29-cell/nse-analyser/actions/workflows/ci.yml/badge.svg)](https://github.com/chandan29-cell/nse-analyser/actions/workflows/ci.yml)

A **production-ready** NSE stock screener and recommendation engine with technical analysis, fundamental analysis, earnings insights, and sentiment-based anomaly detection.

**Status:** v0.1.0 — Core features complete, CI validated ✅, Docker ready, React dashboard included

## Features

### 📊 Core Analysis
- **Technical Analysis** — EMA, RSI, MACD, Bollinger Bands, ADX, Support/Resistance, ATR-based stop-loss/targets
- **Fundamental Analysis** — P/E ratio, market cap, revenue, EPS, profit margins, ROE, debt-to-equity
- **Earnings Insights** — Earnings call parsing, EPS vs. consensus tracking, guidance analysis
- **Quarterly Tracking** — Multi-quarter metrics, trend analysis, cash flow quality assessment

### 🎯 Intelligent Signals
- **Trading Signals** — Rule-based short-term buy/sell recommendations
- **Investing Signals** — Long-term value play identification
- **SEAD/PEAD Detection** — Sell-side and post-earnings anomaly drift for arbitrage opportunities
- **Sentiment Analysis** — Bullish/bearish tone detection from earnings calls and news

### 🎨 User Interface
- **React Dashboard** — Modern dark-themed UI with Recharts visualizations
- **Stock Search** — Real-time lookup and full analysis
- **Quick Scan** — Bulk analysis of multiple symbols
- **Responsive Design** — Works on desktop, tablet, mobile

### 🔧 Production-Ready
- **Docker Containerization** — Single-command deployment
- **GitHub Actions CI** — Automated testing on Python 3.11
- **Graceful Degradation** — Returns "Data unavailable" instead of fabricating values
- **Dual-Provider Strategy** — Finnhub (primary) + Yahoo Finance (fallback)

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone repo
git clone https://github.com/chandan29-cell/nse-analyser.git
cd nse-analyser

# Start backend (port 8000)
docker-compose up -d

# Start frontend (port 3000)
cd frontend && npm install && npm run dev
```

**Backend API:** http://localhost:8000 (docs at `/docs`)
**Frontend:** http://localhost:3000

### Option 2: Local Setup

```bash
# Backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn backend.app.main:app --reload

# Frontend (in new terminal)
cd frontend
npm install
npm run dev
```

### Option 3: Manual Desktop Shortcut (Windows)

```powershell
.\scripts\create_shortcut.ps1
```

## API Endpoints

### Stock Analysis
- `GET /health` — Health check
- `GET /api/stock/{symbol}` — Full analysis for single stock
- `POST /api/scan` — Bulk scan of multiple stocks
  ```json
  {
    "symbols": ["INFY", "TCS"],
    "analysis_type": "trading"  // or "investing"
  }
  ```
- `GET /api/fetch?url=...` — HTML fetcher (for data scraping)

**Full documentation:** http://localhost:8000/docs

## Data Providers (Finalized Strategy)

### Primary: Finnhub API
- **What:** Fundamentals, earnings, company data
- **Setup:** Add `FINNHUB_API_KEY` to `.env` (free tier available)
- **When missing:** System safely marks data unavailable (no fabrication)

### Fallback: Yahoo Finance
- **What:** Price history, volume, technical data
- **Setup:** No configuration needed — works out-of-box
- **Behavior:** Automatic fallback when Finnhub unavailable

### Data Quality
✅ **No fabrication** — Returns empty/unavailable rather than inventing data
✅ **Graceful degradation** — Works with partial data
✅ **Test coverage** — All tests pass with/without API keys

## Project Architecture

### Backend (FastAPI)
```
backend/app/
├── main.py              # API entry point
├── api.py               # Endpoint handlers
├── schemas.py           # Pydantic models
└── core/
    ├── data_fetcher.py        # Multi-source data aggregation
    ├── indicators.py          # Technical analysis (EMA, RSI, MACD, etc.)
    ├── scoring.py             # Trading/investing signal generation
    ├── earnings_parser.py     # Earnings call parsing
    ├── quarterly_extractor.py # Quarterly financial trends
    ├── sentiment_analyzer.py  # SEAD/PEAD anomaly detection
    ├── finnhub_client.py      # Finnhub API wrapper
    └── scrapers.py            # Yahoo fallback scraper
```

### Frontend (React + Vite)
```
frontend/
├── src/
│   ├── App.jsx          # Main dashboard component
│   ├── main.jsx         # React entry point
│   └── index.css        # Tailwind styles
├── index.html
└── vite.config.js
```

### Testing
```
tests/
├── test_scoring.py              # Scoring engine tests
├── test_finnhub.py              # Finnhub API tests
├── test_scrapers.py             # Web scraper tests
└── test_earnings_and_sentiment.py # Earnings/sentiment tests
```

## Environment Setup

Create `.env` file (optional, for Finnhub):

```env
FINNHUB_API_KEY=your_api_key_here
API_HOST=0.0.0.0
API_PORT=8000
```

See `.env.example` for all options.

## Deployment

### Docker
```bash
docker-compose up -d
```

### Cloud Platforms
- **Heroku:** See [DEPLOYMENT.md](./DEPLOYMENT.md#heroku)
- **Google Cloud Run:** See [DEPLOYMENT.md](./DEPLOYMENT.md#google-cloud-run)
- **AWS Lambda:** See [DEPLOYMENT.md](./DEPLOYMENT.md#aws-lambda)
- **DigitalOcean:** See [DEPLOYMENT.md](./DEPLOYMENT.md#digitalocean)

For full deployment guide, see [DEPLOYMENT.md](./DEPLOYMENT.md)

## Development

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_scoring.py -v

# With coverage
pytest --cov=backend tests/
```

### Adding New Features

1. **New data source:** Update `backend/app/core/data_fetcher.py`
2. **New indicator:** Add to `backend/app/core/indicators.py`, test in `tests/test_scoring.py`
3. **New signal:** Update `backend/app/core/scoring.py`
4. **Frontend:** Add components to `frontend/src/` and integrate with API

### Architecture Decisions

- **FastAPI:** Modern, fast, built-in OpenAPI docs
- **Pydantic:** Strong typing for API contract validation
- **Vite + React:** Fast dev experience, production-ready bundler
- **Dual-provider strategy:** Reliability + no data fabrication
- **GitHub Actions:** Native CI/CD, free tier sufficient

## Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Must be 3.8+

# Install dependencies
pip install -r requirements.txt

# Check port 8000 availability
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows
```

### Frontend can't connect to backend
```bash
# Verify backend is running
curl http://localhost:8000/health

# Check CORS headers
curl -I http://localhost:8000/health

# Update API_BASE in frontend/src/App.jsx if needed
```

### Docker issues
```bash
# View logs
docker-compose logs -f backend

# Rebuild
docker-compose down
docker-compose up -d --build

# Clean everything
docker system prune -a
```

### Tests failing
```bash
# Ensure venv is activated
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt

# Run tests with verbose output
pytest -v --tb=short
```

## Roadmap

- [ ] Real-time price updates (WebSocket)
- [ ] Portfolio tracking and watchlists
- [ ] Alert notifications (email, Slack)
- [ ] Advanced backtesting engine
- [ ] Machine learning signal generation
- [ ] Mobile app (React Native)
- [ ] Options analysis module
- [ ] Sector rotation strategies

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add feature"`
4. Push to branch: `git push origin feature/your-feature`
5. Open a Pull Request

Please ensure all tests pass before submitting:
```bash
pytest
```

## License

MIT License — see LICENSE file for details

## Support

- **Issues:** [GitHub Issues](https://github.com/chandan29-cell/nse-analyser/issues)
- **Discussions:** [GitHub Discussions](https://github.com/chandan29-cell/nse-analyser/discussions)
- **Docs:** [DEPLOYMENT.md](./DEPLOYMENT.md), [frontend/README.md](./frontend/README.md)

## Disclaimer

**This tool is for educational and research purposes only.** 
- Not financial advice
- Past performance ≠ future results
- Always do your own research
- Consult a financial advisor before making investment decisions

---

**Made with ❤️ for stock analysis enthusiasts**