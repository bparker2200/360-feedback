---
type: spec
project: system
status: active
owner: shared
created: 2026-01-12
updated: 2026-01-12
tags: [cli, code, explanation, teaching]
---

# Explain

Explain code with visual diagrams, analogies, and codebase-specific gotchas.

## Usage

```
/explain <target>              # Explain specific file, function, or module
/explain src/auth/tokens.ts    # Explain a file
/explain validateToken         # Explain a function (will search for it)
/explain "the payments module" # Explain a conceptual area
```

## Semantic Triggers (Auto-Detect)

This skill also triggers automatically on:
- "How does X work?"
- "Explain X"
- "What does X do?"
- "Walk me through X"
- "I don't understand X"

---

## Instructions

### 1. Locate the Target

If given a file path, read it directly. If given a function/class name or description:

```bash
# Search for the target
rg -l "function_name\|class_name" --type-add 'code:*.{ts,js,py,go,rs}' -t code
```

Read the file(s) containing the target.

### 2. Build Context (2 Levels Up)

Follow imports to understand dependencies, but limit context to **2 levels of abstraction** above the target:

- Target: `validateToken()` function
- Level 1: The module it belongs to (`auth/tokens.ts`)
- Level 2: The system layer (`API middleware`)

Do NOT trace the full call graph unless explicitly asked.

### 3. Check Complexity

**If trivial** (one-liner, obvious assignment):
- Output: One sentence + where it fits in the system
- Skip diagram, analogy, and full template

**If non-trivial**, continue with full template.

### 4. Generate Output

Use this structure (skip sections that don't apply):

```markdown
## Context
[2-level orientation: where this code lives in the system]

## Analogy
[If domain-appropriate: everyday comparison. SKIP for cryptography, shaders, low-level code]

## Diagram
[If helpful: ASCII with Unicode boxes. SKIP if code is linear or diagram would be more complex than the code]

## Walkthrough
[Step-by-step in READING ORDER (top-to-bottom as written), not execution order]

## Side Effects
[ALWAYS include if any exist: DB writes, API calls, filesystem mutations]

## Gotchas
[CODEBASE-SPECIFIC only. Rate by fix urgency: CRITICAL/HIGH/MEDIUM/LOW]

## Dependencies
[Conditional: "This uses X — want me to explain that module?"]
```

### 5. Diagram Style

Use Unicode box drawing:
```
┌─────────────┐      ┌─────────────┐
│   Input     │ ───▶ │   Process   │
└─────────────┘      └──────┬──────┘
                            │
                            ▼
                     ┌─────────────┐
                     │   Output    │
                     └─────────────┘
```

Characters: `┌ ─ ┐ │ └ ┘ ▶ ▼ ◀ ▲`

### 6. Gotcha Severity

Rate by **fix urgency**:

| Severity | Meaning | Example |
|----------|---------|---------|
| **CRITICAL** | Fix now — production risk | Unhandled exception crashes server |
| **HIGH** | Fix soon — bug likely | Race condition under load |
| **MEDIUM** | Tech debt — accumulating risk | Hardcoded config, no validation |
| **LOW** | Nice-to-have — maintainability | Magic numbers, unclear naming |

Format: `**Gotcha [HIGH]:** Description of the issue.`

When helpful, generate hypothetical code showing what would break:
```javascript
// Current (safe):
if (user?.email) { sendNotification(user.email); }

// Without null check (would throw):
sendNotification(user.email); // TypeError if user is undefined
```

### 7. Adaptive Vocabulary

Infer skill level from the question:
- Junior-sounding → Simplify terminology, add context
- Senior-sounding → Use precise terms, assume familiarity

### 8. Session Memory

If you've explained related code earlier in the session, reference it:
> "As I explained when covering AuthModule, the token validation happens here..."

### 9. Flag Unknowns

If code uses unfamiliar libraries:
> "This uses `@acme/flux-capacitor` — I'm inferring from naming that `capacitor.charge()` initiates the async process, but I haven't seen this library. Consult their docs to confirm."

### 10. Suggest, Don't Act

This skill explains and may suggest improvements but **never modifies files**. If asked "how does this work and can you fix it?" — explain first, suggest the fix, but do not apply it.

### 11. Save Output

After generating explanation, save to:
```
.claude/skills/explaining_code/outputs/explain_[target]_[YYYYMMDD-HHMM].md
```

**Target normalization:**
- File path → filename only: `src/auth/tokens.ts` → `tokens`
- Function/class → name: `validateToken` → `validateToken`
- Module/concept → kebab-case: "the payments module" → `payments-module`

**Skip saving when:**
- User says "don't save" or "no output"
- Explanation is trivial (abbreviated response)

---

## Target Length

- **Non-trivial code:** ~500 words
- **Trivial code:** 2-3 sentences

---

## Full Spec

For complete behavioral rules, examples, and edge cases:
`.claude/skills/explaining_code/SPEC.md`
