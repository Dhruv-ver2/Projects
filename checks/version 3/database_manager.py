import json
import os

DB_FILE = "judo_data.json"
AUTH_FILE = "authorize_list.json"

def load_json(filename):
    if not os.path.exists(filename):
        return {}
    with open(filename, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

# --- STRIKE FUNCTIONS ---
def get_strike_level(guild_id, user_id):
    db = load_json(DB_FILE)
    gid, uid = str(guild_id), str(user_id)
    if gid not in db: return 0
    if uid in db[gid].get("strike2", []): return 2
    if uid in db[gid].get("strike1", []): return 1
    return 0

def increment_strike(guild_id, user_id):
    db = load_json(DB_FILE)
    gid, uid = str(guild_id), str(user_id)
    if gid not in db: db[gid] = {"strike1": [], "strike2": []}
    current = get_strike_level(guild_id, user_id)
    if current == 0:
        db[gid]["strike1"].append(uid)
        new_level = 1
    elif current == 1:
        if uid in db[gid]["strike1"]: db[gid]["strike1"].remove(uid)
        db[gid]["strike2"].append(uid)
        new_level = 2
    else:
        if uid in db[gid]["strike2"]: db[gid]["strike2"].remove(uid)
        new_level = 3
    save_json(DB_FILE, db)
    return new_level

# --- AUTHORIZATION FUNCTIONS ---
def get_auth_level(guild_id, user_id):
    auth_db = load_json(AUTH_FILE)
    gid, uid = str(guild_id), str(user_id)
    if gid not in auth_db: return 0
    if uid in auth_db[gid].get("auth1", []): return 1
    if uid in auth_db[gid].get("auth2", []): return 2
    return 0

def set_auth_level(guild_id, user_id, level):
    auth_db = load_json(AUTH_FILE)
    gid, uid = str(guild_id), str(user_id)
    if gid not in auth_db: auth_db[gid] = {"auth1": [], "auth2": []}
    
    # Remove from all levels first to avoid duplicates
    if uid in auth_db[gid]["auth1"]: auth_db[gid]["auth1"].remove(uid)
    if uid in auth_db[gid]["auth2"]: auth_db[gid]["auth2"].remove(uid)
    
    if level == 1: auth_db[gid]["auth1"].append(uid)
    elif level == 2: auth_db[gid]["auth2"].append(uid)
    
    save_json(AUTH_FILE, auth_db)