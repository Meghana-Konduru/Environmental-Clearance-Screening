
"""
Inspect retrieved regulatory passages for passage-level evaluation.

This script does not modify the existing ChromaDB collection.
It displays retrieved passages for manual relevance verification.
"""

from rag.retriever import RegulatoryRetriever


INSPECTION_CASES = [
    {
        "scenario": "SEIAA role",
        "query": (
            "What is the role and responsibility of the "
            "State Level Environment Impact Assessment Authority?"
        ),
    },
    {
        "scenario": "Public hearing",
        "query": (
            "What is the procedure, notice period and responsibility "
            "for conducting an environmental public hearing?"
        ),
    },
    {
        "scenario": "Mining",
        "query": (
            "What environmental clearance requirements, Schedule "
            "entries and thresholds apply to mining projects?"
        ),
    },
    {
        "scenario": "Protected areas",
        "query": (
            "What regulatory procedures apply to projects located "
            "near national parks, wildlife sanctuaries and protected areas?"
        ),
    },
    {
        "scenario": "Forest land",
        "query": (
            "What procedures apply when a project involves forest "
            "land diversion and wildlife habitat?"
        ),
    },
]


def inspect_passages(k=5):

    retriever = RegulatoryRetriever()

    print("\nPASSAGE INSPECTION")
    print("=" * 75)

    for case_number, case in enumerate(INSPECTION_CASES, start=1):

        print(f"\nCASE {case_number}: {case['scenario']}")
        print("-" * 75)
        print("Query:", case["query"])

        documents = retriever.search(
            query=case["query"],
            k=k,
            include_withdrawn=False,
        )

        if not documents:
            print("\nNo passages retrieved.")
            continue

        for rank, document in enumerate(documents, start=1):

            metadata = document.metadata

            print(f"\nPASSAGE {rank}")
            print("-" * 50)
            print(
                "Document:",
                metadata.get("document_name", "Unknown"),
            )
            print(
                "Page:",
                metadata.get("page_number", "Unknown"),
            )
            print(
                "Status:",
                metadata.get(
                    "applicability_status",
                    "pending_verification",
                ),
            )
            print(
                "Distance:",
                metadata.get("similarity_distance"),
            )
            print("\nFull retrieved passage:")
            print(document.page_content)

    print("\n" + "=" * 75)
    print("PASSAGE INSPECTION COMPLETED")
    print("=" * 75)


if __name__ == "__main__":
    inspect_passages(k=5)
