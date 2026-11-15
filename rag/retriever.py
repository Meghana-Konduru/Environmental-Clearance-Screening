
"""
Regulatory document retriever for the Environmental Clearance
Pre-Screening Service.
"""

from typing import List

from langchain_core.documents import Document

from rag.vector_store import ChromaVectorStore


class RegulatoryRetriever:
    """
    Retrieve relevant regulatory documents.

    Withdrawn historical documents are excluded by default.
    Documents awaiting verification remain available with their
    applicability status preserved.
    """

    def __init__(self, vector_store: ChromaVectorStore = None):
        self.vector_store = vector_store or ChromaVectorStore()

    def search(
        self,
        query: str,
        k: int = 5,
        include_withdrawn: bool = False,
    ) -> List[Document]:

        if not query or not query.strip():
            raise ValueError("Search query cannot be empty.")

        if k < 1:
            raise ValueError("k must be at least 1.")

        if include_withdrawn:
            where_filter = None
        else:
            where_filter = {
                "applicability_status": {
                    "$ne": "withdrawn_historical"
                }
            }

        return self.vector_store.similarity_search(
            query=query,
            k=k,
            where=where_filter,
        )


def create_retriever() -> RegulatoryRetriever:
    """Create and return a regulatory retriever."""

    return RegulatoryRetriever()


if __name__ == "__main__":

    retriever = create_retriever()

    test_query = (
        "What is the role of the State Level Environment "
        "Impact Assessment Authority?"
    )

    print("\nREGULATORY RETRIEVER TEST")
    print("=" * 60)

    results = retriever.search(
        query=test_query,
        k=5,
    )

    for index, document in enumerate(results, start=1):

        metadata = document.metadata

        print(f"\nResult {index}")
        print("-" * 60)
        print("Document:", metadata.get("document_name"))
        print("Page:", metadata.get("page_number"))
        print(
            "Status:",
            metadata.get("applicability_status"),
        )
        print(
            "Distance:",
            metadata.get("similarity_distance"),
        )
        print("\nContent:")
        print(document.page_content[:700])
