import requests
import json
import os
from datetime import datetime

# --- CONFIGURATION ---
USERNAME = "DRA3V50"  # Your GitHub username
FOLLOWERS_FILE = "followers.json"
LOG_FILE = "log.json"
GITHUB_TOKEN = os.environ.get("GH_FOLLOW_TOKEN")  # PAT from GitHub Secrets

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

# --- FUNCTIONS ---
def get_followers():
    """Fetch all followers of USERNAME, handling pagination"""
    followers = []
    page = 1
    per_page = 100
    while True:
        url = f"https://api.github.com/users/{USERNAME}/followers?per_page={per_page}&page={page}"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        batch = [u["login"] for u in response.json()]
        if not batch:
            break
        followers.extend(batch)
        page += 1
    return followers

def get_following():
    """Fetch all users you are following"""
    following = []
    page = 1
    per_page = 100
    while True:
        url = f"https://api.github.com/user/following?per_page={per_page}&page={page}"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        batch = [u["login"] for u in response.json()]
        if not batch:
            break
        following.extend(batch)
        page += 1
    return following

def load_previous():
    """Load previous follower snapshot"""
    if not os.path.exists(FOLLOWERS_FILE):
        return []
    try:
        with open(FOLLOWERS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_json(filename, data):
    """Save JSON file with flush/fsync to ensure GitHub Actions detects changes"""
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
        f.flush()
        os.fsync(f.fileno())

def log_changes(unfollowed, new_followers, followed_back):
    """Log follower changes with timestamp to log.json"""
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "unfollowed": unfollowed,
        "new_followers": new_followers,
        "followed_back": followed_back
    }

    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []
    else:
        data = []

    data.append(log_entry)
    save_json(LOG_FILE, data)

def auto_unfollow(users):
    """Automatically unfollow users who unfollowed you"""
    for user in users:
        response = requests.delete(f"https://api.github.com/user/following/{user}", headers=HEADERS)
        if response.status_code == 204:
            print(f"Unfollowed {user} successfully.")
        else:
            print(f"Failed to unfollow {user}: {response.status_code}")

def auto_follow(users):
    """Automatically follow users who followed you but you don't follow yet"""
    for user in users:
        response = requests.put(f"https://api.github.com/user/following/{user}", headers=HEADERS)
        if response.status_code == 204:
            print(f"Followed {user} successfully.")
        else:
            print(f"Failed to follow {user}: {response.status_code}")

# --- MAIN EXECUTION ---
def main():
    current_followers = get_followers()
    current_following = get_following()
    previous_followers = load_previous()

    # Unfollow anyone who unfollowed you but you still follow
    unfollowed = [u for u in previous_followers if u not in current_followers and u in current_following]

    # Detect new followers since last snapshot
    new_followers = [u for u in current_followers if u not in previous_followers]

    # Detect missing follow-backs
    missing_follow_back = [u for u in current_followers if u not in current_following]

    # Log all changes
    log_changes(unfollowed, new_followers, missing_follow_back)

    # Take actions
    if unfollowed:
        auto_unfollow(unfollowed)
    if missing_follow_back:
        auto_follow(missing_follow_back)

    # Update followers snapshot
    save_json(FOLLOWERS_FILE, current_followers)

if __name__ == "__main__":
    main()
