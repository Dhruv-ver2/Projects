import discord
from discord.ext import commands
import time
import datetime
import os

class Telemetry(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()
        self.owner_id = int(os.getenv('OWNER_ID'))
        # Dictionary to track command usage per user (Resets on boot)
        self.user_command_usage = {} 

    @commands.Cog.listener()
    async def on_command(self, ctx):
        """Track every successful command call for telemetry."""
        user_id = ctx.author.id
        self.user_command_usage[user_id] = self.user_command_usage.get(user_id, 0) + 1

    # --- COMMAND: JUDO STATUS (Universal) ---
    @commands.command(name="status")
    async def system_status(self, ctx):
        """Shows the bot's internal vitals."""
        # Calculate Uptime
        current_time = time.time()
        difference = int(round(current_time - self.start_time))
        uptime_str = str(datetime.timedelta(seconds=difference))

        # Get Latency
        latency = round(self.bot.latency * 1000)

        # Build the Telemetry Embed
        embed = discord.Embed(
            title="🥋 Judo System Health Report",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="📡 Latency", value=f"{latency}ms", inline=True)
        embed.add_field(name="⏳ Uptime", value=uptime_str, inline=True)
        embed.add_field(name="👥 Population", value=f"{ctx.guild.member_count} Members", inline=True)
        embed.add_field(name="📉 Traffic", value=f"{self.bot.total_commands_processed} Commands Processed", inline=True)
        
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)

    # --- COMMAND: JUDO USER STATUS <@user> ---
    @commands.command(name="user")
    async def user_status(self, ctx, sub_cmd: str, member: discord.Member = None):
        """judo user status <@user>"""
        if sub_cmd.lower() != "status":
            return

        target = member or ctx.author
        
        # Determine Authority Level
        authorized_ids = []
        if os.path.exists('data/authorized.txt'):
            with open('data/authorized.txt', 'r') as f:
                authorized_ids = [line.strip() for line in f.readlines()]

        if target.id == self.owner_id:
            rank = "👑 Master"
        elif str(target.id) in authorized_ids:
            rank = "🥷 Authorized Ninja"
        else:
            rank = "🎓 Student / Member"

        # Get Command Count from memory
        usage = self.user_command_usage.get(target.id, 0)

        # Build User Intelligence Embed
        embed = discord.Embed(
            title=f"👤 Intel: {target.display_name}",
            color=discord.Color.dark_purple()
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="Tag", value=str(target), inline=True)
        embed.add_field(name="ID", value=target.id, inline=True)
        embed.add_field(name="Authority", value=rank, inline=False)
        embed.add_field(name="Uptime Interactions", value=f"{usage} commands given", inline=False)
        
        embed.set_footer(text="Telemetry data resets on bot restart.")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Telemetry(bot))