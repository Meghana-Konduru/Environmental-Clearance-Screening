
"""Compare original retrieval with hybrid reranking."""

from rag.retriever import RegulatoryRetriever
from rag.reranker import retrieve_and_rerank
from rag.passage_reference_data import PASSAGE_REFERENCE_CASES
from rag.passage_evaluation import (
    passage_precision_at_k,
    passage_recall_at_k,
    passage_reciprocal_rank,
)


def evaluate_method(documents, references, k):
    return {
        "precision": passage_precision_at_k(documents, references, k),
        "recall": passage_recall_at_k(documents, references, k),
        "mrr": passage_reciprocal_rank(documents, references),
    }


def main():

    k = 5
    retriever = RegulatoryRetriever()

    original_results = []
    reranked_results = []

    print("\nORIGINAL VS HYBRID RERANKING")
    print("=" * 75)

    for case in PASSAGE_REFERENCE_CASES:

        query = case["query"]
        references = case["references"]

        # Retrieve candidates once for a fair comparison.
        candidates = retriever.search(
            query=query,
            k=20,
            include_withdrawn=False,
        )

        original_top_k = candidates[:k]

        reranked_top_k = retrieve_and_rerank(
            retriever=retriever,
            query=query,
            candidate_count=20,
            top_k=k,
        )

        original = evaluate_method(
            original_top_k, references, k
        )

        reranked = evaluate_method(
            reranked_top_k, references, k
        )

        original_results.append(original)
        reranked_results.append(reranked)

        print(f"\nScenario: {case['scenario']}")
        print("-" * 75)

        print("Original retrieval:")
        print(f"  Precision@5: {original['precision']:.3f}")
        print(f"  Recall@5:    {original['recall']:.3f}")
        print(f"  MRR:         {original['mrr']:.3f}")

        print("Hybrid reranking:")
        print(f"  Precision@5: {reranked['precision']:.3f}")
        print(f"  Recall@5:    {reranked['recall']:.3f}")
        print(f"  MRR:         {reranked['mrr']:.3f}")

    print("\n" + "=" * 75)
    print("OVERALL COMPARISON")
    print("=" * 75)

    for metric in ["precision", "recall", "mrr"]:

        original_average = sum(
            result[metric] for result in original_results
        ) / len(original_results)

        reranked_average = sum(
            result[metric] for result in reranked_results
        ) / len(reranked_results)

        print(f"\n{metric.upper()}")
        print(f"  Original: {original_average:.3f}")
        print(f"  Reranked: {reranked_average:.3f}")
        print(f"  Change:   {reranked_average - original_average:+.3f}")


if __name__ == "__main__":
    main()
