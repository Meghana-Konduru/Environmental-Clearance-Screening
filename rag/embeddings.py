
from typing import List

from sentence_transformers import SentenceTransformer


# Multilingual model supporting English and Hindi
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

BATCH_SIZE = 32


class SentenceTransformerEmbeddings:
    """
    Generate embeddings for environmental regulatory documents.

    This class provides methods compatible with LangChain's
    embedding interface, which can be used with ChromaDB.
    """

    def __init__(self, model_name: str = MODEL_NAME):
        print(f"Loading embedding model: {model_name}")

        self.model = SentenceTransformer(model_name)

        print("Embedding model loaded successfully.")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Convert multiple document chunks into embeddings.
        """

        if not texts:
            return []

        embeddings = self.model.encode(
            texts,
            batch_size=BATCH_SIZE,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        """
        Convert a user query into an embedding.
        """

        if not text.strip():
            raise ValueError("Query text cannot be empty.")

        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return embedding.tolist()


def create_embedding_model() -> SentenceTransformerEmbeddings:
    """
    Create and return the embedding model.
    """

    return SentenceTransformerEmbeddings()


def generate_embeddings(
    texts: List[str],
    embedding_model: SentenceTransformerEmbeddings
) -> List[List[float]]:
    """
    Generate embeddings for a list of text strings.
    """

    return embedding_model.embed_documents(texts)


if __name__ == "__main__":

    print("Testing the embedding model...")

    embedding_model = create_embedding_model()

    sample_texts = [
        (
            "Environmental clearance is required for projects "
            "covered under the EIA Notification."
        ),
        (
            "The State Level Environment Impact Assessment "
            "Authority is known as SEIAA."
        ),
        (
            "पर्यावरणीय मंजूरी के लिए निर्धारित प्रक्रिया "
            "का पालन करना आवश्यक है।"
        )
    ]

    embeddings = generate_embeddings(
        sample_texts,
        embedding_model
    )

    print("\n========== EMBEDDING SUMMARY ==========")
    print(f"Input texts: {len(sample_texts)}")
    print(f"Generated embeddings: {len(embeddings)}")

    if embeddings:
        print(f"Embedding dimensions: {len(embeddings[0])}")

    print("=======================================\n")

    query = "What is the role of SEIAA?"

    query_embedding = embedding_model.embed_query(query)

    print(f"Query: {query}")
    print(f"Query embedding dimensions: {len(query_embedding)}")
