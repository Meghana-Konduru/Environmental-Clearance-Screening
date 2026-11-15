
"""
Passage-level evaluation for the Environmental Clearance RAG system.

A retrieved passage is considered relevant only when:
1. Its source filename matches a reference.
2. Its page number matches the reference.
3. It contains the manually labelled reference excerpt
   after text normalization.

Metrics:
- Passage Precision@K
- Passage Recall@K
- Passage Mean Reciprocal Rank (MRR)

These metrics evaluate matching against supplied reference excerpts.
They do not establish legal correctness or current applicability.
"""

import re
import unicodedata
from typing import Dict, List, Set

from rag.retriever import RegulatoryRetriever
from rag.passage_reference_data import PASSAGE_REFERENCE_CASES


def normalize_text(text: str) -> str:
    """Normalize case, Unicode, punctuation and whitespace."""

    text = unicodedata.normalize("NFKC", str(text))
    text = text.lower()

    # Replace punctuation and symbols with spaces.
    # Keep letters, numbers and whitespace.
    text = re.sub(r"[^\w\s]", " ", text)

    # Collapse repeated whitespace.
    text = re.sub(r"\s+", " ", text).strip()

    return text


def get_source_name(document) -> str:
    """Get the source PDF filename from document metadata."""

    metadata = document.metadata

    source_file = metadata.get("source_file", "")

    if source_file:
        return str(source_file).replace("\\", "/").split("/")[-1]

    document_name = metadata.get("document_name", "")

    return str(document_name).replace("\\", "/").split("/")[-1]


def get_reference_matches(
    document,
    references: List[Dict]
) -> Set[int]:
    """Return reference indices matched by a retrieved passage."""

    metadata = document.metadata

    source_name = get_source_name(document)

    page_number = str(metadata.get("page_number", "")).strip()

    passage_text = normalize_text(document.page_content)

    matched_indices = set()

    for index, reference in enumerate(references):

        expected_source = reference["source"]
        expected_page = str(reference["page"]).strip()
        expected_excerpt = normalize_text(reference["excerpt"])

        source_matches = source_name == expected_source
        page_matches = page_number == expected_page
        excerpt_matches = (
            bool(expected_excerpt)
            and expected_excerpt in passage_text
        )

        if source_matches and page_matches and excerpt_matches:
            matched_indices.add(index)

    return matched_indices


def passage_precision_at_k(
    retrieved_documents: List,
    references: List[Dict],
    k: int,
) -> float:
    """Calculate the proportion of retrieved passages matching references."""

    if k <= 0:
        return 0.0

    top_k = retrieved_documents[:k]

    if not top_k:
        return 0.0

    relevant_count = sum(
        1
        for document in top_k
        if get_reference_matches(document, references)
    )

    return relevant_count / len(top_k)


def passage_recall_at_k(
    retrieved_documents: List,
    references: List[Dict],
    k: int,
) -> float:
    """Calculate the proportion of reference passages retrieved."""

    if k <= 0 or not references:
        return 0.0

    top_k = retrieved_documents[:k]

    matched_reference_indices = set()

    for document in top_k:
        matched_reference_indices.update(
            get_reference_matches(document, references)
        )

    return len(matched_reference_indices) / len(references)


def passage_reciprocal_rank(
    retrieved_documents: List,
    references: List[Dict],
) -> float:
    """Calculate reciprocal rank of the first matching passage."""

    for rank, document in enumerate(retrieved_documents, start=1):

        if get_reference_matches(document, references):
            return 1.0 / rank

    return 0.0


def evaluate_passage_retrieval(k: int = 5) -> Dict[str, float]:
    """Evaluate passage-level retrieval for all reference cases."""

    if k < 1:
        raise ValueError("k must be at least 1.")

    retriever = RegulatoryRetriever()

    precision_scores = []
    recall_scores = []
    reciprocal_rank_scores = []

    print("\n" + "=" * 75)
    print("ENVIRONMENTAL CLEARANCE - PASSAGE-LEVEL RAG EVALUATION")
    print("=" * 75)

    for case_number, case in enumerate(
        PASSAGE_REFERENCE_CASES,
        start=1,
    ):

        scenario = case["scenario"]
        query = case["query"]
        references = case["references"]

        print(f"\nCASE {case_number}: {scenario}")
        print("-" * 75)
        print("Query:", query)

        documents = retriever.search(
            query=query,
            k=k,
            include_withdrawn=False,
        )

        precision = passage_precision_at_k(
            documents,
            references,
            k,
        )

        recall = passage_recall_at_k(
            documents,
            references,
            k,
        )

        mrr = passage_reciprocal_rank(
            documents,
            references,
        )

        precision_scores.append(precision)
        recall_scores.append(recall)
        reciprocal_rank_scores.append(mrr)

        print("\nRetrieved passages:")

        if not documents:
            print("No passages retrieved.")

        matched_reference_indices = set()

        for rank, document in enumerate(documents, start=1):

            metadata = document.metadata

            matches = get_reference_matches(
                document,
                references,
            )

            matched_reference_indices.update(matches)

            print(f"\nResult {rank}")
            print("Source:", get_source_name(document))
            print("Page:", metadata.get("page_number", "Unknown"))
            print(
                "Applicability:",
                metadata.get(
                    "applicability_status",
                    "pending_verification",
                ),
            )
            print(
                "Similarity distance:",
                metadata.get("similarity_distance"),
            )
            print("Reference passage match:", bool(matches))

            if matches:
                for index in sorted(matches):
                    print("Matched reference:", index + 1)

            print(
                "Passage:",
                document.page_content[:300].replace("\n", " "),
            )

        print("\nReference passages matched:")

        for index, reference in enumerate(references):

            status = (
                "MATCHED"
                if index in matched_reference_indices
                else "NOT RETRIEVED"
            )

            print(
                f"  {index + 1}. {status} | "
                f"{reference['source']} | "
                f"Page {reference['page']}"
            )

        print("\nCase metrics:")
        print(f"Passage Precision@{k}: {precision:.3f}")
        print(f"Passage Recall@{k}:    {recall:.3f}")
        print(f"Passage Reciprocal Rank: {mrr:.3f}")

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
        f"passage_precision_at_{k}": average_precision,
        f"passage_recall_at_{k}": average_recall,
        "passage_mean_reciprocal_rank": average_mrr,
    }

    print("\n" + "=" * 75)
    print("OVERALL PASSAGE-LEVEL EVALUATION")
    print("=" * 75)

    print("Evaluation cases:", len(PASSAGE_REFERENCE_CASES))
    print(f"Average Passage Precision@{k}: {average_precision:.3f}")
    print(f"Average Passage Recall@{k}:    {average_recall:.3f}")
    print(f"Passage Mean Reciprocal Rank:  {average_mrr:.3f}")

    print("\nImportant limitations:")
    print("1. Evaluation uses manually supplied reference excerpts.")
    print("2. Matching requires source, page and normalized excerpt text.")
    print(
        "3. A passage may be relevant even if it does not contain "
        "the exact reference excerpt."
    )
    print(
        "4. Reference matches do not establish legal correctness "
        "or current applicability."
    )

    return results


if __name__ == "__main__":
    evaluate_passage_retrieval(k=5)
