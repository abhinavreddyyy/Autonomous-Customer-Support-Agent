from __future__ import annotations

import json
import logging
from typing import Dict, List, Any
from pathlib import Path
from datetime import datetime
from langchain.memory import ConversationBufferWindowMemory
from langchain.chat_models import ChatOpenAI
from config.settings import settings

logger = logging.getLogger(__name__)


class PersistentMemoryManager:
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.memory_dir = Path("data/memory")
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        self.llm = ChatOpenAI(
            model_name=settings.openai_model,
            temperature=0.7
        )
        
        self.conversation_memory = ConversationBufferWindowMemory(
            k=settings.memory_window_size,
            memory_key="chat_history",
            input_key="input",
            output_key="output",
            human_prefix="User",
            ai_prefix="Assistant"
        )
        
        self.user_preferences = self._load_preferences()
        self.conversation_history = self._load_history()
    
    def _load_preferences(self) -> Dict[str, Any]:
        pref_file = self.memory_dir / f"{self.user_id}_preferences.json"
        
        if pref_file.exists():
            try:
                with open(pref_file, 'r') as f:
                    logger.info(f"Loaded preferences for user {self.user_id}")
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading preferences: {e}")
        
        return {
            "user_id": self.user_id,
            "created_at": datetime.now().isoformat(),
            "preferred_products": [],
            "contact_info": {},
            "interaction_count": 0
        }
    
    def _load_history(self) -> List[Dict[str, Any]]:
        history_file = self.memory_dir / f"{self.user_id}_history.json"
        
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    data = json.load(f)
                    logger.info(f"Loaded {len(data)} conversation messages")
                    return data
            except Exception as e:
                logger.error(f"Error loading history: {e}")
        
        return []
    
    def add_message(self, user_input: str, agent_output: str, metadata: Dict[str, Any] | None = None) -> None:
        self.conversation_memory.save_context(
            {"input": user_input},
            {"output": agent_output}
        )
        
        message = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "agent_output": agent_output,
            "metadata": metadata or {}
        }
        self.conversation_history.append(message)
        self.user_preferences["interaction_count"] += 1
        
        logger.info(f"Added message to history. Total: {len(self.conversation_history)}")
    
    def get_memory_context(self) -> str:
        return self.conversation_memory.buffer
    
    def update_preferences(self, preferences: Dict[str, Any]) -> None:
        self.user_preferences.update(preferences)
        self.user_preferences["updated_at"] = datetime.now().isoformat()
        logger.info(f"Updated preferences for user {self.user_id}")
    
    def save_to_disk(self) -> None:
        try:
            pref_file = self.memory_dir / f"{self.user_id}_preferences.json"
            with open(pref_file, 'w') as f:
                json.dump(self.user_preferences, f, indent=2)
            
            history_file = self.memory_dir / f"{self.user_id}_history.json"
            with open(history_file, 'w') as f:
                json.dump(self.conversation_history, f, indent=2)
            
            logger.info(f"Saved memory to disk for user {self.user_id}")
        
        except Exception as e:
            logger.error(f"Error saving memory to disk: {e}")
    
    def clear_memory(self) -> None:
        self.conversation_memory.clear()
        self.conversation_history = []
        logger.info(f"Cleared conversation memory for user {self.user_id}")
    
    def get_summary(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "message_count": len(self.conversation_history),
            "interaction_count": self.user_preferences.get("interaction_count", 0),
            "preferences": self.user_preferences,
            "recent_messages": self.conversation_history[-5:] if self.conversation_history else []
        }


_memory_manager = None

def get_memory_manager(user_id: str = "default") -> PersistentMemoryManager:
    global _memory_manager
    if _memory_manager is None or _memory_manager.user_id != user_id:
        _memory_manager = PersistentMemoryManager(user_id)
    return _memory_manager