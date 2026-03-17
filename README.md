# 📝 Follow-Audit-Log

 A lightweight script that tracks changes in GitHub followers by comparing snapshots over time and logging differences with timestamps.

## Purpose
This project automates the process of monitoring follower changes on GitHub. Instead of manually checking, it records who followed or unfollowed between runs and stores that history in a structured format.

## How It Works
- Fetches the current follower list using the GitHub API  
- Compares it with the previously saved snapshot  
- Identifies:
  - New followers  
  - Unfollowers  
- Saves the updated list and logs any changes with timestamps  

## Files
- `main.py` — main script  
- `followers.json` — current follower snapshot  
- `log.json` — change history  

## Automation
The script runs automatically once per day using GitHub Actions. It can also be triggered manually from the Actions tab.

## Notes
- The first run creates the initial baseline  
- Changes are only detected on subsequent runs  
- No credentials are required for public follower data  
