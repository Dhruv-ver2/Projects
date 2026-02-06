import discord
from discord.ext import commands
import database_manager as dbm
from datetime import datetime

SUPREME_CREATOR_ID = 757990668357599302 

class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cmd_usage = {} 
        self.voice_history = {} 

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
        base = self.bot.get_cog("ManagementBase")
        if not await base.check_perm(ctx, 2): return
        self.bot.judo_stats["success"] += 1

        member = member or ctx.author
        uid_str = str(member.id)
        
        # --- IMPROVED AUTH STATUS LOGIC ---
        if member.id == SUPREME_CREATOR_ID:
            auth_status = "Supreme Master"
        elif member.id == self.bot.user.id:
            auth_status = "Administrator"
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
        embed.add_field(name="🆔 User ID", value=uid_str, inline=True)
        
        # Displaying the new descriptive Auth Status
        embed.add_field(name="🛡️ Auth Status", value=f"**{auth_status}**", inline=True)
        
        embed.add_field(name="🗓️ Joined Discord", value=member.created_at.strftime("%b %d, %Y"), inline=True)
        embed.add_field(name="📥 Joined Server", value=member.joined_at.strftime("%b %d, %Y"), inline=True)
        embed.add_field(name="💬 Command Channels (Session)", value=", ".join(self.cmd_usage.get(uid_str, ["None"])), inline=False)
        embed.add_field(name="🎙️ Voice Channels (Session)", value=", ".join(self.voice_history.get(uid_str, ["None"])), inline=False)
        embed.add_field(name=f"🎭 Roles [{len(roles)}]", value=" ".join(roles) if roles else "None", inline=False)
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

        # Archive Logic
        archive_ch = discord.utils.get(ctx.guild.text_channels, name="purged-messages")
        if archive_ch:
            collected = []
            async for msg in target_channel.history(limit=amount + (1 if target_channel == ctx.channel else 0)):
                if msg.id == ctx.message.id: continue
                collected.append(f"[{msg.created_at.strftime('%H:%M')}] **{msg.author}**: {msg.content}")
            if collected:
                collected.reverse()
                report = "\n".join(collected)
                for i in range(0, len(report), 1900):
                    await archive_ch.send(embed=discord.Embed(title=f"🗑️ Archive: #{target_channel.name}", description=report[i:i+1900]))

        await target_channel.purge(limit=amount + (1 if target_channel == ctx.channel else 0))
        self.bot.judo_stats["success"] += 1
        await ctx.send(f"🧹 Purge Complete.", delete_after=5)

    @commands.command(name="delete_all")
    async def delete_all(self, ctx):
        if ctx.author.id != SUPREME_CREATOR_ID:
            self.bot.judo_stats["failed"] += 1
            return await ctx.send(f"🚫 Only the Master can use this.")
        
        self.bot.judo_stats["success"] += 1
        name, cat, pos, ow = ctx.channel.name, ctx.channel.category, ctx.channel.position, ctx.channel.overwrites
        await ctx.channel.delete()
        new_ch = await ctx.guild.create_text_channel(name=name, category=cat, overwrites=ow, position=pos)
        await new_ch.send("✨ Channel wiped and recreated by Master.", delete_after=10)

async def setup(bot):
    await bot.add_cog(Utilities(bot))