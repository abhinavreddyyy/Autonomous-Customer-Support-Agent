from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseSettings, Field
import logging

load_dotenv()

class Settings(BaseSettings):
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4-turbo-preview", env="OPENAI_MODEL")
    faiss_index_path: str = Field(default="./data/faiss_index", env="FAISS_INDEX_PATH")
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    memory_type: str = Field(default="conversation_buffer_window", env="MEMORY_TYPE")
    memory_window_size: int = Field(default=5, env="MEMORY_WINDOW_SIZE")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    max_iterations: int = Field(default=10, env="MAX_ITERATIONS")
    timeout_seconds: int = Field(default=30, env="TIMEOUT_SECONDS")
    top_k_results: int = Field(default=3, env="TOP_K_RESULTS")
    similarity_threshold: float = Field(default=0.5, env="SIMILARITY_THRESHOLD")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("Configuration loaded successfully")