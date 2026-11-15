
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


# Chunking configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def create_text_splitter() -> RecursiveCharacterTextSplitter:
    """
    Create a text splitter for regulatory documents.

    Chunk size controls the maximum chunk length.
    Overlap preserves context between consecutive chunks.
    """

    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=[
            "\n\n",
            "\n",
            ". ",
            "; ",
            " ",
            ""
        ],
        keep_separator=True
    )


def chunk_documents(
    documents: List[Document]
) -> List[Document]:
    """
    Split regulatory documents into smaller chunks.

    Original metadata is preserved.
    Each chunk receives additional metadata:
    - chunk_id
    - chunk_index
    """

    if not documents:
        print("No documents received for chunking.")
        return []

    text_splitter = create_text_splitter()

    chunked_documents = text_splitter.split_documents(documents)

    for index, chunk in enumerate(chunked_documents):

        chunk.metadata["chunk_id"] = (
            f"{chunk.metadata.get('document_id', 'unknown')}"
            f"_page_{chunk.metadata.get('page_number', 0)}"
            f"_chunk_{index}"
        )

        chunk.metadata["chunk_index"] = index

    print("\n========== CHUNKING SUMMARY ==========")
    print(f"Original pages: {len(documents)}")
    print(f"Generated chunks: {len(chunked_documents)}")
    print(f"Chunk size: {CHUNK_SIZE}")
    print(f"Chunk overlap: {CHUNK_OVERLAP}")
    print("======================================\n")

    return chunked_documents


if __name__ == "__main__":

    from pathlib import Path
    from rag.document_loader import load_regulatory_documents

    print("Loading regulatory documents...")

    documents = load_regulatory_documents()

    print("\nCreating document chunks...")

    chunks = chunk_documents(documents)

    if chunks:
        print("Sample chunk metadata:")
        print(chunks[0].metadata)

        print("\nSample chunk text:")
        print(chunks[0].page_content[:1000])
