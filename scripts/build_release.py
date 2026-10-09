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


def plugin_version(repo, rev, name):
    text = git(repo, "show", f"{rev}:.claude-plugin/plugin.json")
    try:
        return json.loads(text).get("version")
    except json.JSONDecodeError as e:
        raise ReleaseError(f"plugin.json at {name} is not valid JSON: {e}")


def version_key(version):
    return tuple(int(part) for part in version.split("."))


def build(tag, repo=REPO, branch="release"):
    """Commit the SHIPPED paths of tag onto branch; return the branch head sha."""
    if run(repo, "symbolic-ref", "-q", "HEAD").stdout.strip() == f"refs/heads/{branch}":
        raise ReleaseError(f"{branch} is checked out; switch to main first")
    p = run(repo, "rev-parse", "-q", "--verify", f"refs/tags/{tag}^{{commit}}")
    if p.returncode != 0:
        raise ReleaseError(f"no tag {tag}")
    commit = p.stdout.strip()
    for path in SHIPPED:
        if run(repo, "cat-file", "-e", f"{commit}:{path}").returncode != 0:
            raise ReleaseError(f"{path} is missing at {tag}")
    version = plugin_version(repo, commit, tag)
    if version != tag.removeprefix("v"):
        raise ReleaseError(f"plugin.json version {version} does not match tag {tag}")

    with tempfile.TemporaryDirectory() as d:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(d) / "index"))
        git(repo, "read-tree", commit, env=env)
        keep = [f":!{path}" for path in SHIPPED]
        git(repo, "rm", "--cached", "-r", "-q", "-f", "--", ".", *keep, env=env)
        tree = git(repo, "write-tree", env=env)

    head = None
    # A fresh clone has no local branch yet; continue the pushed one.
    for ref in (f"refs/heads/{branch}", f"refs/remotes/origin/{branch}"):
        p = run(repo, "rev-parse", "-q", "--verify", ref)
        if p.returncode == 0:
            head = p.stdout.strip()
            break
    if head and git(repo, "rev-parse", f"{head}^{{tree}}") == tree:
        return head
    if head:
        released = plugin_version(repo, head, branch)
        if version_key(version) <= version_key(released):
            raise ReleaseError(
                f"version {version} at {tag} is not above {released} on {branch}"
            )
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
    print(f"next: git push origin main {tag} release")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
