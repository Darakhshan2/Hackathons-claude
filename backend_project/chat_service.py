from typing import List, Dict, Any, AsyncGenerator, Optional
import asyncio

# Assuming these imports from other created files
from backend_project.llm_config import UserLLMConfig
from backend_project.strategies import ChatStrategy, KnowledgeEnhancedStrategy, SystemPromptStrategy
from backend_project.retrievers import BedrockKnowledgeBaseRetriever

class ChatService:
    """
    Orchestrates chat interactions, applying various strategies and LLM configurations.
    """
    def __init__(self,
                 bedrock_kb_id: str,
                 llm_config: UserLLMConfig,
                 system_prompt: Optional[str] = None):
        self.bedrock_kb_id = bedrock_kb_id
        self.llm_config = llm_config
        self.system_prompt_content = system_prompt

        # Initialize retriever
        self.bedrock_retriever = BedrockKnowledgeBaseRetriever(
            knowledge_base_id=self.bedrock_kb_id
        )

        # Initialize strategies
        self.strategies: List[ChatStrategy] = []
        if self.system_prompt_content:
            self.strategies.append(SystemPromptStrategy(system_prompt=self.system_prompt_content))
        
        # Knowledge-enhanced strategy is always enabled for this RAG chatbot
        self.strategies.append(KnowledgeEnhancedStrategy(retriever=self.bedrock_retriever))

        # Placeholder for actual LLM client (e.g., OpenAI, Anthropic, Bedrock LLM)
        # This would be initialized based on self.llm_config
        # For now, we'll use a dummy LLM client.
        self.llm_client = self._initialize_llm_client(llm_config)

    def _initialize_llm_client(self, llm_config: UserLLMConfig):
        """
        Initializes a dummy LLM client based on UserLLMConfig.
        In a real application, this would set up an actual client (e.g., from boto3, openai).
        """
        print(f"Initializing dummy LLM client for provider: {llm_config.provider_type}, model: {llm_config.chat_model_name}")
        class DummyLLMClient:
            async def chat_completion(self, messages: List[Dict[str, str]], stream: bool = False) -> AsyncGenerator[str, None]:
                response_text = "This is a dummy LLM response."
                if "physical ai" in messages[-1]['content'].lower():
                    response_text = "Physical AI is about intelligent agents interacting with the real world."
                elif "humanoid robotics" in messages[-1]['content'].lower():
                    response_text = "Humanoid robots are designed to mimic human form and function."

                if stream:
                    for char in response_text:
                        yield char
                        await asyncio.sleep(0.02) # Simulate streaming delay
                else:
                    yield response_text
        return DummyLLMClient()

    async def chat(self, user_message: str, history: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """
        Processes a chat message, applies strategies, and interacts with the LLM.

        Args:
            user_message (str): The current message from the user.
            history (List[Dict[str, str]]): Previous chat messages.

        Returns:
            AsyncGenerator[str, None]: An asynchronous generator yielding chunks of the LLM's response.
        """
        # Apply strategies to enhance the user message
        processed_message = user_message
        for strategy in self.strategies:
            processed_message = strategy.process_message(processed_message, history)
        
        # Prepare messages for the LLM
        llm_messages = [{"role": "user", "content": processed_message}]
        # In a full implementation, history would also be formatted for the LLM

        print(f"Sending to dummy LLM: {llm_messages}")
        async for chunk in self.llm_client.chat_completion(llm_messages, stream=True):
            yield chunk

# Example Usage (for local testing)
async def main():
    print("--- Testing ChatService ---")
    
    # Setup dummy LLM config
    llm_config = UserLLMConfig(
        user_id="test_user",
        provider_type="bedrock",
        chat_model_name="anthropic.claude-v2",
        bedrock_kb_id="test-kb-123"
    )
    
    # Instantiate ChatService
    chat_service = ChatService(
        bedrock_kb_id=llm_config.bedrock_kb_id,
        llm_config=llm_config,
        system_prompt="You are a helpful assistant for Physical AI and Humanoid Robotics."
    )

    print("\n--- Chat 1: Physical AI ---")
    response_gen = chat_service.chat("What is physical AI?", [])
    full_response = ""
    async for chunk in response_gen:
        print(chunk, end="")
        full_response += chunk
    print(f"\nFull response: {full_response}")

    print("\n--- Chat 2: Humanoid Robotics ---")
    response_gen = chat_service.chat("Tell me about humanoid robotics.", [])
    full_response = ""
    async for chunk in response_gen:
        print(chunk, end="")
        full_response += chunk
    print(f"\nFull response: {full_response}")

    print("\n--- Chat 3: General Query ---")
    response_gen = chat_service.chat("How far is the moon?", [])
    full_response = ""
    async for chunk in response_gen:
        print(chunk, end="")
        full_response += chunk
    print(f"\nFull response: {full_response}")

if __name__ == "__main__":
    asyncio.run(main())
