from pathlib import Path

import chromadb


class VectorStore:
    """
    ChromaDB vector store for SentinelAI knowledge-base documents.
    """

    def __init__(
        self,
        persist_directory="data/vector_store",
        collection_name="sentinelai_knowledge_base"
    ):
        self.persist_directory = Path(persist_directory)

        self.persist_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory)
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )

    def add_chunks(self, chunks, embeddings):
        """
        Store document chunks together with their embeddings
        and metadata.
        """

        if len(chunks) != len(embeddings):
            raise ValueError(
                "Number of chunks and embeddings must match."
            )

        ids = []
        documents = []
        metadatas = []

        for index, chunk in enumerate(chunks):

            source = chunk["metadata"].get(
                "source",
                "unknown"
            )

            chunk_index = chunk["metadata"].get(
                "chunk_index",
                index
            )

            chunk_id = f"{source}_{chunk_index}"

            # Chroma IDs should be consistent and unique
            chunk_id = chunk_id.replace(
                "\\",
                "_"
            ).replace(
                "/",
                "_"
            ).replace(
                ":",
                "_"
            ).replace(
                " ",
                "_"
            )

            ids.append(chunk_id)
            documents.append(chunk["content"])
            metadatas.append(chunk["metadata"])

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings.tolist(),
            metadatas=metadatas
        )

    def search(
        self,
        query_embedding,
        n_results=5
    ):
        """
        Search for the most semantically similar chunks.
        """

        return self.collection.query(
            query_embeddings=[
                query_embedding.tolist()
            ],
            n_results=n_results
        )

    def count(self):
        """
        Return the number of chunks stored.
        """

        return self.collection.count()