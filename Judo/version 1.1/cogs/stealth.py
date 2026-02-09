import discord
from discord.ext import commands
import asyncio
from datetime import datetime

class Stealth(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="secret")
    async def self_destruct(self, ctx, time_str: str, *, message: str):
        """Sends a message that deletes itself after X seconds. Level 2+ required."""
        # 1. Permission Check (Junior Mod+)
        base = self.bot.get_cog("ManagementBase")
        if not await base.check_perm(ctx, 2): return

        # 2. Parse the time (Extract number from '10s', '5s', etc.)
        try:
            seconds = int(time_str.lower().replace('s', ''))
            if seconds > 300: # 5 minute cap for safety
                seconds = 300
        except ValueError:
            return await ctx.send("❌ Invalid time format. Use `5s`, `10s`, etc.", delete_after=3)

        # 3. Delete the trigger command immediately for stealth
        try:
            await ctx.message.delete()
        except:
            pass

        # 4. Create the Secret Embed
        embed = discord.Embed(
            title="🔒 SECURE CLEARANCE MESSAGE",
            description=message,
            color=0x2f3136, # Dark blend color
            timestamp=datetime.now()
        )
        embed.set_author(name=f"Issued by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        embed.set_footer(text=f"This message will self-destruct in {seconds} seconds.")

        secret_msg = await ctx.send(embed=embed)

        # 5. The Destruction Countdown
        await asyncio.sleep(seconds)
        
        try:
            await secret_msg.delete()
        except:
            pass

async def setup(bot):
    await bot.add_cog(Stealth(bot))