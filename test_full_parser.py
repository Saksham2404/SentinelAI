from pathlib import Path
from time import perf_counter

from backend.app.services.hdfs_parser import parse_hdfs_file


# Project root directory
BASE_DIR = Path(__file__).resolve().parent

# Full HDFS dataset file
# FILE_PATH = BASE_DIR / "backend" / "data" / "full_dataset" / "HDFS"
FILE_PATH = BASE_DIR / "backend" / "data" / "full_dataset" / "HDFS.log"


def main():
    print("FULL HDFS PARSER TEST")
    print("-" * 50)

    # Check whether file exists
    if not FILE_PATH.exists():
        print(f"ERROR: File not found: {FILE_PATH}")
        return

    # Check whether it is actually a file
    if not FILE_PATH.is_file():
        print(f"ERROR: Path exists but is not a file: {FILE_PATH}")
        return

    # Display file information
    print(f"File: {FILE_PATH}")
    print(f"File size: {FILE_PATH.stat().st_size / (1024 * 1024):.2f} MB")

    # Start timer
    start_time = perf_counter()

    try:
        # Read full log file
        content = FILE_PATH.read_text(
            encoding="utf-8",
            errors="replace"
        )

        # Parse HDFS logs
        events, block_ids, skipped_lines = parse_hdfs_file(content)

    except Exception as e:
        print(f"\nERROR while parsing file: {e}")
        return

    # End timer
    end_time = perf_counter()

    # Calculate statistics
    total_lines = len(content.splitlines())
    parsed_events = len(events)
    elapsed_time = end_time - start_time

    print("\nPARSING COMPLETE")
    print("-" * 50)

    print(f"Total lines:       {total_lines:,}")
    print(f"Parsed events:     {parsed_events:,}")
    print(f"Skipped lines:     {skipped_lines:,}")

    if total_lines > 0:
        parse_rate = (parsed_events / total_lines) * 100
        print(f"Parse success:     {parse_rate:.2f}%")

    print(f"Parsing time:      {elapsed_time:.2f} seconds")

    if elapsed_time > 0:
        print(
            f"Lines per second:  "
            f"{total_lines / elapsed_time:,.0f}"
        )

    # Block ID statistics
    valid_block_ids = [
        block_id
        for block_id in block_ids
        if block_id is not None
    ]

    print("\nBLOCK ID STATISTICS")
    print("-" * 50)
    print(f"Events with Block ID: {len(valid_block_ids):,}")
    print(f"Unique Block IDs:     {len(set(valid_block_ids)):,}")

    # Show sample parsed event
    if events:
        print("\nSAMPLE PARSED EVENT")
        print("-" * 50)

        sample_event = events[0]

        print(f"Timestamp: {sample_event.timestamp}")
        print(f"Log Level: {sample_event.log_level}")
        print(f"Service:   {sample_event.service}")
        print(f"Message:   {sample_event.message}")

    print("\nFULL HDFS PARSER TEST COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    main()