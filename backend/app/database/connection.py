import os
import psycopg
from dotenv import load_dotenv

load_dotenv()


def get_db_connection():
    """
    Create and return a PostgreSQL database connection,
    supporting standard environment variables for production (Railway, Render, etc.).
    """
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return psycopg.connect(db_url)

    db_config = {
        "host": os.getenv("DB_HOST") or os.getenv("POSTGRES_HOST") or os.getenv("PGHOST") or "localhost",
        "port": int(os.getenv("DB_PORT") or os.getenv("POSTGRES_PORT") or os.getenv("PGPORT") or "5432"),
        "dbname": os.getenv("DB_NAME") or os.getenv("POSTGRES_DB") or os.getenv("PGDATABASE") or "sentinelai_db",
        "user": os.getenv("DB_USER") or os.getenv("POSTGRES_USER") or os.getenv("PGUSER") or "postgres",
        "password": os.getenv("DB_PASSWORD") or os.getenv("POSTGRES_PASSWORD") or os.getenv("PGPASSWORD")
    }
    return psycopg.connect(**db_config)