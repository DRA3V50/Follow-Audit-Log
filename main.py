import requests
import json
import os
from datetime import datetime, timezone
import time

USERNAME = "DRA3V50"
FOLLOWERS_FILE = "followers.json"
LOG_FILE = "log.json"

PAT = os.environ.get("FOLLOW_LOG")
if not PAT:
    print("ERROR: FOLLOW_LOG not found!")
    exit(1)

HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {PAT}"
}

def get_followers():
    followers = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{USERNAME}/followers?per_page=100&page={page}"
        r = requests.get(url, headers=HEADERS)
        if r.status_code != 200:
            print("Failed to fetch followers:", r.status_code, r.text)
            break
        batch = [u["login"] for u in r.json()]
        if not batch:
            break
        followers.extend(batch)
        page += 1
    return followers

def load_previous():
    if not os.path.exists(FOLLOWERS_FILE):
        return []
    try:
        with open(FOLLOWERS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)
        f.flush()
        os.fsync(f.fileno())

def log_changes(prev, current):
    unfollowed = [u for u in prev if u not in current]
    new_followers = [u for u in current if u not in prev]
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "unfollowed": unfollowed,
        "new_followers": new_followers
    }
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                logs = json.load(f)
        except:
            logs = []
    else:
        logs = []
    logs.append(entry)
    save_json(LOG_FILE, logs)
    return unfollowed, new_followers

def main():
    prev_followers = load_previous()
    current_followers = get_followers()
    log_changes(prev_followers, current_followers)
    save_json(FOLLOWERS_FILE, current_followers)
    print("Follower tracking complete!")

if __name__ == "__main__":
    main()
