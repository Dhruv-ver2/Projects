import discord
from discord.ext import commands
import asyncio
import database_manager as dbm
from datetime import datetime, timezone

SUPREME_CREATOR_ID = 757990668357599302 

class Emergency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="activate_emergency_panic_control_system")
    async def activate_panic(self, ctx):
        """MASTER ONLY: Initiates Total Global Lockdown."""
        if ctx.author.id != SUPREME_CREATOR_ID:
            return await ctx.send("🚫 Only the Supreme Creator can trigger a Level 5 Lockdown.")

        if self.bot.panic_mode:
            return await ctx.send("⚠️ The system is already in Panic Mode.")

        # 1. Safety Confirmation
        await ctx.send(f"⚠️ **MASTER CONFIRMATION REQUIRED.** {ctx.author.mention}, type `confirm` to initiate Global Lockdown.")
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "confirm"
        
        try:
            await self.bot.wait_for('message', check=check, timeout=15.0)
        except asyncio.TimeoutError:
            return await ctx.send("⏳ Lockdown aborted. Confirmation timed out.")

        # 2. Initialization
        self.bot.panic_mode = True # LEVEL 2 NEUTRALIZED IMMEDIATELY
        self.bot.judo_stats["success"] += 1
        
        # 3. Channel Setup
        auth_db = dbm.load_json(dbm.AUTH_FILE)
        gid = str(ctx.guild.id)
        level1_ids = auth_db.get(gid, {}).get("auth1", [])

        # HQ Setup
        hq_overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            ctx.author: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        for uid in level1_ids:
            m = ctx.guild.get_member(int(uid))
            if m: hq_overwrites[m] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        hq_ch = await ctx.guild.create_text_channel("🔴-emergency-hq", overwrites=hq_overwrites, position=0)
        
        # Crisis Zone Setup
        crisis_overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            ctx.author: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        crisis_ch = await ctx.guild.create_text_channel("🆘-crisis-zone", overwrites=crisis_overwrites, position=1)

        await ctx.send("🚨 **Emergency Crisis Control System Activated.** Channels are being locked. Move to the Crisis Zone.")
        await crisis_ch.send("🛡️ **System Status:** Emergency Crisis Control System Activated by Supreme Creator.\nGlobal lockdown in progress. Live feed starting...")

        # 4. Global Lockdown Loop (Inclusive of Voice/Stage/Category)
        # Using guild.channels to capture everything
        for target in ctx.guild.channels:
            if target.id in [hq_ch.id, crisis_ch.id]: continue
            if target.category and target.category.id == hq_ch.category_id: continue

            # Snapshot state
            self.bot.panic_snapshot[target.id] = target.overwrites_for(ctx.guild.default_role)
            
            # Lockdown Permissions
            lock_overwrite = discord.PermissionOverwrite(
                view_channel=False, 
                send_messages=False,
                connect=False,
                read_message_history=False
            )
            
            try:
                await target.set_permissions(ctx.guild.default_role, overwrite=lock_overwrite)
                
                # Level 1 Bypass
                for uid in level1_ids:
                    m = ctx.guild.get_member(int(uid))
                    if m: await target.set_permissions(m, view_channel=True, send_messages=True)

                # Sycned reporting
                msg = f"🔒 **Locked:** {target.name}"
                await hq_ch.send(msg)
                await crisis_ch.send(msg)
                
                await asyncio.sleep(0.7) 
            except:
                continue

        await crisis_ch.send("✅ **Protocol Finalized.** All public sectors are now secured.")
        await hq_ch.send("✅ **LOCKDOWN COMPLETE.**")

    @commands.command(name="deactivate_panic_control_system")
    async def deactivate_panic(self, ctx):
        """MASTER ONLY: Reverts Lockdown."""
        if ctx.author.id != SUPREME_CREATOR_ID: return
        if not self.bot.panic_mode: return

        # 1. Flip flag FIRST to re-arm staff
        self.bot.panic_mode = False 
        
        hq_ch = discord.utils.get(ctx.guild.text_channels, name="🔴-emergency-hq")
        crisis_ch = discord.utils.get(ctx.guild.text_channels, name="🆘-crisis-zone")
        
        if hq_ch: await hq_ch.send("🔓 **RESTORATION INITIALIZED.** Power returned to Junior Mods. Restoring channels...")

        # 2. Restoration Loop
        for target_id, original_overwrite in self.bot.panic_snapshot.items():
            target = ctx.guild.get_channel(target_id)
            if target:
                try:
                    # Clear Staff Overrides
                    auth_db = dbm.load_json(dbm.AUTH_FILE)
                    level1_ids = auth_db.get(str(ctx.guild.id), {}).get("auth1", [])
                    for uid in level1_ids:
                        m = ctx.guild.get_member(int(uid))
                        if m: await target.set_permissions(m, overwrite=None)

                    # Restore Default
                    await target.set_permissions(ctx.guild.default_role, overwrite=original_overwrite)
                    await asyncio.sleep(0.5)
                except: continue

        # 3. Final Announcement to General
        general = discord.utils.get(ctx.guild.text_channels, name="general")
        target_notif = general if general else ctx.channel
        await target_notif.send("✨ **Emergency Crisis Control System Deactivated.** All channels restored. Thank you for your patience.")

        # 4. Cleanup
        if crisis_ch: await crisis_ch.delete()
        if hq_ch: await hq_ch.delete()
        
        self.bot.panic_snapshot = {}
        await ctx.send("✅ Server Restored Successfully.", delete_after=5)

async def setup(bot):
    await bot.add_cog(Emergency(bot))