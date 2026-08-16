from fastapi import APIRouter, UploadFile, File

router = APIRouter(
    prefix="/mock/investigate",
    tags=["MockInvestigation"]
)

@router.post("/")
async def mock_investigate(file: UploadFile = File(...)):
    """Return a static mock investigation result.

    The real `/investigate/` endpoint performs heavy ML processing. This mock
    endpoint provides a lightweight response with the same JSON shape so that
    the frontend can be developed and tested without consuming Gemini API quota.
    """
    mock_result = {
        "analysis_run_id": "mock-run-123",
        "filename": file.filename,
        "pipeline_summary": {
            "total_lines": 1000,
            "parsed_events": 800,
            "skipped_lines": 200,
            "feature_windows": 50,
            "anomalies_detected": 5,
            "anomalies_investigated": 3,
            "total_pipeline_time_seconds": 1.5,
        },
        "analysis": {
            "summary": {
                "anomalies_detected": 3,
                "total_evidence_chunks": 2,
                "affected_services": ["service-a", "service-b"],
            },
            "anomalies": [],
        },
        "evaluation": {
            "impact": "Low",
            "service_impact": "Minor",
            "historical_pattern": "None",
            "repeated_services": [],
        },
        "investigation_report": "### Mock Investigation Report\n\nNo real analysis performed. This is a placeholder response for UI testing.",
    }
    return mock_result
