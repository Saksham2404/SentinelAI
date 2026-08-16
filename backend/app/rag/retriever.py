from backend.app.rag.embeddings import EmbeddingModel
from backend.app.rag.vector_store import VectorStore


class Retriever:
    """
    Retrieve the most relevant knowledge-base chunks
    for a user query.
    """

    def __init__(self):
        self.embedding_model = EmbeddingModel()
        self.vector_store = VectorStore()

    def retrieve(self, query: str, n_results: int = 5):
        """
        Convert the query into an embedding and retrieve
        the most relevant document chunks.
        """

        query_embedding = self.embedding_model.embed_query(query)

        results = self.vector_store.search(
            query_embedding=query_embedding,
            n_results=n_results
        )

        retrieved_chunks = []

        # Chroma returns nested lists because it supports
        # multiple queries at once.
        if results["documents"]:

            documents = results["documents"][0]
            metadatas = results["metadatas"][0]
            distances = results["distances"][0]

            for document, metadata, distance in zip(
                documents,
                metadatas,
                distances
            ):
                retrieved_chunks.append(
                    {
                        "content": document,
                        "metadata": metadata,
                        "distance": float(distance)
                    }
                )

        return retrieved_chunks