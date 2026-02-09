import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta, timezone
from collections import deque, defaultdict
import database_manager as dbm
import itertools

SUPREME_CREATOR_ID = 757990668357599302 

class ASPProtocol(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_messages = defaultdict(lambda: deque())
        self.status_cycle = itertools.cycle([
            "Over The Servers", 
            "ASP-Anti Spam Protocol", 
            "Modular Mode",
            "Spammers Forbidden",
            "Customizations",
            "Yet Personal",
            "DynamicCount" # Trigger for the server count
        ])
        self.change_status.start()

    def cog_unload(self):
        self.change_status.cancel()

    @tasks.loop(seconds=10)
    async def change_status(self):
        """Rotates statuses and injects the live server count."""
        await self.bot.wait_until_ready()
        try:
            current_item = next(self.status_cycle)
            
            # Formatting the specific 'Watching Over X servers' line
            if current_item == "DynamicCount":
                count = len(self.bot.guilds)
                current_item = f"Over {count} servers"

            await self.bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching, 
                    name=current_item
                )
            )
        except Exception as e:
            print(f"Error updating status: {e}")

    # --- TIERED STRIKE INVESTIGATION SYSTEM (Using 'display') ---

    @commands.group(name="display", invoke_without_command=True)
    async def display_group(self, ctx):
        """Base group for ASP status commands."""
        await ctx.send("❓ Use `judo display strike of @user` or `judo display my strikes`.")

    @display_group.group(name="strike", invoke_without_command=True)
    async def strike_group(self, ctx):
        """Help menu for strike queries."""
        await ctx.send("❓ Use `judo display strike of @user`.")

    @strike_group.command(name="of")
    async def strike_of(self, ctx, member: discord.Member):
        """View strikes of others. Level 2+ Required."""
        base = self.bot.get_cog("ManagementBase")
        if not await base.check_perm(ctx, 2): return

        if member.id == SUPREME_CREATOR_ID:
            return await ctx.send("🛡️ **Master Dhruv is Immune to Timeout strikes under any ASP (Anti-Spam-Protocol).**")

        level = dbm.get_strike_level(ctx.guild.id, member.id)
        await self.send_strike_report(ctx, member, level)

    @display_group.command(name="my")
    async def display_my_strikes(self, ctx, *, item: str = ""):
        """Handles 'judo display my strikes'."""
        if "strikes" in item.lower():
            level = dbm.get_strike_level(ctx.guild.id, ctx.author.id)
            await self.send_strike_report(ctx, ctx.author, level)
        else:
            await ctx.send("❓ Did you mean `judo display my strikes`?")

    async def send_strike_report(self, ctx, member, level):
        """Internal embed builder for strike reports."""
        status_map = {
            0: ("Clean Record ✨", 0x2ecc71),
            1: ("Level 1: Warning Issued ⚠️", 0xf1c40f),
            2: ("Level 2: Final Warning ⛔", 0xe67e22),
            3: ("Level 3: Critical Violation 🚫", 0xe74c3c)
        }
        
        status, hex_color = status_map.get(level, ("Unknown", 0x95a5a6))

        embed = discord.Embed(
            title=f"🛡️ ASP Strike Report: {member.display_name}", 
            color=hex_color
        )
        embed.add_field(name="Current Status", value=f"**{status}**", inline=False)
        
        tips = {
            0: "Status: Secure.",
            1: "Next violation: 10-minute timeout.",
            2: "Next violation: 60-minute timeout.",
            3: "Maximum penalties reached."
        }
        embed.set_footer(text=tips.get(level, "System check complete."))
        await ctx.send(embed=embed)

    # --- PASSIVE DETECTION LOGIC ---

    @commands.Cog.listener()
    async def on_message(self, message):
        prefixes = tuple(self.bot.command_prefix)
        if message.author.bot or message.content.startswith(prefixes):
            return

        user_id = message.author.id
        now = datetime.now(timezone.utc)
        self.user_messages[user_id].append(now)

        while self.user_messages[user_id] and (now - self.user_messages[user_id][0]).total_seconds() > 12:
            self.user_messages[user_id].popleft()

        history = list(self.user_messages[user_id])
        if len(history) > 6 or len([t for t in history if (now - t).total_seconds() <= 6]) > 3:
            if message.author.id == SUPREME_CREATOR_ID:
                return 

            await self.apply_punishment(message.author, message.guild)
            self.user_messages[user_id].clear()

    async def apply_punishment(self, member, guild):
        strike_level = dbm.increment_strike(guild.id, member.id)
        
        minutes = {1: 2, 2: 10, 3: 60}.get(strike_level, 2)
        until = timedelta(minutes=minutes)
        
        try:
            await member.timeout(until, reason=f"ASP Strike {strike_level}: Spamming")
            log_ch = discord.utils.get(guild.text_channels, name="judo-logs")
            if log_ch:
                embed = discord.Embed(title="🚫 ASP Enforcement", color=discord.Color.red(), timestamp=datetime.now(timezone.utc))
                embed.add_field(name="User", value=member.mention, inline=True)
                embed.add_field(name="Strike", value=f"Level {strike_level}", inline=True)
                embed.add_field(name="Duration", value=f"{minutes} Minutes", inline=True)
                await log_ch.send(embed=embed)
        except Exception as e:
            print(f"❌ ASP Error: {e}")

async def setup(bot):
    await bot.add_cog(ASPProtocol(bot))