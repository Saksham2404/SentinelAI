from backend.app.llm.gemini_service import GeminiService


analysis = {
    "analysis_run_id": 1,

    "summary": {
        "anomalies_detected": 1,
        "affected_services": [
            "dfs.DataNode"
        ],
        "total_evidence_chunks": 3
    },

    "current_run": {
        "id": 1,
        "filename": "HDFS_2k.log",
        "total_lines": 2000,
        "parsed_events": 1920,
        "skipped_lines": 80,
        "feature_windows": 1236,
        "anomalies_detected": 37
    },

    "historical_context": {
        "previous_anomaly_counts": {
            "dfs.DataNode": 0
        }
    },

    "retrieved_evidence_sources": [
        "hdfs_datanode_issues.md",
        "hdfs_namenode_issues.md"
    ],

    "anomalies": [
        {
            "window_start": "2026-08-13T10:00:00",
            "window_end": "2026-08-13T10:01:00",
            "service": "dfs.DataNode",
            "total_events": 25,
            "is_anomaly": True,
            "anomaly_score": -0.12
        }
    ]
}


evaluation = {
    "impact": "low",
    "service_impact": "isolated",
    "historical_pattern": "no_previous_history",
    "repeated_services": [],
    "evidence_quality": "sufficient",

    "metrics": {
        "anomaly_count": 1,
        "affected_service_count": 1,
        "evidence_count": 3
    }
}


retrieved_evidence = [
    {
        "content": """
A DataNode may become unavailable because of network
connectivity problems, disk failures, process crashes,
or insufficient system resources.
""",
        "metadata": {
            "source": "hdfs_datanode_issues.md"
        },
        "distance": 0.72
    },
    {
        "content": """
Common investigation steps include checking whether the
DataNode process is running, checking network connectivity,
available disk space, and reviewing DataNode logs for
ERROR or WARN messages.
""",
        "metadata": {
            "source": "hdfs_datanode_issues.md"
        },
        "distance": 0.92
    },
    {
        "content": """
NameNode performance problems can cause RPC timeouts,
DataNode heartbeat failures, connection errors, and
slow file system operations.
""",
        "metadata": {
            "source": "hdfs_namenode_issues.md"
        },
        "distance": 0.85
    }
]


gemini_service = GeminiService()

result = gemini_service.generate_investigation(
    analysis=analysis,
    evaluation=evaluation,
    retrieved_evidence=retrieved_evidence
)

print("\nSENTINELAI INVESTIGATION RESULT:\n")
print(result)