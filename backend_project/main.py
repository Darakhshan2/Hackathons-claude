from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, StreamingResponse
from typing import List, AsyncGenerator
import uvicorn
import os
import asyncio
from pathlib import Path

# Import RAG components
from backend_project.llm_config import (
    UserLLMConfig,
    UserLLMConfigRepository,
    UserLLMConfigService,
    llm_config_repository, # Assuming global instance from llm_config.py
    llm_config_service     # Assuming global instance from llm_config.py
)
from backend_project.chat_service import ChatService
from backend_project.embedding_service import QdrantEmbeddingService # New Import

# For document loading and chunking
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader

app = FastAPI()

# Placeholder for a user ID for demonstration purposes
# In a real application, this would come from an authentication system
DEMO_USER_ID = "demo_user"
DEMO_BEDROCK_KB_ID = os.environ.get("BEDROCK_KB_ID", QDRANT_COLLECTION_NAME)
DEMO_LLM_MODEL_NAME = os.environ.get("LLM_MODEL_NAME", "anthropic.claude-v2")

# Initialize a default LLM config for the demo user
# In a real app, this would be managed via UI/DB
initial_llm_config = UserLLMConfig(
    user_id=DEMO_USER_ID,
    provider_type="bedrock", # Assuming we're using Bedrock LLMs
    chat_model_name=DEMO_LLM_MODEL_NAME,
    bedrock_kb_id=DEMO_BEDROCK_KB_ID,
    bedrock_region_name=os.environ.get("AWS_REGION", "us-east-1")
)
llm_config_repository.save(initial_llm_config)

# Initialize Qdrant Embedding Service
QDRANT_COLLECTION_NAME = "book_chunks_collection"
qdrant_embedding_service = QdrantEmbeddingService(collection_name=QDRANT_COLLECTION_NAME)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the RAG Chatbot Backend!"}

@app.post("/ingest")
async def ingest_documents_from_book():
    """
    Ingests Markdown files from the website/docs/ directory into Qdrant.
    """
    docs_path = Path("../website/docs") # Relative path to the docs directory
    if not docs_path.is_dir():
        raise HTTPException(
            status_code=404,
            detail=f"Documentation directory not found at {docs_path.resolve()}. "
                   "Please ensure the 'website/docs' folder exists relative to backend-project."
        )

    documents_to_add = []
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        add_start_index=True,
    )

    for file_path in docs_path.glob("**/*.md"): # Assuming Markdown files
        try:
            loader = TextLoader(str(file_path))
            docs = loader.load()
            
            # Add source metadata
            for doc in docs:
                doc.metadata["source"] = str(file_path.relative_to(docs_path.parent)) # Relative to website/
            
            chunks = text_splitter.split_documents(docs)

            for i, chunk in enumerate(chunks):
                documents_to_add.append({
                    "text": chunk.page_content,
                    "metadata": {
                        "source": chunk.metadata.get("source", str(file_path.name)),
                        "chunk_index": i,
                        "title": chunk.metadata.get("title", file_path.stem),
                    }
                })
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            raise HTTPException(status_code=500, detail=f"Error processing file {file_path}: {e}")

    if not documents_to_add:
        return {"message": "No documents found or processed in website/docs/."}

    try:
        qdrant_embedding_service.add_documents(documents_to_add)
        return {"message": f"Successfully ingested {len(documents_to_add)} document chunks into Qdrant collection '{QDRANT_COLLECTION_NAME}'."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding documents to Qdrant: {e}")

async def get_chat_service() -> ChatService:
    """Dependency injector for ChatService."""
    llm_config = llm_config_service.get_available_llm_config(DEMO_USER_ID)
    if not llm_config or not llm_config.bedrock_kb_id:
        raise HTTPException(
            status_code=400,
            detail="LLM configuration or Bedrock Knowledge Base ID not found for user."
        )
    
    # Assuming a fixed system prompt for this demo
    system_prompt = "You are a helpful assistant for Physical AI and Humanoid Robotics. Answer based on provided context."
    
    return ChatService(
        bedrock_kb_id=llm_config.bedrock_kb_id,
        llm_config=llm_config,
        system_prompt=system_prompt
    )

@app.post("/chat")
async def chat_with_rag(
    query: str = Form(...),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Endpoint for RAG-enhanced chat.
    """
    # History management is simplified for this example
    history = [] 
    
    # Use the chat_service to get a streaming response
    async def generate_response():
        async for chunk in chat_service.chat(query, history):
            yield chunk

    return StreamingResponse(generate_response(), media_type="text/plain")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)