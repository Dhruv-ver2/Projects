import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class SupremeBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="judo ", intents=intents, help_command=None)

    async def setup_hook(self):
        await self.load_extension("cogs.asp_protocol")
        await self.load_extension("cogs.management")
        print("✅ All Supreme Modules Loaded")

    async def on_ready(self):
        print(f'--- {self.user.name} CORE ONLINE ---')

bot = SupremeBot()

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Online. {round(bot.latency * 1000)}ms")

# DO NOT share this token with anyone!
bot.run('MTM5OTIzMDM2NjAzOTkzNzEwNA.GGgNCx.MBxMlrwJ9tohvhzsm_6U5UOLy-7F18ucTJLd68')