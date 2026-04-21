from flask import Flask, request, jsonify
from agent.react_agent import get_react_agent
import hmac
import hashlib
import logging

logger = logging.getLogger(__name__)

app = Flask(__name__)

def verify_webhook_signature(payload: str, signature: str, secret: str) -> bool:
    """Verify webhook signature."""
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)

@app.route("/webhook/message", methods=["POST"])
def handle_webhook():
    """Handle incoming webhook."""
    signature = request.headers.get("X-Signature")
    payload = request.get_data(as_text=True)
    
    # Verify signature
    if not verify_webhook_signature(payload, signature, "your_webhook_secret"):
        return jsonify({"error": "Invalid signature"}), 401
    
    try:
        data = request.json
        user_id = data.get("user_id")
        message = data.get("message")
        
        agent = get_react_agent(user_id=user_id)
        response, _ = agent.process_input(message)
        
        return jsonify({
            "success": True,
            "response": response,
            "user_id": user_id
        })
    
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000)