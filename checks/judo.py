import discord
from discord.ext import commands, tasks
import itertools
from datetime import datetime, timedelta
from collections import deque, defaultdict
import os

# 1. Setup
intents = discord.Intents.default()
intents.message_content = True 
intents.members = True          

bot = commands.Bot(command_prefix="judo ", intents=intents, help_command=None)

# --- ASP FILE UTILITIES ---
# These ensure the files exist so the code doesn't crash
for file in ["asp1.txt", "asp2.txt"]:
    if not os.path.exists(file):
        open(file, "w").close()

def check_file(filename, user_id):
    """Checks if a user ID is inside a specific text file."""
    with open(filename, "r") as f:
        lines = f.read().splitlines()
        return str(user_id) in lines

def add_to_file(filename, user_id):
    """Adds a user ID to a text file."""
    if not check_file(filename, user_id):
        with open(filename, "a") as f:
            f.write(f"{user_id}\n")

def remove_from_file(filename, user_id):
    """Removes a user ID from a text file."""
    with open(filename, "r") as f:
        lines = f.read().splitlines()
    with open(filename, "w") as f:
        for line in lines:
            if line != str(user_id):
                f.write(f"{line}\n")

# --- MEMORY FOR SPAM DETECTION ---
user_messages = defaultdict(lambda: deque())

async def log_to_channel(guild, embed):
    channel = discord.utils.get(guild.text_channels, name="judo-logs")
    if channel:
        await channel.send(embed=embed)

# 2. Status Cycle
status_messages = itertools.cycle(["over the server", "ASP 3-Strike System", "Database Files"])

@tasks.loop(seconds=10)
async def change_status():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=next(status_messages)))

# 3. ASP Events
@bot.event
async def on_ready():
    print(f'--- {bot.user.name} PERMANENT ASP ONLINE ---')
    change_status.start()

@bot.event
async def on_message(message):
    if message.author.bot or message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
        return

    user_id = message.author.id
    now = datetime.utcnow()
    user_messages[user_id].append(now)

    # Clean old timestamps
    while user_messages[user_id] and (now - user_messages[user_id][0]).total_seconds() > 12:
        user_messages[user_id].popleft()

    # Spam Check Logic
    history = list(user_messages[user_id])
    if len(history) > 6 or len([t for t in history if (now - t).total_seconds() <= 6]) > 3:
        await handle_file_asp(message.author, message.guild)
        user_messages[user_id].clear()
    
    await bot.process_commands(message)

async def handle_file_asp(member, guild):
    uid = member.id
    
    # Strike Logic
    if check_file("asp2.txt", uid):
        # STRIKE 3: Already in file 2 -> Remove and 1 hour timeout
        remove_from_file("asp2.txt", uid)
        duration = 60
        strike_num = 3
    elif check_file("asp1.txt", uid):
        # STRIKE 2: Already in file 1 -> Move to file 2 and 10 min timeout
        remove_from_file("asp1.txt", uid)
        add_to_file("asp2.txt", uid)
        duration = 10
        strike_num = 2
    else:
        # STRIKE 1: Not in any file -> Add to file 1 and 2 min timeout
        add_to_file("asp1.txt", uid)
        duration = 2
        strike_num = 1

    until = timedelta(minutes=duration)
    
    try:
        await member.timeout(until, reason=f"ASP Strike {strike_num}")
        
        embed = discord.Embed(title="🚫 ASP Enforcement", color=discord.Color.dark_red())
        embed.add_field(name="User", value=member.mention)
        embed.add_field(name="Strike Level", value=f"Level {strike_num}")
        embed.add_field(name="Duration", value=f"{duration} Minutes")
        embed.set_footer(text=f"ID Recorded in ASP Files")
        await log_to_channel(guild, embed)
        
    except Exception as e:
        print(f"Error executing timeout: {e}")

# 4. Commands
@bot.command(name="send")
async def send_custom(ctx, *, content: str):
    if " at " in content:
        parts = content.rsplit(" at ", 1)
        msg, ch_tag = parts[0], parts[1]
        ch_id = "".join(filter(str.isdigit, ch_tag))
        target = bot.get_channel(int(ch_id))
        if target:
            await target.send(msg)
            await ctx.send("✅ Sent.", delete_after=2)

@bot.command()
async def clear_data(ctx, member: discord.Member):
    """Admin command to wipe a user from both ASP files."""
    remove_from_file("asp1.txt", member.id)
    remove_from_file("asp2.txt", member.id)
    await ctx.send(f"✅ Records cleared for {member.display_name}.")

# 5. Run
TOKEN = 'MTM5OTIzMDM2NjAzOTkzNzEwNA.GGgNCx.MBxMlrwJ9tohvhzsm_6U5UOLy-7F18ucTJLd68'
bot.run(TOKEN)