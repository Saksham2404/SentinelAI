from backend.app.database.connection import get_db_connection


def save_analysis_run(
    filename,
    total_lines,
    parsed_events,
    skipped_lines,
    feature_windows,
    anomalies_detected
):
    """
    Save one complete log analysis run and return its ID.
    """

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO analysis_runs (
                filename,
                total_lines,
                parsed_events,
                skipped_lines,
                feature_windows,
                anomalies_detected
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id;
            """,
            (
                filename,
                total_lines,
                parsed_events,
                skipped_lines,
                feature_windows,
                anomalies_detected
            )
        )

        analysis_run_id = cursor.fetchone()[0]

        connection.commit()

        return analysis_run_id

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


def save_anomaly_results(analysis_run_id, results):
    """
    Save all anomaly detection results for one analysis run.
    """

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        for result in results:
            cursor.execute(
                """
                INSERT INTO anomaly_results (
                    analysis_run_id,
                    window_start,
                    window_end,
                    service,
                    total_events,
                    is_anomaly,
                    anomaly_score
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s);
                """,
                (
                    analysis_run_id,
                    result["window_start"],
                    result["window_end"],
                    result["service"],
                    result["total_events"],
                    result["is_anomaly"],
                    result["anomaly_score"]
                )
            )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()
        
 
def get_analysis_run(analysis_run_id):
    """
    Fetch details of one analysis run from PostgreSQL.
    """

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT
                id,
                filename,
                total_lines,
                parsed_events,
                skipped_lines,
                feature_windows,
                anomalies_detected,
                created_at
            FROM analysis_runs
            WHERE id = %s;
            """,
            (analysis_run_id,)
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return {
            "id": row[0],
            "filename": row[1],
            "total_lines": row[2],
            "parsed_events": row[3],
            "skipped_lines": row[4],
            "feature_windows": row[5],
            "anomalies_detected": row[6],
            "created_at": row[7]
        }

    finally:
        cursor.close()
        connection.close()


def get_anomaly_history(
    service,
    current_analysis_run_id,
    limit=5
):
    """
    Fetch anomalous results for a service from PREVIOUS analysis runs only.

    The current analysis run is excluded so that its anomalies
    are not incorrectly counted as historical anomalies.
    """

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT
                ar.analysis_run_id,
                ar.window_start,
                ar.window_end,
                ar.service,
                ar.total_events,
                ar.anomaly_score,
                a.filename
            FROM anomaly_results ar
            JOIN analysis_runs a
                ON ar.analysis_run_id = a.id
            WHERE ar.service = %s
              AND ar.is_anomaly = TRUE
              AND ar.analysis_run_id != %s
            ORDER BY ar.window_start DESC
            LIMIT %s;
            """,
            (
                service,
                current_analysis_run_id,
                limit
            )
        )

        rows = cursor.fetchall()

        history = []

        for row in rows:
            history.append(
                {
                    "analysis_run_id": row[0],
                    "window_start": row[1],
                    "window_end": row[2],
                    "service": row[3],
                    "total_events": row[4],
                    "anomaly_score": float(row[5]),
                    "filename": row[6]
                }
            )

        return history

    finally:
        cursor.close()
        connection.close()


def get_all_analysis_runs(limit=50):
    """Fetch all analysis runs, newest first."""
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            SELECT id, filename, total_lines, parsed_events,
                   skipped_lines, feature_windows, anomalies_detected, created_at
            FROM analysis_runs
            ORDER BY created_at DESC
            LIMIT %s;
            """,
            (limit,)
        )
        rows = cursor.fetchall()
        return [
            {
                "id": row[0],
                "filename": row[1],
                "total_lines": row[2],
                "parsed_events": row[3],
                "skipped_lines": row[4],
                "feature_windows": row[5],
                "anomalies_detected": row[6],
                "created_at": row[7].isoformat() if row[7] else None
            }
            for row in rows
        ]
    finally:
        cursor.close()
        connection.close()


def get_anomaly_results_for_run(analysis_run_id):
    """Fetch all anomaly results for a specific analysis run."""
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            SELECT id, analysis_run_id, window_start, window_end,
                   service, total_events, is_anomaly, anomaly_score
            FROM anomaly_results
            WHERE analysis_run_id = %s
            ORDER BY anomaly_score ASC;
            """,
            (analysis_run_id,)
        )
        rows = cursor.fetchall()
        return [
            {
                "id": row[0],
                "analysis_run_id": row[1],
                "window_start": row[2].isoformat() if row[2] else None,
                "window_end": row[3].isoformat() if row[3] else None,
                "service": row[4],
                "total_events": row[5],
                "is_anomaly": row[6],
                "anomaly_score": float(row[7])
            }
            for row in rows
        ]
    finally:
        cursor.close()
        connection.close()


def get_aggregate_stats():
    """Get cumulative stats across all analysis runs."""
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_runs,
                COALESCE(SUM(parsed_events), 0) AS total_parsed_events,
                COALESCE(SUM(anomalies_detected), 0) AS total_anomalies
            FROM analysis_runs;
            """
        )
        row = cursor.fetchone()
        return {
            "total_runs": row[0],
            "total_parsed_events": row[1],
            "total_anomalies": row[2]
        }
    finally:
        cursor.close()
        connection.close()