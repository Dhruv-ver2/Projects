import discord
from discord.ext import commands
import os

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Retrieve IDs from .env
        self.welcome_channel_id = int(os.getenv('WELCOME_CHANNEL_ID'))
        self.student_role_id = int(os.getenv('STUDENT_ROLE_ID'))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Triggers the Auto-Role and Welcome Embed sequence."""
        
        # 1. AUTO-ROLE CEREMONY
        role = member.guild.get_role(self.student_role_id)
        if role:
            try:
                await member.add_roles(role)
            except discord.Forbidden:
                print(f"❌ Error: Judo's role is too low to assign the '{role.name}' role.")
        
        # 2. SUPREME WELCOME EMBED
        channel = self.bot.get_channel(self.welcome_channel_id)
        if not channel:
            return

        # Ninja ID is the member's position in the server (Member Count)
        ninja_id = member.guild.member_count

        embed = discord.Embed(
            title="🥋 A New Ninja Arrives!",
            description=f"Welcome to the Dojo, {member.mention}!",
            color=discord.Color.purple()
        )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        
        embed.add_field(
            name="Ceremony Status", 
            value=f"✅ You have been granted the <@&{self.student_role_id}> role.", 
            inline=False
        )
        
        embed.add_field(
            name="Ninja Identity", 
            value=f"You are Ninja **#{ninja_id}**", 
            inline=True
        )
        
        embed.set_footer(text="Respect the Dojo. Obey the Master.")
        
        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Events(bot))