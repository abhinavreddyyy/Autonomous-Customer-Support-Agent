from __future__ import annotations

import logging
from typing import List, Tuple, Dict, Any
from langchain.agents import initialize_agent
from langchain_core.callbacks import StdOutCallbackHandler
from langchain.chat_models import ChatOpenAI
from config.settings import settings
from agent.prompts import get_system_prompt, get_react_prompt
from memory.persistent_memory import get_memory_manager
from rag.faiss_retriever import get_retrieval_tools
from tools.custom_tools import get_custom_tools

logger = logging.getLogger(__name__)


class ReActAgent:
    def __init__(self, user_id: str = "default", verbose: bool = False):
        self.user_id = user_id
        self.verbose = verbose
        
        self.llm = ChatOpenAI(
            model_name=settings.openai_model,
            temperature=0.7,
            max_tokens=500
        )
        
        self.memory_manager = get_memory_manager(user_id)
        self.tools = self._setup_tools()
        self.agent = self._initialize_agent()
        
        logger.info(f"ReActAgent initialized for user: {user_id}")
    
    def _setup_tools(self) -> List[BaseTool]:
        tools = []
        
        retrieval_tools = get_retrieval_tools()
        tools.extend(retrieval_tools)
        logger.info(f"Added {len(retrieval_tools)} retrieval tools")
        
        custom_tools = get_custom_tools()
        tools.extend(custom_tools)
        logger.info(f"Added {len(custom_tools)} custom tools")
        
        logger.info(f"Total tools available: {len(tools)}")
        return tools
    
    def _initialize_agent(self):
        callbacks = [StdOutCallbackHandler()] if self.verbose else []
    
        agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent="zero-shot-react-description",
            callbacks=callbacks,
            verbose=self.verbose,
            max_iterations=settings.max_iterations,
            timeout=settings.timeout_seconds,
            early_stopping_method="force"
        )
    
        return agent
    
    def _format_memory_context(self) -> str:
        memory_context = self.memory_manager.get_memory_context()
        if memory_context:
            return f"Previous conversation:\n{memory_context}"
        return ""
    
    def process_input(self, user_input: str) -> Tuple[str, Dict[str, Any]]:
        try:
            memory_context = self._format_memory_context()
            
            full_prompt = f"""{memory_context}

New customer request: {user_input}

Please provide a helpful response using the ReAct framework:
1. THINK about what the customer needs
2. ACT by using appropriate tools
3. OBSERVE the results
4. REASON about the best response
5. RESPOND to the customer"""
            
            logger.info(f"Processing input from user {self.user_id}")
            
            response = self.agent.run(full_prompt)
            
            self.memory_manager.add_message(
                user_input=user_input,
                agent_output=response,
                metadata={
                    "agent": "ReAct",
                    "model": settings.openai_model,
                    "tools_used": len(self.tools)
                }
            )
            self.memory_manager.save_to_disk()
            
            logger.info(f"Successfully processed input, response length: {len(response)}")
            
            return response, {
                "success": True,
                "user_id": self.user_id,
                "input_length": len(user_input),
                "response_length": len(response)
            }
        
        except Exception as e:
            logger.error(f"Error processing input: {e}")
            error_response = f"""I apologize, but I encountered an issue processing your request: {str(e)}

This has been logged and a support representative will be notified. 
Would you like me to create a support ticket for you?"""
            
            return error_response, {
                "success": False,
                "error": str(e),
                "user_id": self.user_id
            }
    
    def process_multi_turn(self, conversation: List[str]) -> List[Tuple[str, Dict]]:
        results = []
        for user_input in conversation:
            response, metadata = self.process_input(user_input)
            results.append((response, metadata))
        
        return results
    
    def get_agent_info(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "model": settings.openai_model,
            "max_iterations": settings.max_iterations,
            "timeout_seconds": settings.timeout_seconds,
            "tools_count": len(self.tools),
            "tools": [tool.name for tool in self.tools],
            "memory_window": settings.memory_window_size
        }
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        return self.memory_manager.get_summary()


_agent = None

def get_react_agent(user_id: str = "default", verbose: bool = False) -> ReActAgent:
    global _agent
    if _agent is None or _agent.user_id != user_id:
        _agent = ReActAgent(user_id, verbose)
    return _agent
