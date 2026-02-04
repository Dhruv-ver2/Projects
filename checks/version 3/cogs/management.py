import discord
from discord.ext import commands
import database_manager as dbm
from datetime import datetime

# YOUR HARDCODED ID
SUPREME_CREATOR_ID = 757990668357599302 

class Management(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_authorized(self, user_id, guild_id, required_level):
        """Checks if a user meets the required authorization level."""
        uid, gid = str(user_id), str(guild_id)
        if user_id == SUPREME_CREATOR_ID:
            return True
        user_level = dbm.get_auth_level(gid, uid)
        if user_level == 0:
            return False
        return user_level <= required_level

    def get_author_title(self, user_id, guild_id):
        """Helper to get the string title for logs and announcements."""
        if user_id == SUPREME_CREATOR_ID:
            return "Master"
        level = dbm.get_auth_level(guild_id, user_id)
        if level == 1:
            return "Senior Mod (Level 1)"
        if level == 2:
            return "Junior Mod (Level 2)"
        return "Unauthorized User"

    async def log_action(self, ctx, action_detail):
        """Restores the lost logging functionality to #judo-logs."""
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
        """Handles permission checks and tags unauthorized users."""
        if not self.is_authorized(ctx.author.id, ctx.guild.id, level):
            await ctx.send(f"🚫 {ctx.author.mention}, you attempted to use Judo but don't have Level {level} permission.")
            await self.log_action(ctx, f"UNAUTHORIZED Attempt: Level {level} required.")
            return False
        return True

    # --- AUTHORIZATION COMMANDS ---

    @commands.command(name="authorize")
    async def authorize_user(self, ctx, member: discord.Member, level: int):
        if not await self.check_perm(ctx, 1): return
        if level not in [1, 2]:
            return await ctx.send("⚠️ Level must be 1 (Senior) or 2 (Junior).")
        dbm.set_auth_level(ctx.guild.id, member.id, level)
        await ctx.send(f"✅ {member.display_name} is now **Level {level}**.")
        await self.log_action(ctx, f"Authorized {member.display_name} as Level {level}")

    @commands.command(name="unauthorize")
    async def unauthorize_user(self, ctx, member: discord.Member):
        if not await self.check_perm(ctx, 1): return
        dbm.set_auth_level(ctx.guild.id, member.id, 0)
        await ctx.send(f"🛑 Authorization revoked for {member.display_name}.")
        await self.log_action(ctx, f"Revoked authorization for {member.display_name}")

    # --- COMMUNICATION COMMANDS ---

    @commands.command(name="send")
    async def send_custom(self, ctx, *, content: str):
        if not await self.check_perm(ctx, 2): return
        try:
            if " at " in content:
                parts = content.rsplit(" at ", 1)
                message_text, channel_mention = parts[0], parts[1]
                channel_id = "".join(filter(str.isdigit, channel_mention))
                target_channel = self.bot.get_channel(int(channel_id))
                if target_channel:
                    await target_channel.send(message_text)
                    await ctx.send(f"✅ Delivered to {target_channel.mention}", delete_after=3)
                    await ctx.message.delete()
                    await self.log_action(ctx, f"Sent message to #{target_channel.name}")
            else:
                await ctx.send("❌ Use: `judo send <msg> at <#channel>`")
        except Exception as e:
            await ctx.send(f"⚠️ Error: {e}")

    # --- DELETE & ARCHIVE COMMANDS ---

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
        
        # Capture for #purged-messages before deleting
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
        await self.log_action(ctx, f"Purged {count} messages in #{target_channel.name}")

    @commands.command(name="delete_all")
    async def delete_all_messages(self, ctx):
        if ctx.author.id != SUPREME_CREATOR_ID:
            return await ctx.send(f"🚫 {ctx.author.mention}, only the **Master** can use the Nuclear Option.")

        await self.log_action(ctx, f"NUCLEAR OPTION triggered in #{ctx.channel.name}")
        name, cat, pos, ow = ctx.channel.name, ctx.channel.category, ctx.channel.position, ctx.channel.overwrites
        await ctx.channel.delete()
        new_ch = await ctx.guild.create_text_channel(name=name, category=cat, overwrites=ow, position=pos)
        await new_ch.send("✨ Channel wiped and recreated by **Master**.", delete_after=10)

async def setup(bot):
    await bot.add_cog(Management(bot))