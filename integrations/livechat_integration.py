from flask import Flask, request, jsonify
from agent.react_agent import get_react_agent
import logging

logger = logging.getLogger(__name__)

app = Flask(__name__)
conversations = {}

@app.route("/chat/start", methods=["POST"])
def start_chat():
    """Start a new chat session."""
    data = request.json
    visitor_id = data.get("visitor_id")
    
    conversations[visitor_id] = get_react_agent(user_id=visitor_id)
    
    return jsonify({
        "status": "started",
        "visitor_id": visitor_id,
        "message": "Welcome! How can I help you today?"
    })

@app.route("/chat/message", methods=["POST"])
def send_message():
    """Send message and get response."""
    data = request.json
    visitor_id = data.get("visitor_id")
    message = data.get("message")
    
    if visitor_id not in conversations:
        return jsonify({"error": "Chat session not found"}), 404
    
    try:
        agent = conversations[visitor_id]
        response, _ = agent.process_input(message)
        
        return jsonify({
            "status": "success",
            "response": response,
            "visitor_id": visitor_id
        })
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/chat/end", methods=["POST"])
def end_chat():
    """End chat session."""
    data = request.json
    visitor_id = data.get("visitor_id")
    
    if visitor_id in conversations:
        del conversations[visitor_id]
    
    return jsonify({"status": "ended"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)