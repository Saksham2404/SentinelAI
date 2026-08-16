def chunk_documents(
    documents,
    chunk_size=500,
    chunk_overlap=100
):
    """
    Split loaded documents into smaller text chunks.

    Each chunk keeps the metadata of its original document.
    """

    chunks = []

    for document in documents:

        content = document["content"]
        metadata = document["metadata"]

        start = 0
        chunk_index = 0

        while start < len(content):

            end = start + chunk_size

            chunk_text = content[start:end]

            # Avoid adding empty chunks
            if chunk_text.strip():

                chunk_metadata = metadata.copy()

                chunk_metadata["chunk_index"] = chunk_index

                chunks.append(
                    {
                        "content": chunk_text,
                        "metadata": chunk_metadata
                    }
                )

                chunk_index += 1

            # Move forward while keeping overlap
            start += chunk_size - chunk_overlap

    return chunks