from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from backend.app.api.logs import router as logs_router
from backend.app.api.anomaly import router as anomaly_router
from backend.app.api.investigate import router as investigate_router
from backend.app.api.mock_investigate import router as mock_investigate_router
from backend.app.api.history import router as history_router
from backend.app.database.connection import get_db_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables automatically on startup
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_runs (
                id SERIAL PRIMARY KEY,
                filename VARCHAR(255) NOT NULL,
                total_lines INTEGER NOT NULL,
                parsed_events INTEGER NOT NULL,
                skipped_lines INTEGER NOT NULL,
                feature_windows INTEGER NOT NULL,
                anomalies_detected INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS anomaly_results (
                id SERIAL PRIMARY KEY,
                analysis_run_id INTEGER NOT NULL,
                window_start TIMESTAMP NOT NULL,
                window_end TIMESTAMP NOT NULL,
                service VARCHAR(255),
                total_events INTEGER NOT NULL,
                is_anomaly BOOLEAN NOT NULL,
                anomaly_score DOUBLE PRECISION NOT NULL,
                CONSTRAINT fk_analysis_run
                    FOREIGN KEY (analysis_run_id)
                    REFERENCES analysis_runs(id)
                    ON DELETE CASCADE
            );
        """)
        connection.commit()
        cursor.close()
        connection.close()
        print("SentinelAI database tables verified/created successfully.")
    except Exception as e:
        print(f"Failed to auto-create database tables on startup: {e}")

    # Index RAG knowledge base on startup
    try:
        from backend.app.rag.indexer import index_knowledge_base
        kb_path = "backend/data/knowledge_base"
        import os
        if not os.path.exists(kb_path):
            kb_path = "data/knowledge_base"
        result = index_knowledge_base(kb_path)
        print(f"RAG Knowledge Base indexed: {result}")
    except Exception as e:
        print(f"Failed to index knowledge base on startup: {e}")

    yield

app = FastAPI(
    title="SentinelAI",
    description="AI-powered incident investigation and root cause analysis system.",
    version="1.0.0",
    lifespan=lifespan
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