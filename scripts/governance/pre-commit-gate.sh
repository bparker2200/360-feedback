#!/bin/bash
#
# Pre-commit hook to block commits touching protected paths
#
# Install: cp scripts/governance/pre-commit-gate.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
#
# Override: GOVERNANCE_OVERRIDE=1 git commit -m "message"
#

# Protected paths - customize for your project
PROTECTED_PATHS=(
    "CLAUDE.md"
    "scripts/governance/"
    ".mcp.json"
)

# Check if override is set
if [ "$GOVERNANCE_OVERRIDE" = "1" ]; then
    echo "⚠️  GOVERNANCE_OVERRIDE=1 detected. Allowing protected path modifications."
    exit 0
fi

# Get list of files being committed
FILES=$(git diff --cached --name-only)

# Check each file against protected paths
for file in $FILES; do
    for protected in "${PROTECTED_PATHS[@]}"; do
        # Check if file matches protected path (exact or within directory)
        if [[ "$file" == "$protected"* ]] || [[ "$file" == "$protected" ]]; then
            echo ""
            echo "❌ GOVERNANCE ALERT: Protected path modified."
            echo ""
            echo "   File: $file"
            echo "   Protected pattern: $protected"
            echo ""
            echo "   To proceed, use: GOVERNANCE_OVERRIDE=1 git commit -m \"message\""
            echo ""
            echo "   Agent: Never use GOVERNANCE_OVERRIDE=1 without explicit human approval."
            echo ""
            exit 1
        fi
    done
done

exit 0
