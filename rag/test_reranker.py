
"""Test hybrid reranking against the existing ChromaDB retriever."""

from rag.retriever import RegulatoryRetriever
from rag.reranker import retrieve_and_rerank


def main():

    query = (
        "What procedures apply when a project involves forest "
        "land diversion and wildlife habitat?"
    )

    retriever = RegulatoryRetriever()

    print("\nORIGINAL RETRIEVAL")
    print("=" * 65)

    original_documents = retriever.search(
        query=query,
        k=20,
        include_withdrawn=False,
    )

    for rank, document in enumerate(original_documents[:5], start=1):
        print(
            f"{rank}. {document.metadata.get('document_name')} "
            f"| Page {document.metadata.get('page_number')}"
        )

    print("\nHYBRID RERANKING")
    print("=" * 65)

    reranked_documents = retrieve_and_rerank(
        retriever=retriever,
        query=query,
        candidate_count=20,
        top_k=5,
    )

    for rank, document in enumerate(reranked_documents, start=1):

        metadata = document.metadata

        print(f"\nRank: {rank}")
        print(f"Document: {metadata.get('document_name')}")
        print(f"Page: {metadata.get('page_number')}")
        print(
            "Original rank:",
            metadata.get("original_retrieval_rank"),
        )
        print(
            "Semantic score:",
            metadata.get("reranking_semantic_score"),
        )
        print(
            "Lexical score:",
            metadata.get("reranking_lexical_score"),
        )
        print(
            "Combined score:",
            metadata.get("reranking_score"),
        )
        print("Passage:")
        print(document.page_content[:350].replace("\n", " "))


if __name__ == "__main__":
    main()
