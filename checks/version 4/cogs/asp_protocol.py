import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from collections import deque, defaultdict
import database_manager as dbm
import itertools

class ASPProtocol(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_messages = defaultdict(lambda: deque())
        self.status_cycle = itertools.cycle([
            "over the server", 
            "ASP Active", 
            "Modular Mode",
            "for spammers"
        ])
        self.change_status.start()

    def cog_unload(self):
        self.change_status.cancel()

    @tasks.loop(seconds=10)
    async def change_status(self):
        await self.bot.wait_until_ready()
        try:
            await self.bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching, 
                    name=next(self.status_cycle)
                )
            )
        except Exception as e:
            print(f"Error updating status: {e}")

    @commands.Cog.listener()
    async def on_message(self, message):
        # FIX: Convert the list to a tuple so startswith works
        prefixes = tuple(self.bot.command_prefix)
        
        # Ignore bots and commands
        if message.author.bot or message.content.startswith(prefixes):
            return

        user_id = message.author.id
        now = datetime.utcnow()
        self.user_messages[user_id].append(now)

        while self.user_messages[user_id] and (now - self.user_messages[user_id][0]).total_seconds() > 12:
            self.user_messages[user_id].popleft()

        history = list(self.user_messages[user_id])
        msg_count_12s = len(history)
        msg_count_6s = len([t for t in history if (now - t).total_seconds() <= 6])

        if msg_count_12s > 6 or msg_count_6s > 3:
            await self.apply_punishment(message.author, message.guild)
            self.user_messages[user_id].clear()

    async def apply_punishment(self, member, guild):
        strike_level = dbm.increment_strike(guild.id, member.id)
        
        if strike_level == 1: minutes = 2
        elif strike_level == 2: minutes = 10
        elif strike_level == 3: minutes = 60
        else: minutes = 2
        
        until = timedelta(minutes=minutes)
        
        try:
            await member.timeout(until, reason=f"ASP Strike {strike_level}: Spamming")
            log_ch = discord.utils.get(guild.text_channels, name="judo-logs")
            if log_ch:
                embed = discord.Embed(
                    title="🚫 ASP Enforcement", 
                    color=discord.Color.red(),
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="User", value=member.mention, inline=True)
                embed.add_field(name="Strike", value=f"Level {strike_level}", inline=True)
                embed.add_field(name="Duration", value=f"{minutes} Minutes", inline=True)
                embed.set_footer(text="Anti-Spam Protocol Active")
                await log_ch.send(embed=embed)
        except Exception as e:
            print(f"❌ ASP Error: {e}")

async def setup(bot):
    await bot.add_cog(ASPProtocol(bot))