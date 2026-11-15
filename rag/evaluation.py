
"""
Evaluation module for the Environmental Clearance RAG system.

Evaluates document-level retrieval using expected source-document mappings.

Metrics:
- Precision@K
- Recall@K
- Mean Reciprocal Rank (MRR)

Important:
These metrics measure source-document retrieval. They do not establish
passage-level correctness, legal applicability, or legal validity.

Expected source mappings are provisional and must be manually checked
against the actual regulatory PDFs.
"""

from typing import Dict, List, Set

from rag.retriever import RegulatoryRetriever


# Existing evaluation cases.
# Expected source mappings should be reviewed against the actual PDFs.
EVALUATION_CASES = [
    {
        "scenario": "SEIAA role",
        "query": (
            "What is the role of the State Level Environment "
            "Impact Assessment Authority?"
        ),
        "relevant_sources": [
            "eia_notification_2006_consolidated.pdf",
            "eia_notification_2006_original.pdf",
        ],
    },
    {
        "scenario": "Public hearing",
        "query": (
            "What is the procedure and notice period for "
            "conducting an environmental public hearing?"
        ),
        "relevant_sources": [
            "eia_notification_2006_consolidated.pdf",
            "SO_3067_E_2009.pdf",
        ],
    },
    {
        "scenario": "Forest and wildlife clearance",
        "query": (
            "What is the procedure for forest and wildlife "
            "clearances for environmental clearance projects?"
        ),
        "relevant_sources": [
            "OM_2009-12-02_forest_wildlife_procedure.pdf",
            "OM_2020-07-16_NBWL_clearance_procedure.pdf",
        ],
    },

    # Additional project-oriented evaluation scenarios.
    {
        "scenario": "Industrial manufacturing",
        "query": (
            "What environmental clearance requirements apply to "
            "an industrial manufacturing project, including the "
            "relevant Schedule entry and project category?"
        ),
        "relevant_sources": [
            "eia_notification_2006_consolidated.pdf",
            "eia_notification_2006_original.pdf",
        ],
    },
    {
        "scenario": "Mining project",
        "query": (
            "What environmental clearance requirements and "
            "appraisal procedures apply to mining projects, "
            "including mineral extraction and production capacity?"
        ),
        "relevant_sources": [
            "eia_notification_2006_consolidated.pdf",
            "eia_notification_2006_original.pdf",
        ],
    },
    {
        "scenario": "Building and construction",
        "query": (
            "What are the environmental clearance requirements, "
            "thresholds and project categories for building "
            "construction and area development projects?"
        ),
        "relevant_sources": [
            "eia_notification_2006_consolidated.pdf",
            "eia_notification_2006_original.pdf",
        ],
    },
    {
        "scenario": "Projects near protected areas",
        "query": (
            "What environmental and wildlife clearance procedures "
            "should be reviewed for a project located near a "
            "national park, wildlife sanctuary or protected area?"
        ),
        "relevant_sources": [
            "eia_notification_2006_consolidated.pdf",
            "OM_2019-08-08_projects_within_10km_protected_areas.pdf",
            "OM_2020-07-16_NBWL_clearance_procedure.pdf",
        ],
    },
    {
        "scenario": "Projects involving forest land",
        "query": (
            "What forest clearance and wildlife-related procedures "
            "should be reviewed when a proposed project involves "
            "forest land diversion?"
        ),
        "relevant_sources": [
            "OM_2009-12-02_forest_wildlife_procedure.pdf",
            "OM_2020-07-16_NBWL_clearance_procedure.pdf",
            "eia_notification_2006_consolidated.pdf",
        ],
    },
]


def get_source_name(document) -> str:
    """Get the source filename from a retrieved document."""

    metadata = document.metadata

    source_file = metadata.get("source_file", "")

    if source_file:
        return str(source_file).replace("\\", "/").split("/")[-1]

    document_name = metadata.get("document_name", "")

    return str(document_name).replace("\\", "/").split("/")[-1]


def get_unique_sources(retrieved_sources: List[str]) -> List[str]:
    """
    Return unique source filenames while preserving retrieval order.

    Multiple chunks from the same PDF count as one source document.
    """

    unique_sources = []
    seen_sources = set()

    for source in retrieved_sources:
        if source not in seen_sources:
            unique_sources.append(source)
            seen_sources.add(source)

    return unique_sources


def precision_at_k(
    retrieved_sources: List[str],
    relevant_sources: Set[str],
    k: int,
) -> float:
    """Calculate document-level Precision@K."""

    if k <= 0:
        return 0.0

    unique_sources = get_unique_sources(retrieved_sources)
    top_k = unique_sources[:k]

    if not top_k:
        return 0.0

    relevant_count = sum(
        1 for source in top_k if source in relevant_sources
    )

    return relevant_count / len(top_k)


def recall_at_k(
    retrieved_sources: List[str],
    relevant_sources: Set[str],
    k: int,
) -> float:
    """Calculate document-level Recall@K."""

    if not relevant_sources or k <= 0:
        return 0.0

    unique_sources = get_unique_sources(retrieved_sources)
    top_k = set(unique_sources[:k])

    relevant_retrieved = top_k.intersection(relevant_sources)

    return len(relevant_retrieved) / len(relevant_sources)


def reciprocal_rank(
    retrieved_sources: List[str],
    relevant_sources: Set[str],
) -> float:
    """Calculate reciprocal rank of the first relevant source document."""

    unique_sources = get_unique_sources(retrieved_sources)

    for rank, source in enumerate(unique_sources, start=1):
        if source in relevant_sources:
            return 1.0 / rank

    return 0.0


def evaluate_retrieval(k: int = 5) -> Dict[str, float]:
    """
    Run all evaluation cases and calculate average retrieval metrics.

    The evaluation uses unique source documents for its metrics.
    Individual retrieved passages are still displayed for inspection.
    """

    if k < 1:
        raise ValueError("k must be at least 1.")

    retriever = RegulatoryRetriever()

    precision_scores = []
    recall_scores = []
    reciprocal_rank_scores = []

    print("\n" + "=" * 75)
    print("ENVIRONMENTAL CLEARANCE RAG - RETRIEVAL EVALUATION")
    print("=" * 75)

    for case_number, case in enumerate(EVALUATION_CASES, start=1):

        query = case["query"]
        scenario = case["scenario"]
        relevant_sources = set(case["relevant_sources"])

        print(f"\nTest Case {case_number}: {scenario}")
        print("-" * 75)
        print(f"Query: {query}")

        documents = retriever.search(
            query=query,
            k=k,
            include_withdrawn=False,
        )

        retrieved_sources = [
            get_source_name(document)
            for document in documents
        ]

        unique_sources = get_unique_sources(retrieved_sources)

        precision = precision_at_k(
            retrieved_sources,
            relevant_sources,
            k,
        )

        recall = recall_at_k(
            retrieved_sources,
            relevant_sources,
            k,
        )

        mrr = reciprocal_rank(
            retrieved_sources,
            relevant_sources,
        )

        precision_scores.append(precision)
        recall_scores.append(recall)
        reciprocal_rank_scores.append(mrr)

        print("\nExpected relevant source documents:")

        for source in sorted(relevant_sources):
            print(f"  - {source}")

        print("\nRetrieved passages:")

        if not documents:
            print("  No documents retrieved.")

        for rank, document in enumerate(documents, start=1):

            metadata = document.metadata
            source_name = get_source_name(document)

            source_match = source_name in relevant_sources

            status = metadata.get(
                "applicability_status",
                "pending_verification",
            )

            distance = metadata.get(
                "similarity_distance",
                "Not available",
            )

            print(f"\n  Passage result {rank}")
            print(f"  Source: {source_name}")
            print(f"  Page: {metadata.get('page_number', 'Unknown')}")
            print(f"  Status: {status}")
            print(f"  Similarity distance: {distance}")
            print(f"  Expected source match: {source_match}")
            print(
                "  Passage: "
                + document.page_content[:400].replace("\n", " ")
            )

        print("\nUnique source documents retrieved:")
        for rank, source in enumerate(unique_sources, start=1):
            print(f"  {rank}. {source}")

        print("\nCase metrics:")
        print(f"  Precision@{k}: {precision:.3f}")
        print(f"  Recall@{k}:    {recall:.3f}")
        print(f"  Reciprocal Rank: {mrr:.3f}")

    average_precision = (
        sum(precision_scores) / len(precision_scores)
        if precision_scores else 0.0
    )

    average_recall = (
        sum(recall_scores) / len(recall_scores)
        if recall_scores else 0.0
    )

    average_mrr = (
        sum(reciprocal_rank_scores) / len(reciprocal_rank_scores)
        if reciprocal_rank_scores else 0.0
    )

    results = {
        f"precision_at_{k}": average_precision,
        f"recall_at_{k}": average_recall,
        "mean_reciprocal_rank": average_mrr,
    }

    print("\n" + "=" * 75)
    print("OVERALL EVALUATION RESULTS")
    print("=" * 75)

    print(f"Total evaluation cases: {len(EVALUATION_CASES)}")
    print(f"Average Precision@{k}: {average_precision:.3f}")
    print(f"Average Recall@{k}:    {average_recall:.3f}")
    print(f"Mean Reciprocal Rank:  {average_mrr:.3f}")

    print("\nImportant notes:")
    print(
        "1. These metrics measure expected source-document retrieval."
    )
    print(
        "2. Multiple passages from one PDF count as one source document."
    )
    print(
        "3. Expected source mappings require manual validation against "
        "the regulatory PDFs."
    )
    print(
        "4. Retrieval scores do not establish passage-level correctness "
        "or legal validity."
    )
    print(
        "5. Withdrawn historical documents are excluded by default."
    )

    return results


if __name__ == "__main__":
    evaluate_retrieval(k=5)
