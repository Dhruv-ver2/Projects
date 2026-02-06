import discord
from discord.ext import commands
import database_manager as dbm
from datetime import datetime, timedelta
import asyncio

SUPREME_CREATOR_ID = 757990668357599302 

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def check_hierarchy(self, ctx, member):
        """Armored Hierarchy Shield from your Golden Standard."""
        author_lvl = dbm.get_auth_level(ctx.guild.id, ctx.author.id) if ctx.author.id != SUPREME_CREATOR_ID else -1
        target_lvl = dbm.get_auth_level(ctx.guild.id, member.id) if member.id != SUPREME_CREATOR_ID else -1
        
        if member.id == SUPREME_CREATOR_ID:
            await ctx.send(f"🚫 {ctx.author.mention} level {author_lvl} U don't have permission to target Master Dhruv / Better luck next time.")
            return False
        if author_lvl >= target_lvl and ctx.author.id != SUPREME_CREATOR_ID and target_lvl != 0:
            await ctx.send(f"🚫 {ctx.author.mention} level {author_lvl} U don't have permission to target {member.mention}.")
            return False
        return True

    @commands.command(name="mute")
    async def mute(self, ctx, member: discord.Member, *, content: str = ""):
        base = self.bot.get_cog("ManagementBase")
        if not await base.check_perm(ctx, 2): return
        
        # Self/Judo/Master Checks
        if member.id == ctx.author.id:
            return await ctx.send(f"🚫 {ctx.author.mention} U can't mute yourself, Kindly ask Master or Senior mod for this.")
        if member.id == self.bot.user.id:
            await ctx.send(f"🚫 {ctx.author.mention} U can't mute me, but i can mute you, Don't try this again.")
            def check_repeat(m):
                return m.author == ctx.author and m.channel == ctx.channel and self.bot.user.mention in m.content and "mute" in m.content.lower()
            try:
                await self.bot.wait_for('message', check=check_repeat, timeout=10.0)
                await ctx.author.timeout(timedelta(minutes=2), reason="Attempted to mute Judo twice.")
                return await ctx.send(f"🛡️ {ctx.author.mention} silenced for 2 minutes for attempting to mute the System.")
            except asyncio.TimeoutError: return

        if not await self.check_hierarchy(ctx, member): return

        # Parsing "for X minutes" logic
        minutes = None
        reason = None
        parts = content.split()
        if "for" in parts:
            idx = parts.index("for")
            if len(parts) > idx + 1 and parts[idx+1].isdigit():
                minutes = int(parts[idx+1])
                start = idx + 3 if len(parts) > idx + 2 and parts[idx+2].lower().startswith("minute") else idx + 2
                reason = " ".join(parts[start:]).strip() or None

        if minutes is None:
            return await ctx.send(f"❌ {ctx.author.mention}, use: `judo mute @user for <number> minutes [reason]`")

        if not reason:
            await ctx.send(f"❓ Ok {ctx.author.mention}, rn {member.mention} has to be muted right now, what reason should i mention?")
            try:
                msg = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=15.0)
                reason = msg.content
            except asyncio.TimeoutError:
                return await ctx.send("⏳ Response timed out. Mute cancelled.")

        try:
            await member.timeout(timedelta(minutes=minutes), reason=reason)
            self.bot.judo_stats["success"] += 1
            await ctx.send(f"🔇 {member.mention} muted for {minutes}m | Reason: {reason}")
        except Exception as e: await ctx.send(f"⚠️ Error: {e}")

    @commands.command(name="unmute")
    async def unmute(self, ctx, member: discord.Member):
        base = self.bot.get_cog("ManagementBase")
        if not await base.check_perm(ctx, 2): return
        try:
            await member.timeout(None)
            self.bot.judo_stats["success"] += 1
            await ctx.send(f"🔊 {member.mention} has been unmuted.")
        except Exception as e: await ctx.send(f"⚠️ Error: {e}")

    @commands.command(name="kick")
    async def kick(self, ctx, member: discord.Member):
        base = self.bot.get_cog("ManagementBase")
        if not await base.check_perm(ctx, 1): return
        if not await self.check_hierarchy(ctx, member): return
        try:
            await member.kick()
            self.bot.judo_stats["success"] += 1
            await ctx.send(f"👢 {member.name} has been kicked.")
        except Exception as e: await ctx.send(f"⚠️ Error: {e}")

    @commands.command(name="ban")
    async def ban(self, ctx, member: discord.Member, *, content: str = ""):
        base = self.bot.get_cog("ManagementBase")
        if not await base.check_perm(ctx, 1): return
        if not await self.check_hierarchy(ctx, member): return
        reason = content.split("for", 1)[1].strip() if "for" in content else "No reason"
        try:
            await member.ban(reason=reason)
            self.bot.judo_stats["success"] += 1
            await ctx.send(f"🔨 {member.name} banned | Reason: {reason}")
        except Exception as e: await ctx.send(f"⚠️ Error: {e}")

    @commands.command(name="unauthorize")
    async def unauthorize(self, ctx, member: discord.Member):
        base = self.bot.get_cog("ManagementBase")
        if not await base.check_perm(ctx, 1): return
        dbm.set_auth_level(ctx.guild.id, member.id, 0)
        self.bot.judo_stats["success"] += 1
        await ctx.send(f"🛑 Authorization revoked for {member.display_name}.")

async def setup(bot):
    await bot.add_cog(Moderation(bot))