import discord
from discord.ext import commands
from datetime import datetime
from datetime import datetime, timezone

class SupremeBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=["judo ", "Judo ", "JUDO "], 
            intents=discord.Intents.all(), 
            help_command=None,
            case_insensitive=True
        )

        self.start_time = datetime.now(timezone.utc)
        # Centralized Supreme Analytics
        self.judo_stats = {
            "attempts": 0,
            "success": 0,
            "failed": 0,
            "active_users": set()
        }

    async def setup_hook(self):
        # Loading split modules
        await self.load_extension("cogs.asp_protocol")
        await self.load_extension("cogs.management_base")
        await self.load_extension("cogs.moderation")
        await self.load_extension("cogs.utilities")
        print("✅ Judo Core: All Supreme Modules Synchronized")

    async def on_ready(self):
        print(f'--- {self.user.name} CORE ONLINE ---')

bot = SupremeBot()

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Latency: {round(bot.latency * 1000)}ms")

bot.run('MTM5OTIzMDM2NjAzOTkzNzEwNA.GGgNCx.MBxMlrwJ9tohvhzsm_6U5UOLy-7F18ucTJLd68')