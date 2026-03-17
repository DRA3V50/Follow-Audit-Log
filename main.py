import requests
import json
import os
import time
from datetime import datetime, timezone

USERNAME = "DRA3V50"
FOLLOWERS_FILE = "followers.json"
LOG_FILE = "log.json"

PAT = os.environ.get("GH_FOLLOW_TOKEN")

GITHUB_API_HEADERS = {
    "Accept": "application/vnd.github+json"
}

if PAT:
    GITHUB_API_HEADERS["Authorization"] = f"Bearer {PAT}"
else:
    print("ERROR: GH_FOLLOW_TOKEN not found!")
    exit(1)

# --- Helper functions ---

def get_followers():
    followers = []
    page = 1
    per_page = 100
    while True:
        url = f"https://api.github.com/users/{USERNAME}/followers?per_page={per_page}&page={page}"
        r = requests.get(url, headers=GITHUB_API_HEADERS)
        if r.status_code != 200:
            print("Failed to fetch followers:", r.status_code, r.text)
            break
        batch = [u["login"] for u in r.json()]
        if not batch:
            break
        followers.extend(batch)
        page += 1
    return followers

def get_following():
    following = []
    page = 1
    per_page = 100
    while True:
        url = f"https://api.github.com/user/following?per_page={per_page}&page={page}"
        r = requests.get(url, headers=GITHUB_API_HEADERS)
        if r.status_code != 200:
            print("Failed to fetch following:", r.status_code, r.text)
            break
        batch = [u["login"] for u in r.json()]
        if not batch:
            break
        following.extend(batch)
        page += 1
    return following

def load_previous():
    if not os.path.exists(FOLLOWERS_FILE):
        return []
    try:
        with open(FOLLOWERS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
        f.flush()
        os.fsync(f.fileno())

def log_changes(unfollowed, new_followers, missing_follow_back):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "unfollowed": unfollowed,
        "new_followers": new_followers,
        "missing_follow_back": missing_follow_back
    }

    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            data = []
    else:
        data = []

    data.append(entry)
    save_json(LOG_FILE, data)

def auto_unfollow(users):
    for user in users:
        r = requests.delete(f"https://api.github.com/user/following/{user}", headers=GITHUB_API_HEADERS)
        print(f"Unfollowed {user}" if r.status_code == 204 else f"Failed {user}: {r.status_code} {r.text}")
        time.sleep(1)  # prevent rate limits

def auto_follow(users):
    for user in users:
        r = requests.put(f"https://api.github.com/user/following/{user}", headers=GITHUB_API_HEADERS)
        print(f"Followed {user}" if r.status_code == 204 else f"Failed {user}: {r.status_code} {r.text}")
        time.sleep(1)  # prevent rate limits

# --- Main workflow ---

def main():
    print("PAT loaded:", bool(PAT))

    current_followers = get_followers()
    current_following = get_following()
    previous_followers = load_previous()

    unfollowed = [u for u in previous_followers if u not in current_followers and u in current_following]
    new_followers = [u for u in current_followers if u not in previous_followers]
    missing_follow_back = [u for u in current_followers if u not in current_following]

    log_changes(unfollowed, new_followers, missing_follow_back)

    if unfollowed:
        auto_unfollow(unfollowed)

    if missing_follow_back:
        auto_follow(missing_follow_back)

    save_json(FOLLOWERS_FILE, current_followers)

if __name__ == "__main__":
    main()
