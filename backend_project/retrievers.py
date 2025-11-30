from typing import List, Dict, Any, Optional

# from backend_project.bedrock_rag import query_bedrock_knowledge_base # No longer directly used
from backend_project.embedding_service import QdrantEmbeddingService # New Import

class BedrockKnowledgeBaseRetriever:
    """
    A retriever class that interfaces with a Knowledge Base.
    Originally designed for Bedrock, now adapted to use QdrantEmbeddingService
    for retrieving from ingested book content.
    """
    def __init__(self, knowledge_base_id: str, number_of_results: int = 4):
        # knowledge_base_id will now effectively be the Qdrant collection name
        self.qdrant_collection_name = knowledge_base_id 
        self.number_of_results = number_of_results
        self.qdrant_embedding_service = QdrantEmbeddingService(
            collection_name=self.qdrant_collection_name
        )

    def retrieve(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Retrieves relevant documents from the configured Knowledge Base (now Qdrant).

        Args:
            query (str): The user's query.
            filters (Optional[Dict[str, Any]]): Optional filters for the retrieval.
                                                (Currently not used by QdrantEmbeddingService.query_collection,
                                                 but kept for API compatibility.)

        Returns:
            List[str]: A list of retrieved document contents.
        """
        # The filters parameter is currently not utilized by QdrantEmbeddingService.query_collection
        # but is kept for API compatibility. If filtering is needed, it would be implemented
        # within QdrantEmbeddingService.query_collection or handled here before the call.
        retrieved_documents_payloads = self.qdrant_embedding_service.query_collection(
            query_text=query,
            limit=self.number_of_results
        )
        # Extract just the text content from the retrieved payloads
        retrieved_texts = [doc['text'] for doc in retrieved_documents_payloads]
        return retrieved_texts

if __name__ == "__main__":
    # Example usage
    test_collection_name = "test_book_chunks" # This should match a collection created by embedding_service example

    # Start Qdrant first, then run embedding_service example to populate 'test_book_chunks'
    # before running this example.
    
    # Initialize the retriever
    qdrant_retriever = BedrockKnowledgeBaseRetriever(knowledge_base_id=test_collection_name, number_of_results=2)

    print("\n--- Testing QdrantRetriever (adapted from BedrockKnowledgeBaseRetriever) ---")
    query = "What is physical intelligence?"
    results = qdrant_retriever.retrieve(query)
    print(f"Query: '{query}'")
    for i, doc in enumerate(results):
        print(f"Retrieved Document {i+1}: {doc}")

    query = "human-like robots challenges"
    results = qdrant_retriever.retrieve(query)
    print(f"Query: '{query}'")
    for i, doc in enumerate(results):
        print(f"Retrieved Document {i+1}: {doc}")