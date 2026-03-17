# 📝 Follow-Audit-Log

A lightweight script that tracks GitHub followers, logs changes, and automatically unfollows anyone who no longer follows you.

## Purpose
Automates follower management by recording who follows or unfollows you and taking action to unfollow anyone who has unfollowed you.

## How It Works
- Fetches current follower list from the GitHub API  
- Compares with previous snapshot  
- Logs changes (new followers / unfollowers) with timestamp  
- Automatically unfollows users who no longer follow you  

## Automation
Runs daily via GitHub Actions at 8 AM EST or manually via workflow_dispatch.

## Files
- `main.py` — core script  
- `followers.json` — latest snapshot  
- `log.json` — change history  

---

## ⚠️ Copyright Notice ⚠️
© 2026 DRA3V50. All rights reserved.  
This code is for demonstration and portfolio purposes only.  
Unauthorized copying, redistribution, or commercial use is prohibited.
