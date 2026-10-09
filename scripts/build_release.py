#!/usr/bin/env python3
"""Build the slim `release` branch that the plugin directory tracks.

Takes the shipped files of a version tag and commits them onto `release`
through a temporary git index. The working tree and the real index do not
change, and nothing is pushed.

Usage: python3 scripts/build_release.py v0.1.8
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SHIPPED = (".claude-plugin/plugin.json", "skills/ste-explain", "README.md", "LICENSE")


class ReleaseError(Exception):
    pass


def run(repo, *args, env=None):
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    )


def git(repo, *args, env=None):
    p = run(repo, *args, env=env)
    if p.returncode != 0:
        raise ReleaseError(f"git {' '.join(args)} failed: {p.stderr.strip()}")
    return p.stdout.strip()


def build(tag, repo=REPO, branch="release"):
    """Commit the SHIPPED paths of tag onto branch; return the branch head sha."""
    p = run(repo, "rev-parse", "-q", "--verify", f"refs/tags/{tag}^{{commit}}")
    if p.returncode != 0:
        raise ReleaseError(f"no tag {tag}")
    commit = p.stdout.strip()
    for path in SHIPPED:
        if run(repo, "cat-file", "-e", f"{commit}:{path}").returncode != 0:
            raise ReleaseError(f"{path} is missing at {tag}")
    plugin = json.loads(git(repo, "show", f"{commit}:.claude-plugin/plugin.json"))
    version = plugin.get("version")
    if version != tag.removeprefix("v"):
        raise ReleaseError(f"plugin.json version {version} does not match tag {tag}")

    with tempfile.TemporaryDirectory() as d:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(d) / "index"))
        git(repo, "read-tree", commit, env=env)
        keep = [f":!{path}" for path in SHIPPED]
        git(repo, "rm", "--cached", "-r", "-q", "-f", "--", ".", *keep, env=env)
        tree = git(repo, "write-tree", env=env)

    p = run(repo, "rev-parse", "-q", "--verify", f"refs/heads/{branch}")
    head = p.stdout.strip() if p.returncode == 0 else None
    if head and git(repo, "rev-parse", f"{head}^{{tree}}") == tree:
        return head
    parents = ["-p", head] if head else []
    message = f"release: {tag} (from {commit[:7]})"
    new = git(repo, "commit-tree", tree, *parents, "-m", message)
    git(repo, "update-ref", f"refs/heads/{branch}", new)
    return new


def main(argv):
    if len(argv) != 2:
        print("usage: python3 scripts/build_release.py vX.Y.Z")
        return 2
    tag = argv[1]
    try:
        sha = build(tag)
    except ReleaseError as e:
        print(e)
        return 1
    files = git(REPO, "ls-tree", "-r", "--name-only", sha).splitlines()
    print(f"release {sha[:7]}: {tag}, {len(files)} files")
    print("next: git push origin release")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
