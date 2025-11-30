import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Add the parent directory of backend-project (i.e., hackathon/) to sys.path
# This is a workaround for ModuleNotFoundError when running tests.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend_project.retrievers import BedrockKnowledgeBaseRetriever
from backend_project.bedrock_rag import query_bedrock_knowledge_base

# Mock the underlying query_bedrock_knowledge_base for isolated testing
@patch('backend_project.bedrock_rag.query_bedrock_knowledge_base')
def test_bedrock_knowledge_base_retriever_retrieve(mock_query_bedrock_knowledge_base):
    mock_query_bedrock_knowledge_base.return_value = ["mocked doc 1", "mocked doc 2"]

    kb_id = "test-kb-456"
    num_results = 2
    retriever = BedrockKnowledgeBaseRetriever(knowledge_base_id=kb_id, number_of_results=num_results)

    query = "test query"
    results = retriever.retrieve(query)

    mock_query_bedrock_knowledge_base.assert_called_once_with(
        query=query,
        knowledge_base_id=kb_id,
        number_of_results=num_results,
        filters=None
    )
    assert results == ["mocked doc 1", "mocked doc 2"]

@patch('backend_project.bedrock_rag.query_bedrock_knowledge_base')
def test_bedrock_knowledge_base_retriever_retrieve_with_filters(mock_query_bedrock_knowledge_base):
    mock_query_bedrock_knowledge_base.return_value = ["filtered doc 1"]

    kb_id = "test-kb-789"
    retriever = BedrockKnowledgeBaseRetriever(knowledge_base_id=kb_id)
    
    query = "filtered test query"
    filters = {"category": "tech"}
    results = retriever.retrieve(query, filters=filters)

    mock_query_bedrock_knowledge_base.assert_called_once_with(
        query=query,
        knowledge_base_id=kb_id,
        number_of_results=4, # Default value
        filters=filters
    )
    assert results == ["filtered doc 1"]

def test_bedrock_knowledge_base_retriever_initialization():
    kb_id = "init-test-kb"
    num_results = 5
    retriever = BedrockKnowledgeBaseRetriever(knowledge_base_id=kb_id, number_of_results=num_results)
    assert retriever.knowledge_base_id == kb_id
    assert retriever.number_of_results == num_results

    default_retriever = BedrockKnowledgeBaseRetriever(knowledge_base_id="default-kb")
    assert default_retriever.number_of_results == 4 # Default value
