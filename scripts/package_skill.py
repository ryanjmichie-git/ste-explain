#!/usr/bin/env python3
"""Package skills/ste-explain into dist/ste-explain.zip for claude.ai upload.

Runs validate_skill.py first and refuses to package an invalid skill.
"""

import subprocess
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILL_DIR = REPO / "skills" / "ste-explain"
DIST = REPO / "dist"


def main():
    check = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "validate_skill.py")]
    )
    if check.returncode != 0:
        print("refusing to package: validate_skill.py failed")
        return 1

    DIST.mkdir(exist_ok=True)
    out = DIST / "ste-explain.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(SKILL_DIR.rglob("*")):
            if f.is_file():
                zf.write(f, Path("ste-explain") / f.relative_to(SKILL_DIR))
    print(f"wrote {out}")
    print("install routes:")
    print(
        "  claude.ai    Customize -> Skills -> + -> Create skill -> Upload a skill"
        " (needs Settings -> Capabilities -> Code execution and file creation)"
    )
    print(
        "  Claude Code  claude plugin marketplace add "
        "ryanjmichie-git/ste-explain && claude plugin install ste-explain@ste-explain"
    )
    print("  manual       copy skills/ste-explain/ into ~/.claude/skills/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
