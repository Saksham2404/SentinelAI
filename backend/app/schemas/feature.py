from datetime import datetime

from pydantic import BaseModel


class LogFeatures(BaseModel):
    window_start: datetime
    window_end: datetime
    service: str

    total_events: int
    error_count: int
    warning_count: int
    info_count: int
    debug_count: int
    critical_count: int

    error_rate: float

    avg_response_time_ms: float
    max_response_time_ms: float
    min_response_time_ms: float

    timeout_count: int
    server_error_count: int