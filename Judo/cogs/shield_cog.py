import discord
from discord.ext import commands, tasks
import asyncio
import os
import time
import re
import datetime

class Shield(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.owner_id = int(os.getenv('OWNER_ID'))
        self.spam_tracker = {} 
        self.spam_strikes = {} 
        self.strike_cooldowns = {} 
        self.strike_reset_loop.start()

    @tasks.loop(hours=1.0)
    async def strike_reset_loop(self):
        self.spam_strikes = {}
        self.strike_cooldowns = {}

    def is_module_active(self, file_path, channel_id):
        if not os.path.exists(file_path): return False
        try:
            with open(file_path, 'r') as f:
                return str(channel_id) in f.read().splitlines()
        except: return False

    async def ghost_cleanup(self, message):
        log_channel_id = int(os.getenv('LOG_CHANNEL_ID'))
        if message.channel.id != log_channel_id:
            await asyncio.sleep(5)
            try: await message.delete()
            except: pass

    async def integrated_shield_check(self, message):
        if message.author.id == self.owner_id: return False

        # 1. BANNED WORDS
        if self.is_module_active('config/bw_channels.txt', message.channel.id):
            if os.path.exists('data/banned_words.txt'):
                with open('data/banned_words.txt', 'r') as f:
                    banned = [l.strip().lower() for l in f.readlines() if l.strip()]
                if any(w in message.content.lower() for w in banned):
                    await message.delete()
                    await message.channel.send(f"⚠️ {message.author.mention}, prohibited language.", delete_after=5)
                    # Log the violation
                    sec = self.bot.get_cog('Security')
                    if sec: await sec.judo_log("YELLOW", message.author, "Banned Word Filter", f"Message: {message.content[:50]}...")
                    return True

        # 2. ANTI-SPAM (ASP)
        if self.is_module_active('config/asp_channels.txt', message.channel.id):
            uid = message.author.id
            now = time.time()
            if uid in self.strike_cooldowns and now - self.strike_cooldowns[uid] < 5:
                return True

            if uid not in self.spam_tracker: self.spam_tracker[uid] = []
            self.spam_tracker[uid].append(now)
            self.spam_tracker[uid] = self.spam_tracker[uid][-6:]

            if len(self.spam_tracker[uid]) == 6:
                if now - self.spam_tracker[uid][0] < 12:
                    self.strike_cooldowns[uid] = now 
                    strikes = self.spam_strikes.get(uid, 0) + 1
                    self.spam_strikes[uid] = strikes
                    duration = 120 if strikes == 1 else 600
                    try:
                        until = discord.utils.utcnow() + datetime.timedelta(seconds=duration)
                        await message.author.timeout(until, reason="ASP Violation")
                        await message.channel.send(f"🚫 {message.author.mention}, stop spamming (Strike {strikes})", delete_after=10)
                        # --- CENTRAL LOGGING CALL ---
                        sec = self.bot.get_cog('Security')
                        if sec: await sec.judo_log("RED", message.author, f"ASP Strike {strikes}", "6 messages in 12s")
                    except: pass
                    self.spam_tracker[uid] = []
                    return True
        return False

    @commands.command(name="activate")
    async def activate_module(self, ctx, module, *, extra=None):
        mod = module.upper()
        file_map = {"ASP": "config/asp_channels.txt", "FI": "config/fi_channels.txt", "BW": "config/bw_channels.txt"}
        if mod not in file_map: return await ctx.send(f"❌ Unknown module: `{mod}`", delete_after=5)
        target = ctx.message.channel_mentions[0] if ctx.message.channel_mentions else ctx.channel
        os.makedirs('config', exist_ok=True)
        with open(file_map[mod], 'a+') as f:
            f.seek(0)
            if str(target.id) not in f.read():
                f.write(f"{target.id}\n")
                await ctx.send(f"✅ {mod} activated in {target.mention}.")
                sec = self.bot.get_cog('Security')
                if sec: await sec.judo_log("BLUE", ctx.author, f"Module Activated", f"{mod} at {target.name}")
        await self.ghost_cleanup(ctx.message)

async def setup(bot):
    await bot.add_cog(Shield(bot))