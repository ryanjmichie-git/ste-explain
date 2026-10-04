#!/usr/bin/env python3
"""Blind copies and a majority tally for a screen of several arms.

make   copies every ITER/EVAL/arm-*/run-*/output.md to ITER/blind/EVAL/NN.md
       in a seeded shuffled order and writes the key (NN -> arm, run) to KEY.
       Put KEY outside the repo so that graders cannot find it.
tally  reads ITER/blind/EVAL/grader-*.json, each {"NN": {"passed": bool, ...}},
       and prints per arm how many outputs a majority of graders passed. A
       1-1 split counts as a fail and is listed; add a third grader file that
       covers the split outputs and run tally again.

Usage:
  python3 scripts/screen_blind.py make  ITER EVAL KEY [--seed 14]
  python3 scripts/screen_blind.py tally ITER EVAL KEY [--field passed]
"""

import argparse
import json
import random
import shutil
from pathlib import Path


def make(it, ev, key_path, seed):
    outs = sorted((it / ev).glob("arm-*/run-*/output.md"))
    random.Random(seed).shuffle(outs)
    blind = it / "blind" / ev
    blind.mkdir(parents=True, exist_ok=True)
    key = {}
    for i, src in enumerate(outs, 1):
        nn = f"{i:02d}"
        shutil.copyfile(src, blind / f"{nn}.md")
        key[nn] = {"arm": src.parent.parent.name, "run": src.parent.name}
    key_path.write_text(json.dumps(key, indent=1), encoding="utf-8")
    print(f"{len(outs)} outputs copied to {blind}; key written to {key_path}")


def tally(it, ev, key_path, field):
    key = json.loads(key_path.read_text(encoding="utf-8"))
    files = sorted((it / "blind" / ev).glob("grader-*.json"))
    graders = [json.loads(p.read_text(encoding="utf-8")) for p in files]
    arms, split, ungraded = {}, [], []
    for nn, where in sorted(key.items()):
        votes = [bool(g[nn][field]) for g in graders if nn in g]
        if not votes:
            ungraded.append(nn)
            continue
        if len(set(votes)) > 1:
            split.append(nn)
        passed = sum(votes) * 2 > len(votes)
        arms.setdefault(where["arm"], []).append((where["run"], passed))
    for arm, runs in sorted(arms.items()):
        detail = " ".join(f"{r}:{'P' if p else 'F'}" for r, p in sorted(runs))
        print(f"{ev} {arm} {field}: {sum(p for _, p in runs)}/{len(runs)}  {detail}")
    print(f"grader files: {len(files)}")
    print(f"split votes: {', '.join(split) or 'none'}")
    print(f"ungraded: {', '.join(ungraded) or 'none'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["make", "tally"])
    ap.add_argument("iteration")
    ap.add_argument("eval")
    ap.add_argument("key")
    ap.add_argument("--seed", type=int, default=14)
    ap.add_argument("--field", default="passed")
    args = ap.parse_args()
    it, key_path = Path(args.iteration), Path(args.key)
    if args.command == "make":
        make(it, args.eval, key_path, args.seed)
    else:
        tally(it, args.eval, key_path, args.field)


if __name__ == "__main__":
    main()
