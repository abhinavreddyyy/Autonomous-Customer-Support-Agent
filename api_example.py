from __future__ import annotations

from flask import Flask, request, jsonify
from agent.react_agent import get_react_agent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

agents = {}

def get_agent(user_id: str):
    if user_id not in agents:
        agents[user_id] = get_react_agent(user_id)
    return agents[user_id]


@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_id = data.get('user_id', 'default')
        message = data.get('message', '')
        
        if not message:
            return jsonify({"error": "No message provided"}), 400
        
        agent = get_agent(user_id)
        response, metadata = agent.process_input(message)
        
        return jsonify({
            "success": metadata['success'],
            "response": response,
            "user_id": user_id
        })
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/history/<user_id>', methods=['GET'])
def get_history(user_id):
    try:
        agent = get_agent(user_id)
        summary = agent.get_conversation_summary()
        return jsonify(summary)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/agent/info/<user_id>', methods=['GET'])
def agent_info(user_id):
    try:
        agent = get_agent(user_id)
        info = agent.get_agent_info()
        return jsonify(info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200


if __name__ == '__main__':
    print("Starting Support Agent API...")
    print("Endpoints:")
    print("  POST   /api/chat - Send message")
    print("  GET    /api/history/<user_id> - Get conversation history")
    print("  GET    /api/agent/info/<user_id> - Get agent info")
    print("  GET    /health - Health check")
    print("\nServer running on http://localhost:5000")
    
    app.run(debug=True, port=5000)