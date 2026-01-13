---
description: Load context from previous shift handoff (RUN AT START OF YOUR SHIFT)
allowed-tools: Bash(git:*), Read, Grep, Glob
---

# Shift Catchup - Load Previous Session Context

You are starting a new development shift. Load and present the handoff from the previous developer.

## Step 1: Verify Git Sync

First, ensure we have the latest code:

```bash
git fetch origin
git status
```

If there are upstream changes, advise pulling:
```bash
git pull origin main
```

## Step 2: Load Handoff Document

Read the handoff file at `.claude/handoffs/CURRENT-HANDOFF.md`

If the file doesn't exist, check:
1. `.claude/handoffs/archive/` for recent handoffs
2. `CONTEXT.md` (legacy handoff file)
3. `DEVELOPMENT_STATUS.md` for project status

## Step 3: Present Handoff Summary

Provide a clear, actionable summary:

### 📋 Shift Handoff Summary

**From**: [Previous developer name]
**Date**: [Handoff date/time]
**Time Since Handoff**: [Calculate from timestamp]

---

### 🎯 Immediate Priority
[The single most important thing to work on]

**Task**: [Task name]
**Current State**: [Where it was left off]
**Next Step**: [Exact next action to take]
**Files to Open**: [List key files]

---

### 📁 Key Files Modified Last Session
[List the most important files that were changed]

---

### ⚠️ Blockers to Be Aware Of
[Any issues or blockers mentioned]

---

### 🧪 Test Status
- Tests: [Passing/Failing count]
- Coverage: [Percentage]

---

## Step 4: Verify Test Suite

Run a quick test check:
```bash
pytest --tb=no -q 2>/dev/null | tail -5
```

## Step 5: Offer Options

Ask the developer what they'd like to do:

> **Ready to continue! What would you like to do?**
> 
> 1. **Continue top priority** - [Brief description of priority task]
> 2. **Review changed files** - Open and examine recent modifications
> 3. **Run full test suite** - Verify everything is working
> 4. **Check blockers** - Address any issues first
> 5. **Work on something else** - Tell me what you'd like to focus on

---

## Step 6: Load Additional Context (if needed)

If the developer wants to dive deeper, offer to read:
- `DEVELOPMENT_STATUS.md` - Full project status
- `README.md` - Project overview
- Specific source files mentioned in the handoff

---

**IMPORTANT**: Your goal is to get the developer productive as quickly as possible. Present only the essential information upfront, with options to drill deeper if needed.
