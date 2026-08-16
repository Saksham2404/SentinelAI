from pathlib import Path
from collections import defaultdict
import time

from backend.app.services.hdfs_parser import parse_hdfs_file
from backend.app.services.feature_engineering import engineer_features
from backend.app.ml.anomaly_detector import AnomalyDetector

from backend.app.database.anomaly_queries import (
    save_analysis_run,
    save_anomaly_results
)

from backend.app.graph.workflow import create_workflow


FULL_DATASET_PATH = Path(
    "backend/data/full_dataset/HDFS.log"
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
    4. Sort representatives by anomaly score.
    5. Return up to max_anomalies.

    Lower Isolation Forest scores are more anomalous.
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
        anomalies_by_service[service].append(anomaly)

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


def main():

    print("\nFULL SENTINELAI END-TO-END INVESTIGATION")
    print("=" * 60)

    # --------------------------------------------------
    # CHECK DATASET
    # --------------------------------------------------

    if not FULL_DATASET_PATH.exists():
        print(
            f"ERROR: Dataset not found:\n"
            f"{FULL_DATASET_PATH.resolve()}"
        )
        return

    print(f"\nDataset: {FULL_DATASET_PATH.resolve()}")

    print(
        f"File size: "
        f"{FULL_DATASET_PATH.stat().st_size / (1024 * 1024):.2f} MB"
    )

    total_start_time = time.time()

    # --------------------------------------------------
    # STEP 1: READ FULL DATASET
    # --------------------------------------------------

    print("\nSTEP 1: READING FULL DATASET")

    start_time = time.time()

    content = FULL_DATASET_PATH.read_text(
        encoding="utf-8",
        errors="replace"
    )

    total_lines = len(content.splitlines())

    read_time = time.time() - start_time

    print(f"Total lines: {total_lines:,}")
    print(f"Read time: {read_time:.2f} seconds")

    # --------------------------------------------------
    # STEP 2: PARSE FULL DATASET
    # --------------------------------------------------

    print("\nSTEP 2: PARSING LOG EVENTS")

    start_time = time.time()

    events, block_ids, skipped_lines = parse_hdfs_file(
        content
    )

    # Save this BEFORE deleting events later
    parsed_events_count = len(events)

    parse_time = time.time() - start_time

    print(f"Parsed events: {parsed_events_count:,}")
    print(f"Skipped lines: {skipped_lines:,}")
    print(f"Parse time: {parse_time:.2f} seconds")

    # Free raw text because the full dataset is large
    del content

    # --------------------------------------------------
    # STEP 3: FEATURE ENGINEERING
    # --------------------------------------------------

    print("\nSTEP 3: FEATURE ENGINEERING")

    start_time = time.time()

    feature_windows = engineer_features(events)

    feature_time = time.time() - start_time

    print(
        f"Feature windows: "
        f"{len(feature_windows):,}"
    )

    print(
        f"Feature time: "
        f"{feature_time:.2f} seconds"
    )

    # Events and block IDs are no longer needed
    # after feature engineering
    del events
    del block_ids

    # --------------------------------------------------
    # STEP 4: TRAIN ISOLATION FOREST
    # --------------------------------------------------

    print("\nSTEP 4: TRAINING ISOLATION FOREST")

    detector = AnomalyDetector()

    start_time = time.time()

    trained = detector.train(feature_windows)

    training_time = time.time() - start_time

    if not trained:
        print("ERROR: Model training failed.")
        return

    print("Model training completed.")

    print(
        f"Training time: "
        f"{training_time:.2f} seconds"
    )

    # --------------------------------------------------
    # STEP 5: DETECT ANOMALIES
    # --------------------------------------------------

    print("\nSTEP 5: DETECTING ANOMALIES")

    start_time = time.time()

    anomaly_results = detector.predict(
        feature_windows
    )

    prediction_time = time.time() - start_time

    anomalies_detected = sum(
        result["is_anomaly"]
        for result in anomaly_results
    )

    print(
        f"Total windows: "
        f"{len(anomaly_results):,}"
    )

    print(
        f"Anomalies detected: "
        f"{anomalies_detected:,}"
    )

    print(
        f"Prediction time: "
        f"{prediction_time:.2f} seconds"
    )

    # --------------------------------------------------
    # STEP 6: SAVE FULL RUN TO POSTGRESQL
    # --------------------------------------------------

    print("\nSTEP 6: SAVING ANALYSIS TO POSTGRESQL")

    analysis_run_id = save_analysis_run(
        filename=FULL_DATASET_PATH.name,
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

    print(
        f"Analysis Run ID: "
        f"{analysis_run_id}"
    )

    print(
        f"Saved anomaly results: "
        f"{len(anomaly_results):,}"
    )

    # --------------------------------------------------
    # STEP 7: SELECT REPRESENTATIVE ANOMALIES
    # --------------------------------------------------

    print("\nSTEP 7: SELECTING REPRESENTATIVE ANOMALIES")

    selected_anomalies = (
        select_representative_anomalies(
            anomaly_results,
            max_anomalies=3
        )
    )

    if not selected_anomalies:
        print(
            "No anomalies available for investigation."
        )
        return

    print(
        f"Selected anomalies: "
        f"{len(selected_anomalies)}"
    )

    for index, anomaly in enumerate(
        selected_anomalies,
        start=1
    ):
        print(f"\nAnomaly {index}")

        print(
            f"Service: "
            f"{anomaly['service']}"
        )

        print(
            f"Window: "
            f"{anomaly['window_start']} -> "
            f"{anomaly['window_end']}"
        )

        print(
            f"Events: "
            f"{anomaly['total_events']:,}"
        )

        print(
            f"Score: "
            f"{anomaly['anomaly_score']:.6f}"
        )

    # --------------------------------------------------
    # STEP 8: CREATE LANGGRAPH WORKFLOW
    # --------------------------------------------------

    print(
        "\nSTEP 8: STARTING LANGGRAPH INVESTIGATION"
    )

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

    start_time = time.time()

    result = workflow.invoke(
        investigation_state
    )

    workflow_time = time.time() - start_time

    # --------------------------------------------------
    # FINAL OUTPUT
    # --------------------------------------------------

    total_time = time.time() - total_start_time

    print("\n" + "=" * 60)
    print("FULL SENTINELAI INVESTIGATION COMPLETE")
    print("=" * 60)

    print("\nPIPELINE SUMMARY")

    print(
        f"Analysis Run ID: "
        f"{analysis_run_id}"
    )

    print(
        f"Total lines: "
        f"{total_lines:,}"
    )

    print(
        f"Parsed events: "
        f"{parsed_events_count:,}"
    )

    print(
        f"Skipped lines: "
        f"{skipped_lines:,}"
    )

    print(
        f"Feature windows: "
        f"{len(feature_windows):,}"
    )

    print(
        f"Anomalies detected: "
        f"{anomalies_detected:,}"
    )

    print(
        f"Anomalies investigated: "
        f"{len(selected_anomalies)}"
    )

    # --------------------------------------------------
    # TIMING
    # --------------------------------------------------

    print("\nTIMING")

    print(
        f"Read time: "
        f"{read_time:.2f} seconds"
    )

    print(
        f"Parse time: "
        f"{parse_time:.2f} seconds"
    )

    print(
        f"Feature time: "
        f"{feature_time:.2f} seconds"
    )

    print(
        f"Training time: "
        f"{training_time:.2f} seconds"
    )

    print(
        f"Prediction time: "
        f"{prediction_time:.2f} seconds"
    )

    print(
        f"LangGraph + RAG + LLM time: "
        f"{workflow_time:.2f} seconds"
    )

    print(
        f"Total pipeline time: "
        f"{total_time:.2f} seconds"
    )

    # --------------------------------------------------
    # INVESTIGATION RESULTS
    # --------------------------------------------------

    print("\nSTRUCTURED ANALYSIS:")
    print(result["analysis"])

    print("\nEVALUATION:")
    print(result["evaluation"])

    print("\nFINAL SENTINELAI INVESTIGATION:\n")
    print(result["final_result"])


if __name__ == "__main__":
    main()