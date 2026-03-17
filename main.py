import requests
import json
import os
from datetime import datetime

# --- CONFIGURATION ---
USERNAME = "DRA3V50"                        # Your GitHub username
FOLLOWERS_FILE = "followers.json"           # Stores last snapshot of followers
LOG_FILE = "log.json"                        # Stores history of follower changes
GITHUB_TOKEN = os.environ.get("GH_FOLLOW_TOKEN")  # PAT from GitHub Secrets
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}  # Auth header

# --- FUNCTIONS ---
def get_followers():
    """Fetch all followers of USERNAME (paginated)"""
    followers = []
    page = 1
    per_page = 100
    while True:
        url = f"https://api.github.com/users/{USERNAME}/followers?per_page={per_page}&page={page}"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        batch = [user["login"] for user in response.json()]
        if not batch:
            break
        followers.extend(batch)
        page += 1
    return followers

def get_following():
    """Fetch all users you are currently following (paginated)"""
    following = []
    page = 1
    per_page = 100
    while True:
        url = f"https://api.github.com/user/following?per_page={per_page}&page={page}"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        batch = [user["login"] for user in response.json()]
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

def save_followers(followers):
    """Save current follower snapshot"""
    with open(FOLLOWERS_FILE, "w") as f:
        json.dump(followers, f, indent=2)

def log_changes(unfollowed, new_followers, followed_back):
    """Log changes with timestamps"""
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "unfollowed": unfollowed,
        "new_followers": new_followers,
        "followed_back": followed_back
    }

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    data.append(log_entry)
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def auto_unfollow(users):
    """Unfollow users who unfollowed you"""
    for user in users:
        response = requests.delete(f"https://api.github.com/user/following/{user}", headers=HEADERS)
        if response.status_code == 204:
            print(f"Unfollowed {user} successfully.")
        else:
            print(f"Failed to unfollow {user}: {response.status_code}")

def auto_follow(users):
    """Follow users who aren’t followed back"""
    for user in users:
        response = requests.put(f"https://api.github.com/user/following/{user}", headers=HEADERS)
        if response.status_code == 204:
            print(f"Followed {user} successfully.")
        else:
            print(f"Failed to follow {user}: {response.status_code}")

# --- MAIN EXECUTION ---
def main():
    current_followers = get_followers()       # Get current followers
    current_following = get_following()       # Get current following
    previous = load_previous()                # Load previous snapshot

    # Detect unfollowers (were following before, now missing)
    unfollowed = [user for user in previous if user not in current_followers and user in current_following]

    # Detect new followers
    new_followers = [user for user in current_followers if user not in previous]

    # Detect missing follow-backs
    missing_follow_back = [user for user in current_followers if user not in current_following]

    # Take actions
    if unfollowed or new_followers or missing_follow_back:
        log_changes(unfollowed, new_followers, missing_follow_back)
        if unfollowed:
            auto_unfollow(unfollowed)
        if missing_follow_back:
            auto_follow(missing_follow_back)
        print("Changes detected and processed.")
    else:
        print("No changes detected.")

    save_followers(current_followers)  # Update snapshot

if __name__ == "__main__":
    main()
