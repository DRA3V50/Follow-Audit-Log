import requests
import json
import os
from datetime import datetime

USERNAME = "DRA3V50"
FOLLOWERS_FILE = "followers.json"
LOG_FILE = "log.json"

def get_followers():
    url = f"https://api.github.com/users/{USERNAME}/followers"
    response = requests.get(url)
    response.raise_for_status()
    return [user["login"] for user in response.json()]

def load_previous():
    if not os.path.exists(FOLLOWERS_FILE):
        return []
    with open(FOLLOWERS_FILE, "r") as f:
        return json.load(f)

def save_followers(followers):
    with open(FOLLOWERS_FILE, "w") as f:
        json.dump(followers, f, indent=2)

def log_changes(unfollowed, new_followers):
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "unfollowed": unfollowed,
        "new_followers": new_followers
    }

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
    else:
        data = []

    data.append(log_entry)

    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def main():
    current = get_followers()
    previous = load_previous()

    unfollowed = list(set(previous) - set(current))
    new_followers = list(set(current) - set(previous))

    if unfollowed or new_followers:
        log_changes(unfollowed, new_followers)
        print("Changes detected.")
    else:
        print("No changes.")

    save_followers(current)

if __name__ == "__main__":
    main()
