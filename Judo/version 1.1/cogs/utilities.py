import discord
from discord.ext import commands
import database_manager as dbm
from datetime import datetime, timezone
import asyncio

SUPREME_CREATOR_ID = 757990668357599302 

class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cmd_usage = {} 
        self.voice_history = {} 

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Silences the 'Command Not Found' error for sub-command phrases."""
        if isinstance(error, commands.CommandNotFound):
            if "my commands info" in ctx.message.content.lower():
                return

    @commands.Cog.listener()
    async def on_command(self, ctx):
        uid = str(ctx.author.id)
        if uid not in self.cmd_usage: self.cmd_usage[uid] = set()
        self.cmd_usage[uid].add(ctx.channel.mention)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel and before.channel != after.channel:
            uid = str(member.id)
            if uid not in self.voice_history: self.voice_history[uid] = set()
            self.voice_history[uid].add(after.channel.name)

    @commands.command(name="user")
    async def user_details(self, ctx, member: discord.Member = None):
        """Generates a detailed Dossier for a member. Level 2+ required."""
        base = self.bot.get_cog("ManagementBase")
        if not await base.check_perm(ctx, 2): return
        self.bot.judo_stats["success"] += 1
        member = member or ctx.author
        uid_str = str(member.id)
        if member.id == SUPREME_CREATOR_ID:
            auth_status = "Supreme Master"
        elif member.id == self.bot.user.id:
            auth_status = "System Administrator"
        else:
            level = dbm.get_auth_level(ctx.guild.id, member.id)
            if level == 1:
                auth_status = "Senior Moderator (Level 1)"
            elif level == 2:
                auth_status = "Junior Moderator (Level 2)"
            else:
                auth_status = "Member"
        roles = [r.mention for r in member.roles if r.name != "@everyone"]
        embed = discord.Embed(title=f"👤 User Dossier: {member.display_name}", color=discord.Color.purple())
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="🆔 User ID", value=f"`{uid_str}`", inline=True)
        embed.add_field(name="🛡️ Auth Status", value=f"**{auth_status}**", inline=True)
        embed.add_field(name="🗓️ Created", value=member.created_at.strftime("%b %d, %Y"), inline=True)
        embed.add_field(name="📥 Joined", value=member.joined_at.strftime("%b %d, %Y"), inline=True)
        embed.add_field(name="💬 Activity (Session)", value=", ".join(self.cmd_usage.get(uid_str, ["None"])), inline=False)
        embed.add_field(name="🎙️ Voice (Session)", value=", ".join(self.voice_history.get(uid_str, ["None"])), inline=False)
        embed.add_field(name=f"🎭 Roles [{len(roles)}]", value=" ".join(roles) if roles else "None", inline=False)
        await ctx.send(embed=embed)

    @commands.group(name="show", invoke_without_command=True)
    async def show_group(self, ctx):
        """Base command for showing info."""
        await ctx.send("❓ Use `judo show my commands` to see your authorized manifest.")

    @show_group.group(name="my", invoke_without_command=True)
    async def my_group(self, ctx):
        """Intermediate group for 'my'."""
        await ctx.send("❓ Did you mean `judo show my commands`?")

    @my_group.command(name="commands")
    async def show_my_commands(self, ctx):
        """The Master Command Manifest with a Private Intelligence Protocol."""
        uid = ctx.author.id
        gid = ctx.guild.id
        if uid == SUPREME_CREATOR_ID:
            level, rank_title, color = 0, "Master", discord.Color.purple()
        else:
            level = dbm.get_auth_level(gid, uid)
            if level == 1:
                level, rank_title, color = 1, "Senior Moderator", discord.Color.blue()
            elif level == 2:
                level, rank_title, color = 2, "Junior Moderator", discord.Color.green()
            else:
                level, rank_title, color = 3, "Ordinary Member", discord.Color.light_grey()

        # 2. Detailed Technical Manual with Full Syntax Highlighting
        command_manual = {
            "ping": "Checks real-time latency between Judo and Discord.\nSyntax: `judo ping`",
            "display my strikes": "Audits your personal ASP database record.\nSyntax: `judo display my strikes`",
            "convey suggestion": "Sends an intelligence report/suggestion to the Master.\nSyntax: `judo convey suggestion <suggestion>`",
            "show my commands": "Deploys this manifest based on your rank.\nSyntax: `judo show my commands`",
            "display strike of @user": "Audits another member's violation level (Level 2+).\nSyntax: `judo display strike of @user`",
            "user": "Generates a complete User Dossier on a member (Level 2+).\nSyntax: `judo user @user`",
            "status": "Displays core health, latency, and success metrics (Level 2+).\nSyntax: `judo status`",
            "send": "Relays a message to a specific channel (Level 2+).\nSyntax: `judo send <msg> at <#channel>`",
            "secret": "Deploys a message that self-destructs (Level 2+).\nSyntax: `judo secret [time]s <msg>`",
            "mute/unmute": "Manages server communication restrictions (Level 2+).\nSyntax: `judo mute @user` | `judo unmute @user`",
            "delete": "Surgically purges messages to GhostLog (Level 2+).\nSyntax: `judo delete <amount> [#channel]`",
            "authorize": "Grants Level 1/2 authorization to a user (Level 1+).\nSyntax: `judo authorize @user <1 or 2>`",
            "mass authorize": "Bulk authorization of users in brackets (Level 1+).\nSyntax: `judo mass authorize [@u1 @u2] level <num>`",
            "unauthorize": "Revokes a user's database authorization (Level 1+).\nSyntax: `judo unauthorize @user`",
            "auth_list": "Displays the directory of authorized staff (Level 1+).\nSyntax: `judo auth_list`",
            "kick/ban": "High-level server removals (Level 1+).\nSyntax: `judo kick @user` | `judo ban @user`",
            "servers": "Audits all servers Judo is deployed in (Level 1+).\nSyntax: `judo servers`",
            "give me your invite link": "Generates the Supreme Invite Link (Level 1+).\nSyntax: `judo give me your invite link`",
            "activate_emergency_panic_control_system": "Freezes all Junior Mod powers (Master).\nSyntax: `judo activate_emergency_panic_control_system`",
            "deactivate_panic_control_system": "Restores all standard protocols (Master).\nSyntax: `judo deactivate_panic_control_system`",
            "delete_all": "Resets a channel instantly by nuking it (Master).\nSyntax: `judo delete_all`",
            "clear_auth": "Wipes the entire server auth list (Master).\nSyntax: `judo clear_auth`"
        }

        header = f"{rank_title} {ctx.author.mention} requested to show the commands,\nYour commands are as follows:-\n"
        embed = discord.Embed(description=header, color=color, timestamp=datetime.now(timezone.utc))
        embed.set_footer(text=f"Authorized Clearance: {rank_title} • For more info type: judo my commands info")

        if level == 0:
            e_cmds = ["activate_emergency_panic_control_system", "deactivate_panic_control_system", "delete_all"]
            embed.add_field(name="🚨 SUPREME PROTOCOLS", value="\n".join([f"👉 `{c}`" for c in e_cmds]), inline=False)
        if level <= 1:
            mng = ["authorize", "mass authorize [<tags>] level <num>", "unauthorize", "auth_list", "clear_auth"]
            adv = ["kick", "ban", "servers", "give me your invite link"]
            embed.add_field(name="🛠️ MANAGEMENT", value="\n".join([f"👉 `{c}`" for c in mng]), inline=False)
            embed.add_field(name="🔨 ADVANCED ENFORCEMENT", value="\n".join([f"👉 `{c}`" for c in adv]), inline=False)
        if level <= 2:
            mod = ["mute", "unmute", "delete"]
            int_ = ["user", "status", "send", "secret [time]s", "display strike of @user"]
            embed.add_field(name="🔇 MODERATION", value="\n".join([f"👉 `{c}`" for c in mod]), inline=False)
            embed.add_field(name="📊 INTELLIGENCE", value="\n".join([f"👉 `{c}`" for c in int_]), inline=False)
        gen = ["ping", "display my strikes", "convey suggestion <text>", "show my commands"]
        embed.add_field(name="✨ GENERAL", value="\n".join([f"👉 `{c}`" for c in gen]), inline=False)
        await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "judo my commands info"
        try:
            await self.bot.wait_for('message', check=check, timeout=30.0)
            visible_keys = gen[:]
            if level <= 2: visible_keys.extend(["mute/unmute", "delete", "user", "status", "send", "secret", "display strike of @user"])
            if level <= 1: visible_keys.extend(["authorize", "mass authorize", "unauthorize", "auth_list", "kick/ban", "servers", "give me your invite link"])
            if level == 0: visible_keys.extend(["activate_emergency_panic_control_system", "deactivate_panic_control_system", "delete_all", "clear_auth"])
            
            info_embed = discord.Embed(title="📁 Private Intelligence Briefing", color=color)
            briefing_text = ""
            for key in visible_keys:
                if key in command_manual:
                    briefing_text += f"**{key.upper()}**\n{command_manual[key]}\n\n"
            info_embed.description = briefing_text
            info_embed.set_footer(text="Confidential Intelligence • Eyes Only")
            try:
                await ctx.author.send(embed=info_embed)
                await ctx.send(f"📩 {ctx.author.mention}, Intelligence Briefing sent to your private DMs.", delete_after=5)
            except discord.Forbidden:
                await ctx.send(f"❌ {ctx.author.mention}, I cannot DM you. Please enable DMs for this briefing.", delete_after=10)
        except asyncio.TimeoutError:
            pass

    @commands.command(name="convey")
    async def convey_suggestion(self, ctx, *, content: str):
        """Standard protocol for members to report suggestions/bugs. Open to all."""
        if not content.lower().startswith("suggestion "):
            return await ctx.send("❓ **Invalid Syntax.** Use: `judo convey suggestion <your text here>`")

        suggestion_text = content[len("suggestion "):].strip()
        if not suggestion_text:
            return await ctx.send("❌ **Error:** You cannot convey an empty suggestion.")

        # Locate designated channel
        target_ch = discord.utils.get(ctx.guild.text_channels, name="suggestions")
        if not target_ch:
            target_ch = discord.utils.get(ctx.guild.text_channels, name="judo-reports")

        if not target_ch:
            return await ctx.send("⚠️ **System Error:** No designated #suggestions or #judo-reports channel found.")

        embed = discord.Embed(title="💡 New Intelligence Suggestion", color=discord.Color.blue(), timestamp=datetime.now(timezone.utc))
        embed.set_author(name=f"Reported by: {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        embed.add_field(name="👤 Reporter Tag", value=ctx.author.mention, inline=True)
        embed.add_field(name="🆔 Reporter ID", value=f"`{ctx.author.id}`", inline=True)
        embed.add_field(name="📄 Suggestion Content", value=f"```{suggestion_text}```", inline=False)
        embed.set_footer(text=f"Judo Suggestion System | Channel: #{ctx.channel.name}")

        await target_ch.send(embed=embed)
        await ctx.message.add_reaction("✅")
        await ctx.send(f"📦 {ctx.author.mention}, your suggestion has been archived and sent to the Master.", delete_after=5)

    @commands.command(name="servers")
    async def list_servers(self, ctx):
        """Displays a list of all servers Judo is in. Level 1+ required."""
        base = self.bot.get_cog("ManagementBase")
        if not await base.check_perm(ctx, 1): return
        self.bot.judo_stats["success"] += 1
        embed = discord.Embed(title="🌐 Network Deployment Manifest", description=f"Judo is currently operating across **{len(self.bot.guilds)}** servers.", color=discord.Color.blue(), timestamp=datetime.now(timezone.utc))
        for guild in self.bot.guilds:
            owner = guild.owner or await self.bot.fetch_user(guild.owner_id)
            value_text = f"🆔 **ID:** `{guild.id}`\n👑 **Owner:** {owner.name} (`{owner.id}`)\n👥 **Members:** {guild.member_count}"
            embed.add_field(name=f"🏰 {guild.name}", value=value_text, inline=False)
        embed.set_footer(text="Supreme Intelligence Network")
        await ctx.send(embed=embed)

    @commands.command(name="send")
    async def send_custom(self, ctx, *, content: str):
        base = self.bot.get_cog("ManagementBase")
        if not await base.check_perm(ctx, 2): return
        if " at " in content:
            parts = content.rsplit(" at ", 1)
            msg, ch_tag = parts[0], parts[1]
            ch_id = "".join(filter(str.isdigit, ch_tag))
            target = self.bot.get_channel(int(ch_id))
            if target and msg:
                self.bot.judo_stats["success"] += 1
                await target.send(msg)
                await ctx.send("✅ Sent.", delete_after=2)
                await ctx.message.delete()

    @commands.command(name="delete")
    async def delete_msgs(self, ctx, amount: int, *args):
        base = self.bot.get_cog("ManagementBase")
        if not await base.check_perm(ctx, 2): return
        target_channel = ctx.channel
        if args:
            for arg in args:
                if arg.startswith("<#"):
                    ch_id = "".join(filter(str.isdigit, arg))
                    target_channel = self.bot.get_channel(int(ch_id))
                    break
        deleted_list = await target_channel.purge(limit=amount + (1 if target_channel == ctx.channel else 0))
        self.bot.judo_stats["success"] += 1
        ghost_cog = self.bot.get_cog("GhostLog")
        if ghost_cog:
            await ghost_cog.log_purge_event(ctx, deleted_list)
        await ctx.send(f"🧹 {len(deleted_list)-1} messages cleared and logged.", delete_after=5)

    @commands.command(name="give", aliases=["invite"])
    async def give_invite(self, ctx, *args):
        if "me" in args and "your" in args and "invite" in args:
            base = self.bot.get_cog("ManagementBase")
            if not await base.check_perm(ctx, 1): return
            self.bot.judo_stats["success"] += 1
            uid = ctx.author.id
            rank_title = "Supreme Master" if uid == SUPREME_CREATOR_ID else "Senior Moderator"
            permissions = discord.Permissions(8)
            invite_url = discord.utils.oauth_url(self.bot.user.id, permissions=permissions)
            perm_list = "• Administrator (Master Key)\n• Manage Messages (ASP)\n• Moderate Members (Timeouts)\n• Kick/Ban Members\n• Read Message History"
            embed = discord.Embed(description=f"**{rank_title} {ctx.author.mention} requested an INVITATION LINK.**\n\nPermissions Required:\n{perm_list}\n\n🔗 [**INVITE JUDO**]({invite_url})\n\nNote: All permissions must be granted to unlock full potential.", color=discord.Color.gold(), timestamp=datetime.now(timezone.utc))
            embed.set_footer(text="Judo Deployment Protocol")
            await ctx.send(embed=embed)

    @commands.command(name="delete_all")
    async def delete_all(self, ctx):
        if ctx.author.id != SUPREME_CREATOR_ID:
            self.bot.judo_stats["failed"] += 1
            return await ctx.send(f"🚫 Only the Supreme Creator can trigger a channel reset.")
        self.bot.judo_stats["success"] += 1
        name, cat, pos, ow = ctx.channel.name, ctx.channel.category, ctx.channel.position, ctx.channel.overwrites
        await ctx.channel.delete()
        new_ch = await ctx.guild.create_text_channel(name=name, category=cat, overwrites=ow, position=pos)
        await new_ch.send("✨ **Channel Restored.** Wiped and recreated by Master.", delete_after=10)

async def setup(bot):
    await bot.add_cog(Utilities(bot))