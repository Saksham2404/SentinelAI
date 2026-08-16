import time
from fastapi import APIRouter, HTTPException

from backend.app.database.anomaly_queries import (
    get_all_analysis_runs,
    get_analysis_run,
    get_anomaly_results_for_run,
    get_aggregate_stats
)

router = APIRouter(
    prefix="/api/history",
    tags=["History"]
)

# Global in-memory cache for aggregate stats
_stats_cache = {
    "data": None,
    "expiry": 0.0
}
CACHE_TTL_SECONDS = 30.0


@router.get("/runs")
def list_analysis_runs(limit: int = 50):
    """List all past analysis runs, newest first."""
    runs = get_all_analysis_runs(limit=limit)
    return {"runs": runs}


@router.get("/runs/{run_id}")
def get_run_detail(run_id: int):
    """Get details of a specific analysis run including its anomaly results."""
    run = get_analysis_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Analysis run not found.")

    # Convert created_at to isoformat if it's a datetime
    if run.get("created_at") and hasattr(run["created_at"], "isoformat"):
        run["created_at"] = run["created_at"].isoformat()

    anomalies = get_anomaly_results_for_run(run_id)
    run["anomaly_results"] = anomalies
    return run


@router.get("/stats")
def get_stats():
    """Get cumulative statistics across all analysis runs, with a 30s cache."""
    now = time.time()
    if _stats_cache["data"] is not None and now < _stats_cache["expiry"]:
        return _stats_cache["data"]

    stats = get_aggregate_stats()
    _stats_cache["data"] = stats
    _stats_cache["expiry"] = now + CACHE_TTL_SECONDS
    return stats

