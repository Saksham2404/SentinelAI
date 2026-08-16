from backend.app.rag.document_loader import load_documents
from backend.app.rag.chunker import chunk_documents
from backend.app.rag.embeddings import EmbeddingModel
from backend.app.rag.vector_store import VectorStore


def index_knowledge_base(
    knowledge_base_path="data/knowledge_base"
):
    """
    Load knowledge-base documents, split them into chunks,
    generate embeddings, and store them in ChromaDB.
    """

    # Step 1: Load documents
    documents = load_documents(knowledge_base_path)

    if not documents:
        return {
            "documents_loaded": 0,
            "chunks_created": 0,
            "chunks_stored": 0
        }

    # Step 2: Split documents into chunks
    chunks = chunk_documents(documents)

    # Step 3: Generate embeddings
    embedding_model = EmbeddingModel()

    texts = [
        chunk["content"]
        for chunk in chunks
    ]

    embeddings = embedding_model.embed_texts(texts)

    # Step 4: Store in ChromaDB
    vector_store = VectorStore()

    vector_store.add_chunks(
        chunks=chunks,
        embeddings=embeddings
    )

    return {
        "documents_loaded": len(documents),
        "chunks_created": len(chunks),
        "chunks_stored": len(chunks),
        "total_vectors_in_store": vector_store.count()
    }