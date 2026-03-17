import requests              # For making HTTP requests to GitHub API
import json                  # For reading/writing JSON files
import os                    # For checking if files exist / environment variables
from datetime import datetime  # For timestamping logs

# --- CONFIGURATION ---
USERNAME = "YOUR_GITHUB_USERNAME"          # Replace with your GitHub username
FOLLOWERS_FILE = "followers.json"          # Stores the current follower snapshot
LOG_FILE = "log.json"                      # Stores history of follower changes
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")  # Read token from GitHub Secrets
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}  # Header for authenticated API requests

# --- FUNCTIONS ---
def get_followers():
    """Fetch current followers from GitHub API"""
    url = f"https://api.github.com/users/{USERNAME}/followers"
    response = requests.get(url)  # GET request
    response.raise_for_status()   # Raise error if request fails
    return [user["login"] for user in response.json()]  # Extract usernames

def load_previous():
    """Load previously saved follower list"""
    if not os.path.exists(FOLLOWERS_FILE):
        return []  # First run: empty list
    with open(FOLLOWERS_FILE, "r") as f:
        return json.load(f)

def save_followers(followers):
    """Save current followers to file"""
    with open(FOLLOWERS_FILE, "w") as f:
        json.dump(followers, f, indent=2)

def log_changes(unfollowed, new_followers):
    """Log any follower changes with timestamps"""
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

def auto_unfollow(users):
    """Automatically unfollow users who unfollowed you"""
    for user in users:
        response = requests.delete(
            f"https://api.github.com/user/following/{user}",
            headers=HEADERS
        )
        if response.status_code == 204:
            print(f"Unfollowed {user} successfully.")
        else:
            print(f"Failed to unfollow {user}: {response.status_code}")

# --- MAIN EXECUTION ---
def main():
    current = get_followers()       # Fetch current followers
    previous = load_previous()      # Load previous snapshot

    unfollowed = list(set(previous) - set(current))      # Users who unfollowed
    new_followers = list(set(current) - set(previous))   # Users who newly followed

    if unfollowed or new_followers:
        log_changes(unfollowed, new_followers)          # Log changes
        if unfollowed:
            auto_unfollow(unfollowed)                  # Automatically unfollow them
        print("Changes detected and processed.")
    else:
        print("No changes.")

    save_followers(current)                             # Update snapshot

if __name__ == "__main__":
    main()                                               # Run script
