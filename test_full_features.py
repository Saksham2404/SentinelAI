from pathlib import Path
from time import perf_counter

from backend.app.services.hdfs_parser import parse_hdfs_file
from backend.app.services.feature_engineering import engineer_features


# Project root directory
BASE_DIR = Path(__file__).resolve().parent

# Full HDFS dataset
FILE_PATH = (
    BASE_DIR
    / "backend"
    / "data"
    / "full_dataset"
    / "HDFS.log"
)


def main():
    print("FULL HDFS FEATURE ENGINEERING TEST")
    print("-" * 60)

    # Check file
    if not FILE_PATH.exists():
        print(f"ERROR: File not found: {FILE_PATH}")
        return

    print(f"File: {FILE_PATH}")
    print(f"File size: {FILE_PATH.stat().st_size / (1024 * 1024):.2f} MB")

    # --------------------------------------------------
    # Step 1: Read full file
    # --------------------------------------------------
    print("\nSTEP 1: READING FULL DATASET")

    read_start = perf_counter()

    with open(
        FILE_PATH,
        "r",
        encoding="utf-8",
        errors="replace"
    ) as file:
        content = file.read()

    read_time = perf_counter() - read_start

    print(f"Dataset loaded in: {read_time:.2f} seconds")

    # --------------------------------------------------
    # Step 2: Parse
    # --------------------------------------------------
    print("\nSTEP 2: PARSING EVENTS")

    parse_start = perf_counter()

    events, block_ids, skipped_lines = parse_hdfs_file(content)

    parse_time = perf_counter() - parse_start

    total_lines = len(content.splitlines())

    print(f"Total lines:      {total_lines:,}")
    print(f"Parsed events:    {len(events):,}")
    print(f"Skipped lines:    {skipped_lines:,}")
    print(f"Parsing time:     {parse_time:.2f} seconds")

    # Free unnecessary memory
    del content
    del block_ids

    # --------------------------------------------------
    # Step 3: Feature engineering
    # --------------------------------------------------
    print("\nSTEP 3: FEATURE ENGINEERING")

    feature_start = perf_counter()

    features = engineer_features(events)

    feature_time = perf_counter() - feature_start

    print(f"Feature windows created: {len(features):,}")
    print(f"Feature engineering time: {feature_time:.2f} seconds")

    # --------------------------------------------------
    # Sample feature records
    # --------------------------------------------------
    print("\nSAMPLE FEATURES")
    print("-" * 60)

    for index, feature in enumerate(features[:5], start=1):
        print(f"\nFeature Window {index}")
        print(f"Window: {feature.window_start} -> {feature.window_end}")
        print(f"Service: {feature.service}")
        print(f"Total events: {feature.total_events}")
        print(f"Errors: {feature.error_count}")
        print(f"Warnings: {feature.warning_count}")
        print(f"Info: {feature.info_count}")
        print(f"Error rate: {feature.error_rate:.4f}")
        print(f"Timeouts: {feature.timeout_count}")

    # --------------------------------------------------
    # Final summary
    # --------------------------------------------------
    total_time = read_time + parse_time + feature_time

    print("\n" + "=" * 60)
    print("FULL FEATURE ENGINEERING TEST COMPLETED")
    print("=" * 60)

    print(f"Total events processed: {len(events):,}")
    print(f"Total feature windows:  {len(features):,}")
    print(f"Read time:              {read_time:.2f} seconds")
    print(f"Parse time:             {parse_time:.2f} seconds")
    print(f"Feature time:           {feature_time:.2f} seconds")
    print(f"Total measured time:    {total_time:.2f} seconds")


if __name__ == "__main__":
    main()