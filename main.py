import requests              # For making API requests to GitHub
import json                  # For reading/writing JSON files
import os                    # For checking if files exist
from datetime import datetime  # For timestamps

USERNAME = "YOUR_GITHUB_USERNAME"  # Your GitHub username
FOLLOWERS_FILE = "followers.json"  # Stores latest follower snapshot
LOG_FILE = "log.json"              # Stores change history

def get_followers():
    url = f"https://api.github.com/users/{USERNAME}/followers"  # GitHub API endpoint
    response = requests.get(url)  # Send GET request
    response.raise_for_status()   # Raise error if request fails
    return [user["login"] for user in response.json()]  # Extract usernames

def load_previous():
    if not os.path.exists(FOLLOWERS_FILE):  # If no previous file
        return []                           # Return empty list (first run)
    with open(FOLLOWERS_FILE, "r") as f:    # Open saved follower file
        return json.load(f)                 # Load JSON data

def save_followers(followers):
    with open(FOLLOWERS_FILE, "w") as f:    # Open file for writing
        json.dump(followers, f, indent=2)   # Save current followers

def log_changes(unfollowed, new_followers):
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Current time
        "unfollowed": unfollowed,        # List of users who unfollowed
        "new_followers": new_followers   # List of new followers
    }

    if os.path.exists(LOG_FILE):         # If log file exists
        with open(LOG_FILE, "r") as f:
            data = json.load(f)          # Load existing logs
    else:
        data = []                        # Start new log list

    data.append(log_entry)               # Add new log entry

    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)     # Save updated log

def main():
    current = get_followers()            # Get current followers from API
    previous = load_previous()           # Load previous snapshot

    unfollowed = list(set(previous) - set(current))      # Users who unfollowed
    new_followers = list(set(current) - set(previous))   # Users who followed

    if unfollowed or new_followers:      # If any changes detected
        log_changes(unfollowed, new_followers)  # Save to log
        print("Changes detected.")
    else:
        print("No changes.")             # No differences found

    save_followers(current)              # Update stored snapshot

if __name__ == "__main__":
    main()                               # Run script
