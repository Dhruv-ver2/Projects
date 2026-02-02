import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from collections import deque, defaultdict
import database_manager as dbm  # Import our Brain file
import itertools

class ASPProtocol(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Memory storage for message frequency
        self.user_messages = defaultdict(lambda: deque())
        # Rotating status messages
        self.status_cycle = itertools.cycle([
            "over the server", 
            "ASP Active", 
            "Modular Mode",
            "for spammers"
        ])
        # Start the background task
        self.change_status.start()

    def cog_unload(self):
        """Clean up when the cog is unloaded."""
        self.change_status.cancel()

    @tasks.loop(seconds=10)
    async def change_status(self):
        """
        Background task to rotate the bot's status.
        Includes wait_until_ready to prevent 'NoneType' errors on startup.
        """
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
        # Ignore bots and commands (don't punish people for typing 'judo send...')
        if message.author.bot or message.content.startswith(self.bot.command_prefix):
            return

        user_id = message.author.id
        now = datetime.utcnow()
        self.user_messages[user_id].append(now)

        # Cleanup old history (older than 12 seconds)
        while self.user_messages[user_id] and (now - self.user_messages[user_id][0]).total_seconds() > 12:
            self.user_messages[user_id].popleft()

        # --- THE SPAM CHECK ---
        history = list(self.user_messages[user_id])
        msg_count_12s = len(history)
        msg_count_6s = len([t for t in history if (now - t).total_seconds() <= 6])

        # Rules: 6 messages in 12s OR 3 messages in 6s
        if msg_count_12s > 6 or msg_count_6s > 3:
            await self.apply_punishment(message.author, message.guild)
            self.user_messages[user_id].clear() # Reset memory after punishment

    async def apply_punishment(self, member, guild):
        """Handles the strike escalation and timeout logic."""
        # Get next strike level from the database engine (Server-Specific)
        strike_level = dbm.increment_strike(guild.id, member.id)
        
        # Determine duration based on strike level
        if strike_level == 1:
            minutes = 2
        elif strike_level == 2:
            minutes = 10
        elif strike_level == 3:
            minutes = 60
        else:
            minutes = 2 # Fallback
        
        until = timedelta(minutes=minutes)
        
        try:
            # Apply the timeout (requires 'Moderate Members' permission)
            await member.timeout(until, reason=f"ASP Strike {strike_level}: Spamming")
            
            # Find and log to the judo-logs channel
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
                
        except discord.Forbidden:
            print(f"❌ Missing Permission to timeout {member.name}.")
        except Exception as e:
            print(f"❌ ASP Error: {e}")

async def setup(bot):
    await bot.add_cog(ASPProtocol(bot))