import discord
from discord.ext import commands
import asyncio
import database_manager as dbm
import os
from datetime import datetime, timezone

SUPREME_CREATOR_ID = 757990668357599302 
SNAPSHOT_FILE = "emergency_snapshot.json"

class Emergency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="activate_emergency_panic_control_system")
    async def activate_panic(self, ctx):
        """Phase 1 & 2: Documentation and Execution."""
        if ctx.author.id != SUPREME_CREATOR_ID:
            return await ctx.send("🚫 **Unauthorized.** Only the Supreme Creator can trigger Level 5 protocols.")

        # Safety check: Prevent overwriting a good snapshot with a locked one
        if os.path.exists(SNAPSHOT_FILE):
            return await ctx.send("⚠️ **System Blocked:** A snapshot already exists on disk. Please deactivate the current lockdown first.")

        # 1. Master Confirmation
        await ctx.send(f"⚠️ **MASTER CONFIRMATION REQUIRED.** {ctx.author.mention}, type `confirm` to initiate Global Lockdown.")
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "confirm"
        
        try:
            await self.bot.wait_for('message', check=check, timeout=15.0)
        except asyncio.TimeoutError:
            return await ctx.send("⏳ Lockdown aborted. Confirmation timed out.")

        # --- PHASE 1: DISK DOCUMENTATION ---
        await ctx.send("📑 **Phase 1: Documenting Server Permissions to Disk...**")
        full_snapshot = {}
        
        for target in ctx.guild.channels:
            # Capture @everyone overwrites specifically
            ov = target.overwrites_for(ctx.guild.default_role)
            # Convert the PermissionOverwrite object into a dictionary of active permissions
            full_snapshot[str(target.id)] = {p: val for p, val in dict(ov).items() if val is not None}

        dbm.save_json(SNAPSHOT_FILE, full_snapshot)

        # --- PHASE 2: EXECUTION ---
        self.bot.panic_mode = True # LEVEL 2 STAFF NEUTRALIZED
        self.bot.judo_stats["success"] += 1
        
        auth_db = dbm.load_json(dbm.AUTH_FILE)
        gid = str(ctx.guild.id)
        level1_ids = auth_db.get(gid, {}).get("auth1", [])

        # Setup Secure Channels
        hq_overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            ctx.author: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        for uid in level1_ids:
            m = ctx.guild.get_member(int(uid))
            if m: hq_overwrites[m] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        hq_ch = await ctx.guild.create_text_channel("🔴-emergency-hq", overwrites=hq_overwrites, position=0)
        crisis_ch = await ctx.guild.create_text_channel("🆘-crisis-zone", position=1)

        await hq_ch.send("⚡ **PHASE 2: LOCKDOWN INITIALIZED.** Snapshot secured to `emergency_snapshot.json`.")
        await crisis_ch.send("🛡️ **System Status:** Emergency Crisis Control System Activated. All sectors are being secured.")

        for target in ctx.guild.channels:
            if target.id in [hq_ch.id, crisis_ch.id]: continue
            if target.category and target.category.id == hq_ch.category_id: continue

            lock_overwrite = discord.PermissionOverwrite(
                view_channel=False, 
                send_messages=False,
                connect=False,
                read_message_history=False
            )
            
            try:
                await target.set_permissions(ctx.guild.default_role, overwrite=lock_overwrite)
                
                # Apply Level 1 bypass for tactical coordination
                for uid in level1_ids:
                    m = ctx.guild.get_member(int(uid))
                    if m: await target.set_permissions(m, view_channel=True, send_messages=True)

                status_msg = f"🔒 **Locked:** {target.name}"
                await hq_ch.send(status_msg)
                await crisis_ch.send(status_msg)
                await asyncio.sleep(0.7) 
            except: continue

        await crisis_ch.send("✅ **Protocol Finalized.** All public sectors secured.")
        await hq_ch.send("✅ **LOCKDOWN COMPLETE.** Standing by for deactivation.")

    @commands.command(name="deactivate_panic_control_system")
    async def deactivate_panic(self, ctx):
        """Phase 3 & 4: Restoration and Handover."""
        if ctx.author.id != SUPREME_CREATOR_ID: return
        
        if not os.path.exists(SNAPSHOT_FILE):
            return await ctx.send("❌ **Restoration Aborted:** No snapshot file found. System cannot verify original state.")

        hq_ch = discord.utils.get(ctx.guild.text_channels, name="🔴-emergency-hq")
        crisis_ch = discord.utils.get(ctx.guild.text_channels, name="🆘-crisis-zone")
        
        if hq_ch: await hq_ch.send("🔓 **PHASE 3: RESTORATION STARTED.** Monitoring restoration process...")

        # --- PHASE 3: RESTORATION FROM DISK ---
        snapshot_data = dbm.load_json(SNAPSHOT_FILE)
        
        for target_id, perms in snapshot_data.items():
            target = ctx.guild.get_channel(int(target_id))
            if target:
                try:
                    # Clear manual Level 1 staff overrides
                    auth_db = dbm.load_json(dbm.AUTH_FILE)
                    level1_ids = auth_db.get(str(ctx.guild.id), {}).get("auth1", [])
                    for uid in level1_ids:
                        m = ctx.guild.get_member(int(uid))
                        if m: await target.set_permissions(m, overwrite=None)

                    # Reconstruct and apply original @everyone permissions
                    restore_ov = discord.PermissionOverwrite(**perms)
                    await target.set_permissions(ctx.guild.default_role, overwrite=restore_ov)
                    
                    status_msg = f"🔓 **Restored:** {target.name}"
                    if hq_ch: await hq_ch.send(status_msg)
                    if crisis_ch: await crisis_ch.send(status_msg)
                    
                    await asyncio.sleep(0.5)
                except: continue

        # --- PHASE 4: THE HANDOVER ---
        self.bot.panic_mode = False # RE-ARM LEVEL 2 STAFF
        
        if hq_ch: await hq_ch.delete()
        if crisis_ch: await crisis_ch.delete()

        # Securely remove the snapshot to prevent re-runs
        os.remove(SNAPSHOT_FILE)

        # Final announcement to the restored general channel
        general = discord.utils.get(ctx.guild.text_channels, name="general")
        target_notif = general if general else ctx.channel
        await target_notif.send("✨ **Emergency Crisis Control System Deactivated.** Server restored by Supreme Creator.")
        await ctx.send("✅ **System Reverted Successfully.** Flags and snapshots cleared.")

async def setup(bot):
    await bot.add_cog(Emergency(bot))