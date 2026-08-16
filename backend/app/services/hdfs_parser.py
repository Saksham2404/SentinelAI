import re
from datetime import datetime

from backend.app.schemas.log_event import LogEvent


HDFS_LOG_PATTERN = re.compile(
    r"^(?P<date>\d{6})\s+"
    r"(?P<time>\d{6})\s+"
    r"(?P<pid>\d+)\s+"
    r"(?P<level>[A-Z]+)\s+"
    r"(?P<service>[^:]+):\s*"
    r"(?P<message>.*)$"
)

BLOCK_ID_PATTERN = re.compile(
    r"(blk_-?\d+)"
)


def parse_hdfs_line(line: str) -> tuple[LogEvent | None, str | None]:
    """
    Parse one HDFS log line.

    Returns:
        - LogEvent
        - HDFS block ID, if present
    """

    line = line.strip()

    if not line:
        return None, None

    match = HDFS_LOG_PATTERN.match(line)

    if not match:
        return None, None

    data = match.groupdict()

    try:
        timestamp = datetime.strptime(
            f"{data['date']} {data['time']}",
            "%y%m%d %H%M%S"
        )
    except ValueError:
        return None, None

    message = data["message"]

    block_match = BLOCK_ID_PATTERN.search(message)
    block_id = block_match.group(1) if block_match else None

    event = LogEvent(
        timestamp=timestamp,
        log_level=data["level"],
        service=data["service"],
        message=message,
        status_code=None,
        response_time_ms=None
    )

    return event, block_id


def parse_hdfs_file(content: str) -> tuple[list[LogEvent], list[str | None], int]:
    """
    Parse an HDFS log file.

    Returns:
        - parsed log events
        - corresponding block IDs
        - skipped line count
    """

    events = []
    block_ids = []
    skipped_lines = 0

    for line in content.splitlines():
        event, block_id = parse_hdfs_line(line)

        if event is None:
            skipped_lines += 1
            continue

        events.append(event)
        block_ids.append(block_id)

    return events, block_ids, skipped_lines