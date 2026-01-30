#!/usr/bin/env python3
"""
Safe shell wrapper that blocks destructive operations on protected paths.

Usage:
    python3 safe_shell.py rm -rf protected_file.txt
    python3 safe_shell.py mv CLAUDE.md old_claude.md
"""

import sys
import subprocess
from pathlib import Path

# Protected paths - customize for your project
PROTECTED_PATHS = [
    "CLAUDE.md",
    "scripts/governance",
    ".mcp.json",
    "NOW.md"
]

# Destructive commands that require path checking
DESTRUCTIVE_COMMANDS = ["rm", "mv", "rmdir"]


def is_protected(path_str: str) -> bool:
    """Check if path matches any protected pattern."""
    path = Path(path_str)

    for protected in PROTECTED_PATHS:
        protected_path = Path(protected)

        # Exact match
        if path == protected_path:
            return True

        # Check if path is inside protected directory
        try:
            path.relative_to(protected_path)
            return True
        except ValueError:
            pass

        # Check if protected path is inside this path (directory removal)
        try:
            protected_path.relative_to(path)
            return True
        except ValueError:
            pass

    return False


def safe_shell(args: list) -> int:
    """Execute shell command with safety checks."""

    if not args:
        print("Error: No command provided", file=sys.stderr)
        return 1

    command = args[0]

    # Check if this is a destructive command
    if command in DESTRUCTIVE_COMMANDS:
        # Check all arguments for protected paths
        for arg in args[1:]:
            # Skip flags
            if arg.startswith("-"):
                continue

            if is_protected(arg):
                print(f"❌ BLOCKED: Cannot {command} protected path: {arg}", file=sys.stderr)
                print(f"Protected paths: {', '.join(PROTECTED_PATHS)}", file=sys.stderr)
                print(f"If you need to modify this file, edit it directly instead of using {command}", file=sys.stderr)
                return 1

    # Execute command
    try:
        result = subprocess.run(args, check=False)
        return result.returncode
    except FileNotFoundError:
        print(f"Error: Command not found: {command}", file=sys.stderr)
        return 127


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: safe_shell.py <command> [args...]")
        print("Example: safe_shell.py rm -rf dangerous_file.txt")
        return 1

    return safe_shell(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())
