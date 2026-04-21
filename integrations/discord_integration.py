import discord
from discord.ext import commands
from agent.react_agent import get_react_agent
import logging

logger = logging.getLogger(__name__)

# Initialize bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Agent per user
user_agents = {}

@bot.event
async def on_ready():
    """Bot connected."""
    logger.info(f'{bot.user} has connected to Discord!')

@bot.event
async def on_message(message):
    """Handle incoming messages."""
    # Ignore bot's own messages
    if message.author == bot.user:
        return
    
    # Only respond to mentions
    if bot.user.mentioned_in(message):
        user_id = str(message.author.id)
        
        # Get or create agent
        if user_id not in user_agents:
            user_agents[user_id] = get_react_agent(user_id=user_id)
        
        agent = user_agents[user_id]
        
        # Remove mention from message
        text = message.content.replace(f"<@{bot.user.id}>", "").strip()
        
        try:
            response, _ = agent.process_input(text)
            
            # Send response (split if too long)
            if len(response) > 2000:
                chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
                for chunk in chunks:
                    await message.reply(chunk)
            else:
                await message.reply(response)
        
        except Exception as e:
            logger.error(f"Error: {e}")
            await message.reply(f"Error: {str(e)}")

@bot.command(name="help")
async def help_command(ctx):
    """Show help."""
    help_text = """
    **Support Agent Commands:**
    - Just mention me with your question
    - I can help with product info, orders, shipping, and more
    """
    await ctx.send(help_text)

# Run bot
bot.run("your-discord-token")