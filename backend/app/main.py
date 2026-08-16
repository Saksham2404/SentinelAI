from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI

from backend.app.api.logs import router as logs_router
from backend.app.api.anomaly import router as anomaly_router
from backend.app.api.investigate import router as investigate_router
from backend.app.api.mock_investigate import router as mock_investigate_router
from backend.app.api.history import router as history_router

app = FastAPI(
    title="SentinelAI",
    description="AI-powered incident investigation and root cause analysis system.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(logs_router)
app.include_router(anomaly_router)
app.include_router(investigate_router)
app.include_router(mock_investigate_router)
app.include_router(history_router)

@app.get("/")
def root():
    return {
        "project": "SentinelAI",
        "status": "running",
        "message": "SentinelAI backend is running successfully."
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }