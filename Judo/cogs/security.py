import discord
from discord.ext import commands
import os

class Security(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.auth_file = "authorized.txt"
        self.authorized_users = self.load_auth_users()

    def load_auth_users(self):
        """Reads user IDs from the text file into a set."""
        if not os.path.exists(self.auth_file):
            with open(self.auth_file, "w") as f: pass
            return set()
        with open(self.auth_file, "r") as f:
            return {int(line.strip()) for line in f if line.strip().isdigit()}

    def save_auth_users(self):
        """Writes current set of IDs back to the text file."""
        with open(self.auth_file, "w") as f:
            for user_id in self.authorized_users:
                f.write(f"{user_id}\n")

    def is_allowed(self, user_id):
        """Helper to check if a user is the owner or authorized."""
        return user_id == self.bot.owner_id or user_id in self.authorized_users

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return

        content = message.content.lower()

        if content.startswith("judo") or self.bot.user.mentioned_in(message):
            if not self.is_allowed(message.author.id):
                await message.channel.send(f"JUDO Couldn't obey U {message.author.mention}")
                return

            if message.author.id == self.bot.owner_id:
                # --- SHOW LIST COMMAND ---
                if "show" in content and "authorized list" in content:
                    # CHECK: If the list is empty
                    if not self.authorized_users:
                        await message.channel.send("📭 **No user yet added to the authorized list.**")
                        return
                    
                    user_entries = []
                    for idx, user_id in enumerate(self.authorized_users, 1):
                        user = self.bot.get_user(user_id)
                        tag = user.mention if user else "Unknown User"
                        user_entries.append(f"{idx}. {tag} | ID: `{user_id}`")
                    
                    list_output = "\n".join(user_entries)
                    await message.channel.send(
                        f"🥋 **Dojo Access Registry**\n"
                        f"Total Authorized Users: **{len(self.authorized_users)}**\n\n"
                        f"{list_output}"
                    )
                    return

                # --- CLEAR LIST ---
                if "clear" in content and "authorized list" in content:
                    self.authorized_users.clear()
                    self.save_auth_users()
                    await message.channel.send("🧹 **The Dojo has been swept.** The list is empty.")
                    return

                # --- BATCH ADD ---
                if "add" in content and "authorized list" in content:
                    if message.mentions:
                        added = [t.mention for t in message.mentions if t.id not in self.authorized_users]
                        for t in message.mentions: self.authorized_users.add(t.id)
                        self.save_auth_users()
                        await message.channel.send(f"✅ Added: {', '.join(added)}" if added else "No new users added.")
                    return

                # --- BATCH REMOVE ---
                elif "remove" in content and "authorized list" in content:
                    if message.mentions:
                        removed = [t.mention for t in message.mentions if t.id in self.authorized_users]
                        for t in message.mentions: self.authorized_users.discard(t.id)
                        self.save_auth_users()
                        await message.channel.send(f"🗑️ Removed: {', '.join(removed)}" if removed else "No users were in the list.")
                    return

        # Ensure other commands still work
        await self.bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(Security(bot))