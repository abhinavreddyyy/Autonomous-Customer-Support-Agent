from __future__ import annotations

import pytest
import json
from pathlib import Path
from rag.vector_store import VectorStore


class TestVectorStore:
    @pytest.fixture
    def vector_store(self):
        vs = VectorStore()
        vs.load_documents()
        vs.create_embeddings()
        vs.build_index()
        return vs
    
    def test_load_documents(self, vector_store):
        assert len(vector_store.documents) > 0
    
    def test_search_products(self, vector_store):
        results = vector_store.search("headphones", k=3)
        assert len(results) > 0
    
    def test_search_faq(self, vector_store):
        results = vector_store.search("return policy", k=3)
        assert len(results) > 0
    
    def test_similarity_threshold(self, vector_store):
        results = vector_store.search("xyz123random", k=5)
        assert isinstance(results, list)


if __name__ == "__main__":
    pytest.main([__file__])