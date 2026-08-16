from backend.app.database.connection import get_db_connection


def create_tables():
    connection = get_db_connection()
    cursor = connection.cursor()

    # Table 1: Stores each complete log analysis request
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_runs (
            id SERIAL PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            total_lines INTEGER NOT NULL,
            parsed_events INTEGER NOT NULL,
            skipped_lines INTEGER NOT NULL,
            feature_windows INTEGER NOT NULL,
            anomalies_detected INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Table 2: Stores individual anomaly detection results
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS anomaly_results (
            id SERIAL PRIMARY KEY,
            analysis_run_id INTEGER NOT NULL,
            window_start TIMESTAMP NOT NULL,
            window_end TIMESTAMP NOT NULL,
            service VARCHAR(255),
            total_events INTEGER NOT NULL,
            is_anomaly BOOLEAN NOT NULL,
            anomaly_score DOUBLE PRECISION NOT NULL,

            CONSTRAINT fk_analysis_run
                FOREIGN KEY (analysis_run_id)
                REFERENCES analysis_runs(id)
                ON DELETE CASCADE
        );
    """)

    connection.commit()

    cursor.close()
    connection.close()

    print("SentinelAI tables created successfully!")


if __name__ == "__main__":
    create_tables()