import discord
import os
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

# --- INITIALIZATION ---
load_dotenv()
TOKEN = os.getenv('TOKEN')
OWNER_ID = int(os.getenv('OWNER_ID'))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class JudoBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=lambda bot, msg: ["judo ", "Judo "], 
            intents=intents,
            help_command=None,
            owner_id=OWNER_ID
        )
        self.total_commands_processed = 0 

    async def setup_hook(self):
        print("--- Initiating Judo Cogs ---")
        for filename in os.listdir('./cogs'):
            if filename.endswith('_cog.py'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    print(f'✅ Loaded: {filename}')
                except Exception as e:
                    print(f'❌ Failed to load {filename}: {e}')
        print("--- Cogs Integration Complete ---")

    async def on_ready(self):
        print(f"🥋 {self.user.name} is online and guarding the Dojo.")
        await self.change_presence(activity=discord.Game(name="Guarding the Dojo | judo help"))

    async def on_message(self, message):
        if message.author.bot:
            return

        # 1. INTEGRATED SHIELD CHECK
        shield = self.get_cog('Shield')
        if shield:
            is_violating = await shield.integrated_shield_check(message)
            if is_violating: 
                return 

        # 2. SUPREME GUARD
        triggered = message.content.lower().startswith('judo ') or self.user.mentioned_in(message)
        
        if triggered:
            authorized_ids = []
            if os.path.exists('data/authorized.txt'):
                with open('data/authorized.txt', 'r') as f:
                    authorized_ids = [line.strip() for line in f.readlines()]

            is_owner = message.author.id == OWNER_ID
            is_authorized = str(message.author.id) in authorized_ids

            if not (is_owner or is_authorized):
                return 

            self.total_commands_processed += 1

            # --- THE LOGGING BRIDGE ---
            # Logs every successful command use to #judo-logs
            sec = self.get_cog('Security')
            if sec:
                await sec.judo_log("BLUE", message.author, "Command Executed", message.content)
        
        await self.process_commands(message)

bot = JudoBot()

async def main():
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Judo is going to sleep. Farewell, Master Dhruv.")