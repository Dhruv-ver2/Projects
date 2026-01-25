import discord
import os
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime

# --- CONFIGURATION ---
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
OWNER_ID = int(os.getenv('OWNER_ID'))

intents = discord.Intents.default()
intents.message_content = True 
intents.members = True          

bot = commands.Bot(command_prefix="JUDO ", intents=intents)
bot.owner_id = OWNER_ID

@bot.event
async def on_ready():
    current_time = datetime.now().strftime("%H:%M:%S")
    print("-" * 30)
    print(f"[{current_time}] LOGGING ACTION: Connection Established.")
    print(f"[{current_time}] Judo is online now.")
    print(f"Logged in as: {bot.user.name}")
    print("-" * 30)

async def load_extensions():
    base_path = os.path.dirname(os.path.abspath(__file__))
    cogs_path = os.path.join(base_path, 'cogs')
    if not os.path.exists(cogs_path):
        os.makedirs(cogs_path)

    for filename in os.listdir(cogs_path):
        if filename.endswith('.py') and filename != '__init__.py':
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Cog Loaded: {filename}")
            except Exception as e:
                print(f"❌ Error loading {filename}: {e}")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Judo is shutting down...")