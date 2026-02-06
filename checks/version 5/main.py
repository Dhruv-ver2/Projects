import discord
from discord.ext import commands
import os
from datetime import datetime, timezone

# 1. Bot Setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class SupremeBot(commands.Bot):
    def __init__(self):
        # FIX: Ensure all parentheses are closed and commas are present
        super().__init__(
            command_prefix=["judo ", "Judo ", "JUDO "], 
            intents=intents, 
            help_command=None,
            case_insensitive=True
        ) # <--- This closing parenthesis was likely missing or misplaced
        
        # Now these assignments will work perfectly
        self.panic_mode = False  
        self.panic_snapshot = {} 
        self.start_time = datetime.now(timezone.utc)
        
        self.judo_stats = {
            "attempts": 0,
            "success": 0,
            "failed": 0,
            "active_users": set()
        }

    async def setup_hook(self):
        # Loading the Power Modules
        await self.load_extension("cogs.asp_protocol")
        await self.load_extension("cogs.management_base")
        await self.load_extension("cogs.moderation")
        await self.load_extension("cogs.utilities")
        await self.load_extension("cogs.emergency") # Ensure this is loaded!
        print("✅ All Supreme Modules Loaded")

    async def on_ready(self):
        print(f'--- {self.user.name} CORE ONLINE ---')

bot = SupremeBot()

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Online. {round(bot.latency * 1000)}ms")

# Use your token here
bot.run('MTM5OTIzMDM2NjAzOTkzNzEwNA.GGgNCx.MBxMlrwJ9tohvhzsm_6U5UOLy-7F18ucTJLd68')