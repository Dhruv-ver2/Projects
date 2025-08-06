from discord.ext import commands
import discord
import re
import asyncio


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # -----------------------------------
    # Utility: count and delete messages
    # -----------------------------------
    async def count_messages(self, target_channel: discord.TextChannel, limit: int = None):
        count = 0
        async for _ in target_channel.history(limit=limit):
            count += 1
        return count

    async def delete_messages(self, target_channel: discord.TextChannel, skip_ids: set, limit: int = None):
        """Delete messages, but skip ones in skip_ids."""
        msgs = []
        async for msg in target_channel.history(limit=limit):
            if msg.id in skip_ids:
                continue
            msgs.append(msg)

        count = 0
        for msg in msgs:
            try:
                await msg.delete()
                count += 1
                await asyncio.sleep(0.2)
            except Exception:
                pass
        return count

    async def purge_sequence(self, message: discord.Message, target_channel, limit=None):
        """
        Purge messages and delete everything including the command message,
        leaving only one final confirmation message.
        """
        ctx_channel = message.channel
        command_message_id = message.id

        # Count messages
        msg_count = await self.count_messages(target_channel, limit)

        # Acknowledge
        ack = await ctx_channel.send(f"Purging {msg_count} messages from {target_channel.mention}...")

        # Delete all except the confirmation message
        skip_ids = {ack.id}
        deleted_count = await self.delete_messages(target_channel, skip_ids, limit)

        # Delete original command if in same channel
        try:
            if target_channel.id == ctx_channel.id:
                original_msg = await target_channel.fetch_message(command_message_id)
                await original_msg.delete()
        except:
            pass

        # Send final confirmation
        await ctx_channel.send(f"✅ Purge Complete! {deleted_count} messages deleted from {target_channel.mention}")

    # -----------------------------------
    # Natural language only
    # -----------------------------------
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        content_lower = message.content.lower()
        bot_mention = f"<@{self.bot.user.id}>"
        bot_mention_nick = f"<@!{self.bot.user.id}>"

        called_to_bot = (
            content_lower.startswith("judo")
            or content_lower.startswith("hey judo")
            or bot_mention in content_lower
            or bot_mention_nick in content_lower
        )
        if not called_to_bot:
            return

        # --- Natural purge ---
        if "delete" in content_lower and "messages from" in content_lower:
            if not message.author.guild_permissions.administrator:
                await message.channel.send("❌ You don’t have permission.")
                return
            if not message.channel_mentions:
                await message.channel.send("❌ Please mention a channel.")
                return

            target_channel = message.channel_mentions[0]
            match = re.search(r"delete\s+(\d+)\s+messages\s+from", content_lower)
            amount = int(match.group(1)) if match else None

            await self.purge_sequence(message, target_channel, limit=amount)
            return

        # --- Natural language kick with DEBUG ---
        if "kick" in content_lower:
            if not message.author.guild_permissions.kick_members:
                await message.channel.send("❌ You don’t have permission to kick members.")
                return
            if not message.mentions:
                await message.channel.send("❌ Please mention a user to kick.")
                return

            member_to_kick = message.mentions[0]

            # Debug info about roles and permissions
            debug_info = (
                f"Bot top role: {message.guild.me.top_role}\n"
                f"Target top role: {member_to_kick.top_role}\n"
                f"Author top role: {message.author.top_role}\n"
                f"Bot has kick_members: {message.guild.me.guild_permissions.kick_members}\n"
                f"Bot has administrator: {message.guild.me.guild_permissions.administrator}"
            )
            await message.channel.send(f"DEBUG INFO:\n```{debug_info}```")

            # Extract reason (case-sensitive)
            full_text = message.content
            after_kick_text = full_text.split("kick", 1)[1].strip()
            mention_text = f"<@{member_to_kick.id}>"
            reason = after_kick_text.replace(mention_text, "").strip() or "No reason provided"

            # Can't kick yourself
            if member_to_kick == message.author:
                await message.channel.send("❌ You cannot kick yourself.")
                return
            # Bot's role must be higher than target's
            if member_to_kick.top_role >= message.guild.me.top_role:
                await message.channel.send("❌ I cannot kick this user because their top role is higher or equal to my role.")
                return

            # Ask for confirmation
            confirm_msg = await message.channel.send(
                f"⚠️ {message.author.mention}, confirm kicking {member_to_kick.mention}?\n"
                f"Reason: {reason}\nReact ✅ to confirm, ❌ to cancel."
            )
            await confirm_msg.add_reaction("✅")
            await confirm_msg.add_reaction("❌")

            def check(reaction, user):
                return (
                    user == message.author
                    and reaction.message.id == confirm_msg.id
                    and str(reaction.emoji) in ["✅", "❌"]
                )

            try:
                reaction, _ = await self.bot.wait_for("reaction_add", timeout=15.0, check=check)
            except asyncio.TimeoutError:
                await confirm_msg.edit(content="⌛ Kick cancelled (no response).")
                await confirm_msg.clear_reactions()
                return

            if str(reaction.emoji) == "❌":
                await confirm_msg.edit(content="❌ Kick cancelled.")
                await confirm_msg.clear_reactions()
                return

            # Kick if confirmed
            try:
                await member_to_kick.kick(reason=reason)
                await confirm_msg.edit(content=f"✅ {member_to_kick.mention} has been kicked. Reason: {reason}")
            except Exception as e:
                await confirm_msg.edit(content=f"❌ Failed to kick {member_to_kick.mention}. Error: {e}")
            await confirm_msg.clear_reactions()
            return


# Setup function for bot
async def setup(bot):
    await bot.add_cog(Moderation(bot))
