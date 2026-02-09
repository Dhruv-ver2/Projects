import discord
from discord.ext import commands
import database_manager as dbm
from datetime import datetime, timezone
import asyncio
import re  # Added for bracket parsing

SUPREME_CREATOR_ID = 757990668357599302 

class ManagementBase(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_authorized(self, user_id, guild_id, required_level):
        uid, gid = str(user_id), str(guild_id)
        if user_id == SUPREME_CREATOR_ID: return True
        user_level = dbm.get_auth_level(gid, uid)
        return user_level != 0 and user_level <= required_level

    async def log_action(self, ctx, action_detail):
        """Universal Logger for all Management actions."""
        log_ch = discord.utils.get(ctx.guild.text_channels, name="judo-logs")
        if log_ch:
            embed = discord.Embed(
                title="📜 Management Log", 
                color=discord.Color.blue(), 
                timestamp=datetime.now(timezone.utc)
            )
            embed.add_field(name="Executor", value=ctx.author.mention, inline=True)
            embed.add_field(name="Action", value=action_detail, inline=True)
            await log_ch.send(embed=embed)

    async def check_perm(self, ctx, level):
        user_lvl = self.is_authorized(ctx.author.id, ctx.guild.id, level)
        actual_level = dbm.get_auth_level(ctx.guild.id, ctx.author.id)
        
        if self.bot.panic_mode and actual_level == 2:
            await ctx.send("🚫 **CRITICAL:** Junior Moderator powers are suspended during Emergency Lockdown.")
            return False

        if not self.is_authorized(ctx.author.id, ctx.guild.id, level):
            self.bot.judo_stats["failed"] += 1
            await ctx.send(f"🚫 {ctx.author.mention}, you don't have Level {level} permission.")
            await self.log_action(ctx, f"UNAUTHORIZED Attempt: Level {level} required.")
            return False
        return True

    @commands.Cog.listener()
    async def on_command(self, ctx):
        if ctx.command.name == "status": return 
        self.bot.judo_stats["attempts"] += 1
        self.bot.judo_stats["active_users"].add(ctx.author.display_name)

    @commands.command(name="auth_list")
    async def show_auth_list(self, ctx):
        if not await self.check_perm(ctx, 1): return
        self.bot.judo_stats["success"] += 1
        auth_db = dbm.load_json(dbm.AUTH_FILE)
        gid = str(ctx.guild.id)

        if gid not in auth_db or (not auth_db[gid].get("auth1") and not auth_db[gid].get("auth2")):
            return await ctx.send("📋 No authorized members found in the database (excluding Master).")

        embed = discord.Embed(title="🛡️ Judo Authorization Directory", color=discord.Color.blue(), timestamp=datetime.now(timezone.utc))
        level1_ids = auth_db[gid].get("auth1", [])
        l1_text = "".join([f"• <@{uid}> | ID: `{uid}`\n" for uid in level1_ids])
        if l1_text: embed.add_field(name="🎖️ Senior Moderators (Level 1)", value=l1_text, inline=False)

        level2_ids = auth_db[gid].get("auth2", [])
        l2_text = "".join([f"• <@{uid}> | ID: `{uid}`\n" for uid in level2_ids])
        if l2_text: embed.add_field(name="🎗️ Junior Moderators (Level 2)", value=l2_text, inline=False)

        embed.description = f"**Supreme Creator:** <@{SUPREME_CREATOR_ID}>"
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        await ctx.send(embed=embed)

    @commands.command(name="clear_auth")
    async def clear_authorization_list(self, ctx):
        if ctx.author.id != SUPREME_CREATOR_ID:
            self.bot.judo_stats["failed"] += 1
            return await ctx.send(f"🚫 {ctx.author.mention}, only the Master can initiate a full authorization wipe.")
        await ctx.send(f"⚠️ {ctx.author.mention}, are you sure? (Type `confirm` to proceed)")
        def check(m): return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "confirm"
        try:
            await self.bot.wait_for('message', check=check, timeout=15.0)
        except asyncio.TimeoutError:
            return await ctx.send("⏳ Wipe cancelled. Confirmation timed out.")
        auth_db = dbm.load_json(dbm.AUTH_FILE)
        gid = str(ctx.guild.id)
        if gid in auth_db:
            auth_db[gid] = {"auth1": [], "auth2": []}
            dbm.save_json(dbm.AUTH_FILE, auth_db)
            self.bot.judo_stats["success"] += 1
            await ctx.send(f"🧹 **Authorization List Cleared.**")
            await self.log_action(ctx, "CRITICAL: Full Authorization Wipe Performed by Master.")
        else:
            await ctx.send("📋 No authorization data found to clear for this server.")

    @commands.command(name="status")
    async def status(self, ctx):
        self.bot.judo_stats["attempts"] += 1
        self.bot.judo_stats["active_users"].add(ctx.author.display_name)
        if not await self.check_perm(ctx, 2): return
        self.bot.judo_stats["success"] += 1
        uptime = datetime.now(timezone.utc) - self.bot.start_time
        h, r = divmod(int(uptime.total_seconds()), 3600)
        m, s = divmod(r, 60)
        embed = discord.Embed(title="🛡️ Judo Core Status", color=discord.Color.gold(), timestamp=datetime.now(timezone.utc))
        embed.add_field(name="📶 Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="⏳ Uptime", value=f"{h}h {m}m {s}s", inline=True)
        embed.add_field(name="📊 Total Attempts", value=str(self.bot.judo_stats["attempts"]), inline=False)
        embed.add_field(name="✅ Successful", value=str(self.bot.judo_stats["success"]), inline=True)
        embed.add_field(name="❌ Denied", value=str(self.bot.judo_stats["failed"]), inline=True)
        embed.add_field(name="👤 Users Active", value=", ".join(self.bot.judo_stats["active_users"]), inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="authorize")
    async def authorize(self, ctx, member: discord.Member, level: int):
        if not await self.check_perm(ctx, 1): return
        # Senior Mods cannot grant Level 1
        if dbm.get_auth_level(ctx.guild.id, ctx.author.id) == 1 and level == 1 and ctx.author.id != SUPREME_CREATOR_ID:
            return await ctx.send(f"🚫 {ctx.author.mention}, you don't have the privilege to give Level 1 (Senior Moderator) Authorization.")
        
        dbm.set_auth_level(ctx.guild.id, member.id, level)
        self.bot.judo_stats["success"] += 1
        await ctx.send(f"✅ {member.display_name} is now Level {level}.")
        await self.log_action(ctx, f"Authorized {member.name} to Level {level}.")

    @commands.command(name="mass")
    async def mass_authorize(self, ctx, *, content: str):
        """Syntax: judo mass authorize [@user1 @user2] level <number>"""
        if "authorize" not in content.lower(): return
        if not await self.check_perm(ctx, 1): return

        # Extraction Logic
        member_match = re.search(r"\[(.*?)\]", content)
        level_match = re.search(r"level\s+([12])", content.lower())

        if not member_match or not level_match:
            return await ctx.send("❓ **Syntax Error.** Use: `judo mass authorize [@user1 @user2] level <1 or 2>`")

        target_level = int(level_match.group(1))
        
        # Hierarchy Validation
        if dbm.get_auth_level(ctx.guild.id, ctx.author.id) == 1 and target_level == 1 and ctx.author.id != SUPREME_CREATOR_ID:
             return await ctx.send(f"🚫 {ctx.author.mention}, you don't have the privilege to give Level 1 (Senior Moderator) Authorization.")

        # ID Extraction
        user_ids = re.findall(r"<@!?(\d+)>", member_match.group(1))
        if not user_ids: return await ctx.send("❓ No valid user tags found inside `[]`.")

        success_tags = []
        for uid in user_ids:
            dbm.set_auth_level(ctx.guild.id, int(uid), target_level)
            success_tags.append(f"<@{uid}>")
            self.bot.judo_stats["success"] += 1

        if success_tags:
            embed = discord.Embed(
                title="🛡️ Mass Authorization Protocol",
                description=f"**Level {target_level}** granted to:\n" + ", ".join(success_tags),
                color=discord.Color.green(),
                timestamp=datetime.now(timezone.utc)
            )
            await ctx.send(embed=embed)
            await self.log_action(ctx, f"MASS AUTH: {len(success_tags)} users set to Level {target_level}.")

async def setup(bot):
    await bot.add_cog(ManagementBase(bot))