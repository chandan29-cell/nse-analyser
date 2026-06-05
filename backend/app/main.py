from fastapi import FastAPI
from .api import router

app = FastAPI(title="NSE Analyser API", version="0.1.0")
app.include_router(router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
