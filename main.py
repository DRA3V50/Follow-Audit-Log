import requests
import json
import os
from datetime import datetime

# --- CONFIGURATION ---
USERNAME = "DRA3V50"                       # Your GitHub username
FOLLOWERS_FILE = "followers.json"          # File storing last snapshot of followers
LOG_FILE = "log.json"                      # File storing history of changes
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
    """Fetch all accounts USERNAME is following, handling pagination"""
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
    """Load previous follower snapshot, return empty list if missing"""
    if not os.path.exists(FOLLOWERS_FILE):
        return []
    try:
        with open(FOLLOWERS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_json(filename, data):
    """Save JSON safely and flush to disk"""
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
        f.flush()
        os.fsync(f.fileno())

def log_changes(unfollowed, new_followers, follow_back):
    """Log all changes with timestamp to log.json"""
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "unfollowed": unfollowed,
        "new_followers": new_followers,
        "followed_back": follow_back
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
    """Automatically unfollow users"""
    for user in users:
        response = requests.delete(f"https://api.github.com/user/following/{user}", headers=HEADERS)
        if response.status_code == 204:
            print(f"Unfollowed {user} successfully.")
        else:
            print(f"Failed to unfollow {user}: {response.status_code}")

def auto_follow(users):
    """Automatically follow back users"""
    followed = []
    for user in users:
        response = requests.put(f"https://api.github.com/user/following/{user}", headers=HEADERS)
        if response.status_code == 204:
            print(f"Followed {user} successfully.")
            followed.append(user)
        else:
            print(f"Failed to follow {user}: {response.status_code}")
    return followed

# --- MAIN EXECUTION ---
def main():
    current_followers = get_followers()
    current_following = get_following()
    previous_followers = load_previous()

    # Users who unfollowed but you still follow
    unfollowed = [u for u in previous_followers if u not in current_followers and u in current_following]

    # New followers since last snapshot
    new_followers = [u for u in current_followers if u not in previous_followers]

    # Followers you haven't followed back yet
    missing_follow_back = [u for u in current_followers if u not in current_following]

    # Follow back users and capture who succeeded
    followed_back = auto_follow(missing_follow_back) if missing_follow_back else []

    # Unfollow users who unfollowed
    if unfollowed:
        auto_unfollow(unfollowed)

    # Log everything
    log_changes(unfollowed, new_followers, followed_back)

    # Update followers snapshot
    save_json(FOLLOWERS_FILE, current_followers)

if __name__ == "__main__":
    main()
