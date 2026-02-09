import discord
from discord.ext import commands
from datetime import datetime, timezone

class GhostLog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_log_channel(self, guild):
        return discord.utils.get(guild.text_channels, name="ghost-logs")

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """Standard log for any modified message."""
        if before.author.bot or before.content == after.content:
            return

        log_ch = await self.get_log_channel(before.guild)
        if not log_ch: return

        embed = discord.Embed(
            title="📝 Message Edited",
            description=f"**Author:** {before.author.mention}\n**Channel:** {before.channel.mention}",
            color=0xf1c40f, # Gold
            timestamp=datetime.now(timezone.utc)
        )
        embed.add_field(name="Before", value=before.content[:1024] if before.content else "None", inline=False)
        embed.add_field(name="After", value=after.content[:1024] if after.content else "None", inline=False)
        await log_ch.send(embed=embed)

    async def log_purge_event(self, ctx, deleted_messages):
        """Specialized function called by Judo's delete command."""
        log_ch = await self.get_log_channel(ctx.guild)
        if not log_ch: return

        # Remove the bot's command message from the list to keep it clean
        messages = [m for m in deleted_messages if m.id != ctx.message.id]
        if not messages: return

        embed = discord.Embed(
            title="🧹 Judo Purge Event",
            description=f"**Total:** {len(messages)} messages\n**Channel:** {ctx.channel.mention}\n**Triggered By:** {ctx.author.mention}",
            color=0x3498db, # Blue
            timestamp=datetime.now(timezone.utc)
        )

        # Generate preview of what was removed
        report = ""
        for msg in reversed(messages[:20]): # Show top 20 for detail
            content = msg.content[:60] + "..." if len(msg.content) > 60 else msg.content
            report += f"**{msg.author.name}**: {content}\n"

        embed.add_field(name="Purge Content Preview", value=report if report else "No text data.", inline=False)
        await log_ch.send(embed=embed)

async def setup(bot):
    await bot.add_cog(GhostLog(bot))