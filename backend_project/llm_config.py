from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class UserLLMConfig(BaseModel):
    """
    Represents a user's configuration for an LLM.
    This is a simplified Pydantic model for demonstration purposes.
    In a real application, this would likely be an ORM model (e.g., SQLAlchemy, FastAPI Users).
    """
    id: Optional[str] = None
    user_id: str
    provider_type: str = Field(..., description="e.g., 'openai', 'anthropic', 'bedrock'")
    chat_endpoint: Optional[str] = None
    chat_api_key: Optional[str] = None
    chat_model_name: str
    # Add fields for Bedrock KB if needed
    bedrock_kb_id: Optional[str] = None
    bedrock_region_name: Optional[str] = None

class UserLLMConfigRepository:
    """
    A simplified repository for managing UserLLMConfig.
    In a real application, this would interact with a database.
    """
    def __init__(self):
        self._configs: Dict[str, UserLLMConfig] = {} # In-memory store

    def get_by_user_id(self, user_id: str) -> Optional[UserLLMConfig]:
        """Retrieves an LLM config by user ID."""
        return self._configs.get(user_id)

    def save(self, config: UserLLMConfig) -> UserLLMConfig:
        """Saves or updates an LLM config."""
        if not config.id:
            config.id = f"llm-config-{len(self._configs) + 1}"
        self._configs[config.user_id] = config
        return config

class UserLLMConfigService:
    """
    Service layer for interacting with LLM configurations.
    """
    def __init__(self, repository: UserLLMConfigRepository):
        self.repository = repository

    def get_available_llm_config(self, user_id: str) -> Optional[UserLLMConfig]:
        """
        Retrieves the available LLM configuration for a given user.
        In a real scenario, this might involve more complex logic
        to determine the 'best' or 'default' available LLM.
        """
        return self.repository.get_by_user_id(user_id)

# Global instances for simple dependency injection
llm_config_repository = UserLLMConfigRepository()
llm_config_service = UserLLMConfigService(repository=llm_config_repository)

if __name__ == "__main__":
    # Example usage
    print("--- Testing UserLLMConfig ---")
    user_id = "test_user_123"

    # Create and save a config
    config = UserLLMConfig(
        user_id=user_id,
        provider_type="openai",
        chat_model_name="gpt-4",
        chat_api_key="sk-test-key"
    )
    saved_config = llm_config_repository.save(config)
    print(f"Saved config: {saved_config.model_dump_json(indent=2)}")

    # Retrieve the config
    retrieved_config = llm_config_service.get_available_llm_config(user_id)
    if retrieved_config:
        print(f"Retrieved config: {retrieved_config.model_dump_json(indent=2)}")
    else:
        print("Config not found for user.")

    # Test with Bedrock KB details
    bedrock_config = UserLLMConfig(
        user_id="bedrock_user",
        provider_type="bedrock",
        chat_model_name="anthropic.claude-v2",
        bedrock_kb_id="test-bedrock-kb-456",
        bedrock_region_name="us-east-1"
    )
    llm_config_repository.save(bedrock_config)
    print(f"\nSaved Bedrock config: {bedrock_config.model_dump_json(indent=2)}")
    retrieved_bedrock_config = llm_config_service.get_available_llm_config("bedrock_user")
    print(f"Retrieved Bedrock config: {retrieved_bedrock_config.model_dump_json(indent=2)}")
