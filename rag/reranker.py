
"""Hybrid semantic and lexical reranking for regulatory passages."""

import re
from typing import List

import numpy as np
from langchain_core.documents import Document

SEMANTIC_WEIGHT = 0.90
LEXICAL_WEIGHT = 0.10
DEFAULT_CANDIDATE_COUNT = 20

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by",
    "for", "from", "in", "into", "is", "it", "of",
    "on", "or", "that", "the", "their", "this", "to",
    "was", "were", "with", "within", "which"
}


def tokenize(text: str) -> set:
    """Convert text into lowercase tokens and remove common stopwords."""
    tokens = re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())
    return {token for token in tokens if token not in STOPWORDS}


def calculate_lexical_score(query: str, passage: str) -> float:
    """Calculate the proportion of query terms present in a passage."""
    query_tokens = tokenize(query)
    passage_tokens = tokenize(passage)

    if not query_tokens:
        return 0.0

    matched_tokens = query_tokens.intersection(passage_tokens)
    return len(matched_tokens) / len(query_tokens)


def calculate_semantic_score(cosine_distance: float) -> float:
    """Convert cosine distance into a bounded similarity score."""
    return float(np.clip(1.0 - cosine_distance, 0.0, 1.0))


def rerank_documents(
    query: str,
    documents: List[Document],
    top_k: int = 5
) -> List[Document]:
    """Rerank retrieved documents using semantic and lexical scores."""

    if not query.strip():
        raise ValueError("Query cannot be empty.")

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")

    if not documents:
        return []

    for index, document in enumerate(documents):
        distance = document.metadata.get("similarity_distance", 1.0)

        semantic_score = calculate_semantic_score(float(distance))
        lexical_score = calculate_lexical_score(
            query,
            document.page_content
        )

        combined_score = (
            SEMANTIC_WEIGHT * semantic_score
            + LEXICAL_WEIGHT * lexical_score
        )

        document.metadata["reranking_score"] = combined_score
        document.metadata["reranking_semantic_score"] = semantic_score
        document.metadata["reranking_lexical_score"] = lexical_score
        document.metadata["original_retrieval_rank"] = index + 1

    ranked_documents = sorted(
        documents,
        key=lambda document: document.metadata["reranking_score"],
        reverse=True
    )

    return ranked_documents[:top_k]


def retrieve_and_rerank(
    retriever,
    query: str,
    candidate_count: int = DEFAULT_CANDIDATE_COUNT,
    top_k: int = 5
) -> List[Document]:
    """Retrieve candidate passages and rerank them."""

    candidates = retriever.search(
        query=query,
        k=candidate_count,
        include_withdrawn=False
    )

    return rerank_documents(
        query=query,
        documents=candidates,
        top_k=top_k
    )
