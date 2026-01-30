# Claude Project Template

A lightweight template for Claude-assisted development with built-in safety infrastructure.

## Features

- **CLAUDE.md** — Behavioral rules for AI-assisted development
- **NOW.md** — Current task tracking and decisions log
- **Protected paths** — Git pre-commit hook prevents accidental modifications
- **Safe shell wrapper** — Blocks destructive operations on critical files
- **MCP integration** — Pre-configured for local-dev-mcp

## Quick Start

### 1. Use This Template

**Option A: GitHub Template (Recommended)**
```bash
# Click "Use this template" on GitHub, then clone
git clone https://github.com/YOUR_USERNAME/YOUR_PROJECT_NAME.git
cd YOUR_PROJECT_NAME
```

**Option B: Manual Clone**
```bash
git clone https://github.com/brandonparker/claude-project-template.git YOUR_PROJECT_NAME
cd YOUR_PROJECT_NAME
rm -rf .git
git init
```

### 2. Install Pre-Commit Hook

```bash
cp scripts/governance/pre-commit-gate.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### 3. Configure MCP

Update `.mcp.json` with your local-dev-mcp path:
```json
{
  "mcpServers": {
    "local-dev-mcp": {
      "command": "/path/to/your/local-dev-mcp/run.sh",
      "args": [],
      "env": {}
    }
  }
}
```

### 4. Customize Protected Paths (Optional)

Edit these files to customize which paths are protected:
- `scripts/governance/pre-commit-gate.sh` — Git commit protection
- `scripts/utils/safe_shell.py` — Shell command protection

### 5. Start Working

Read `CLAUDE.md` for behavioral rules, then start your work:
```bash
# Session start
# Say "cockpit" or "session start" to Claude

# Work on your project...

# Session end
# Say "close out" or "end session" to Claude
```

## File Structure

```
claude-project-template/
├── CLAUDE.md              # Behavioral rules for Claude
├── NOW.md                 # Current task and next actions
├── .mcp.json              # MCP server configuration
├── .gitignore             # Standard ignores
├── scripts/
│   ├── utils/
│   │   └── safe_shell.py  # Safe shell wrapper
│   └── governance/
│       └── pre-commit-gate.sh  # Git pre-commit hook
└── docs/
    └── README.md          # This file
```

## Protected Paths

By default, these paths require `GOVERNANCE_OVERRIDE=1` to commit:
- `CLAUDE.md`
- `scripts/governance/*`
- `.mcp.json`

**Override example:**
```bash
GOVERNANCE_OVERRIDE=1 git commit -m "fix: update protected file"
```

**Important:** Claude should never use `GOVERNANCE_OVERRIDE=1` without explicit human approval.

## Usage Tips

### Session Start
Say "cockpit" or "session start" to Claude. It will:
1. Read `NOW.md`
2. Display current task and blocker
3. Show next 3 items

### Session End
Say "close out" or "end session" to Claude. It will:
1. Sweep chat for important items
2. Surface deferred work
3. Offer to update `NOW.md`

### Working Style
Claude follows these patterns (from CLAUDE.md):
- Visual formats over paragraphs
- Do the thing over explaining
- Short bullets over long explanations
- Bias toward action

## Customization

### Add More Protected Paths

Edit `PROTECTED_PATHS` in both:
1. `scripts/governance/pre-commit-gate.sh`
2. `scripts/utils/safe_shell.py`

### Modify Behavioral Rules

Edit `CLAUDE.md` to customize how Claude works in your project.

### Extend NOW.md

Add project-specific sections to `NOW.md`:
- Sprint goals
- Blockers list
- Reference links
- Team decisions

## License

MIT

## Credits

Based on patterns from [Double-Post-Training](https://github.com/DblPost/double-post-training).
