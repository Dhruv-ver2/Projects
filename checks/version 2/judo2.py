import discord
from discord.ext import commands, tasks
import itertools
from datetime import datetime, timedelta
from collections import deque, defaultdict
import json
import os

# 1. Setup
intents = discord.Intents.default()
intents.message_content = True 
intents.members = True          

bot = commands.Bot(command_prefix="judo ", intents=intents, help_command=None)

# --- JSON ASP DATABASE UTILITIES ---
DB_FILE = "asp_data.json"

def load_db():
    """Loads the JSON database. Creates it if it doesn't exist."""
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_db(data):
    """Saves the current state to the JSON file."""
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_user_strike_level(guild_id, user_id):
    """Checks which 'file' (list) the user is in for a specific server."""
    db = load_db()
    guild_id, user_id = str(guild_id), str(user_id)
    
    if guild_id not in db:
        return 0 # No strikes in this server
    
    if user_id in db[guild_id].get("asp2", []):
        return 2 # User is in the 'asp2' list for this server
    if user_id in db[guild_id].get("asp1", []):
        return 1 # User is in the 'asp1' list for this server
    return 0

def update_user_strike(guild_id, user_id, action):
    """Handles adding/removing users from server-specific strike lists."""
    db = load_db()
    gid, uid = str(guild_id), str(user_id)
    
    if gid not in db:
        db[gid] = {"asp1": [], "asp2": []}
    
    # Logic: Move user through levels
    if action == "to_asp1":
        if uid not in db[gid]["asp1"]:
            db[gid]["asp1"].append(uid)
    elif action == "to_asp2":
        if uid in db[gid]["asp1"]:
            db[gid]["asp1"].remove(uid)
        if uid not in db[gid]["asp2"]:
            db[gid]["asp2"].append(uid)
    elif action == "clear_asp2":
        if uid in db[gid]["asp2"]:
            db[gid]["asp2"].remove(uid)
            
    save_db(db)

# --- MEMORY FOR LIVE SPAM DETECTION ---
user_messages = defaultdict(lambda: deque())

async def log_to_channel(guild, embed):
    channel = discord.utils.get(guild.text_channels, name="judo-logs")
    if channel:
        await channel.send(embed=embed)

# 2. Status Cycle
status_messages = itertools.cycle(["over the server", "ASP Server-Specific", "Supreme Mode"])

@tasks.loop(seconds=10)
async def change_status():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=next(status_messages)))

# 3. ASP Events
@bot.event
async def on_ready():
    print(f'--- {bot.user.name} BUG-FIXED ASP ONLINE ---')
    change_status.start()

@bot.event
async def on_message(message):
    if message.author.bot or message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
        return

    user_id = message.author.id
    now = datetime.utcnow()
    user_messages[user_id].append(now)

    while user_messages[user_id] and (now - user_messages[user_id][0]).total_seconds() > 12:
        user_messages[user_id].popleft()

    history = list(user_messages[user_id])
    if len(history) > 6 or len([t for t in history if (now - t).total_seconds() <= 6]) > 3:
        await handle_server_specific_asp(message.author, message.guild)
        user_messages[user_id].clear()
    
    await bot.process_commands(message)

async def handle_server_specific_asp(member, guild):
    current_level = get_user_strike_level(guild.id, member.id)
    
    if current_level == 2:
        # STRIKE 3: Found in asp2 -> Reset (remove from all) and 1 hour timeout
        update_user_strike(guild.id, member.id, "clear_asp2")
        duration, strike_num = 60, 3
    elif current_level == 1:
        # STRIKE 2: Found in asp1 -> Move to asp2 and 10 min timeout
        update_user_strike(guild.id, member.id, "to_asp2")
        duration, strike_num = 10, 2
    else:
        # STRIKE 1: Not found in this server's data -> Add to asp1 and 2 min timeout
        update_user_strike(guild.id, member.id, "to_asp1")
        duration, strike_num = 2, 1

    until = timedelta(minutes=duration)
    
    try:
        await member.timeout(until, reason=f"ASP Strike {strike_num}")
        embed = discord.Embed(title="🚫 ASP Enforcement", color=discord.Color.dark_red())
        embed.add_field(name="User", value=member.mention)
        embed.add_field(name="Server Strike", value=f"Level {strike_num}")
        embed.add_field(name="Duration", value=f"{duration} Minutes")
        await log_to_channel(guild, embed)
    except Exception as e:
        print(f"Error: {e}")

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
    """Clears a user's strikes for THIS server only."""
    db = load_db()
    gid = str(ctx.guild.id)
    uid = str(member.id)
    if gid in db:
        if uid in db[gid]["asp1"]: db[gid]["asp1"].remove(uid)
        if uid in db[gid]["asp2"]: db[gid]["asp2"].remove(uid)
        save_db(db)
    await ctx.send(f"✅ Records cleared for {member.display_name} in this server.")

# 5. Run
TOKEN = 'MTM5OTIzMDM2NjAzOTkzNzEwNA.GGgNCx.MBxMlrwJ9tohvhzsm_6U5UOLy-7F18ucTJLd68'
bot.run(TOKEN)