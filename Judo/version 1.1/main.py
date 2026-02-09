import os
import discord
from discord.ext import commands
from datetime import datetime, timezone
from dotenv import load_dotenv
import database_manager as dbm  # Ensure your db_manager is in the same folder

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# 1. Bot Setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class SupremeBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=["judo ", "Judo ", "JUDO "],
            intents=intents,
            help_command=None,
            case_insensitive=True
        )

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
        # Loading the 7 Power Modules
        await self.load_extension("cogs.asp_protocol")
        await self.load_extension("cogs.management_base")
        await self.load_extension("cogs.moderation")
        await self.load_extension("cogs.utilities")
        await self.load_extension("cogs.emergency")
        await self.load_extension("cogs.ghost_log")
        await self.load_extension("cogs.stealth")
        print("✅ All Supreme Modules Loaded")

    async def scrub_ghost_data(self):
        """Audits JSON files and removes data for servers Judo has left."""
        print("🔍 Initiating Database Integrity Check...")
        
        # Get IDs of all servers Judo is currently in (as strings for JSON comparison)
        active_guild_ids = [str(guild.id) for guild in self.guilds]
        
        # 1. Audit authorize_list.json
        auth_data = dbm.load_json(dbm.AUTH_FILE)
        initial_auth_count = len(auth_data)
        # We use list() to avoid 'dictionary changed size during iteration' error
        for gid in list(auth_data.keys()):
            if gid not in active_guild_ids:
                del auth_data[gid]
        
        if len(auth_data) != initial_auth_count:
            dbm.save_json(dbm.AUTH_FILE, auth_data)
            print(f"🧹 Scrubbed {initial_auth_count - len(auth_data)} ghost entries from authorize_list.json")

        # 2. Audit judo_data.json
        judo_data = dbm.load_json(dbm.DB_FILE)
        initial_judo_count = len(judo_data)
        for gid in list(judo_data.keys()):
            if gid not in active_guild_ids:
                del judo_data[gid]
        
        if len(judo_data) != initial_judo_count:
            dbm.save_json(dbm.DB_FILE, judo_data)
            print(f"🧹 Scrubbed {initial_judo_count - len(judo_data)} ghost entries from judo_data.json")

        if len(auth_data) == initial_auth_count and len(judo_data) == initial_judo_count:
            print("✅ Database Integrity Verified: No ghost data found.")

    async def on_ready(self):
        print(f'--- {self.user.name} CORE ONLINE ---')
        # Run the scrub once the bot has fully connected to all guilds
        await self.scrub_ghost_data()

bot = SupremeBot()

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Online. {round(bot.latency * 1000)}ms")

# Start the bot using the secure token
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ ERROR: DISCORD_TOKEN not found in .env file.")