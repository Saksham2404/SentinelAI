"""Verify status_code and response_time_ms extraction from standard app logs."""
from backend.app.services.hdfs_parser import parse_hdfs_file

STANDARD_LOG = """2026-08-17 10:05:01 INFO PaymentService Request completed - 200 - 120ms
2026-08-17 10:05:15 ERROR DatabaseService Connection pool timeout. Active: 50/50, Idle: 0, Pending: 15
2026-08-17 10:05:20 ERROR PaymentService Request failed - 500 - 3200ms
2026-08-17 10:05:35 CRITICAL PaymentService Multiple database timeouts detected - 504 - 5000ms
2026-08-17 10:05:40 ERROR PaymentService API Gateway reported socket timeout - 504 - 6000ms
2026-08-17 10:10:35 CRITICAL AuthService Heap memory allocation limit reached (2048MB)!
2026-08-17 10:10:40 CRITICAL AuthService OutOfMemoryError: GC overhead limit exceeded
"""

events, _, _ = parse_hdfs_file(STANDARD_LOG)

print("=" * 70)
print("STATUS CODE & RESPONSE TIME EXTRACTION TEST")
print("=" * 70)

for ev in events:
    print(f"\n  Level: {ev.log_level:10s} Service: {ev.service:20s}")
    print(f"  Status: {str(ev.status_code):>5s}   ResponseTime: {str(ev.response_time_ms):>8s}ms")
    print(f"  Message: {ev.message[:70]}")

# Verify specific values
assert events[0].status_code == 200, f"Expected 200, got {events[0].status_code}"
assert events[0].response_time_ms == 120.0, f"Expected 120.0, got {events[0].response_time_ms}"
assert events[2].status_code == 500, f"Expected 500, got {events[2].status_code}"
assert events[2].response_time_ms == 3200.0, f"Expected 3200.0, got {events[2].response_time_ms}"
assert events[3].status_code == 504, f"Expected 504, got {events[3].status_code}"
assert events[3].response_time_ms == 5000.0, f"Expected 5000.0, got {events[3].response_time_ms}"

print("\n" + "=" * 70)
print("ALL ASSERTIONS PASSED!")
print("=" * 70)
