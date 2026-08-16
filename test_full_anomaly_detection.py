from pathlib import Path
from time import perf_counter

from backend.app.services.hdfs_parser import parse_hdfs_file
from backend.app.services.feature_engineering import (
    engineer_features
)

from backend.app.ml.anomaly_detector import (
    AnomalyDetector
)

BASE_DIR = Path(__file__).resolve().parent

FILE_PATH = (
    BASE_DIR
    / "backend"
    / "data"
    / "full_dataset"
    / "HDFS.log"
)


def main():

    print("FULL HDFS ANOMALY DETECTION TEST")
    print("=" * 60)

    # --------------------------------------------------
    # Validate dataset
    # --------------------------------------------------
    if not FILE_PATH.exists():
        print(f"ERROR: File not found: {FILE_PATH}")
        return

    print(f"File: {FILE_PATH}")
    print(
        f"File size: "
        f"{FILE_PATH.stat().st_size / (1024 * 1024):.2f} MB"
    )

    # --------------------------------------------------
    # Step 1: Read dataset
    # --------------------------------------------------
    print("\nSTEP 1: READING DATASET")

    read_start = perf_counter()

    with open(
        FILE_PATH,
        "r",
        encoding="utf-8",
        errors="replace"
    ) as file:
        content = file.read()

    read_time = perf_counter() - read_start

    print(f"Read time: {read_time:.2f} seconds")

    # --------------------------------------------------
    # Step 2: Parse logs
    # --------------------------------------------------
    print("\nSTEP 2: PARSING LOG EVENTS")

    parse_start = perf_counter()

    events, block_ids, skipped_lines = parse_hdfs_file(
        content
    )

    parse_time = perf_counter() - parse_start

    total_lines = len(content.splitlines())

    print(f"Total lines:   {total_lines:,}")
    print(f"Parsed events: {len(events):,}")
    print(f"Skipped lines: {skipped_lines:,}")
    print(f"Parse time:    {parse_time:.2f} seconds")

    # Free memory no longer needed
    del content
    del block_ids

    # --------------------------------------------------
    # Step 3: Feature engineering
    # --------------------------------------------------
    print("\nSTEP 3: FEATURE ENGINEERING")

    feature_start = perf_counter()

    features = engineer_features(events)

    feature_time = perf_counter() - feature_start

    print(
        f"Feature windows: {len(features):,}"
    )

    print(
        f"Feature time: "
        f"{feature_time:.2f} seconds"
    )

    # Events are no longer needed after feature creation
    del events

    # --------------------------------------------------
    # Step 4: Train model
    # --------------------------------------------------
    print("\nSTEP 4: TRAINING ISOLATION FOREST")

    detector = AnomalyDetector()

    train_start = perf_counter()

    trained = detector.train(features)

    train_time = perf_counter() - train_start

    if not trained:
        print("ERROR: Model training failed.")
        return

    print("Model training completed.")
    print(
        f"Training time: "
        f"{train_time:.2f} seconds"
    )

    # --------------------------------------------------
    # Step 5: Predict anomalies
    # --------------------------------------------------
    print("\nSTEP 5: DETECTING ANOMALIES")

    predict_start = perf_counter()

    results = detector.predict(features)

    predict_time = perf_counter() - predict_start

    anomalies = [
        result
        for result in results
        if result["is_anomaly"]
    ]

    normal_count = len(results) - len(anomalies)

    print(
        f"Total windows: {len(results):,}"
    )

    print(
        f"Anomalies detected: {len(anomalies):,}"
    )

    print(
        f"Normal windows: {normal_count:,}"
    )

    print(
        f"Anomaly rate: "
        f"{(len(anomalies) / len(results)) * 100:.2f}%"
    )

    print(
        f"Prediction time: "
        f"{predict_time:.2f} seconds"
    )

    # --------------------------------------------------
    # Step 6: Show strongest anomalies
    # Lower Isolation Forest score = more anomalous
    # --------------------------------------------------
    print("\nTOP 10 MOST ANOMALOUS WINDOWS")
    print("-" * 60)

    anomalies.sort(
        key=lambda result: result["anomaly_score"]
    )

    for index, anomaly in enumerate(
        anomalies[:10],
        start=1
    ):
        print(f"\nAnomaly {index}")

        print(
            f"Window: "
            f"{anomaly['window_start']} "
            f"-> {anomaly['window_end']}"
        )

        print(
            f"Service: "
            f"{anomaly['service']}"
        )

        print(
            f"Total events: "
            f"{anomaly['total_events']}"
        )

        print(
            f"Anomaly score: "
            f"{anomaly['anomaly_score']:.6f}"
        )

    # --------------------------------------------------
    # Final summary
    # --------------------------------------------------
    total_time = (
        read_time
        + parse_time
        + feature_time
        + train_time
        + predict_time
    )

    print("\n" + "=" * 60)
    print("FULL HDFS ANOMALY DETECTION COMPLETED")
    print("=" * 60)

    print(
        f"Total events processed: "
        f"{len(features):,} feature windows"
    )

    print(
        f"ML training records:    "
        f"{len(features):,}"
    )

    print(
        f"Anomalies detected:     "
        f"{len(anomalies):,}"
    )

    print(
        f"Read time:              "
        f"{read_time:.2f} seconds"
    )

    print(
        f"Parse time:             "
        f"{parse_time:.2f} seconds"
    )

    print(
        f"Feature time:           "
        f"{feature_time:.2f} seconds"
    )

    print(
        f"Training time:          "
        f"{train_time:.2f} seconds"
    )

    print(
        f"Prediction time:        "
        f"{predict_time:.2f} seconds"
    )

    print(
        f"Total pipeline time:    "
        f"{total_time:.2f} seconds"
    )


if __name__ == "__main__":
    main()