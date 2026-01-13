---
description: Quick project and handoff status check
allowed-tools: Bash(git:*), Read
---

# Quick Status Check

Provide a rapid status overview without the full catchup process.

## Gather Status Information

Run these commands and compile results:

```bash
# Git status
git status --short
git log --oneline -3

# Check for handoff
ls -la .claude/handoffs/CURRENT-HANDOFF.md 2>/dev/null || echo "No handoff file"

# Quick test count (if fast)
pytest --collect-only -q 2>/dev/null | tail -1 || echo "Tests not checked"
```

## Present Quick Status

Format output as:

```
╔══════════════════════════════════════════════════════════════╗
║                    PTV TRANSIT - STATUS                       ║
╠══════════════════════════════════════════════════════════════╣
║ Branch:     [current branch]                                  ║
║ Last Commit: [short hash] [message] ([time ago])             ║
║ Uncommitted: [count] files                                    ║
╠══════════════════════════════════════════════════════════════╣
║ HANDOFF STATUS                                                ║
║ Last Handoff: [date/time] by [developer]                     ║
║ Top Priority: [brief description]                             ║
╠══════════════════════════════════════════════════════════════╣
║ TESTS: [X] passing | Coverage: [Y]%                          ║
╚══════════════════════════════════════════════════════════════╝
```

## Quick Actions

After showing status, offer:

- `/catchup` - Full context from last handoff
- `/handoff` - Generate handoff for next shift
- `pytest` - Run test suite
- `git pull` - Sync with remote

---

Keep this output **brief and scannable**. The developer should understand project state in under 10 seconds.
