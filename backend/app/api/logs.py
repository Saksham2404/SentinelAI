from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.app.services.hdfs_parser import parse_hdfs_file
from backend.app.schemas.feature import LogFeatures
from backend.app.schemas.log_event import LogParseResponse
from backend.app.services.feature_engineering import engineer_features
from backend.app.services.log_parser import parse_log_file


router = APIRouter(
    prefix="/api/logs",
    tags=["Logs"]
)


async def read_log_file(file: UploadFile) -> str:
    """
    Validate and read an uploaded log file.
    """

    allowed_extensions = (".log", ".txt")

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="File must have a name."
        )

    if not file.filename.lower().endswith(allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail="Only .log and .txt files are supported."
        )

    try:
        content = await file.read()
        return content.decode("utf-8")

    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="File must be UTF-8 encoded."
        )


@router.post(
    "/parse",
    response_model=LogParseResponse
)
async def parse_logs(file: UploadFile = File(...)):

    decoded_content = await read_log_file(file)

    events, skipped_lines = parse_log_file(decoded_content)

    return {
        "total_lines": len(decoded_content.splitlines()),
        "parsed_events_count": len(events),
        "skipped_lines_count": skipped_lines,
        "events": events
    }


@router.post(
    "/features",
    response_model=list[LogFeatures]
)
async def generate_features(file: UploadFile = File(...)):

    decoded_content = await read_log_file(file)

    events, _ = parse_log_file(decoded_content)

    features = engineer_features(events)

    return features

@router.post("/hdfs/parse")
async def parse_hdfs_logs(file: UploadFile = File(...)):
    decoded_content = await read_log_file(file)

    events, block_ids, skipped_lines = parse_hdfs_file(decoded_content)

    unique_blocks = len(
        {block_id for block_id in block_ids if block_id is not None}
    )

    return {
        "total_lines": len(decoded_content.splitlines()),
        "parsed_events_count": len(events),
        "skipped_lines_count": skipped_lines,
        "unique_block_count": unique_blocks,
        "events_with_block_id": sum(
            block_id is not None for block_id in block_ids
        ),
        "sample_events": [
            {
                "timestamp": event.timestamp.isoformat(),
                "log_level": event.log_level,
                "service": event.service,
                "message": event.message,
                "block_id": block_ids[index]
            }
            for index, event in enumerate(events[:5])
        ]
    }