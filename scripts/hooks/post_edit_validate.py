#!/usr/bin/env python3
"""PostToolUse hook: validate the skill whenever SKILL.md is written.

Reads the hook payload from stdin. If the edited file is the shipped
SKILL.md, runs validate_skill.py. On violations, exits 2 so Claude sees the
problems on stderr and fixes them. Fails open on anything unexpected — a
broken hook must never block normal work.
"""
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent


def main():
    try:
        payload = json.load(sys.stdin)
        file_path = (payload.get("tool_input") or {}).get("file_path", "")
    except Exception:
        return 0
    norm = file_path.replace("\\", "/")
    if not norm.endswith("SKILL.md") or "skills/" not in norm:
        return 0
    proc = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "validate_skill.py"), file_path],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        sys.stderr.write("SKILL.md violates platform constraints — fix now:\n")
        sys.stderr.write(proc.stdout + proc.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
