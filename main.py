#!/usr/bin/env python3
"""
Main entry point for the Autonomous Customer Support Agent.
"""

import logging
import sys
from agent.react_agent import get_react_agent
from rag.vector_store import get_vector_store

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def initialize_system():
    """Initialize vector store and agent."""
    logger.info("Initializing vector store...")
    vector_store = get_vector_store()
    logger.info(f"Vector store ready with {len(vector_store.documents)} documents")
    
    logger.info("Initializing agent...")
    agent = get_react_agent(user_id="default", verbose=False)
    logger.info("Agent initialized successfully")
    
    return agent


def interactive_chat(agent):
    """Run interactive chat with agent."""
    print("\n" + "="*60)
    print("AUTONOMOUS CUSTOMER SUPPORT AGENT")
    print("="*60)
    print("Type 'quit' or 'exit' to end conversation")
    print("Type 'info' to see agent information")
    print("Type 'summary' to see conversation summary")
    print("="*60 + "\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit']:
                print("\nThank you for using our support service. Goodbye!")
                break
            
            if user_input.lower() == 'info':
                info = agent.get_agent_info()
                print("\n=== Agent Information ===")
                for key, value in info.items():
                    print(f"{key}: {value}")
                print()
                continue
            
            if user_input.lower() == 'summary':
                summary = agent.get_conversation_summary()
                print("\n=== Conversation Summary ===")
                print(f"Messages: {summary['message_count']}")
                print(f"Total Interactions: {summary['interaction_count']}")
                print()
                continue
            
            print("\nAssistant: ", end="", flush=True)
            response, metadata = agent.process_input(user_input)
            print(response)
            print()
        
        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"\nError: {e}\n")


def demo_mode():
    """Run demo with predefined queries."""
    agent = initialize_system()
    
    demo_queries = [
        "What's the price of Premium Wireless Headphones?",
        "What is your return policy?",
        "Can I use USB-C charger with iPhone?",
        "Look up my order ORD001",
        "How long is shipping?"
    ]
    
    print("\n" + "="*60)
    print("DEMO MODE - AUTONOMOUS SUPPORT AGENT")
    print("="*60 + "\n")
    
    for query in demo_queries:
        print(f"User: {query}")
        response, _ = agent.process_input(query)
        print(f"Agent: {response}\n")
        print("-"*60 + "\n")


if __name__ == "__main__":
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "demo":
            demo_mode()
        else:
            agent = initialize_system()
            interactive_chat(agent)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
