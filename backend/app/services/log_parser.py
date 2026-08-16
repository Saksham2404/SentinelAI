import re
from datetime import datetime
from typing import Optional

from backend.app.schemas.log_event import LogEvent


# ==========================================================
# Synthetic / General Log Format
# Example:
# 2026-08-13 10:00:01 INFO PaymentService Request completed - 200 - 120ms
# ==========================================================

GENERAL_LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+"
    r"(?P<log_level>INFO|WARNING|WARN|ERROR|DEBUG|CRITICAL|FATAL)\s+"
    r"(?:(?P<service>[\w.-]+)\s+)?"
    r"(?P<message>.+)$"
)


# ==========================================================
# HDFS Log Format
# Example:
# 081109 203615 148 INFO dfs.DataNode$PacketResponder:
# PacketResponder 1 for block blk_38865049604139660 terminating
# ==========================================================

HDFS_LOG_PATTERN = re.compile(
    r"^(?P<date>\d{6})\s+"
    r"(?P<time>\d{6})\s+"
    r"(?P<thread_id>\d+)\s+"
    r"(?P<log_level>INFO|WARNING|ERROR|DEBUG|CRITICAL)\s+"
    r"(?P<service>[^:]+):\s*"
    r"(?P<message>.+)$"
)


STATUS_CODE_PATTERN = re.compile(r"\b([1-5]\d{2})\b")

RESPONSE_TIME_PATTERN = re.compile(
    r"\b(\d+(?:\.\d+)?)\s*ms\b",
    re.IGNORECASE
)


def normalize_log_level(log_level: str) -> str:
    """
    Normalize different logging level names
    to our standard format.
    """

    log_level = log_level.upper()

    mapping = {
        "WARN": "WARNING",
        "WARNING": "WARNING",
        "FATAL": "CRITICAL",
        "CRITICAL": "CRITICAL",
        "ERROR": "ERROR",
        "INFO": "INFO",
        "DEBUG": "DEBUG"
    }

    return mapping.get(log_level, log_level)


def extract_status_code(message: str) -> Optional[int]:
    match = STATUS_CODE_PATTERN.search(message)

    if match:
        return int(match.group(1))

    return None


def extract_response_time(message: str) -> Optional[float]:
    match = RESPONSE_TIME_PATTERN.search(message)

    if match:
        return float(match.group(1))

    return None


def parse_general_log(line: str) -> Optional[LogEvent]:
    """
    Parse our general / synthetic log format.
    """

    match = GENERAL_LOG_PATTERN.match(line)

    if not match:
        return None

    data = match.groupdict()

    try:
        timestamp = datetime.strptime(
            data["timestamp"],
            "%Y-%m-%d %H:%M:%S"
        )

    except ValueError:
        return None

    message = data["message"]

    return LogEvent(
        timestamp=timestamp,
        log_level=normalize_log_level(data["log_level"]),
        service=data["service"],
        message=message,
        status_code=extract_status_code(message),
        response_time_ms=extract_response_time(message)
    )


def parse_hdfs_log(line: str) -> Optional[LogEvent]:
    """
    Parse HDFS log format.
    """

    match = HDFS_LOG_PATTERN.match(line)

    if not match:
        return None

    data = match.groupdict()

    try:
        timestamp = datetime.strptime(
            f'{data["date"]}{data["time"]}',
            "%y%m%d%H%M%S"
        )

    except ValueError:
        return None

    message = data["message"]

    return LogEvent(
        timestamp=timestamp,
        log_level=normalize_log_level(data["log_level"]),
        service=data["service"],
        message=message,
        status_code=extract_status_code(message),
        response_time_ms=extract_response_time(message)
    )


def parse_log_line(line: str) -> Optional[LogEvent]:
    """
    Automatically detect and parse supported log formats.
    """

    line = line.strip()

    if not line:
        return None

    # Try HDFS format first
    event = parse_hdfs_log(line)

    if event:
        return event

    # Try general/synthetic format
    event = parse_general_log(line)

    if event:
        return event

    return None


def parse_log_file(content: str) -> tuple[list[LogEvent], int]:
    """
    Parse an entire log file.
    """

    lines = content.splitlines()

    events = []
    skipped_lines = 0

    for line in lines:
        event = parse_log_line(line)

        if event:
            events.append(event)

        elif line.strip():
            skipped_lines += 1

    return events, skipped_lines