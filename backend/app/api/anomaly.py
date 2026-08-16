from fastapi import APIRouter, UploadFile, File, HTTPException

from backend.app.services.log_parser import parse_log_file
from backend.app.services.feature_engineering import engineer_features
from backend.app.ml.anomaly_detector import AnomalyDetector

from backend.app.database.anomaly_queries import (
    save_analysis_run,
    save_anomaly_results
)

from backend.app.graph.workflow import create_workflow

router = APIRouter(
    prefix="/anomaly",
    tags=["Anomaly Detection"]
)


@router.post("/detect")
async def detect_anomalies(
    file: UploadFile = File(...)
):
    """
    Upload a log file, generate features,
    train the Isolation Forest model,
    and detect anomalies.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file uploaded"
        )

    content = await file.read()

    try:
        text_content = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="File must be UTF-8 encoded"
        )

    # Step 1: Parse logs
    events, skipped_lines = parse_log_file(text_content)

    if not events:
        raise HTTPException(
            status_code=400,
            detail="No valid log events found"
        )

    # Step 2: Generate features
    feature_windows = engineer_features(events)

    if not feature_windows:
        raise HTTPException(
            status_code=400,
            detail="Could not generate features"
        )

    # Step 3: Create and train model
    detector = AnomalyDetector()

    detector.train(feature_windows)

    # Step 4: Detect anomalies
    results = detector.predict(feature_windows)

    anomaly_count = sum(
        1 for result in results
        if result["is_anomaly"]
    )

        # Step 5: Save analysis run to PostgreSQL
    analysis_run_id = save_analysis_run(
        filename=file.filename,
        total_lines=len(text_content.splitlines()),
        parsed_events=len(events),
        skipped_lines=skipped_lines,
        feature_windows=len(feature_windows),
        anomalies_detected=anomaly_count
    )

    # Step 6: Save individual anomaly results
    save_anomaly_results(
        analysis_run_id=analysis_run_id,
        results=results
    )

    # Step 7: Run the LangGraph investigation workflow
    workflow = create_workflow()

    workflow_result = workflow.invoke(
        {
            "analysis_run_id": analysis_run_id,
            "anomaly_results": results
        }
    )

    # Step 8: Return complete SentinelAI investigation
    return {
        "analysis_run_id": analysis_run_id,
        "filename": file.filename,
        "total_lines": len(text_content.splitlines()),
        "parsed_events": len(events),
        "skipped_lines": skipped_lines,
        "feature_windows": len(feature_windows),
        "anomalies_detected": anomaly_count,
        "results": results,

        "investigation": {
            "analysis": workflow_result.get("analysis"),
            "evaluation": workflow_result.get("evaluation"),
            "final_result": workflow_result.get("final_result")
        }
    }