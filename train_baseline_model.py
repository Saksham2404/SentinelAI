from pathlib import Path
import time

from backend.app.services.hdfs_parser import parse_hdfs_file
from backend.app.services.feature_engineering import engineer_features
from backend.app.ml.anomaly_detector import AnomalyDetector


FULL_DATASET_PATH = Path(
    "backend/data/full_dataset/HDFS.log"
)


def main():

    print("\nSENTINELAI BASELINE MODEL TRAINING")
    print("=" * 60)

    # --------------------------------------------------
    # CHECK DATASET
    # --------------------------------------------------

    if not FULL_DATASET_PATH.exists():
        print(
            f"\nERROR: Dataset not found:\n"
            f"{FULL_DATASET_PATH.resolve()}"
        )
        return

    print(
        f"\nDataset: "
        f"{FULL_DATASET_PATH.resolve()}"
    )

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
    # STEP 2: PARSE LOG EVENTS
    # --------------------------------------------------

    print("\nSTEP 2: PARSING LOG EVENTS")

    start_time = time.time()

    events, block_ids, skipped_lines = parse_hdfs_file(
        content
    )

    total_events_count = len(events)


    parse_time = time.time() - start_time

    print(f"Parsed events: {len(events):,}")
    print(f"Skipped lines: {skipped_lines:,}")
    print(f"Parse time: {parse_time:.2f} seconds")

    # Free raw dataset text from memory
    del content
    del block_ids

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

    # Events are no longer needed
    del events

    # --------------------------------------------------
    # STEP 4: TRAIN BASELINE MODEL
    # --------------------------------------------------

    print("\nSTEP 4: TRAINING BASELINE ISOLATION FOREST")

    detector = AnomalyDetector()

    start_time = time.time()

    trained = detector.train(feature_windows)

    training_time = time.time() - start_time

    if not trained:
        print(
            "\nERROR: Model training failed. "
            "No feature windows were available."
        )
        return

    print("Baseline model training completed.")

    print(
        f"Training time: "
        f"{training_time:.2f} seconds"
    )

    # --------------------------------------------------
    # STEP 5: SAVE MODEL
    # --------------------------------------------------

    print("\nSTEP 5: SAVING BASELINE MODEL")

    start_time = time.time()

    model_path = detector.save_model()

    save_time = time.time() - start_time

    print(
        f"Model saved successfully:\n"
        f"{model_path.resolve()}"
    )

    print(
        f"Model save time: "
        f"{save_time:.2f} seconds"
    )

    # --------------------------------------------------
    # FINAL SUMMARY
    # --------------------------------------------------

    total_time = time.time() - total_start_time

    print("\n" + "=" * 60)
    print("BASELINE MODEL TRAINING COMPLETE")
    print("=" * 60)

    print("\nDATASET SUMMARY")
    print(f"Total lines: {total_lines:,}")
    print(f"Parsed events: {total_events_count:,}")
    print(f"Skipped lines: {skipped_lines:,}")
    print(f"Feature windows: {len(feature_windows):,}")
    

    print("\nMODEL SUMMARY")
    print("Algorithm: Isolation Forest")
    print("Contamination: 0.05")
    print(f"Training windows: {len(feature_windows):,}")
    print(f"Model location: {model_path.resolve()}")

    print("\nTIMING")
    print(f"Read time: {read_time:.2f} seconds")
    print(f"Parse time: {parse_time:.2f} seconds")
    print(f"Feature time: {feature_time:.2f} seconds")
    print(f"Training time: {training_time:.2f} seconds")
    print(f"Save time: {save_time:.2f} seconds")
    print(f"Total time: {total_time:.2f} seconds")

    print(
        "\nThe baseline model is now ready to detect "
        "anomalies in newly uploaded log files."
    )


if __name__ == "__main__":
    main()