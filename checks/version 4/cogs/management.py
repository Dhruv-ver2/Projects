import discord
from discord.ext import commands
import database_manager as dbm
from datetime import datetime, timedelta
import asyncio

# My HARDCODED ID
SUPREME_CREATOR_ID = 757990668357599302 

class Management(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_authorized(self, user_id, guild_id, required_level):
        """Checks authorization levels using string-based IDs."""
        uid, gid = str(user_id), str(guild_id)
        if user_id == SUPREME_CREATOR_ID:
            return True
        user_level = dbm.get_auth_level(gid, uid)
        if user_level == 0:
            return False
        return user_level <= required_level

    def get_author_title(self, user_id, guild_id):
        """Returns the specific title for logs and announcements."""
        if user_id == SUPREME_CREATOR_ID:
            return "Master"
        level = dbm.get_auth_level(guild_id, user_id)
        if level == 1:
            return "Senior Mod (Level 1)"
        if level == 2:
            return "Junior Mod (Level 2)"
        return "Unauthorized User"

    async def log_action(self, ctx, action_detail):
        """Logs all management actions to the #judo-logs channel."""
        log_ch = discord.utils.get(ctx.guild.text_channels, name="judo-logs")
        if log_ch:
            embed = discord.Embed(
                title="📜 Management Log", 
                color=discord.Color.blue(), 
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Executor", value=ctx.author.mention, inline=True)
            embed.add_field(name="Action", value=action_detail, inline=True)
            await log_ch.send(embed=embed)

    async def check_perm(self, ctx, level):
        """Helper to verify permissions and tag unauthorized users."""
        if not self.is_authorized(ctx.author.id, ctx.guild.id, level):
            await ctx.send(f"🚫 {ctx.author.mention}, you attempted to use Judo but don't have Level {level} permission.")
            await self.log_action(ctx, f"UNAUTHORIZED Attempt: Level {level} required.")
            return False
        return True

    # --- MODERATION SUITE ---

    @commands.command(name="mute")
    async def mute_user(self, ctx, member: discord.Member, *, content: str = ""):
        """Syntax: judo mute @user for <number> minutes [reason]"""
        if not await self.check_perm(ctx, 2): return

        # Hierarchy Shield
        author_lvl = dbm.get_auth_level(ctx.guild.id, ctx.author.id) if ctx.author.id != SUPREME_CREATOR_ID else -1
        target_lvl = dbm.get_auth_level(ctx.guild.id, member.id) if member.id != SUPREME_CREATOR_ID else -1

        if member.id == SUPREME_CREATOR_ID:
            return await ctx.send(f"🚫 {ctx.author.mention} level {author_lvl} U don't have permission to mute Master Dhruv / Better luck next time.")
        
        if author_lvl >= target_lvl and ctx.author.id != SUPREME_CREATOR_ID and target_lvl != 0:
            return await ctx.send(f"🚫 {ctx.author.mention} level {author_lvl} U don't have permission to mute {member.mention}.")

        minutes = None
        reason = None
        parts = content.split()
        
        if "for" in parts:
            idx = parts.index("for")
            if len(parts) > idx + 1 and parts[idx+1].isdigit():
                minutes = int(parts[idx+1])
                # Skip "minutes" or "minute" suffix if present
                reason_start = idx + 3 if len(parts) > idx + 2 and parts[idx+2].lower().startswith("minute") else idx + 2
                reason_text = " ".join(parts[reason_start:])
                if reason_text.strip():
                    reason = reason_text

        if minutes is None:
            return await ctx.send(f"❌ {ctx.author.mention}, use: `judo mute @user for <number> minutes [reason]`")

        if not reason:
            await ctx.send(f"❓ Ok {ctx.author.mention}, rn {member.mention} has to be muted right now, what reason should i mention?")
            def check(m): return m.author == ctx.author and m.channel == ctx.channel
            try:
                msg = await self.bot.wait_for('message', check=check, timeout=15.0)
                reason = msg.content
            except asyncio.TimeoutError:
                return await ctx.send(f"⏳ Response timed out. Mute cancelled.")

        try:
            await member.timeout(timedelta(minutes=minutes), reason=reason)
            await ctx.send(f"🔇 {member.mention} has been muted for {minutes} minutes | Reason: {reason}")
            await self.log_action(ctx, f"MUTED {member.name} for {minutes}m. Reason: {reason}")
        except Exception as e:
            await ctx.send(f"⚠️ Error: {e}")

    @commands.command(name="unmute")
    async def unmute_user(self, ctx, member: discord.Member):
        if not await self.check_perm(ctx, 2): return
        try:
            await member.timeout(None)
            await ctx.send(f"🔊 {member.mention} has been unmuted.")
            await self.log_action(ctx, f"UNMUTED {member.name}")
        except Exception as e:
            await ctx.send(f"⚠️ Error: {e}")

    @commands.command(name="kick")
    async def kick_user(self, ctx, member: discord.Member):
        if not await self.check_perm(ctx, 1): return
        if member.id == SUPREME_CREATOR_ID:
            return await ctx.send(f"🚫 Better luck next time, Master Dhruv is unkickable.")
        try:
            await member.kick(reason=f"Kicked by {ctx.author}")
            await ctx.send(f"👢 {member.name} has been kicked.")
            await self.log_action(ctx, f"KICKED {member.name}")
        except Exception as e:
            await ctx.send(f"⚠️ Error: {e}")

    @commands.command(name="ban")
    async def ban_user(self, ctx, member: discord.Member, *, content: str = ""):
        """Syntax: judo ban @user for <reason>"""
        if not await self.check_perm(ctx, 1): return # Level 1+ Authority

        # Hierarchy Shield
        author_lvl = dbm.get_auth_level(ctx.guild.id, ctx.author.id) if ctx.author.id != SUPREME_CREATOR_ID else -1
        if member.id == SUPREME_CREATOR_ID:
            return await ctx.send(f"🚫 {ctx.author.mention} level {author_lvl} U don't have permission to ban Master Dhruv / Better luck next time.")

        reason = content.split("for", 1)[1].strip() if "for" in content else None
        if not reason:
            return await ctx.send(f"❌ {ctx.author.mention}, use: `judo ban @user for <reason>`")

        try:
            await member.ban(reason=reason)
            await ctx.send(f"🔨 {member.name} has been banned | Reason: {reason}")
            await self.log_action(ctx, f"BANNED {member.name}. Reason: {reason}")
        except Exception as e:
            await ctx.send(f"⚠️ Error: {e}")

    # --- MANAGEMENT & ARCHIVING ---

    @commands.command(name="authorize")
    async def authorize_user(self, ctx, member: discord.Member, level: int):
        if not await self.check_perm(ctx, 1): return
        dbm.set_auth_level(ctx.guild.id, member.id, level)
        await ctx.send(f"✅ {member.display_name} has now **Level {level}** Authorization.")

    @commands.command(name="unauthorize")
    async def unauthorize_user(self, ctx, member: discord.Member):
        if not await self.check_perm(ctx, 1): return
        dbm.set_auth_level(ctx.guild.id, member.id, 0)
        await ctx.send(f"🛑 Authorization revoked for {member.display_name}.")

    @commands.command(name="send")
    async def send_custom(self, ctx, *, content: str):
        if not await self.check_perm(ctx, 2): return
        if " at " in content:
            parts = content.rsplit(" at ", 1)
            msg, ch_tag = parts[0], parts[1]
            ch_id = "".join(filter(str.isdigit, ch_tag))
            target = self.bot.get_channel(int(ch_id))
            if target and msg:
                await target.send(msg)
                await ctx.send("✅ Sent.", delete_after=2)
                await ctx.message.delete()

    @commands.command(name="delete")
    async def delete_messages(self, ctx, amount: int, *args):
        if not await self.check_perm(ctx, 2): return
        target_channel = ctx.channel
        if args:
            for arg in args:
                if arg.startswith("<#"):
                    ch_id = "".join(filter(str.isdigit, arg))
                    target_channel = self.bot.get_channel(int(ch_id))
                    break

        purge_limit = amount + 1 if target_channel == ctx.channel else amount
        archive_ch = discord.utils.get(ctx.guild.text_channels, name="purged-messages")
        if archive_ch:
            collected = []
            async for msg in target_channel.history(limit=purge_limit):
                if msg.id == ctx.message.id: continue
                time = msg.created_at.strftime("%H:%M:%S")
                collected.append(f"[{time}] **{msg.author}**: {msg.content}")
            if collected:
                collected.reverse()
                report = "\n".join(collected)
                for i in range(0, len(report), 1900):
                    embed = discord.Embed(title=f"🗑️ Purge Archive: #{target_channel.name}", description=report[i:i+1900], color=discord.Color.dark_gray())
                    await archive_ch.send(embed=embed)

        deleted = await target_channel.purge(limit=purge_limit)
        count = len(deleted) - 1 if target_channel == ctx.channel else len(deleted)
        title = self.get_author_title(ctx.author.id, ctx.guild.id)
        await ctx.send(f"🧹 **{count}** messages purged by **{title}**.", delete_after=5)

    @commands.command(name="delete_all")
    async def delete_all_messages(self, ctx):
        if ctx.author.id != SUPREME_CREATOR_ID:
            return await ctx.send(f"🚫 {ctx.author.mention}, only the Master can use this.")
        name, cat, pos, ow = ctx.channel.name, ctx.channel.category, ctx.channel.position, ctx.channel.overwrites
        await ctx.channel.delete()
        new_ch = await ctx.guild.create_text_channel(name=name, category=cat, overwrites=ow, position=pos)
        await new_ch.send("✨ Channel wiped and recreated by Master.", delete_after=10)

async def setup(bot):
    await bot.add_cog(Management(bot))