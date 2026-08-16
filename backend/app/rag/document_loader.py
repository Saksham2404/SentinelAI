from pathlib import Path


SUPPORTED_EXTENSIONS = {".txt", ".md"}


def load_documents(directory_path: str):
    """
    Load all supported text documents from a directory.

    Supported formats:
    - .txt
    - .md

    Returns a list of dictionaries containing
    document content and metadata.
    """

    documents = []

    directory = Path(directory_path)

    if not directory.exists():
        raise FileNotFoundError(
            f"Knowledge base directory not found: {directory_path}"
        )

    for file_path in directory.rglob("*"):

        # Skip directories
        if not file_path.is_file():
            continue

        # Skip unsupported file types
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        try:
            content = file_path.read_text(
                encoding="utf-8"
            )
        except UnicodeDecodeError:
            print(
                f"Skipping file due to encoding issue: {file_path}"
            )
            continue

        # Skip empty documents
        if not content.strip():
            continue

        documents.append(
            {
                "content": content,
                "metadata": {
                    "source": str(file_path),
                    "filename": file_path.name,
                    "extension": file_path.suffix.lower()
                }
            }
        )

    return documents