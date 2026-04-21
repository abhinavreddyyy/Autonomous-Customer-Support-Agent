from __future__ import annotations

import logging
from typing import List
from langchain.schema import Document
from langchain.tools import BaseTool
from rag.vector_store import get_vector_store

logger = logging.getLogger(__name__)


class FAISSRetrieverTool(BaseTool):
    name = "semantic_search"
    description = (
        "Searches the product catalog and FAQ database using semantic similarity. "
        "Use this to find information about products, pricing, policies, and FAQs. "
        "Input: A search query (e.g., 'battery life of headphones', 'return policy')"
    )
    
    def __init__(self, top_k: int = 3):
        super().__init__()
        self.top_k = top_k
        self.vector_store = get_vector_store()
    
    def _run(self, query: str) -> str:
        try:
            logger.info(f"Searching for: {query}")
            results = self.vector_store.search(query, k=self.top_k)
            
            if not results:
                return "No relevant information found in the knowledge base."
            
            formatted_results = "Found the following relevant information:\n\n"
            for i, (text, score, metadata) in enumerate(results, 1):
                formatted_results += f"{i}. (Relevance: {score:.2%})\n"
                formatted_results += f"{text}\n\n"
            
            return formatted_results
        
        except Exception as e:
            logger.error(f"Error during semantic search: {e}")
            return f"Error searching knowledge base: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        return self._run(query)


class ProductSearchTool(BaseTool):
    name = "product_search"
    description = (
        "Search for products by name, category, or features. "
        "Returns product details including price and warranty. "
        "Input: Product name or category (e.g., 'wireless headphones', 'storage devices')"
    )
    
    def __init__(self):
        super().__init__()
        self.vector_store = get_vector_store()
    
    def _run(self, query: str) -> str:
        try:
            results = self.vector_store.search(f"product {query}", k=5)
            
            product_results = [r for r in results if isinstance(r[2], dict) and 'category' in r[2]]
            
            if not product_results:
                return "No products found matching your search."
            
            formatted = "Found the following products:\n\n"
            for text, score, metadata in product_results:
                formatted += f"• {metadata.get('name', 'Unknown')}\n"
                formatted += f"  Price: ${metadata.get('price', 'N/A')}\n"
                formatted += f"  Warranty: {metadata.get('warranty', 'N/A')}\n\n"
            
            return formatted
        
        except Exception as e:
            logger.error(f"Error during product search: {e}")
            return f"Error searching products: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        return self._run(query)


class FAQSearchTool(BaseTool):
    name = "faq_search"
    description = (
        "Search the FAQ database for answers to common questions. "
        "Use for questions about policies, shipping, warranty, or general information. "
        "Input: Your question (e.g., 'What is the return policy?')"
    )
    
    def __init__(self):
        super().__init__()
        self.vector_store = get_vector_store()
    
    def _run(self, query: str) -> str:
        try:
            results = self.vector_store.search(query, k=3)
            
            if not results:
                return "No matching FAQ found. Please contact support for more information."
            
            formatted = "Found the following answers:\n\n"
            for text, score, metadata in results:
                if 'answer' in metadata:
                    formatted += f"Q: {metadata.get('question', 'Unknown')}\n"
                    formatted += f"A: {metadata.get('answer', 'No answer available')}\n\n"
                else:
                    formatted += f"{text}\n\n"
            
            return formatted
        
        except Exception as e:
            logger.error(f"Error during FAQ search: {e}")
            return f"Error searching FAQ: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        return self._run(query)


def get_retrieval_tools() -> List[BaseTool]:
    return [
        FAISSRetrieverTool(top_k=3),
        ProductSearchTool(),
        FAQSearchTool()
    ]