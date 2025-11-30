from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class ChatStrategy(ABC):
    """Abstract base class for chat strategies."""
    @abstractmethod
    def process_message(self, message: str, history: List[Dict[str, str]], **kwargs) -> str:
        """Processes a user message using the specific strategy."""
        pass

class SystemPromptStrategy(ChatStrategy):
    """
    A simple strategy that prepends a system prompt to the user's message
    or uses it to guide the LLM's response.
    """
    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt

    def process_message(self, message: str, history: List[Dict[str, str]], **kwargs) -> str:
        """
        In this simple implementation, the system prompt might be combined with the
        current message or used to influence the LLM context.
        For actual LLM calls, this prompt would be part of the messages array.
        """
        # For demonstration, we'll just return a combined string.
        # In a real scenario, this would format messages for an LLM API.
        return f"System Prompt: {self.system_prompt}\nUser Message: {message}"

class KnowledgeEnhancedStrategy(ChatStrategy):
    """
    A strategy that enhances the chat with retrieved knowledge from a RAG system.
    """
    def __init__(self, retriever: Any, system_prompt: Optional[str] = None):
        self.retriever = retriever
        self.system_prompt = system_prompt

    def process_message(self, message: str, history: List[Dict[str, str]], **kwargs) -> str:
        """
        Retrieves relevant documents based on the current message and history,
        then combines them with the message for the LLM.
        """
        retrieved_docs = self.retriever.retrieve(query=message)
        
        context = "\n".join(retrieved_docs)
        
        # Construct the enhanced prompt for the LLM
        enhanced_message = f"User Query: {message}\n\nContext from Knowledge Base:\n{context}\n\nBased on the context, please answer the user query."
        
        if self.system_prompt:
            return f"System Prompt: {self.system_prompt}\n{enhanced_message}"
        else:
            return enhanced_message

if __name__ == "__main__":
    # Dummy Retriever for testing strategies
    class DummyRetriever:
        def retrieve(self, query: str) -> List[str]:
            print(f"Dummy Retriever called with query: {query}")
            if "RAG" in query:
                return ["RAG stands for Retrieval Augmented Generation.", "It improves LLM responses with external knowledge."]
            return ["No specific document found by dummy retriever."]

    dummy_retriever = DummyRetriever()

    # Test SystemPromptStrategy
    print("\n--- Testing SystemPromptStrategy ---")
    sys_strategy = SystemPromptStrategy("You are a helpful AI assistant.")
    result = sys_strategy.process_message("Hello there!", [])
    print(result)

    # Test KnowledgeEnhancedStrategy
    print("\n--- Testing KnowledgeEnhancedStrategy with system prompt ---")
    kb_strategy = KnowledgeEnhancedStrategy(retriever=dummy_retriever, system_prompt="Answer concisely.")
    result = kb_strategy.process_message("What is RAG?", [])
    print(result)

    print("\n--- Testing KnowledgeEnhancedStrategy without system prompt ---")
    kb_strategy_no_sys = KnowledgeEnhancedStrategy(retriever=dummy_retriever)
    result = kb_strategy_no_sys.process_message("Another query.", [])
    print(result)
