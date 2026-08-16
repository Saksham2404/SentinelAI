from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    """
    Wrapper around a SentenceTransformer model
    for converting text into numerical vectors.
    """

    def __init__(
        self,
        model_name="all-MiniLM-L6-v2"
    ):
        self.model = SentenceTransformer(
            model_name
        )

    def embed_texts(self, texts):
        """
        Convert multiple texts into embeddings.
        """

        return self.model.encode(
            texts,
            convert_to_numpy=True
        )

    def embed_query(self, query):
        """
        Convert a single user query into an embedding.
        """

        return self.model.encode(
            query,
            convert_to_numpy=True
        )