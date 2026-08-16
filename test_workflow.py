from backend.app.graph.workflow import create_workflow


workflow = create_workflow()

test_state = {
    "analysis_run_id": 1,

    # ML / Isolation Forest results
    "anomaly_results": [
        {
            "window_start": "2026-08-13T10:00:00",
            "window_end": "2026-08-13T10:01:00",
            "service": "dfs.DataNode",
            "total_events": 25,
            "is_anomaly": True,
            "anomaly_score": -0.12
        },
        {
            "window_start": "2026-08-13T10:01:00",
            "window_end": "2026-08-13T10:02:00",
            "service": "dfs.NameNode",
            "total_events": 15,
            "is_anomaly": False,
            "anomaly_score": 0.08
        }
    ],

    # PostgreSQL - populated by LangGraph node
    "database_context": {},

    # RAG - populated by LangGraph node
    "retrieved_evidence": [],

    # Later nodes
    "analysis": None,
    "evaluation": None,
    "final_result": None
}

result = workflow.invoke(test_state)


print("\nLANGGRAPH WORKFLOW COMPLETE\n")

print("Analysis Run ID:")
print(result["analysis_run_id"])

print("\nRetrieved Evidence:")

for index, evidence in enumerate(
    result["retrieved_evidence"],
    start=1
):
    print(f"\nResult {index}")
    print("Source:", evidence["metadata"].get("source"))
    print("Distance:", evidence["distance"])
    print("Content:")
    print(evidence["content"])
    print("-" * 60)

print("\nDATABASE CONTEXT:\n")

database_context = result["database_context"]

print("Analysis Run:")
print(database_context["analysis_run"])

print("\nAnomaly History:")

for service, history in database_context[
    "anomaly_history"
].items():

    print(f"\nService: {service}")

    if not history:
        print("No previous anomaly history found.")

    for record in history:
        print(record)
        
print("\nSTRUCTURED ANALYSIS:\n")

analysis = result["analysis"]

print("Summary:")
print(analysis["summary"])

print("\nAffected Services:")
for service in analysis["summary"]["affected_services"]:
    print("-", service)

print("\nHistorical Context:")
print(analysis["historical_context"])

print("\nEvidence Sources:")
for source in analysis["retrieved_evidence_sources"]:
    print("-", source)

print("\nAnomalies Used For Analysis:")
for anomaly in analysis["anomalies"]:
    print(anomaly)
    
print("\nEVALUATION:\n")

evaluation = result["evaluation"]

print("Impact:")
print(evaluation["impact"])

print("\nService Impact:")
print(evaluation["service_impact"])

print("\nHistorical Pattern:")
print(evaluation["historical_pattern"])

print("\nRepeated Services:")
print(evaluation["repeated_services"])

print("\nEvidence Quality:")
print(evaluation["evidence_quality"])

print("\nMetrics:")
print(evaluation["metrics"])

print("\nFINAL SENTINELAI INVESTIGATION:\n")

print(result["final_result"])