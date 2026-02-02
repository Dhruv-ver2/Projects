import discord
from discord.ext import commands
import database_manager as dbm

# YOUR HARDCODED ID
SUPREME_CREATOR_ID = 757990668357599302 

class Management(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_authorized(self, user_id, guild_id, required_level):
        uid, gid = str(user_id), str(guild_id)
        if user_id == SUPREME_CREATOR_ID:
            return True
        
        user_level = dbm.get_auth_level(gid, uid)
        if user_level == 0:
            return False
        # Level 1 is a lower number but higher rank, so Level 1 passes Level 2 checks
        return user_level <= required_level

    @commands.command(name="authorize")
    async def authorize_user(self, ctx, member: discord.Member, level: int):
        if not self.is_authorized(ctx.author.id, ctx.guild.id, required_level=1):
            return await ctx.send("🚫 You need Level 1 Authorization to manage staff.")
        
        if level not in [1, 2]:
            return await ctx.send("⚠️ Level must be 1 (Senior) or 2 (Junior).")
        
        dbm.set_auth_level(ctx.guild.id, member.id, level)
        await ctx.send(f"✅ {member.display_name} is now **Level {level}**.")

    @commands.command(name="unauthorize")
    async def unauthorize_user(self, ctx, member: discord.Member):
        if not self.is_authorized(ctx.author.id, ctx.guild.id, required_level=1):
            return await ctx.send("🚫 You need Level 1 Authorization to manage staff.")
        
        dbm.set_auth_level(ctx.guild.id, member.id, 0)
        await ctx.send(f"🛑 Authorization revoked for {member.display_name}.")

    @commands.command(name="send")
    async def send_custom(self, ctx, *, content: str):
        if not self.is_authorized(ctx.author.id, ctx.guild.id, required_level=2):
            return await ctx.send("🚫 Level 2 Authorization required.")

        try:
            if " at " in content:
                parts = content.rsplit(" at ", 1)
                message_text, channel_mention = parts[0], parts[1]
                channel_id = "".join(filter(str.isdigit, channel_mention))
                target_channel = self.bot.get_channel(int(channel_id))

                if target_channel:
                    await target_channel.send(message_text)
                    await ctx.send(f"✅ Sent.", delete_after=3)
                    await ctx.message.delete()
            else:
                await ctx.send("❌ Syntax: `judo send <msg> at <#channel>`")
        except Exception as e:
            await ctx.send(f"⚠️ Error: {e}")

    @commands.command(name="delete")
    async def delete_messages(self, ctx, amount: int):
        # Level 1 required for mass deletion
        if not self.is_authorized(ctx.author.id, ctx.guild.id, required_level=1):
            return await ctx.send("🚫 Level 1 (Senior) Authorization required to delete messages.")
        
        if amount < 1 or amount > 100:
            return await ctx.send("⚠️ Please choose a number between 1 and 100.")
        
        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"🧹 Cleared {len(deleted)-1} messages.", delete_after=5)

async def setup(bot):
    await bot.add_cog(Management(bot))