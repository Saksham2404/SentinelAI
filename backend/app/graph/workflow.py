from langgraph.graph import StateGraph, START, END

from backend.app.graph.state import InvestigationState
from backend.app.graph.nodes import (
    load_database_context_node,
    retrieve_evidence_node,
    analyze_node,
    evaluate_node,
    generate_investigation_node
)


def create_workflow():
    """
    Create and compile the SentinelAI investigation workflow.
    """

    graph = StateGraph(InvestigationState)

    # Add nodes
    graph.add_node(
        "load_database_context",
        load_database_context_node
    )

    graph.add_node(
        "retrieve_evidence",
        retrieve_evidence_node
    )

    graph.add_node(
        "analyze",
        analyze_node
    )

    graph.add_node(
        "evaluate",
        evaluate_node
    )

    graph.add_node(
        "generate_investigation",
        generate_investigation_node
    )

    # Define workflow
    graph.add_edge(
        START,
        "load_database_context"
    )

    graph.add_edge(
        "load_database_context",
        "retrieve_evidence"
    )

    graph.add_edge(
        "retrieve_evidence",
        "analyze"
    )

    graph.add_edge(
        "analyze",
        "evaluate"
    )

    graph.add_edge(
        "evaluate",
        "generate_investigation"
    )

    graph.add_edge(
        "generate_investigation",
        END
    )

    return graph.compile()