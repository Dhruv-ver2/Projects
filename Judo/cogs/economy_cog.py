import discord
from discord.ext import commands
import json
import os
import time
import asyncio

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.owner_id = int(os.getenv('OWNER_ID'))
        self.xp_file = 'data/xp_data.json'
        self.settings_file = 'data/xp_settings.json'
        
        # XP Throttling: {user_id: [count, last_reset_timestamp]}
        self.xp_throttle = {}
        
        # Lock to prevent file corruption during simultaneous writes
        self.lock = asyncio.Lock()
        
        # Load or Create Data
        self.ensure_data()

    def ensure_data(self):
        """Ensures the JSON files exist to prevent crashes."""
        for file in [self.xp_file, self.settings_file]:
            if not os.path.exists(file):
                with open(file, 'w') as f:
                    json.dump({}, f)

    async def get_data(self, file_path):
        async with self.lock:
            with open(file_path, 'r') as f:
                return json.load(f)

    async def save_data(self, file_path, data):
        async with self.lock:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)

    # --- THE XP PROCESSING LOGIC ---
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.content.lower().startswith('judo'):
            return

        settings = await self.get_data(self.settings_file)
        
        # 1. Global & Channel Kill-Switches
        if settings.get('global_disabled', False): return
        if str(message.channel.id) in settings.get('disabled_channels', []): return
        
        # 2. User Blacklist Check
        if str(message.author.id) in settings.get('disabled_users', []): return

        # 3. 4/60 Throttle Check (4 messages per 60 seconds)
        user_id = str(message.author.id)
        now = time.time()
        
        if user_id not in self.xp_throttle:
            self.xp_throttle[user_id] = [1, now]
        else:
            count, last_reset = self.xp_throttle[user_id]
            if now - last_reset > 60:
                self.xp_throttle[user_id] = [1, now]
            elif count < 4:
                self.xp_throttle[user_id][0] += 1
            else:
                # Limit reached: Silent ignore
                return

        # 4. Award XP
        xp_data = await self.get_data(self.xp_file)
        current_xp = xp_data.get(user_id, 0)
        
        # Use channel-specific minimum if set, else default 10
        reward = settings.get('channel_min_xp', {}).get(str(message.channel.id), 10)
        
        xp_data[user_id] = current_xp + reward
        await self.save_data(self.xp_file, xp_data)

    # --- XP MANAGEMENT COMMANDS (OWNER ONLY FOR NOW) ---
    @commands.command(name="add")
    async def add_xp(self, ctx, amount: int, *, target: str):
        """judo add 500 xp for @user"""
        if ctx.author.id != self.owner_id: return
        
        if ctx.message.mentions:
            user = ctx.message.mentions[0]
            xp_data = await self.get_data(self.xp_file)
            xp_data[str(user.id)] = xp_data.get(str(user.id), 0) + amount
            await self.save_data(self.xp_file, xp_data)
            await ctx.send(f"✅ Added {amount} XP to {user.mention}.", delete_after=5)

    @commands.command(name="wipe_xp")
    async def wipe_xp_cmd(self, ctx, *, target: str):
        """judo wipe_xp all xp for @user"""
        if ctx.author.id != self.owner_id: return
        
        if "all xp for" in target.lower() and ctx.message.mentions:
            user = ctx.message.mentions[0]
            xp_data = await self.get_data(self.xp_file)
            xp_data[str(user.id)] = 0
            await self.save_data(self.xp_file, xp_data)
            await ctx.send(f"⚠️ All XP for {user.mention} has been wiped.", delete_after=5)

    @commands.command(name="disable")
    async def disable_xp(self, ctx, *, target: str):
        """judo disable xp system for entire server / at #channel"""
        if ctx.author.id != self.owner_id: return
        settings = await self.get_data(self.settings_file)

        if "entire server" in target.lower():
            settings['global_disabled'] = True
            await ctx.send("🚫 XP System disabled globally.", delete_after=5)
        elif ctx.message.channel_mentions:
            channel = ctx.message.channel_mentions[0]
            disabled_channels = settings.get('disabled_channels', [])
            if str(channel.id) not in disabled_channels:
                disabled_channels.append(str(channel.id))
                settings['disabled_channels'] = disabled_channels
                await ctx.send(f"🚫 XP disabled in {channel.mention}.", delete_after=5)
        
        await self.save_data(self.settings_file, settings)

    @commands.command(name="enable")
    async def enable_xp(self, ctx, *, target: str):
        if ctx.author.id != self.owner_id: return
        settings = await self.get_data(self.settings_file)

        if "entire server" in target.lower():
            settings['global_disabled'] = False
            await ctx.send("✅ XP System enabled globally.", delete_after=5)
        elif ctx.message.channel_mentions:
            channel = ctx.message.channel_mentions[0]
            settings['disabled_channels'] = [c for c in settings.get('disabled_channels', []) if c != str(channel.id)]
            await ctx.send(f"✅ XP enabled in {channel.mention}.", delete_after=5)
            
        await self.save_data(self.settings_file, settings)

async def setup(bot):
    await bot.add_cog(Economy(bot))