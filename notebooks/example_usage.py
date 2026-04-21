from __future__ import annotations

import logging
from agent.react_agent import get_react_agent
from evaluation.evaluate_agent import AgentEvaluator
from rag.vector_store import get_vector_store

logging.basicConfig(level=logging.INFO)

print("="*60)
print("AUTONOMOUS SUPPORT AGENT - EXAMPLE USAGE")
print("="*60)

print("\n### Example 1: Initialize Agent ###")
agent = get_react_agent(user_id="demo_user")
print(f"Agent initialized: {agent.user_id}")

print("\n### Example 2: Process Single Query ###")
query = "What's the price of Premium Wireless Headphones?"
print(f"Query: {query}")
response, metadata = agent.process_input(query)
print(f"Response: {response}")
print(f"Success: {metadata['success']}")

print("\n### Example 3: Follow-up Query (Uses Memory) ###")
follow_up = "What's the warranty on that?"
print(f"Query: {follow_up}")
response2, _ = agent.process_input(follow_up)
print(f"Response: {response2}")

print("\n### Example 4: Agent Information ###")
info = agent.get_agent_info()
print(f"Model: {info['model']}")
print(f"Tools Available: {len(info['tools'])}")
print(f"Tool Names: {', '.join(info['tools'][:3])}...")

print("\n### Example 5: Conversation Summary ###")
summary = agent.get_conversation_summary()
print(f"Messages: {summary['message_count']}")
print(f"Interactions: {summary['interaction_count']}")

print("\n### Example 6: Vector Store (RAG) ###")
vs = get_vector_store()
results = vs.search("how long battery", k=2)
print(f"Found {len(results)} results for 'how long battery'")
for i, (text, score, meta) in enumerate(results, 1):
    print(f"\n  Result {i} (score: {score:.2%})")
    print(f"  {text[:100]}...")

print("\n### Example 7: Order Lookup ###")
order_query = "Look up my order ORD001"
response, _ = agent.process_input(order_query)
print(f"Order lookup result: {response[:200]}...")

print("\n### Example 8: Create Support Ticket ###")
ticket_query = "I need help with my headphones, please create a ticket"
response, _ = agent.process_input(ticket_query)
print(f"Ticket creation: {response[:200]}...")

print("\n" + "="*60)
print("All examples completed successfully!")
print("="*60)