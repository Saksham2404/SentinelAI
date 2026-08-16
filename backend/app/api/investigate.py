from collections import defaultdict
import time

from fastapi import APIRouter, UploadFile, File, HTTPException

from backend.app.services.hdfs_parser import parse_hdfs_file
from backend.app.services.feature_engineering import engineer_features
from backend.app.ml.anomaly_detector import AnomalyDetector

from backend.app.database.anomaly_queries import (
    save_analysis_run,
    save_anomaly_results
)

from backend.app.graph.workflow import create_workflow


router = APIRouter(
    prefix="/investigate",
    tags=["Investigation"]
)


def select_representative_anomalies(
    anomaly_results,
    max_anomalies=3
):
    """
    Select representative anomalies for investigation.

    Strategy:
    1. Keep only detected anomalies.
    2. Group anomalies by service.
    3. Select the strongest anomaly from each service.
    4. Sort by anomaly score.
    5. Return up to max_anomalies.
    """

    anomalies = [
        result
        for result in anomaly_results
        if result["is_anomaly"]
    ]

    if not anomalies:
        return []

    anomalies_by_service = defaultdict(list)

    for anomaly in anomalies:
        service = anomaly["service"]

        anomalies_by_service[service].append(
            anomaly
        )

    representatives = []

    for service_anomalies in anomalies_by_service.values():

        strongest = min(
            service_anomalies,
            key=lambda item: item["anomaly_score"]
        )

        representatives.append(strongest)

    representatives.sort(
        key=lambda item: item["anomaly_score"]
    )

    return representatives[:max_anomalies]


@router.post("/")
async def investigate_log(
    file: UploadFile = File(...)
):
    """
    Run the complete SentinelAI investigation pipeline.
    """

    start_time = time.time()

    # --------------------------------------------
    # STEP 1: VALIDATE FILE
    # --------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file uploaded."
        )

    # --------------------------------------------
    # STEP 2: READ FILE
    # --------------------------------------------

    try:
        file_bytes = await file.read()

        content = file_bytes.decode(
            "utf-8",
            errors="replace"
        )

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=f"Could not read uploaded file: {str(error)}"
        )

    total_lines = len(content.splitlines())

    # --------------------------------------------
    # STEP 3: PARSE LOGS
    # --------------------------------------------

    events, block_ids, skipped_lines = parse_hdfs_file(
        content
    )

    if not events:
        raise HTTPException(
            status_code=400,
            detail=(
                "No valid HDFS log events could be parsed "
                "from the uploaded file."
            )
        )

    parsed_events_count = len(events)

    # --------------------------------------------
    # STEP 4: FEATURE ENGINEERING
    # --------------------------------------------

    feature_windows = engineer_features(events)

    if not feature_windows:
        raise HTTPException(
            status_code=400,
            detail="Feature engineering produced no results."
        )

    # Events/block IDs no longer needed
    del events
    del block_ids

    # --------------------------------------------
    # STEP 5: ANOMALY DETECTION
    # --------------------------------------------

    detector = AnomalyDetector()

    try:
        detector.load_model()

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Baseline anomaly detection model was not found. "
                f"{str(error)}"
            )
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Could not load the baseline anomaly detection "
                f"model: {str(error)}"
            )
        )

    anomaly_results = detector.predict(
        feature_windows
    )

    anomalies_detected = sum(
        result["is_anomaly"]
        for result in anomaly_results
    )

    # --------------------------------------------
    # STEP 6: SAVE TO POSTGRESQL
    # --------------------------------------------

    analysis_run_id = save_analysis_run(
        filename=file.filename,
        total_lines=total_lines,
        parsed_events=parsed_events_count,
        skipped_lines=skipped_lines,
        feature_windows=len(feature_windows),
        anomalies_detected=anomalies_detected
    )

    save_anomaly_results(
        analysis_run_id=analysis_run_id,
        results=anomaly_results
    )

    # --------------------------------------------
    # STEP 7: SELECT ANOMALIES FOR RCA
    # --------------------------------------------

    selected_anomalies = (
        select_representative_anomalies(
            anomaly_results,
            max_anomalies=3
        )
    )

    # --------------------------------------------
    # STEP 8: LANGGRAPH INVESTIGATION
    # --------------------------------------------

    final_result = None
    analysis = None
    evaluation = None

    if selected_anomalies:

        workflow = create_workflow()

        investigation_state = {
            "analysis_run_id": analysis_run_id,
            "database_context": {},
            "anomaly_results": selected_anomalies,
            "retrieved_evidence": [],
            "analysis": None,
            "evaluation": None,
            "final_result": None
        }

        workflow_result = workflow.invoke(
            investigation_state
        )

        final_result = workflow_result[
            "final_result"
        ]

        analysis = workflow_result["analysis"]

        evaluation = workflow_result["evaluation"]

    total_time = time.time() - start_time

    # --------------------------------------------
    # STEP 9: RETURN COMPLETE RESULT
    # --------------------------------------------

    return {
        "analysis_run_id": analysis_run_id,

        "filename": file.filename,

        "pipeline_summary": {
            "total_lines": total_lines,
            "parsed_events": parsed_events_count,
            "skipped_lines": skipped_lines,
            "feature_windows": len(feature_windows),
            "anomalies_detected": anomalies_detected,
            "anomalies_investigated": len(
                selected_anomalies
            ),
            "total_pipeline_time_seconds": round(
                total_time,
                2
            )
        },

        "analysis": analysis,

        "evaluation": evaluation,

        "investigation_report": final_result
    }