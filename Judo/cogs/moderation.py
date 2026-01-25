import discord
from discord.ext import commands
import asyncio
import os

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Load environment IDs
        self.welcome_channel_id = int(os.getenv('WELCOME_CHANNEL_ID', 0))
        self.auto_role_id = int(os.getenv('AUTO_ROLE_ID', 0))

    # --- AUTOMATED WELCOME & AUTO-ROLE ---
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Greets new members and automatically assigns the 'Student' role."""
        # 1. ASSIGN THE ROLE
        if self.auto_role_id != 0:
            role = member.guild.get_role(self.auto_role_id)
            if role:
                try:
                    await member.add_roles(role)
                    print(f"[{member.name}] Automatically assigned role: {role.name}")
                except Exception as e:
                    print(f"❌ Failed to assign auto-role: {e}")

        # 2. SEND WELCOME MESSAGE
        channel = self.bot.get_channel(self.welcome_channel_id)
        if channel:
            embed = discord.Embed(
                title="✨ A New Ninja Joins the Dojo!",
                description=f"Welcome to the server, {member.mention}! We are glad to have you here.",
                color=discord.Color.purple()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(name="Assigned Role", value=f"<@&{self.auto_role_id}>", inline=True)
            embed.add_field(name="Member Count", value=f"#{len(member.guild.members)}", inline=True)
            embed.set_footer(text="Read the rules and enjoy your stay!")
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return

        content = message.content.lower()

        if content.startswith("judo") or self.bot.user.mentioned_in(message):
            sec_cog = self.bot.get_cog('Security')
            if not sec_cog or not sec_cog.is_allowed(message.author.id):
                return 

            # --- SHOW ACTIVE INVITES ---
            if "show" in content and "invites" in content:
                invites = await message.guild.invites()
                if not invites:
                    await message.channel.send("No active invite links found.")
                    return
                invite_list = [f"{i+1}. **{v.code}** | Uses: `{v.uses}` | Creator: {v.inviter.name}" for i, v in enumerate(invites)]
                await message.channel.send("🔗 **Active Server Invites:**\n" + "\n".join(invite_list))
                return

            # --- GENERATE INVITE ---
            if "generate" in content and "invite" in content:
                try:
                    invite = await message.channel.create_invite(max_age=86400, unique=True)
                    await message.channel.send(f"✅ **Invite Link Generated:**\n{invite.url}")
                    log_cog = self.bot.get_cog('Logs')
                    if log_cog:
                        await log_cog.send_log_embed("🔗 Invite Created", discord.Color.gold(), {
                            "Channel": message.channel.mention, "Created By": message.author.mention, "Link": invite.url
                        })
                except Exception as e: await message.channel.send(f"❌ Error: {e}")
                return

            # --- FLEXIBLE KICK ---
            if "kick" in content:
                if not message.mentions:
                    await message.channel.send("Master, you must tag a user to kick!")
                    return
                target = message.mentions[0]
                member = message.guild.get_member(target.id)
                if not member or member.top_role >= message.guild.me.top_role:
                    await message.channel.send("❌ Action impossible (User not found or rank too high).")
                    return

                # Reason logic
                clean_content = message.content
                for m in message.mentions: clean_content = clean_content.replace(m.mention, "").replace(f"<@!{m.id}>", "").replace(f"<@{m.id}>", "")
                for word in ["judo kick", "judo", "kick"]: clean_content = clean_content.lower().replace(word, "")
                reason = clean_content.strip()

                if reason:
                    await self.execute_kick(message.channel, member, message.author, reason)
                else:
                    await message.channel.send(f"Are you really want to kick {target.mention}? What reason should I mention?")
                    def check(m): return m.author == message.author and m.channel == message.channel and m.content.lower().strip().startswith("yes,")
                    try:
                        resp = await self.bot.wait_for('message', check=check, timeout=30.0)
                        await self.execute_kick(message.channel, member, message.author, resp.content[4:].strip() or "No reason provided")
                    except asyncio.TimeoutError: await message.channel.send("⏳ Timeout.")
                return

            # --- DELETE WITH SNAPSHOT ---
            if "delete" in content and "from" in content:
                try:
                    words = content.split()
                    amount = next((int(w) for w in words if w.isdigit()), 0)
                    if message.channel_mentions:
                        target_chan = message.channel_mentions[0]
                        limit = amount + 1 if target_chan.id == message.channel.id else amount
                        history = [f"**{m.author.name}**: {m.content}" async for m in target_chan.history(limit=limit) if m.id != message.id]
                        snapshot = "\n".join(history[::-1])
                        deleted = await target_chan.purge(limit=limit)
                        log_cog = self.bot.get_cog('Logs')
                        if log_cog:
                            await log_cog.send_log_embed("🧹 Purge Snapshot", discord.Color.blue(), {
                                "Channel": target_chan.mention, "Purged By": message.author.mention, "Messages": snapshot or "Empty"
                            })
                        await target_chan.send(f"! Judo has PURGED {len(deleted)-1 if target_chan.id == message.channel.id else len(deleted)} messages")
                except Exception as e: print(f"Delete Error: {e}")

            # --- SEND RELAY ---
            elif "send" in content and "at" in content:
                send_idx = content.find("send") + 4
                at_idx = content.rfind("at")
                msg_to_send = message.content[send_idx:at_idx].strip()
                if message.channel_mentions:
                    await message.channel_mentions[0].send(msg_to_send)
                    await message.add_reaction('🥋')

        await self.bot.process_commands(message)

    async def execute_kick(self, channel, member, requester, reason):
        try:
            await member.kick(reason=f"{reason} (Requested by {requester.name})")
            await channel.send(f"🥋 **{member.display_name}** has been kicked for: *{reason}*")
            log_cog = self.bot.get_cog('Logs')
            if log_cog:
                await log_cog.send_log_embed("👤 User Kicked", discord.Color.orange(), {
                    "Target": f"{member.mention}", "Reason": reason, "Action By": requester.mention
                })
        except Exception as e: await channel.send(f"❌ Kick failed: {e}")

async def setup(bot):
    await bot.add_cog(Moderation(bot))