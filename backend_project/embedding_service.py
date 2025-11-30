import os
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient, models
from fastembed import TextEmbedding
from uuid import uuid4

class QdrantEmbeddingService:
    """
    Service for generating embeddings and storing/retrieving them from Qdrant.
    """
    def __init__(self, collection_name: str = "book_chunks", qdrant_host: str = "localhost", qdrant_port: int = 6333):
        self.collection_name = collection_name
        self.qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port)
        self.embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        self._initialize_collection()

    def _get_embedding_dimension(self) -> int:
        """
        Robustly gets the embedding dimension.
        If embedding_model.embedding_dimension is not available (e.g., due to model load failure),
        it attempts to infer it by embedding a dummy string.
        """
        try:
            return self.embedding_model.embedding_dimension
        except AttributeError:
            # Fallback: model might not be fully initialized, try inferring from a dummy embedding
            print("WARNING: 'embedding_dimension' attribute not found. Attempting to infer from dummy embedding.")
            dummy_embedding = list(self.embedding_model.embed(["hello world"]))[0] # Embed a list, get first embedding
            return len(dummy_embedding)

    def _initialize_collection(self):
        """
        Ensures the Qdrant collection exists with the correct configuration.
        """
        vector_size = self._get_embedding_dimension() # Use the robust method
        
        # Check if collection exists
        if not self.qdrant_client.collection_exists(collection_name=self.collection_name):
            self.qdrant_client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
            )
            print(f"Qdrant collection '{self.collection_name}' recreated with vector size {vector_size}.")
        else:
            print(f"Qdrant collection '{self.collection_name}' already exists.")

    def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generates embeddings for a list of texts.
        """
        # The TextEmbedding model returns a generator, convert to list
        embeddings = list(self.embedding_model.embed(texts))
        return embeddings

    def add_documents(self, documents: List[Dict[str, Any]]):
        """
        Adds documents (chunks of text) to the Qdrant collection.

        Args:
            documents (List[Dict[str, Any]]): List of dictionaries, each with:
                - 'text': The text content of the chunk.
                - 'metadata': A dictionary of metadata (e.g., {'source': 'chapter1.md'}).
        """
        if not documents:
            return

        texts = [doc['text'] for doc in documents]
        metadatas = [doc['metadata'] for doc in documents]
        
        embeddings = self._generate_embeddings(texts)

        points = []
        for i, text in enumerate(texts):
            points.append(models.PointStruct(
                id=str(uuid4()), # Generate a unique ID for each point
                vector=embeddings[i],
                payload={"text": text, **metadatas[i]}
            ))

        self.qdrant_client.upsert(
            collection_name=self.collection_name,
            points=points,
            wait=True
        )
        print(f"Added {len(documents)} documents to Qdrant collection '{self.collection_name}'.")

    def query_collection(self, query_text: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Queries the Qdrant collection for similar documents.

        Args:
            query_text (str): The query string.
            limit (int): The maximum number of results to return.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each containing 'text' and 'metadata'
                                   of the retrieved documents.
        """
        query_embedding = self._generate_embeddings([query_text])[0]

        search_result = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit,
            with_payload=True
        )

        results = []
        for hit in search_result:
            results.append({
                "text": hit.payload["text"],
                "metadata": {k: v for k, v in hit.payload.items() if k != "text"}
            })
        return results

# Example Usage
if __name__ == "__main__":
    # Ensure Qdrant is running, e.g., via Docker: docker run -p 6333:6333 qdrant/qdrant
    
    embedding_service = QdrantEmbeddingService(collection_name="test_book_chunks")

    # Add some dummy documents
    dummy_docs = [
        {"text": "Chapter 1: Introduction to Physical AI.", "metadata": {"source": "chapter1.md"}},
        {"text": "Physical AI systems interact with the real world.", "metadata": {"source": "chapter1.md"}},
        {"text": "Humanoid robots aim to mimic human form and function.", "metadata": {"source": "chapter2.md"}},
        {"text": "Bipedal locomotion is a challenge in humanoid robotics.", "metadata": {"source": "chapter2.md"}},
        {"text": "The future of AI involves embodied intelligence.", "metadata": {"source": "chapter3.md"}},
    ]
    embedding_service.add_documents(dummy_docs)

    # Query the collection
    print("\n--- Querying Qdrant ---")
    query = "what is physical intelligence?"
    search_results = embedding_service.query_collection(query, limit=2)
    print(f"\nQuery: '{query}'")
    for res in search_results:
        print(f"  - Score: N/A (Qdrant search result implicit score)")
        print(f"    Text: {res['text']}")
        print(f"    Metadata: {res['metadata']}")

    query = "human-like robots challenges"
    search_results = embedding_service.query_collection(query, limit=1)
    print(f"\nQuery: '{query}'")
    for res in search_results:
        print(f"  - Score: N/A (Qdrant search result implicit score)")
        print(f"    Text: {res['text']}")
        print(f"    Metadata: {res['metadata']}")
