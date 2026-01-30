# Explain Skill - Full Specification

> **Primary Spec Location:** `/commands/explain.md`

This file is referenced by the explain skill but the canonical specification lives at:

```
/commands/explain.md
```

## Quick Reference

**Usage:** `/explain <target>`

**Output Location:** `.claude/skills/explaining_code/outputs/explain_[target]_[YYYYMMDD-HHMM].md`

**Triggers:**
- `/explain <target>`
- "How does X work?"
- "Explain X"
- "What does X do?"
- "Walk me through X"

## Key Behaviors

1. **Read before modifying** - Always read target file/function first
2. **2-level context** - Only trace 2 levels of abstraction up
3. **Skip trivial** - One-liners get 1 sentence, not full template
4. **Visual over text** - Use Unicode diagrams when helpful
5. **Flag unknowns** - Admit when inferring library behavior
6. **Never modify** - Explain only, suggest fixes but don't apply

## Severity Ratings

| Level | Fix Urgency |
|-------|-------------|
| CRITICAL | Production risk - fix now |
| HIGH | Bug likely - fix soon |
| MEDIUM | Tech debt accumulating |
| LOW | Maintainability only |

---

For complete instructions, edge cases, and examples, see `/commands/explain.md`.
