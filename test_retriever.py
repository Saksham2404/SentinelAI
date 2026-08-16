from backend.app.rag.retriever import Retriever


retriever = Retriever()

query = "What can cause DataNode connection failures?"

results = retriever.retrieve(
    query=query,
    n_results=3
)

print("\nQuery:")
print(query)

print("\nRetrieved Results:\n")

for index, result in enumerate(results, start=1):
    print(f"Result {index}")
    print("Source:", result["metadata"]["filename"])
    print("Distance:", result["distance"])
    print("Content:")
    print(result["content"])
    print("-" * 60)