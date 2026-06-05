# Deployment Guide

This guide covers running NSE Analyser locally with Docker, deployment options, and troubleshooting.

## Local Deployment with Docker

### Prerequisites
- Docker Desktop installed ([download](https://www.docker.com/products/docker-desktop))
- Git (for cloning the repo)

### Quick Start

1. **Clone and enter the repo:**
   ```bash
   git clone https://github.com/chandan29-cell/nse-analyser.git
   cd nse-analyser
   ```

2. **Create `.env` file (optional, for Finnhub):**
   ```bash
   cp .env.example .env
   # Edit .env and add FINNHUB_API_KEY if you have one
   # If omitted, the system will safely use Yahoo fallback
   ```

3. **Start the backend with Docker Compose:**
   ```bash
   docker-compose up -d
   ```
   - Backend API available at: `http://localhost:8000`
   - Health check: `curl http://localhost:8000/health`
   - Logs: `docker-compose logs -f backend`

4. **Stop the services:**
   ```bash
   docker-compose down
   ```

### View Logs

```bash
# Follow backend logs in real-time
docker-compose logs -f backend

# View full logs with timestamps
docker-compose logs backend --timestamps
```

### Rebuild After Code Changes

```bash
# Rebuild Docker image and restart
docker-compose up -d --build
```

### Access the API

The API documentation is available at:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

Example API calls:

```bash
# Health check
curl http://localhost:8000/health

# Scan stocks (POST request)
curl -X POST http://localhost:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["INFY", "TCS"], "analysis_type": "trading"}'

# Analyze a single stock
curl http://localhost:8000/api/stock/INFY

# Fetch HTML (for scraping support)
curl "http://localhost:8000/api/fetch?url=https://example.com"
```

## Environment Variables

Supported variables (set in `.env` or via `docker-compose` environment):

| Variable | Description | Required | Default |
|----------|-------------|----------|----------|
| `FINNHUB_API_KEY` | API key for Finnhub (optional) | No | None |
| `API_HOST` | Backend host binding | No | `0.0.0.0` |
| `API_PORT` | Backend port | No | `8000` |

### Example `.env`
```env
FINNHUB_API_KEY=your_key_here
API_HOST=0.0.0.0
API_PORT=8000
```

## Production Deployment

### Cloud Options

#### 1. **Heroku** (Easiest)
```bash
# Install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli

# Login and create app
heroku login
heroku create nse-analyser-prod

# Create Procfile
echo "web: uvicorn backend.app.main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Deploy
git push heroku main
```

#### 2. **Google Cloud Run** (Recommended)
```bash
# Requires Google Cloud SDK
gcloud auth login

# Build and deploy
gcloud run deploy nse-analyser \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars FINNHUB_API_KEY=your_key
```

#### 3. **AWS (Lambda + API Gateway)**
- Use AWS SAM or CloudFormation
- Deploy as Docker image to ECR, then Lambda
- Set up API Gateway as front door
- Environment variables via Lambda console

#### 4. **DigitalOcean App Platform**
- Connect GitHub repo
- Auto-deploy on push (optional)
- Built-in monitoring and logs

### Docker Registry (for any platform)

1. **Build and tag image:**
   ```bash
   docker build -t nse-analyser:latest .
   docker tag nse-analyser:latest your-registry/nse-analyser:latest
   ```

2. **Push to registry:**
   ```bash
   # Docker Hub
   docker push your-registry/nse-analyser:latest

   # Or Google Container Registry
   gcloud builds submit --tag gcr.io/your-project/nse-analyser
   ```

3. **Pull and run:**
   ```bash
   docker run -p 8000:8000 \
     -e FINNHUB_API_KEY=your_key \
     nse-analyser:latest
   ```

## Troubleshooting

### Port 8000 Already in Use
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process or use a different port
docker-compose up -d -e API_PORT=9000
```

### Docker Daemon Not Running
```bash
# macOS/Linux
docker-compose logs backend  # Check if daemon is running

# Windows
# Restart Docker Desktop from system tray
```

### API Key Issues
- Omit `FINNHUB_API_KEY` in `.env` — system will use Yahoo fallback (fully functional)
- Invalid key logs warnings but doesn't crash
- Check logs: `docker-compose logs backend`

### Container Exits Immediately
```bash
# Check logs for error
docker-compose logs backend

# Rebuild from scratch
docker-compose down
docker-compose up -d --build
```

## Monitoring & Maintenance

### Health Checks
```bash
# API is up
curl http://localhost:8000/health

# Full system status (when implemented)
curl http://localhost:8000/status
```

### Disk Usage
```bash
# Clean up unused images/volumes
docker system prune

# Full cleanup (warning: removes unused everything)
docker system prune -a
```

### Updating the App
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose up -d --build
```

## Performance Tuning

### Docker Resource Limits
Edit `docker-compose.yml` to add resource constraints:
```yaml
services:
  backend:
    # ... existing config ...
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

### Connection Pooling
Enable in `requirements.txt` (already included):
- `requests` with connection pooling (default in backend)
- `yfinance` reuses connections

## Next Steps

- **Frontend:** Build React dashboard (see `frontend/README.md`)
- **Data ingestion:** Set up scheduled data updates with APScheduler
- **Notifications:** Add alerts for trading signals (email, SMS, Slack)
- **Monitoring:** Integrate with Sentry for error tracking

## Support

For issues or questions:
1. Check [GitHub Issues](https://github.com/chandan29-cell/nse-analyser/issues)
2. Review logs: `docker-compose logs backend`
3. Test without Docker: `python -m uvicorn backend.app.main:app --reload`
