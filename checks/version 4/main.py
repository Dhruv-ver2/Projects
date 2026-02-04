import discord
from discord.ext import commands
import os

# 1. Bot Setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class SupremeBot(commands.Bot):
    def __init__(self):
        # The prefix is now a list to handle capitalization
        # case_insensitive=True allows 'SEND', 'Send', and 'send' to work
        super().__init__(
            command_prefix=["judo ", "Judo ", "JUDO "], 
            intents=intents, 
            help_command=None,
            case_insensitive=True
        )

    async def setup_hook(self):
        # Loading the Power Modules
        await self.load_extension("cogs.asp_protocol")
        await self.load_extension("cogs.management")
        print("✅ All Supreme Modules Loaded")

    async def on_ready(self):
        print(f'--- {self.user.name} CORE ONLINE ---')

bot = SupremeBot()

# A simple core command available to everyone
@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Online. {round(bot.latency * 1000)}ms")

# Use your newly reset token here
bot.run('MTM5OTIzMDM2NjAzOTkzNzEwNA.GGgNCx.MBxMlrwJ9tohvhzsm_6U5UOLy-7F18ucTJLd68')