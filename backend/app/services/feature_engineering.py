from collections import defaultdict
from datetime import timedelta

from backend.app.schemas.feature import LogFeatures
from backend.app.schemas.log_event import LogEvent


def get_window_start(timestamp):
    """
    Round a timestamp down to the start of its minute.

    Example:
        10:00:47 -> 10:00:00
    """
    return timestamp.replace(second=0, microsecond=0)


def engineer_features(events: list[LogEvent]) -> list[LogFeatures]:
    """
    Group log events by:

    1. Service
    2. One-minute time window

    Instead of storing every LogEvent object in memory, this function
    incrementally aggregates numerical statistics for each window.

    This makes it more memory-efficient for large datasets.
    """

    grouped_features = defaultdict(
        lambda: {
            "total_events": 0,
            "error_count": 0,
            "warning_count": 0,
            "info_count": 0,
            "debug_count": 0,
            "critical_count": 0,
            "timeout_count": 0,
            "server_error_count": 0,
            "response_time_sum": 0.0,
            "response_time_count": 0,
            "max_response_time_ms": None,
            "min_response_time_ms": None,
        }
    )

    # Process each event one at a time
    for event in events:

        window_start = get_window_start(event.timestamp)

        # Use UnknownService if service is missing
        service = event.service or "UnknownService"

        key = (window_start, service)

        stats = grouped_features[key]

        # Total events
        stats["total_events"] += 1

        # Log level counts
        if event.log_level == "ERROR":
            stats["error_count"] += 1

        elif event.log_level == "WARNING":
            stats["warning_count"] += 1

        elif event.log_level == "INFO":
            stats["info_count"] += 1

        elif event.log_level == "DEBUG":
            stats["debug_count"] += 1

        elif event.log_level == "CRITICAL":
            stats["critical_count"] += 1

        # Timeout detection
        if event.message and "timeout" in event.message.lower():
            stats["timeout_count"] += 1

        # 5xx server errors
        if (
            event.status_code is not None
            and 500 <= event.status_code < 600
        ):
            stats["server_error_count"] += 1

        # Response time statistics
        if event.response_time_ms is not None:

            response_time = event.response_time_ms

            stats["response_time_sum"] += response_time
            stats["response_time_count"] += 1

            if (
                stats["max_response_time_ms"] is None
                or response_time > stats["max_response_time_ms"]
            ):
                stats["max_response_time_ms"] = response_time

            if (
                stats["min_response_time_ms"] is None
                or response_time < stats["min_response_time_ms"]
            ):
                stats["min_response_time_ms"] = response_time

    feature_records = []

    # Convert aggregated statistics into LogFeatures
    for (window_start, service), stats in grouped_features.items():

        total_events = stats["total_events"]

        error_count = stats["error_count"]
        critical_count = stats["critical_count"]

        error_rate = (
            (error_count + critical_count) / total_events
            if total_events > 0
            else 0.0
        )

        # Response-time statistics
        if stats["response_time_count"] > 0:

            avg_response_time_ms = (
                stats["response_time_sum"]
                / stats["response_time_count"]
            )

            max_response_time_ms = (
                stats["max_response_time_ms"]
            )

            min_response_time_ms = (
                stats["min_response_time_ms"]
            )

        else:

            avg_response_time_ms = 0.0
            max_response_time_ms = 0.0
            min_response_time_ms = 0.0

        feature_records.append(
            LogFeatures(
                window_start=window_start,
                window_end=window_start + timedelta(minutes=1),
                service=service,

                total_events=total_events,
                error_count=stats["error_count"],
                warning_count=stats["warning_count"],
                info_count=stats["info_count"],
                debug_count=stats["debug_count"],
                critical_count=stats["critical_count"],

                error_rate=error_rate,

                avg_response_time_ms=avg_response_time_ms,
                max_response_time_ms=max_response_time_ms,
                min_response_time_ms=min_response_time_ms,

                timeout_count=stats["timeout_count"],
                server_error_count=stats["server_error_count"]
            )
        )

    # Sort results for predictable output
    feature_records.sort(
        key=lambda record: (
            record.window_start,
            record.service
        )
    )

    return feature_records