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
        if ctx.author.id != SUPREME_CREATOR_ID:
            return await ctx.send("🚫 Only the Supreme Creator can trigger a Level 5 Lockdown.")

        if self.bot.panic_mode:
            return await ctx.send("⚠️ The system is already in Panic Mode.")

        self.bot.panic_mode = True
        self.bot.judo_stats["success"] += 1

        # 1. Immediate Announcement
        await ctx.send("🚨 **ATTENTION: Emergency Crisis Control System Activated.**\nServer is entering TOTAL BLACKOUT. Permissions and history are being revoked.")

        # 2. Setup HQ and Crisis Zone
        hq_overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            ctx.author: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }
        
        auth_db = dbm.load_json(dbm.AUTH_FILE)
        gid = str(ctx.guild.id)
        level1_ids = auth_db.get(gid, {}).get("auth1", [])
        for uid in level1_ids:
            m = ctx.guild.get_member(int(uid))
            if m: hq_overwrites[m] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        hq_ch = await ctx.guild.create_text_channel("🔴-emergency-hq", overwrites=hq_overwrites, position=0)
        
        crisis_overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }
        crisis_ch = await ctx.guild.create_text_channel("🆘-crisis-zone", overwrites=crisis_overwrites, position=1)

        await hq_ch.send(f"⚡ **PANIC SYSTEM INITIALIZED.**\nStarting TOTAL BLACKOUT (Disabling Threads & History)...")

        # 3. Enhanced Lockdown Loop
        for channel in ctx.guild.text_channels:
            if channel.id in [hq_ch.id, crisis_ch.id]: continue
            
            # Save original snapshot
            self.bot.panic_snapshot[channel.id] = channel.overwrites_for(ctx.guild.default_role)
            
            # SUPREME LOCKDOWN: Disables everything including Threads
            lockdown_overwrite = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=False,
                send_messages_in_threads=False, # FIX: Disables thread chatting
                create_public_threads=False,    # FIX: Removes "Create Thread" UI
                create_private_threads=False,   # FIX: Removes "Create Thread" UI
                read_message_history=False,     # Hides all previous messages
                add_reactions=False             # Prevents reaction spam during panic
            )
            
            try:
                await channel.set_permissions(ctx.guild.default_role, overwrite=lockdown_overwrite)
                await channel.send("🚨 **CRITICAL LOCKDOWN:** This channel is temporarily offline. History hidden.")
                await hq_ch.send(f"🔒 Total Blackout Applied: {channel.mention}")
                await asyncio.sleep(0.8) 
            except:
                await hq_ch.send(f"⚠️ Failed to lock: {channel.name}")

        await hq_ch.send("✅ **LOCKDOWN COMPLETE.** Server is now a Fortress.")

    @commands.command(name="deactivate_panic_control_system")
    async def deactivate_panic(self, ctx):
        if ctx.author.id != SUPREME_CREATOR_ID: return
        if not self.bot.panic_mode: return

        # 1. Restore Permissions
        hq_ch = discord.utils.get(ctx.guild.text_channels, name="🔴-emergency-hq")
        if hq_ch: await hq_ch.send("🔓 **DEACTIVATION INITIALIZED.** Restoring original state...")

        for ch_id, original_overwrite in self.bot.panic_snapshot.items():
            channel = self.bot.get_channel(ch_id)
            if channel:
                try:
                    await channel.set_permissions(ctx.guild.default_role, overwrite=original_overwrite)
                    await asyncio.sleep(0.5)
                except: continue

        # 2. Final Message SENT TO ORIGINAL CONTEXT
        # We try to send it to the channel where the command was typed
        try:
            await ctx.send("✨ **Emergency Crisis Control System Deactivated.** All channels restored.")
        except discord.errors.NotFound:
            # If the current channel was deleted/missing, we don't crash
            pass

        # 3. Cleanup
        crisis_ch = discord.utils.get(ctx.guild.text_channels, name="🆘-crisis-zone")
        if crisis_ch: await crisis_ch.delete()
        if hq_ch: await hq_ch.delete()

        self.bot.panic_mode = False
        self.bot.panic_snapshot = {}

async def setup(bot):
    await bot.add_cog(Emergency(bot))