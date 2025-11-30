import sys
import os
import pytest

# Add the parent directory of backend-project (i.e., hackathon/) to sys.path
# This is a workaround for ModuleNotFoundError when running tests.
# test_bedrock_rag.py is in backend-project/tests, so '..' goes to backend-project, '..' again goes to hackathon.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend_project.bedrock_rag import query_bedrock_knowledge_base

def test_query_bedrock_knowledge_base_physical_ai():
    """
    Test retrieval for 'physical ai' query.
    """
    query = "What is physical AI?"
    kb_id = "test-kb-123"
    results = query_bedrock_knowledge_base(query, kb_id)
    assert len(results) > 0
    assert any("Physical AI" in doc for doc in results)
    assert any("sensors and actuators" in doc for doc in results)

def test_query_bedrock_knowledge_base_humanoid_robotics():
    """
    Test retrieval for 'humanoid robotics' query.
    """
    query = "Tell me about humanoid robotics."
    kb_id = "test-kb-123"
    results = query_bedrock_knowledge_base(query, kb_id)
    assert len(results) > 0
    assert any("Humanoid robotics" in doc for doc in results)
    assert any("bipedal locomotion" in doc for doc in results)

def test_query_bedrock_knowledge_base_generic_query():
    """
    Test retrieval for a generic query with no specific matches in dummy data.
    """
    query = "What is the capital of France?"
    kb_id = "test-kb-123"
    results = query_bedrock_knowledge_base(query, kb_id)
    assert len(results) > 0
    assert all("generic retrieved document" in doc or "system is designed" in doc for doc in results)
    
def test_query_bedrock_knowledge_base_with_filters():
    """
    Test if filters are passed through (dummy implementation just prints them).
    """
    query = "filtered query"
    kb_id = "test-kb-456"
    filters = {"key": "value", "another_key": 123}
    # Since the dummy implementation just prints, we can't assert on filter application
    # but we can ensure it runs without error and returns dummy data.
    results = query_bedrock_knowledge_base(query, kb_id, filters=filters)
    assert len(results) > 0
