---
description: Sync with GitHub repository (pull latest or push changes)
allowed-tools: Bash(git:*)
---

# Git Sync Command

Synchronize local repository with GitHub remote.

## Determine Sync Direction

Ask the user or infer from context:
- **Start of shift**: Pull latest changes
- **End of shift**: Push local changes

## Option 1: Pull (Start of Shift)

```bash
# Fetch and show status
git fetch origin

# Check for upstream changes
git status -uno

# If behind, pull
git pull origin main
```

Show summary:
- Files updated
- New commits received
- Any merge conflicts

## Option 2: Push (End of Shift)

```bash
# Stage all changes
git add .

# Show what will be committed
git status

# Commit with handoff message
git commit -m "$ARGUMENTS"

# Push to remote
git push origin main
```

## Usage Examples

```
/sync pull                    # Pull latest changes
/sync push "Handoff: Jan 14"  # Commit and push with message
/sync                         # Interactive - ask what to do
```

## Error Handling

### Merge Conflicts
If conflicts occur:
1. List conflicting files
2. Offer to help resolve
3. Guide through resolution process

### Push Rejected
If push is rejected:
1. Suggest pulling first
2. Handle any merge conflicts
3. Retry push

### Uncommitted Changes Before Pull
If local changes exist:
1. Show changed files
2. Offer to stash or commit first
3. Proceed with user's choice

---

Always confirm before destructive operations (force push, reset, etc.)
