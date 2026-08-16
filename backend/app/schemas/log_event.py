from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class LogEvent(BaseModel):
    timestamp: datetime
    log_level: str
    service: Optional[str] = None
    message: str
    status_code: Optional[int] = None
    response_time_ms: Optional[float] = None


class LogParseResponse(BaseModel):
    total_lines: int
    parsed_events_count: int
    skipped_lines_count: int
    events: list[LogEvent]