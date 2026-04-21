from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request
from agent.react_agent import get_react_agent
import logging

logger = logging.getLogger(__name__)

# Initialize Slack app
slack_app = App(token="xoxb-your-bot-token", signing_secret="your-signing-secret")
flask_app = Flask(__name__)
handler = SlackRequestHandler(slack_app)

# Keep track of conversations
user_agents = {}

@slack_app.event("message")
def handle_message_events(body, say, logger):
    """Handle incoming Slack messages."""
    user_id = body["user"]
    text = body["text"]
    
    # Get or create agent for user
    if user_id not in user_agents:
        user_agents[user_id] = get_react_agent(user_id=user_id)
    
    agent = user_agents[user_id]
    
    # Process with agent
    try:
        response, _ = agent.process_input(text)
        say(response)
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        say(f"Sorry, I encountered an error: {str(e)}")

@slack_app.command("/support")
def handle_support_command(ack, body, say):
    """Handle /support slash command."""
    ack()
    say("Support agent ready! Ask me anything about our products.")

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    """Slack events endpoint."""
    return handler.handle(request)

if __name__ == "__main__":
    flask_app.run(port=3000)