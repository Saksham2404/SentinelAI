from backend.app.rag.retriever import Retriever

from backend.app.database.anomaly_queries import (
    get_analysis_run,
    get_anomaly_history
)

from backend.app.llm.gemini_service import GeminiService


def load_database_context_node(state):
    """
    Load the current analysis run and historical anomaly
    information from PostgreSQL.
    """

    analysis_run_id = state["analysis_run_id"]

    # Get details of the current analysis run
    analysis_run = get_analysis_run(analysis_run_id)

    if analysis_run is None:
        return {
            "database_context": {
                "analysis_run": None,
                "anomaly_history": {}
            }
        }

    # Find all services with detected anomalies
    anomalous_services = {
        anomaly.get("service", "UnknownService")
        for anomaly in state.get("anomaly_results", [])
        if anomaly.get("is_anomaly")
    }

    # Get historical anomaly information
    anomaly_history = {}

    for service in anomalous_services:
        anomaly_history[service] = get_anomaly_history(
            service=service,
            current_analysis_run_id=analysis_run_id,
            limit=5
        )

    return {
        "database_context": {
            "analysis_run": analysis_run,
            "anomaly_history": anomaly_history
        }
    }


def retrieve_evidence_node(state):
    """
    Retrieve relevant knowledge-base evidence
    based on the services where anomalies were detected.
    """

    retriever = Retriever()

    anomaly_results = state.get("anomaly_results", [])

    anomalous_services = {
        anomaly.get("service", "UnknownService")
        for anomaly in anomaly_results
        if anomaly.get("is_anomaly")
    }

    # No anomalies -> no evidence retrieval needed
    if not anomalous_services:
        return {
            "retrieved_evidence": []
        }

    retrieved_evidence = []

    # Retrieve evidence once per unique affected service
    for service in anomalous_services:

        query = (
            f"What could cause an anomaly, failure, unusual behavior, "
            f"error, or performance issue in the HDFS service {service}? "
            f"Include possible symptoms, root causes, and investigation steps."
        )

        results = retriever.retrieve(
            query=query,
            n_results=3
        )

        retrieved_evidence.extend(results)

    return {
        "retrieved_evidence": retrieved_evidence
    }


def analyze_node(state):
    """
    Combine anomaly detection results, PostgreSQL context,
    and retrieved RAG evidence into a structured investigation analysis.
    """

    anomaly_results = state.get("anomaly_results", [])
    database_context = state.get("database_context", {})
    retrieved_evidence = state.get("retrieved_evidence", [])

    # Keep only anomalous windows
    anomalous_results = [
        result
        for result in anomaly_results
        if result.get("is_anomaly")
    ]

    # Get unique affected services
    affected_services = sorted({
        result.get("service", "UnknownService")
        for result in anomalous_results
    })

    anomaly_count = len(anomalous_results)

    # Current analysis run information
    analysis_run = database_context.get("analysis_run")

    # Historical anomaly information
    anomaly_history = database_context.get(
        "anomaly_history",
        {}
    )

    historical_counts = {
        service: len(history)
        for service, history in anomaly_history.items()
    }

    # Get unique evidence sources
    evidence_sources = sorted({
        evidence.get("metadata", {}).get(
            "source",
            "unknown"
        )
        for evidence in retrieved_evidence
    })

    analysis = {
        "analysis_run_id": state["analysis_run_id"],

        "summary": {
            "anomalies_detected": anomaly_count,
            "affected_services": affected_services,
            "total_evidence_chunks": len(
                retrieved_evidence
            )
        },

        "current_run": analysis_run,

        "historical_context": {
            "previous_anomaly_counts": historical_counts
        },

        "retrieved_evidence_sources": evidence_sources,

        "anomalies": anomalous_results
    }

    return {
        "analysis": analysis
    }


def evaluate_node(state):
    """
    Evaluate the structured investigation analysis.

    This node assesses anomaly severity, service impact,
    historical patterns, and evidence availability before
    passing the investigation to the LLM.
    """

    analysis = state.get("analysis", {})

    summary = analysis.get("summary", {})

    historical_context = analysis.get(
        "historical_context",
        {}
    )

    anomaly_count = summary.get(
        "anomalies_detected",
        0
    )

    affected_services = summary.get(
        "affected_services",
        []
    )

    evidence_count = summary.get(
        "total_evidence_chunks",
        0
    )

    previous_anomaly_counts = historical_context.get(
        "previous_anomaly_counts",
        {}
    )

    # -----------------------------------
    # Determine overall impact
    # -----------------------------------

    if anomaly_count == 0:
        impact = "none"

    elif anomaly_count <= 2:
        impact = "low"

    elif anomaly_count <= 10:
        impact = "medium"

    else:
        impact = "high"

    # -----------------------------------
    # Determine service impact
    # -----------------------------------

    if len(affected_services) == 0:
        service_impact = "none"

    elif len(affected_services) == 1:
        service_impact = "isolated"

    else:
        service_impact = "multiple_services"

    # -----------------------------------
    # Determine historical pattern
    # -----------------------------------

    repeated_services = [
        service
        for service, count in previous_anomaly_counts.items()
        if count > 0
    ]

    if repeated_services:
        historical_pattern = "repeated"
    else:
        historical_pattern = "no_previous_history"

    # -----------------------------------
    # Evaluate evidence availability
    # -----------------------------------

    if evidence_count == 0:
        evidence_quality = "insufficient"

    elif evidence_count <= 2:
        evidence_quality = "limited"

    else:
        evidence_quality = "sufficient"

    evaluation = {
        "impact": impact,
        "service_impact": service_impact,
        "historical_pattern": historical_pattern,
        "repeated_services": repeated_services,
        "evidence_quality": evidence_quality,

        "metrics": {
            "anomaly_count": anomaly_count,
            "affected_service_count": len(
                affected_services
            ),
            "evidence_count": evidence_count
        }
    }

    return {
        "evaluation": evaluation
    }


def generate_investigation_node(state):
    """
    Generate the final evidence-based investigation
    using the Gemini LLM.
    """

    gemini_service = GeminiService()

    final_result = gemini_service.generate_investigation(
        analysis=state.get("analysis", {}),
        evaluation=state.get("evaluation", {}),
        retrieved_evidence=state.get(
            "retrieved_evidence",
            []
        )
    )

    return {
        "final_result": final_result
    }