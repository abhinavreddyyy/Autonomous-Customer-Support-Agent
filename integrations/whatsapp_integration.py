from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from flask import Flask, request
from agent.react_agent import get_react_agent
import logging

logger = logging.getLogger(__name__)

# Initialize Twilio
account_sid = "your_account_sid"
auth_token = "your_auth_token"
client = Client(account_sid, auth_token)

app = Flask(__name__)
user_agents = {}

@app.route("/whatsapp", methods=["POST"])
def whatsapp_message():
    """Handle incoming WhatsApp messages."""
    incoming_msg = request.values.get("Body", "").strip()
    sender = request.values.get("From")
    
    # Get or create agent
    if sender not in user_agents:
        user_agents[sender] = get_react_agent(user_id=sender)
    
    agent = user_agents[sender]
    
    try:
        # Process message
        response, _ = agent.process_input(incoming_msg)
        
        # Send response
        resp = MessagingResponse()
        resp.message(response)
        
        return str(resp)
    
    except Exception as e:
        logger.error(f"Error: {e}")
        resp = MessagingResponse()
        resp.message("Sorry, I encountered an error. Please try again.")
        return str(resp)

if __name__ == "__main__":
    app.run(debug=False, port=5000)