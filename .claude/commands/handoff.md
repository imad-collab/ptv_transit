---
description: Generate shift handoff document for next developer (RUN BEFORE ENDING YOUR SHIFT)
allowed-tools: Bash(git:*), Read, Grep, Glob
---

# Generate Shift Handoff

You are ending your development shift. Create a comprehensive handoff document for the next developer.

## Step 1: Gather Information

First, collect the following information:

1. **Git Status**: Run `git status` and `git diff --name-only` to see changed files
2. **Recent Commits**: Run `git log --oneline -5` to see recent commits
3. **Test Status**: Run `pytest --tb=no -q 2>/dev/null || echo "Tests not run"` to check test status
4. **Current Branch**: Run `git branch --show-current`

## Step 2: Analyze Session Context

Review our conversation to identify:
- Tasks completed this session
- Work in progress (partially done)
- Blockers or issues discovered
- Decisions made and their rationale
- Files modified or created

## Step 3: Create Handoff Document

Create/overwrite the file `.claude/handoffs/CURRENT-HANDOFF.md` with the following structure:

```markdown
# Shift Handoff

**Date/Time**: [ISO 8601 timestamp, e.g., 2026-01-14T18:00:00+11:00]
**Developer**: [Name of developer ending shift]
**Handoff To**: [Name of next developer]
**Session Duration**: [Approximate duration]

---

## ✅ Completed This Session

[List all tasks completed with specific outcomes]
- ✅ [Task 1] - [Brief outcome/result]
- ✅ [Task 2] - [Brief outcome/result]

---

## 🔄 Work In Progress

[For each task currently being worked on:]

### [Task Name]
- **Current State**: [Exactly where we left off]
- **Files Modified**: 
  - `path/to/file1.py` - [What was changed]
  - `path/to/file2.py` - [What was changed]
- **Next Immediate Step**: [The very next action needed]
- **Estimated Remaining**: [Time estimate if possible]

---

## ⚠️ Blockers & Issues

[Any problems discovered that need attention]
1. **[Issue Title]**: [Description]
   - Impact: [How it affects work]
   - Workaround: [If any]
   - Suggested Fix: [If known]

---

## 📝 Decisions Made

[Key technical decisions made this session]
1. **[Decision]**: [Rationale behind it]

---

## 🎯 Priorities for Next Session

[Ordered by importance]
1. **[HIGH]** [Task] - [Brief description]
2. **[HIGH]** [Task] - [Brief description]
3. **[MEDIUM]** [Task] - [Brief description]
4. **[LOW]** [Task] - [Brief description]

---

## 📁 Files Changed This Session

[Output of git diff --name-only or list manually]
- `path/to/file1.py` - [Brief description of changes]
- `path/to/file2.py` - [Brief description of changes]

---

## 🧪 Test Status

- **Tests Run**: [Yes/No]
- **Tests Passing**: [X/Y]
- **Coverage**: [Percentage if known]
- **Failing Tests**: [List if any]

---

## 🔧 Environment Notes

[Any special setup or commands needed]
- [Note 1]
- [Note 2]

---

## 💬 Notes for Next Developer

[Personal notes, tips, or context that would help]
- [Note 1]
- [Note 2]

---

## Git Commands to Sync

```bash
# After reviewing this handoff, commit and push:
git add .
git commit -m "Handoff: [DATE] [YOUR-NAME] -> [NEXT-DEV]"
git push origin main
```

---

*Handoff generated: [timestamp]*
```

## Step 4: Archive Previous Handoff (if exists)

If `.claude/handoffs/CURRENT-HANDOFF.md` already exists, first copy it to:
`.claude/handoffs/archive/[YYYY-MM-DD-HHMM]-[developer].md`

Create the archive directory if it doesn't exist:
```bash
mkdir -p .claude/handoffs/archive
```

## Step 5: Provide Summary

After creating the handoff file, provide:

1. A brief 3-4 line summary of the handoff
2. The git commands to commit and push:

```bash
git add .claude/handoffs/
git add .  # Any other changes
git commit -m "Handoff: [DATE] [YOUR-NAME]"
git push origin main
```

3. Remind the developer to:
   - Review the handoff document
   - Ensure all code changes are committed
   - Push to GitHub before ending their session

---

**IMPORTANT**: Be thorough and specific. The next developer will start their session with ONLY this handoff document as context. Include everything they need to continue seamlessly.
