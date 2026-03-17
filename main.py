import requests              # For making HTTP requests to GitHub API
import json                  # For reading/writing JSON files
import os                    # For environment variables and file checks
from datetime import datetime  # For timestamping logs

# --- CONFIGURATION ---
USERNAME = "DRA3V50"                       # Your GitHub username
FOLLOWERS_FILE = "followers.json"          # File storing last snapshot of followers
LOG_FILE = "log.json"                      # File storing history of changes
GITHUB_TOKEN = os.environ.get("GH_FOLLOW_TOKEN")  # Read PAT from GitHub Secrets
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}  # Header for authenticated requests

# --- FUNCTIONS ---
def get_followers():
    """Fetch all followers of USERNAME, handling pagination"""
    followers = []
    page = 1
    per_page = 100  # GitHub max per page
    while True:
        url = f"https://api.github.com/users/{USERNAME}/followers?per_page={per_page}&page={page}"
        response = requests.get(url, headers=HEADERS)  # GET request to GitHub API
        response.raise_for_status()  # Raise error if request fails
        batch = [user["login"] for user in response.json()]  # Extract usernames
        if not batch:  # Stop if no more followers
            break
        followers.extend(batch)
        page += 1
    return followers

def load_previous():
    """Load previous follower snapshot from followers.json, return empty list if missing"""
    if not os.path.exists(FOLLOWERS_FILE):
        return []
    try:
        with open(FOLLOWERS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_followers(followers):
    """Save current followers to followers.json"""
    with open(FOLLOWERS_FILE, "w") as f:
        json.dump(followers, f, indent=2)

def log_changes(unfollowed, new_followers):
    """Log follower changes with timestamp to log.json"""
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "unfollowed": unfollowed,
        "new_followers": new_followers
    }

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    data.append(log_entry)  # Append new log entry

    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def auto_unfollow(users):
    """Automatically unfollow users who unfollowed you"""
    for user in users:
        response = requests.delete(
            f"https://api.github.com/user/following/{user}",
            headers=HEADERS
        )
        if response.status_code == 204:  # 204 = success
            print(f"Unfollowed {user} successfully.")
        else:
            print(f"Failed to unfollow {user}: {response.status_code}")

def auto_follow(users):
    """Automatically follow new followers"""
    for user in users:
        response = requests.put(
            f"https://api.github.com/user/following/{user}",
            headers=HEADERS
        )
        if response.status_code == 204:  # 204 = success
            print(f"Followed {user} successfully.")
        else:
            print(f"Failed to follow {user}: {response.status_code}")

# --- MAIN EXECUTION ---
def main():
    current = get_followers()       # Fetch current followers
    previous = load_previous()      # Load previous snapshot

    # Determine who unfollowed and who is new
    unfollowed = list(set(previous) - set(current))
    new_followers = list(set(current) - set(previous))

    # If there are changes, log them and take actions
    if unfollowed or new_followers:
        log_changes(unfollowed, new_followers)
        if unfollowed:
            auto_unfollow(unfollowed)      # Unfollow people who unfollowed you
        if new_followers:
            auto_follow(new_followers)     # Follow back new followers
        print("Changes detected and processed.")
    else:
        print("No changes detected.")

    save_followers(current)             # Update snapshot file

if __name__ == "__main__":
    main()
