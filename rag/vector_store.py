
from pathlib import Path
from typing import List, Optional, Dict, Any

import chromadb
from langchain_core.documents import Document

from rag.embeddings import SentenceTransformerEmbeddings, create_embedding_model


PROJECT_ROOT = Path(__file__).resolve().parent.parent

CHROMA_DB_DIR = PROJECT_ROOT / "data" / "chroma_db"
COLLECTION_NAME = "environmental_regulations"

BATCH_SIZE = 100


class ChromaVectorStore:
    """
    Store and retrieve environmental regulatory document embeddings
    using a persistent ChromaDB database.
    """

    def __init__(
        self,
        embedding_model: Optional[SentenceTransformerEmbeddings] = None,
        persist_directory: Path = CHROMA_DB_DIR
    ):
        self.embedding_model = (
            embedding_model
            if embedding_model is not None
            else create_embedding_model()
        )

        self.persist_directory = Path(persist_directory).resolve()
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory)
        )

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )

        print("ChromaDB vector store initialized.")
        print(f"Database location: {self.persist_directory}")
        print(f"Collection: {COLLECTION_NAME}")

    def add_documents(self, documents: List[Document]) -> int:
        """
        Generate embeddings and store document chunks in ChromaDB.

        Existing chunk IDs are updated instead of duplicated.
        """

        if not documents:
            print("No documents received for storage.")
            return 0

        total_stored = 0

        for start in range(0, len(documents), BATCH_SIZE):

            batch = documents[start:start + BATCH_SIZE]

            texts = [document.page_content for document in batch]

            ids = [
                document.metadata.get(
                    "chunk_id",
                    f"chunk_{start + index}"
                )
                for index, document in enumerate(batch)
            ]

            metadatas = [
                {
                    key: value
                    for key, value in document.metadata.items()
                    if isinstance(value, (str, int, float, bool))
                }
                for document in batch
            ]

            embeddings = self.embedding_model.embed_documents(texts)

            self.collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas
            )

            total_stored += len(batch)

            print(
                f"Stored {total_stored}/{len(documents)} chunks."
            )

        print("\n========== VECTOR STORE SUMMARY ==========")
        print(f"Chunks processed: {total_stored}")
        print(f"Collection records: {self.collection.count()}")
        print("==========================================\n")

        return total_stored

    def similarity_search(
        self,
        query: str,
        k: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Retrieve the top-k most similar document chunks.

        Args:
            query: User's regulatory question.
            k: Maximum number of results.
            where: Optional ChromaDB metadata filter.

        Returns:
            Retrieved LangChain Document objects.
        """

        if not query or not query.strip():
            raise ValueError("Search query cannot be empty.")

        if k < 1:
            raise ValueError("k must be at least 1.")

        if self.collection.count() == 0:
            print("The vector store is empty.")
            return []

        query_embedding = self.embedding_model.embed_query(query)

        query_arguments = {
            "query_embeddings": [query_embedding],
            "n_results": min(k, self.collection.count()),
            "include": ["documents", "metadatas", "distances"]
        }

        if where is not None:
            query_arguments["where"] = where

        results = self.collection.query(**query_arguments)

        retrieved_documents = []

        result_documents = results.get("documents", [[]])[0]
        result_metadatas = results.get("metadatas", [[]])[0]
        result_distances = results.get("distances", [[]])[0]

        for text, metadata, distance in zip(
            result_documents,
            result_metadatas,
            result_distances
        ):
            result_metadata = dict(metadata or {})
            result_metadata["similarity_distance"] = float(distance)

            retrieved_documents.append(
                Document(
                    page_content=text,
                    metadata=result_metadata
                )
            )

        return retrieved_documents

    def get_collection_count(self) -> int:
        """Return the number of stored chunks."""

        return self.collection.count()


def create_vector_store() -> ChromaVectorStore:
    """Create and return the ChromaDB vector store."""

    return ChromaVectorStore()


if __name__ == "__main__":

    from rag.chunking import chunk_documents
    from rag.document_loader import load_regulatory_documents

    print("Loading regulatory documents...")

    documents = load_regulatory_documents()

    print("\nChunking regulatory documents...")

    chunks = chunk_documents(documents)

    print("\nInitializing ChromaDB...")

    vector_store = create_vector_store()

    print("\nStoring document embeddings...")

    vector_store.add_documents(chunks)

    print("\nTesting similarity search...")

    test_query = (
        "What is the role of the State Level Environment "
        "Impact Assessment Authority?"
    )

    search_results = vector_store.similarity_search(
        query=test_query,
        k=5,
        where={
            "applicability_status": {
                "$ne": "withdrawn_historical"
            }
        }
    )

    print(f"\nSearch query: {test_query}")
    print(f"Results retrieved: {len(search_results)}")

    for index, result in enumerate(search_results, start=1):

        print(f"\n--- Result {index} ---")
        print(f"Document: {result.metadata.get('document_name')}")
        print(f"Page: {result.metadata.get('page_number')}")
        print(f"Status: {result.metadata.get('applicability_status')}")
        print(f"Distance: {result.metadata.get('similarity_distance')}")
        print(f"Text:\n{result.page_content[:500]}")
