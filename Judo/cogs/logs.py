import discord
from discord.ext import commands
from datetime import datetime
import os

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = int(os.getenv('LOG_CHANNEL_ID'))

    async def send_log_embed(self, title, color, fields):
        """Standardized helper for professional system embeds."""
        channel = self.bot.get_channel(self.log_channel_id)
        if channel:
            embed = discord.Embed(title=title, color=color, timestamp=datetime.now())
            for name, value in fields.items():
                embed.add_field(name=name, value=value, inline=False)
            embed.set_footer(text="Judo Internal Logs")
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return

        content = message.content.lower()
        # Full list of keywords Judo recognizes
        valid_commands = ["delete", "send", "add", "remove", "wipe", "clear", "kick", "show", "invite", "generate"]
        
        # Check if it's a command or a direct mention
        is_command = content.startswith("judo") and any(cmd in content for cmd in valid_commands)

        if is_command or self.bot.user.mentioned_in(message):
            sec_cog = self.bot.get_cog('Security')
            is_owner = message.author.id == self.bot.owner_id
            is_allowed = sec_cog.is_allowed(message.author.id) if sec_cog else False

            # OWNER-ONLY: Wipe the log channel
            if is_owner and "wipe" in content and "judo-logs" in content:
                log_chan = self.bot.get_channel(self.log_channel_id)
                if log_chan: 
                    await log_chan.purge(limit=None)
                    await log_chan.send("🚨 **THE DOJO LOGS HAVE BEEN WIPED BY SUPREME OWNER.**")
                return

            if is_allowed:
                # We skip logging for commands that have their own custom embeds in moderation.py
                # This prevents duplicate messages in your log channel
                complex_cmds = ["delete", "kick", "generate", "invite"]
                if all(cmd not in content for cmd in complex_cmds):
                    await self.send_log_embed("✅ Authorized Action", discord.Color.green(), {
                        "User": message.author.mention,
                        "Command": f"`{message.content}`",
                        "Location": message.channel.mention
                    })
            else:
                # Log unauthorized attempts as security alerts
                await self.send_log_embed("🚨 Security Alert", discord.Color.red(), {
                    "User": message.author.mention,
                    "Attempted": f"`{message.content}`",
                    "Location": message.channel.mention
                })

        await self.bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(Logs(bot))