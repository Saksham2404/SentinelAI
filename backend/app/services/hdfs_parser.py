import re
from datetime import datetime, timedelta

from backend.app.schemas.log_event import LogEvent

# Pattern 1: Strict HDFS Native format (e.g. 081110 103000 1001 INFO dfs.FSNamesystem:)
HDFS_LOG_PATTERN = re.compile(
    r"^(?P<date>\d{6})\s+"
    r"(?P<time>\d{6})\s+"
    r"(?P<pid>\d+)\s+"
    r"(?P<level>[A-Z]+)\s+"
    r"(?P<service>[^:]+):\s*"
    r"(?P<message>.*)$"
)

# Pattern 2: Standard App format (e.g. 2026-08-17 10:00:01 INFO PaymentService: Request completed)
APP_LOG_PATTERN_1 = re.compile(
    r"^(?P<datetime>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}(?:\.\d+)?)\s+"
    r"(?P<level>[A-Z]+)\s+"
    r"(?P<service>[^\s:-]+)(?::|-)?\s+"
    r"(?P<message>.*)$"
)

# Pattern 3: Standard ISO-8601 with T separator (e.g. 2026-08-17T10:00:01 INFO PaymentService - Request completed)
APP_LOG_PATTERN_2 = re.compile(
    r"^(?P<datetime>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?)\s+"
    r"(?P<level>[A-Z]+)\s+"
    r"(?P<service>[^\s:-]+)(?::|-)?\s+"
    r"(?P<message>.*)$"
)

BLOCK_ID_PATTERN = re.compile(
    r"(blk_-?\d+)"
)


def parse_hdfs_line(line: str, line_index: int = 0) -> tuple[LogEvent | None, str | None]:
    """
    Parse one log line using HDFS native, standard app, or universal fallback patterns.

    Returns:
        - LogEvent
        - HDFS block ID, if present
    """
    line = line.strip()
    if not line:
        return None, None

    timestamp = None
    level = "INFO"
    service = "System"
    message = line

    # 1. Try HDFS Native Format
    match = HDFS_LOG_PATTERN.match(line)
    if match:
        data = match.groupdict()
        try:
            timestamp = datetime.strptime(
                f"{data['date']} {data['time']}",
                "%y%m%d %H%M%S"
            )
            level = data["level"]
            service = data["service"]
            message = data["message"]
        except ValueError:
            pass

    # 2. Try Standard App format (space separated datetime)
    if not timestamp:
        match = APP_LOG_PATTERN_1.match(line)
        if match:
            data = match.groupdict()
            try:
                dt_str = data["datetime"].split(".")[0]  # strip milliseconds if any
                timestamp = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                level = data["level"]
                service = data["service"]
                message = data["message"]
            except ValueError:
                pass

    # 3. Try Standard App format (ISO T-separator)
    if not timestamp:
        match = APP_LOG_PATTERN_2.match(line)
        if match:
            data = match.groupdict()
            try:
                dt_str = data["datetime"].split(".")[0]
                timestamp = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S")
                level = data["level"]
                service = data["service"]
                message = data["message"]
            except ValueError:
                pass

    # 4. Universal Fallback Parser (guarantees the line is parsed successfully)
    if not timestamp:
        # Search for any standard date pattern in the line
        date_match = re.search(r"(\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2})", line)
        if date_match:
            try:
                dt_str = date_match.group(1).replace("T", " ")
                timestamp = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                pass

        # If still no timestamp, fallback to sequential offset from base time
        if not timestamp:
            timestamp = datetime.now() - timedelta(minutes=10) + timedelta(seconds=line_index)

        # Guess Log Level from keywords
        upper_line = line.upper()
        if "CRITICAL" in upper_line or "FATAL" in upper_line:
            level = "CRITICAL"
        elif "ERROR" in upper_line or "SEVERE" in upper_line:
            level = "ERROR"
        elif "WARN" in upper_line or "WARNING" in upper_line:
            level = "WARNING"
        elif "DEBUG" in upper_line:
            level = "DEBUG"
        else:
            level = "INFO"

        # Guess service name by looking at words
        parts = line.split()
        if len(parts) > 2:
            for p in parts[1:4]:
                clean_p = p.strip(":-[]()")
                if clean_p and clean_p.isalpha() and clean_p not in ["INFO", "WARN", "ERROR", "DEBUG", "CRITICAL", "FATAL", "WARNING"]:
                    service = clean_p
                    break

    # Block ID check
    block_match = BLOCK_ID_PATTERN.search(message)
    block_id = block_match.group(1) if block_match else None

    event = LogEvent(
        timestamp=timestamp,
        log_level=level,
        service=service,
        message=message,
        status_code=None,
        response_time_ms=None
    )

    return event, block_id


def parse_hdfs_file(content: str) -> tuple[list[LogEvent], list[str | None], int]:
    """
    Parse a log file using universal parsing.

    Returns:
        - parsed log events
        - corresponding block IDs
        - skipped line count
    """
    events = []
    block_ids = []
    skipped_lines = 0

    for idx, line in enumerate(content.splitlines()):
        event, block_id = parse_hdfs_line(line, line_index=idx)

        if event is None:
            skipped_lines += 1
            continue

        events.append(event)
        block_ids.append(block_id)

    return events, block_ids, skipped_lines