# CLAUDE.md

> Behavioral rules for Claude-assisted development in this repository.

---

## Consent Protocol

Before modifying files:
1. State what file(s) will change
2. State what the change does
3. Wait for approval ("yes" / "approve" / "do it")

**Exception:** Read-only operations (view, search, git status/diff).

---

## Git Safety

**Before scary operations** (bulk deletes, folder moves, 10+ file changes, cleanup scripts):
```bash
git branch backup-$(date +%Y-%m-%d)
# do scary thing
# if wrong: git reset --hard backup-YYYY-MM-DD
# if right: git branch -d backup-YYYY-MM-DD
```

**Full safety protocol:**
- Create backup branch before risky operations
- Verify changes before deleting backup
- Never use `git push --force` on main/master without explicit approval

---

## Protected Paths

These paths require `GOVERNANCE_OVERRIDE=1` to commit:
- `CLAUDE.md`
- `scripts/governance/*`
- `.mcp.json`

**Override usage:**
```bash
GOVERNANCE_OVERRIDE=1 git commit -m "message"
```

Agent must **never** use override without explicit human approval in the same message.

---

## Working Style

| Preference | Meaning |
|------------|----------|
| Visual formats > paragraphs | Default to tables, diagrams |
| Do the thing > explain | Execute, don't describe how |
| One clear action > multiple options | Decide, don't present choices |
| Short bullets > long explanations | Brevity |
| When stuck, offer to just do it | Bias toward action |

**Tone:** Direct, precise. State corrections immediately. Skip pleasantries. Challenge flawed assumptions. Waste no words.

---

## Session Start

**Trigger:** "cockpit" or "session start"

**Action:**
1. Read `NOW.md`
2. Display current task and blocker
3. Ask: "Ready to continue?"

**Format:**
```
Current Task: [task from NOW.md]
Blocker: [blocker or "None"]
Next 3: [first item from next_3 list]
```

---

## Session End

**Trigger:** "close out" or "end session"

**Action:**
1. Sweep chat for important items
2. Surface deferred work
3. Prompt: "Update NOW.md with decisions and next tasks?"

---

## Git Commits

Format: `[type]: [description]`

| Type | Use |
|------|-----|
| feat | New capability |
| fix | Bug fix |
| docs | Documentation only |
| refactor | Restructure, no behavior change |
| chore | Maintenance, cleanup |

**Commit message requirements:**
- Clear, concise description
- Include "what" and "why" when non-obvious
- Co-authored tag: `Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>`

---

## Rules

| Don't | Do Instead |
|-------|------------|
| Create files without reading this guide first | Read CLAUDE.md before starting |
| Make assumptions about preferences | Ask or check NOW.md |
| Present options when action is clear | Execute directly |
| Use verbose explanations | Short, direct statements |
| Skip consent protocol | Always state changes and wait for approval |

---

**Last updated:** 2026-01-29
**Version:** 1.0
