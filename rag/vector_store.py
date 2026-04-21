from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import List, Tuple, Dict, Any
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from config.settings import settings

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self):
        self.embedding_model = SentenceTransformer(settings.embedding_model)
        self.index = None
        self.documents = []
        self.embeddings = None
        self.index_path = Path(settings.faiss_index_path)
        
    def load_documents(self) -> None:
        self.documents = []
        
        product_file = Path("data/product_catalog.json")
        if product_file.exists():
            with open(product_file, 'r') as f:
                product_data = json.load(f)
                for product in product_data.get("products", []):
                    doc_text = (
                        f"Product: {product['name']}. "
                        f"Category: {product['category']}. "
                        f"Price: ${product['price']}. "
                        f"Description: {product['description']}. "
                        f"Features: {', '.join(product['features'])}. "
                        f"Warranty: {product['warranty']}. "
                        f"Return Policy: {product['return_policy']}"
                    )
                    self.documents.append({
                        "id": product["id"],
                        "type": "product",
                        "text": doc_text,
                        "metadata": product
                    })
            logger.info(f"Loaded {len(product_data.get('products', []))} products")
        
        faq_file = Path("data/faq_data.json")
        if faq_file.exists():
            with open(faq_file, 'r') as f:
                faq_data = json.load(f)
                for faq in faq_data.get("faqs", []):
                    doc_text = f"Q: {faq['question']} A: {faq['answer']}"
                    self.documents.append({
                        "id": faq["id"],
                        "type": "faq",
                        "text": doc_text,
                        "metadata": faq
                    })
            logger.info(f"Loaded {len(faq_data.get('faqs', []))} FAQs")
        
        logger.info(f"Total documents loaded: {len(self.documents)}")
    
    def create_embeddings(self) -> None:
        if not self.documents:
            logger.warning("No documents to embed")
            return
        
        texts = [doc["text"] for doc in self.documents]
        logger.info(f"Creating embeddings for {len(texts)} documents...")
        
        self.embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
        logger.info(f"Embeddings created with shape: {self.embeddings.shape}")
    
    def build_index(self) -> None:
        if self.embeddings is None:
            logger.error("Embeddings not created. Call create_embeddings first.")
            return
        
        embeddings_float32 = self.embeddings.astype(np.float32)
        dimension = embeddings_float32.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings_float32)
        
        logger.info(f"FAISS index created with {self.index.ntotal} vectors")
    
    def save_index(self) -> None:
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        
        index_file = str(self.index_path)
        faiss.write_index(self.index, index_file)
        
        docs_file = f"{index_file}_documents.json"
        with open(docs_file, 'w') as f:
            json.dump(self.documents, f, indent=2)
        
        logger.info(f"Index saved to {index_file}")
    
    def load_index(self) -> bool:
        index_file = str(self.index_path)
        docs_file = f"{index_file}_documents.json"
        
        if not os.path.exists(index_file):
            logger.warning(f"Index file not found at {index_file}")
            return False
        
        self.index = faiss.read_index(index_file)
        
        with open(docs_file, 'r') as f:
            self.documents = json.load(f)
        
        logger.info(f"Index loaded from {index_file}")
        return True
    
    def search(self, query: str, k: int | None = None) -> List[Tuple[str, float, dict]]:
        if k is None:
            k = settings.top_k_results
        
        if self.index is None or not self.documents:
            logger.warning("Index not initialized or no documents loaded")
            return []
        
        query_embedding = self.embedding_model.encode([query], show_progress_bar=False)
        query_embedding_float32 = query_embedding.astype(np.float32)
        
        distances, indices = self.index.search(query_embedding_float32, k)
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.documents):
                doc = self.documents[idx]
                similarity_score = 1 / (1 + distance)
                
                if similarity_score >= settings.similarity_threshold:
                    results.append((
                        doc["text"],
                        similarity_score,
                        doc["metadata"]
                    ))
        
        return results
    
    def initialize(self) -> None:
        self.load_documents()
        
        if not self.load_index():
            self.create_embeddings()
            self.build_index()
            self.save_index()


_vector_store = None

def get_vector_store() -> VectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
        _vector_store.initialize()
    return _vector_store