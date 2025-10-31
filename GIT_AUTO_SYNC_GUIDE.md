# Git Auto-Sync Setup Guide

**Purpose**: Automatically sync AYA repository to GitHub  
**For**: Arthur  
**Date**: October 29, 2025  

---

## Quick Setup

### Option 1: Automated Background Sync (Recommended)

**Runs every 15 minutes automatically**:

```bash
cd /Users/arthurdell/AYA/scripts
chmod +x install_git_autosync.sh
./install_git_autosync.sh
```

That's it! The service is now running.

---

## How It Works

### Automatic Sync Service

The launchd service (`com.aya.git.autosync`) will:

1. **Run every 15 minutes**
2. **Check for changes** in `/Users/arthurdell/AYA/`
3. **Auto-commit** with descriptive message
4. **Push to GitHub** automatically
5. **Log everything** to `/Users/arthurdell/AYA/logs/git_sync.log`

### What Gets Synced

- Modified files
- New files
- Deleted files
- Everything tracked by git

### Safety Features

- **Lock file** prevents concurrent runs
- **Fetch first** to check for remote changes
- **Warns** if local is behind remote
- **Logs rotation** when logs get too large (>10MB)
- **Dry-run mode** for testing

---

## Manual Commands

### Test Without Committing

```bash
/Users/arthurdell/AYA/scripts/auto_git_sync.sh --dry-run
```

### Run Sync Manually

```bash
/Users/arthurdell/AYA/scripts/auto_git_sync.sh
```

### Force Push (Use Carefully!)

```bash
/Users/arthurdell/AYA/scripts/auto_git_sync.sh --force
```

---

## Service Management

### Check Status

```bash
launchctl list | grep com.aya.git.autosync
```

### View Logs

```bash
# Main sync log
tail -f /Users/arthurdell/AYA/logs/git_sync.log

# Launchd stdout
tail -f /Users/arthurdell/AYA/logs/git_autosync.out.log

# Launchd errors
tail -f /Users/arthurdell/AYA/logs/git_autosync.err.log
```

### Stop Service

```bash
launchctl unload ~/Library/LaunchAgents/com.aya.git.autosync.plist
```

### Restart Service

```bash
launchctl unload ~/Library/LaunchAgents/com.aya.git.autosync.plist
launchctl load ~/Library/LaunchAgents/com.aya.git.autosync.plist
```

### Permanently Remove

```bash
launchctl unload ~/Library/LaunchAgents/com.aya.git.autosync.plist
rm ~/Library/LaunchAgents/com.aya.git.autosync.plist
```

---

## Alternative Options

### Option 2: Git Hooks (Post-Commit Auto-Push)

**Pushes immediately after every commit**:

```bash
cat > /Users/arthurdell/AYA/.git/hooks/post-commit << 'EOF'
#!/bin/bash
# Auto-push to GitHub after commit

echo "Auto-pushing to GitHub..."
git push origin main || echo "Push failed - manual intervention needed"
EOF

chmod +x /Users/arthurdell/AYA/.git/hooks/post-commit
```

**Pros**: Immediate sync after commits  
**Cons**: Only runs when YOU commit (not for auto-changes)

### Option 3: Cron Job (If You Prefer Cron)

```bash
# Add to crontab
crontab -e

# Add this line (runs every 15 minutes):
*/15 * * * * /Users/arthurdell/AYA/scripts/auto_git_sync.sh >> /Users/arthurdell/AYA/logs/git_sync_cron.log 2>&1
```

**Pros**: Simple, standard Unix tool  
**Cons**: Launchd is more Mac-native, better for laptops (handles sleep)

### Option 4: Watch Script (Real-Time)

**Not recommended** - uses more resources, but syncs immediately on file changes.

---

## Configuration

### Change Sync Interval

Edit `/Users/arthurdell/AYA/scripts/com.aya.git.autosync.plist`:

```xml
<!-- Change this value (in seconds) -->
<key>StartInterval</key>
<integer>900</integer>  <!-- 900 = 15 minutes -->
```

Common values:
- 5 minutes: `300`
- 10 minutes: `600`
- 15 minutes: `900` (default)
- 30 minutes: `1800`
- 1 hour: `3600`

Then restart the service.

### Exclude Files from Auto-Sync

Add to `.gitignore`:

```bash
echo "temp_files/" >> /Users/arthurdell/AYA/.gitignore
echo "*.tmp" >> /Users/arthurdell/AYA/.gitignore
```

---

## Monitoring

### Check Last Sync

```bash
tail -20 /Users/arthurdell/AYA/logs/git_sync.log
```

### Watch for Syncs in Real-Time

```bash
tail -f /Users/arthurdell/AYA/logs/git_sync.log
```

### See What Was Last Pushed

```bash
cd /Users/arthurdell/AYA
git log --oneline -5
```

---

## Troubleshooting

### Sync Not Running

1. Check if service is loaded:
   ```bash
   launchctl list | grep com.aya.git.autosync
   ```

2. Check logs for errors:
   ```bash
   cat /Users/arthurdell/AYA/logs/git_autosync.err.log
   ```

3. Test manually:
   ```bash
   /Users/arthurdell/AYA/scripts/auto_git_sync.sh --dry-run
   ```

### "Failed to push to GitHub"

**Cause**: Remote has changes you don't have locally

**Fix**:
```bash
cd /Users/arthurdell/AYA
git pull --rebase origin main
# Resolve any conflicts
git push origin main
```

### "Another sync is running"

**Cause**: Lock file exists from previous run

**Fix**:
```bash
rm -f /tmp/aya_git_sync.lock
```

### SSH Key Issues

**Symptom**: "Permission denied (publickey)"

**Fix**: Ensure SSH key is added to ssh-agent:
```bash
ssh-add -K ~/.ssh/id_rsa  # or your key file
ssh -T git@github.com  # Test GitHub connection
```

---

## Current Git Status

### Check What's Uncommitted

```bash
cd /Users/arthurdell/AYA
git status
```

### See What Will Be Synced Next

```bash
/Users/arthurdell/AYA/scripts/auto_git_sync.sh --dry-run
```

---

## Best Practices

### Do's ✅

- Let auto-sync handle routine updates
- Monitor logs occasionally
- Keep `.gitignore` updated
- Test with `--dry-run` before changes

### Don'ts ❌

- Don't commit secrets or passwords
- Don't force-push without reason
- Don't disable the service without reason
- Don't manually edit launchd plist while service is running

---

## Security Notes

### What's Safe ✅

- Auto-sync uses your existing SSH key
- Runs as your user account
- Only pushes to configured remote
- Logs are local only

### What to Watch ⚠️

- **Secrets in code**: Add to `.gitignore`
- **Large files**: May slow down sync (use Git LFS if needed)
- **Merge conflicts**: Auto-sync will fail, requires manual fix

---

## Examples

### Typical Log Entry

```
[2025-10-29 14:30:00] ========== Git Sync Started ==========
[2025-10-29 14:30:00] Fetching from remote...
[2025-10-29 14:30:01] Found uncommitted changes
[2025-10-29 14:30:01] Staging changes...
[2025-10-29 14:30:01] Changes to commit:
 M CLAUDE.md
?? NEW_FILE.md
[2025-10-29 14:30:01] Committing changes: Auto-sync: 2 files changed at 2025-10-29 14:30:01
[2025-10-29 14:30:02] Pushing to GitHub...
[2025-10-29 14:30:03] SUCCESS: Changes pushed to GitHub
[2025-10-29 14:30:03] Repository is in sync with GitHub
[2025-10-29 14:30:03] ========== Git Sync Completed ==========
```

---

## FAQ

**Q: Will this commit my work-in-progress code?**  
A: Yes - it commits everything. Use `.gitignore` for WIP files or disable the service while working.

**Q: What if I'm offline?**  
A: Sync will fail gracefully, retry on next interval when online.

**Q: Can I run this on BETA too?**  
A: Yes! Copy the scripts and plist, update paths, install same way.

**Q: Will it handle merge conflicts?**  
A: No - you'll need to resolve conflicts manually. Service will fail and log the error.

**Q: Can I change the commit messages?**  
A: Edit the script at line 90 to customize commit message format.

---

## Summary

**Recommended Setup**: Option 1 (Launchd service, 15-minute interval)

**Installation**:
```bash
cd /Users/arthurdell/AYA/scripts
./install_git_autosync.sh
```

**Monitor**:
```bash
tail -f /Users/arthurdell/AYA/logs/git_sync.log
```

**Done!** Your repository will now automatically stay synced with GitHub.

---

**Created**: October 29, 2025  
**For**: Arthur  
**Files**: auto_git_sync.sh, com.aya.git.autosync.plist, install_git_autosync.sh

