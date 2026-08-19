"""Test universal parser against all sample log formats."""
from backend.app.services.hdfs_parser import parse_hdfs_file

test_files = [
    ("sample-temp.log", "HDFS Native"),
    ("sample_test_logs/healthy_cluster_run.log", "HDFS Healthy"),
    ("sample_test_logs/datanode_outage.log", "HDFS DataNode Outage"),
    ("sample_test_logs/namenode_crash.log", "HDFS NameNode Crash"),
]

# Also test standard app log format inline
STANDARD_APP_LOG = """2026-08-17 10:00:01 INFO PaymentService Request completed - 200 - 120ms
2026-08-17 10:00:05 WARNING DatabaseService Slow response detected - 850ms
2026-08-17 10:00:10 ERROR PaymentService Request failed - 500 - 3200ms
2026-08-17 10:00:15 CRITICAL AuthService OutOfMemoryError: GC overhead limit exceeded
2026-08-17 10:00:20 INFO NotificationService Push notification queued - 202 - 10ms
"""

ISO_FORMAT_LOG = """2026-08-17T10:00:01.123 INFO PaymentService Request completed - 200 - 120ms
2026-08-17T10:00:05.456 ERROR DatabaseService Connection timeout after 5000ms
2026-08-17T10:00:10.789 CRITICAL AuthService Heap memory exceeded
"""

MESSY_LOG = """[2026-08-17 10:00:01] ERROR - Something went wrong in production
warn: this is a warning from some random system
just a random line with no structure at all
error detected in module XYZ at line 42
"""

print("=" * 70)
print("UNIVERSAL LOG PARSER TEST SUITE")
print("=" * 70)

all_passed = True

# Test file-based logs
for filepath, label in test_files:
    try:
        with open(filepath, "r") as f:
            content = f.read()
        events, block_ids, skipped = parse_hdfs_file(content)
        total_lines = len(content.strip().splitlines())
        parsed = len(events)
        status = "PASS" if parsed > 0 else "FAIL"
        if status == "FAIL":
            all_passed = False
        print(f"\n[{status}] {label} ({filepath})")
        print(f"  Lines: {total_lines}, Parsed: {parsed}, Skipped: {skipped}")
        if events:
            print(f"  First: {events[0].timestamp} {events[0].log_level} {events[0].service}")
            print(f"  Last:  {events[-1].timestamp} {events[-1].log_level} {events[-1].service}")
    except Exception as e:
        all_passed = False
        print(f"\n[FAIL] {label}: {e}")

# Test inline standard app format
for label, content in [
    ("Standard App Format (YYYY-MM-DD HH:MM:SS)", STANDARD_APP_LOG),
    ("ISO-8601 Format (T separator)", ISO_FORMAT_LOG),
    ("Messy/Unstructured Logs", MESSY_LOG),
]:
    events, block_ids, skipped = parse_hdfs_file(content)
    total_lines = len(content.strip().splitlines())
    parsed = len(events)
    status = "PASS" if parsed > 0 else "FAIL"
    if status == "FAIL":
        all_passed = False
    print(f"\n[{status}] {label}")
    print(f"  Lines: {total_lines}, Parsed: {parsed}, Skipped: {skipped}")
    for i, ev in enumerate(events[:3]):
        print(f"  Event {i+1}: {ev.timestamp} {ev.log_level} {ev.service} - {ev.message[:60]}")

print("\n" + "=" * 70)
if all_passed:
    print("ALL TESTS PASSED!")
else:
    print("SOME TESTS FAILED!")
print("=" * 70)
