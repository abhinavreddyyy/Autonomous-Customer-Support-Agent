from telegram import Update, ChatAction
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from agent.react_agent import get_react_agent
import logging

logger = logging.getLogger(__name__)

# Store agents
user_agents = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message."""
    await update.message.reply_text(
        "Welcome to Support Agent! Ask me about our products, policies, and more."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message."""
    await update.message.reply_text(
        """I can help with:
        - Product information
        - Pricing and promotions
        - Shipping information
        - Return policy
        - Order tracking
        - And much more!
        
        Just ask me anything!"""
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages."""
    user_id = str(update.effective_user.id)
    text = update.message.text
    
    # Show typing indicator
    await update.message.chat.send_action(ChatAction.TYPING)
    
    # Get or create agent
    if user_id not in user_agents:
        user_agents[user_id] = get_react_agent(user_id=user_id)
    
    agent = user_agents[user_id]
    
    try:
        # Process message
        response, _ = agent.process_input(text)
        
        # Send response
        if len(response) > 4096:
            # Telegram limit is 4096 chars
            chunks = [response[i:i+4096] for i in range(0, len(response), 4096)]
            for chunk in chunks:
                await update.message.reply_text(chunk)
        else:
            await update.message.reply_text(response)
    
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(f"Error: {str(e)}")

def main():
    """Start the bot."""
    # Create application
    application = Application.builder().token("your_telegram_token").build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start bot
    application.run_polling()

if __name__ == "__main__":
    main()