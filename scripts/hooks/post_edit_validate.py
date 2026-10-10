#!/usr/bin/env python3
"""PostToolUse hook: validate the skill and the files that must agree with it.

Reads the hook payload from stdin. If the edited file is the shipped
SKILL.md, runs validate_skill.py. If it is one of the files that
check_consistency.py watches (the skill, README, manifests, spec, evals),
runs that too. On violations, exits 2 so Claude sees the problems on stderr
and fixes them. Fails open on anything unexpected — a broken hook must never
block normal work.
"""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent


def watched_files():
    """The paths check_consistency.py watches, or none if it cannot be imported."""
    try:
        sys.path.insert(0, str(REPO / "scripts"))
        from check_consistency import FILES

        return FILES
    except Exception:
        return ()


def main(stdin=None):
    try:
        payload = json.load(stdin or sys.stdin)
        file_path = (payload.get("tool_input") or {}).get("file_path", "")
        target = Path(file_path).resolve()
    except Exception:
        return 0
    norm = file_path.replace("\\", "/")
    if norm.endswith("SKILL.md") and "skills/" in norm:
        proc = subprocess.run(
            [sys.executable, str(REPO / "scripts" / "validate_skill.py"), file_path],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            sys.stderr.write("SKILL.md violates platform constraints — fix now:\n")
            sys.stderr.write(proc.stdout + proc.stderr)
            return 2
    if any(target == (REPO / f).resolve() for f in watched_files()):
        proc = subprocess.run(
            [sys.executable, str(REPO / "scripts" / "check_consistency.py"), str(REPO)],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            sys.stderr.write("repo consistency checks failed - fix now:\n")
            sys.stderr.write(proc.stdout + proc.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
