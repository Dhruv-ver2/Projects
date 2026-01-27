import discord
from discord.ext import commands
import asyncio
import os
import datetime

class Security(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.owner_id = int(os.getenv('OWNER_ID'))
        self.log_channel_id = int(os.getenv('LOG_CHANNEL_ID'))

    # --- THE CENTRAL LOGGING ENGINE ---
    async def judo_log(self, type, user, action, detail):
        """Standardized logging for all Judo Cogs."""
        channel = self.bot.get_channel(self.log_channel_id)
        if not channel: 
            print(f"❌ LOG ERROR: Could not find Channel ID {self.log_channel_id}")
            return

        colors = {
            "RED": discord.Color.red(),      # Security/Spam
            "PURPLE": discord.Color.purple(), # Nuclear
            "YELLOW": discord.Color.gold(),   # Mod
            "BLUE": discord.Color.blue()      # System/Info
        }

        embed = discord.Embed(
            title=f"🥋 JUDO {type} ALERT", 
            color=colors.get(type, discord.Color.greyple()),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="User", value=f"{user.mention} ({user.id})", inline=False)
        embed.add_field(name="Action", value=action, inline=True)
        embed.add_field(name="Details", value=detail, inline=False)
        embed.set_footer(text="Dojo Telemetry System")
        
        try:
            await channel.send(embed=embed)
        except Exception as e:
            print(f"❌ LOG ERROR: Permission denied in log channel: {e}")

    # --- PILLAR 1: THE ANTI-SABOTAGE WALL ---
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: return
        triggered = message.content.lower().startswith('judo ') or self.bot.user.mentioned_in(message)
        
        if triggered:
            authorized_ids = []
            if os.path.exists('data/authorized.txt'):
                with open('data/authorized.txt', 'r') as f:
                    authorized_ids = [line.strip() for line in f.readlines()]

            if message.author.id != self.owner_id and str(message.author.id) not in authorized_ids:
                await self.apply_security_strike(message)

    async def apply_security_strike(self, message):
        user = message.author
        p1_path, p2_path = 'security/phase1.txt', 'security/phase2.txt'
        p1 = open(p1_path, 'r').read().splitlines() if os.path.exists(p1_path) else []
        p2 = open(p2_path, 'r').read().splitlines() if os.path.exists(p2_path) else []

        strike = 3 if str(user.id) in p2 else (2 if str(user.id) in p1 else 1)
        duration = 86400 if strike == 3 else (600 if strike == 2 else 120)

        try:
            await user.timeout(datetime.timedelta(seconds=duration), reason=f"Security Strike {strike}")
            if strike == 1:
                with open(p1_path, 'a') as f: f.write(f"{user.id}\n")
            elif strike == 2:
                new_p1 = [uid for uid in p1 if uid != str(user.id)]
                with open(p1_path, 'w') as f: f.write("\n".join(new_p1) + "\n")
                with open(p2_path, 'a') as f: f.write(f"{user.id}\n")

            await message.reply(f"! JUDO Couldn't Obey you, kindly don't try to command me again.")
            await self.judo_log("RED", user, f"Security Strike {strike}", f"Unauthorized Access Attempt")
        except: pass

    # --- PILLAR 2: THE NUCLEAR PROTOCOL ---
    async def nuclear_confirm(self, ctx, task_name):
        if ctx.author.id != self.owner_id: return False
        await ctx.send(f"Master Dhruv, are you sure u want to do {task_name}?")
        def check(m): return m.author.id == self.owner_id and m.channel == ctx.channel and m.content.lower() in ['yes', 'no']
        try:
            msg = await self.bot.wait_for('message', timeout=15.0, check=check)
            return msg.content.lower() == 'yes'
        except asyncio.TimeoutError: return False

    @commands.command(name="wipe_logs")
    async def wipe_logs_cmd(self, ctx, target):
        if target == "the judo-logs":
            if await self.nuclear_confirm(ctx, "Wipe Logs"):
                await ctx.send("! Judo has WIPED the logs.")
                await self.judo_log("PURPLE", ctx.author, "Nuclear Action", "Wiped Judo-Logs")

async def setup(bot):
    await bot.add_cog(Security(bot))