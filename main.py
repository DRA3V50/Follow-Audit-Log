import requests
import json
import os
import time
from datetime import datetime, timezone

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
        r.raise_for_status()
        batch = [u["login"] for u in r.json()]
        if not batch:
            break
        followers.extend(batch)
        page += 1
    return followers

def get_following():
    following = []
    page = 1
    while True:
        url = f"https://api.github.com/user/following?per_page=100&page={page}"
        r = requests.get(url, headers=HEADERS)
        r.raise_for_status()
        batch = [u["login"] for u in r.json()]
        if not batch:
            break
        following.extend(batch)
        page += 1
    return following

def auto_follow(users):
    for user in users:
        r = requests.put(f"https://api.github.com/user/following/{user}", headers=HEADERS)
        print(f"Followed {user}" if r.status_code == 204 else f"Failed {user}: {r.status_code}")
        time.sleep(1)

def auto_unfollow(users):
    for user in users:
        r = requests.delete(f"https://api.github.com/user/following/{user}", headers=HEADERS)
        print(f"Unfollowed {user}" if r.status_code == 204 else f"Failed {user}: {r.status_code}")
        time.sleep(1)

def main():
    prev_followers = []
    if os.path.exists(FOLLOWERS_FILE):
        with open(FOLLOWERS_FILE, "r") as f:
            prev_followers = json.load(f)

    current_followers = get_followers()
    current_following = get_following()

    # New followers you are not following yet
    missing_follow_back = [u for u in current_followers if u not in current_following]

    # Users who unfollowed you but you are still following
    unfollowed = [u for u in prev_followers if u not in current_followers and u in current_following]

    if missing_follow_back:
        auto_follow(missing_follow_back)
    if unfollowed:
        auto_unfollow(unfollowed)

    # Update local JSON
    with open(FOLLOWERS_FILE, "w") as f:
        json.dump(current_followers, f, indent=2)

    # Update log.json
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "new_followers": [u for u in current_followers if u not in prev_followers],
        "unfollowed": unfollowed,
        "missing_follow_back": missing_follow_back
    }
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try:
                logs = json.load(f)
            except:
                logs = []
    logs.append(log_entry)
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

    print("Auto-follow/unfollow completed.")
    
if __name__ == "__main__":
    main()
