#!/usr/bin/env python3
"""Checks for the eval tooling: trigger_eval, screen_blind, tabulate_eval.

No headless session starts. run_claude, the one slow external call of
trigger_eval.py, is replaced by a fake that returns stream-json text. The
plugin copies, the stream parsing, the retry, the counts, and the exit codes
are the real code.

Usage: python3 scripts/test_tools.py
"""

import contextlib
import io
import json
import shutil
import sys
import tempfile
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import screen_blind  # noqa: E402
import tabulate_eval  # noqa: E402
import trigger_eval as te  # noqa: E402

OWN = "ste-explain:ste-explain"
FIVE = [
    {"query": "P1", "should_trigger": True},
    {"query": "P2", "should_trigger": True},
    {"query": "P3", "should_trigger": True},
    {"query": "N1", "should_trigger": False},
    {"query": "N2", "should_trigger": False},
]
TWENTY = [{"query": f"P{i}", "should_trigger": True} for i in range(1, 11)] + [
    {"query": f"N{i}", "should_trigger": False} for i in range(1, 11)
]
OLD_ALL = {("P1", "old"), ("P2", "old"), ("P3", "old")}
NEW_ALL = {("P1", "new"), ("P2", "new"), ("P3", "new")}


def stream(skill_calls=(), loaded=(OWN,), assistant=True, content=None):
    """Stream-json text of one session, with the events trigger_eval reads."""
    events = [
        {
            "type": "system",
            "subtype": "init",
            "skills": list(loaded) + ["other:thing"],
            "model": "fake-model",
        }
    ]
    if assistant:
        if content is None:
            content = [{"type": "text", "text": "ok"}]
            content += [
                {"type": "tool_use", "name": "Skill", "input": {"skill": s}}
                for s in skill_calls
            ]
        events.append({"type": "assistant", "message": {"content": content}})
    events.append({"type": "result", "result": "reply text"})
    return "\n".join(json.dumps(e) for e in events)


def good(query, variant, nth):
    return stream([OWN] if query.startswith("P") else [])


def only(triggering):
    """Only the sessions in `triggering`, a set of (query, variant), call the skill."""
    return lambda q, v, nth: stream([OWN] if (q, v) in triggering else [])


def scenario(
    behavior,
    queries=FIVE,
    args=(),
    ref="HEAD",
    workers="2",
    out_stream=None,
    queries_path=None,
):
    """Run trigger_eval.main() with a fake run_claude.

    behavior(query, variant, nth_call) returns stream text, or (rc, text).
    Returns code, rows, text, calls, and leftover (temp dirs that remain).
    """
    variant_of, calls, made, lock = {}, {}, [], threading.Lock()
    real_copy, real_run, real_mkdtemp = (
        te.make_plugin_copy,
        te.run_claude,
        tempfile.mkdtemp,
    )
    work = Path(real_mkdtemp())
    qfile, out = work / "q.json", work / "out" / "rows.jsonl"
    qfile.write_text(json.dumps(queries), encoding="utf-8")

    def copy(ref=None):
        d = real_copy(ref)
        variant_of[str(d)] = "old" if ref else "new"
        return d

    def fake_run_claude(cmd, cwd):
        query = cmd[2]
        variant = variant_of[cmd[cmd.index("--plugin-dir") + 1]]
        with lock:
            calls[(query, variant)] = calls.get((query, variant), 0) + 1
            nth = calls[(query, variant)]
        res = behavior(query, variant, nth)
        return res if isinstance(res, tuple) else (0, res)

    def mkdtemp(*a, **k):
        d = real_mkdtemp(*a, **k)
        made.append(d)
        return d

    argv = ["trigger_eval.py", "--runs", "1", "--workers", workers]
    argv += ["--queries", queries_path or str(qfile), "--out", str(out)]
    argv += (["--ref", ref] if ref else []) + list(args)
    buf = out_stream or io.StringIO()
    old_argv = sys.argv
    te.make_plugin_copy, te.run_claude, tempfile.mkdtemp = (
        copy,
        fake_run_claude,
        mkdtemp,
    )
    sys.argv = argv
    try:
        with contextlib.redirect_stdout(buf):
            code = te.main()
    finally:
        sys.argv = old_argv
        te.make_plugin_copy, te.run_claude, tempfile.mkdtemp = (
            real_copy,
            real_run,
            real_mkdtemp,
        )
    rows = []
    if out.exists():
        rows = [
            json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()
        ]
    shutil.rmtree(work, ignore_errors=True)
    return {
        "code": code,
        "rows": rows,
        "text": "" if out_stream else buf.getvalue(),
        "calls": calls,
        "leftover": [d for d in made if Path(d).exists()],
    }


def test_pair_rule():
    # Both variants correct: pass. Rows carry variant, valid, model.
    r = scenario(good)
    assert r["code"] == 0, r["text"]
    assert len(r["rows"]) == 10
    assert {x["variant"] for x in r["rows"]} == {"new", "old"}
    assert all(x["valid"] and x["model"] == "fake-model" for x in r["rows"])
    assert "new total: should-trigger 3/3, should-not triggered 0/2" in r["text"]
    assert "old total: should-trigger 3/3, should-not triggered 0/2" in r["text"]
    assert "invalid sessions (left out): 0/10" in r["text"] and "PASS" in r["text"]
    assert r["leftover"] == [], r["leftover"]
    # New is 2 should-trigger hits below old: still a pass. 3 below: fail.
    r = scenario(only(OLD_ALL | {("P1", "new")}))
    assert r["code"] == 0 and "new total: should-trigger 1/3" in r["text"], r["text"]
    r = scenario(only(OLD_ALL))
    assert r["code"] == 1 and "FAIL" in r["text"], r["text"]
    # New has 1 more false trigger than old: pass. 2 more: fail.
    r = scenario(only(OLD_ALL | NEW_ALL | {("N1", "new")}))
    assert r["code"] == 0, r["text"]
    r = scenario(only(OLD_ALL | NEW_ALL | {("N1", "new"), ("N2", "new")}))
    assert r["code"] == 1, r["text"]


def test_unpaired_floor():
    # No --ref: only the "new" variant runs, judged against 22/30 and 2/30.
    r = scenario(good, ref=None)
    assert r["code"] == 0 and len(r["rows"]) == 5, r["text"]
    assert {x["variant"] for x in r["rows"]} == {"new"}
    # 2 of 3 should-trigger is below 22/30. A bare "ste-explain" call counts
    # as a trigger; a call to another skill does not.
    calls = {"P1": ["ste-explain"], "P2": [OWN], "P3": ["other:thing"]}
    r = scenario(lambda q, v, nth: stream(calls.get(q, [])), ref=None)
    by_q = {x["query"]: x["triggered"] for x in r["rows"]}
    assert [by_q[q] for q in ("P1", "P2", "P3")] == [True, True, False]
    assert r["code"] == 1 and "new total: should-trigger 2/3" in r["text"], r["text"]
    # 1 of 2 false triggers is above 2/30.
    r = scenario(only(NEW_ALL | {("N1", "new")}), ref=None)
    assert r["code"] == 1, r["text"]


def test_retry_and_invalid():
    # A session with no assistant message is retried once; the retry counts.
    def flaky(q, v, nth):
        return "" if (q, v, nth) == ("P1", "new", 1) else good(q, v, nth)

    r = scenario(flaky)
    assert r["code"] == 0 and r["calls"][("P1", "new")] == 2, r["text"]
    assert r["calls"][("P2", "new")] == 1 and all(x["valid"] for x in r["rows"])

    # A session that fails twice is left out. 1 of 10 is over 5%: invalid run.
    def dead(q, v, nth):
        return stream(assistant=False) if (q, v) == ("P1", "new") else good(q, v, nth)

    r = scenario(dead)
    assert r["code"] == 2 and "INVALID RUN" in r["text"], r["text"]
    assert r["calls"][("P1", "new")] == 2


def test_other_copy():
    # Another ste-explain copy in the session: invalid run.
    def confounded(q, v, nth):
        calls = [OWN] if q.startswith("P") else []
        return stream(calls, loaded=(OWN, "anthropic-skills:ste-explain"))

    r = scenario(confounded)
    assert r["code"] == 2 and "other ste-explain copies loaded" in r["text"], r["text"]


def test_paired_drops_both_sides():
    # A (run, query) with a failed session on one side leaves both sides.
    def new_p1_dead(q, v, nth):
        return "" if (q, v) == ("P1", "new") else good(q, v, nth)

    r = scenario(new_p1_dead, queries=TWENTY, args=["--runs", "3"])
    assert "invalid sessions (left out): 3/120" in r["text"], r["text"]
    assert "new total: should-trigger 27/27" in r["text"], r["text"]
    assert "old total: should-trigger 27/27" in r["text"], r["text"]
    assert r["code"] == 0, r["text"]

    # Mirror: the old side loses P1, and new misses 5 of its other 27.
    def old_p1_dead(q, v, nth):
        if (q, v) == ("P1", "old"):
            return ""
        if (q, v) == ("P2", "new") or ((q, v) == ("P3", "new") and nth > 1):
            return stream([])
        return good(q, v, nth)

    r = scenario(old_p1_dead, queries=TWENTY, args=["--runs", "3"], workers="1")
    assert "new total: should-trigger 22/27" in r["text"], r["text"]
    assert "old total: should-trigger 27/27" in r["text"], r["text"]
    assert r["code"] == 1, r["text"]


def test_timeout_and_broken_stream():
    # A timeout with no trigger seen is a failed session, not a miss. A timeout
    # after the skill call still counts as a trigger. A malformed assistant
    # event fails its session; it does not crash the run.
    def behavior(q, v, nth):
        if (q, v) == ("P1", "new"):
            return ("timeout", stream([]))
        if (q, v) == ("P2", "new"):
            return ("timeout", stream([OWN]))
        if (q, v) == ("P3", "new"):
            return stream(content="a plain string")
        return good(q, v, nth)

    r = scenario(behavior, queries=TWENTY)
    row = {(x["query"], x["variant"]): x for x in r["rows"]}
    assert row[("P1", "new")]["valid"] is False and r["calls"][("P1", "new")] == 2
    assert (
        row[("P2", "new")]["valid"] is True and row[("P2", "new")]["triggered"] is True
    )
    assert r["calls"][("P2", "new")] == 1
    assert row[("P3", "new")]["valid"] is False and r["calls"][("P3", "new")] == 2
    assert "new total: should-trigger 8/8" in r["text"], r["text"]
    assert "old total: should-trigger 8/8" in r["text"], r["text"]
    assert r["code"] == 0, r["text"]


def test_crash_is_invalid_run():
    # A crash must not look like FAIL (exit 1), and it leaves no temp dirs.
    r = scenario(good, ref="nosuchref")
    assert r["code"] == 2 and "INVALID RUN" in r["text"], r["text"]
    assert r["leftover"] == [], r["leftover"]
    r = scenario(good, queries_path="no-such-file.json")
    assert r["code"] == 2 and "INVALID RUN" in r["text"], r["text"]
    assert r["leftover"] == [], r["leftover"]


def test_print_survives_cp1252():
    # Windows gives a redirected stdout the cp1252 codec. A query with a
    # character outside it must not crash the summary after every session ran.
    queries = [
        {"query": "P→1", "should_trigger": True},
        {"query": "N1", "should_trigger": False},
    ]
    raw = io.BytesIO()
    out = io.TextIOWrapper(raw, encoding="cp1252")
    r = scenario(good, queries=queries, out_stream=out)
    out.flush()
    assert r["code"] == 0, raw.getvalue()
    assert b"P\\u21921" in raw.getvalue(), raw.getvalue()


def tally_text(graders, key):
    it = Path(tempfile.mkdtemp())
    blind = it / "blind" / "demo"
    blind.mkdir(parents=True)
    key_path = it / "key.json"
    key_path.write_text(json.dumps(key), encoding="utf-8")
    for i, g in enumerate(graders, 1):
        (blind / f"grader-{i}.json").write_text(json.dumps(g), encoding="utf-8")
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            screen_blind.tally(it, "demo", key_path, "passed")
    finally:
        shutil.rmtree(it, ignore_errors=True)
    return buf.getvalue()


def test_tally_single_vote_and_strings():
    key = {
        "01": {"arm": "arm-a", "run": "run-1"},
        "02": {"arm": "arm-a", "run": "run-2"},
        "03": {"arm": "arm-a", "run": "run-3"},
        "04": {"arm": "arm-b", "run": "run-1"},
        "05": {"arm": "arm-b", "run": "run-2"},
    }
    yes = {"passed": True}
    # The second grader covers two outputs only: the tally names the rest.
    text = tally_text([{n: yes for n in key}, {"01": yes, "02": yes}], key)
    assert "single vote: 03, 04, 05" in text, text
    assert "split votes: none" in text and "ungraded: none" in text, text
    # Two full graders: nothing to name.
    text = tally_text([{n: yes for n in key}, {n: yes for n in key}], key)
    assert "single vote: none" in text, text
    # Only a JSON true is a pass. The string "false" is not.
    no = {"passed": "false"}
    text = tally_text([{"01": no}, {"01": no}], {"01": key["01"]})
    assert "demo arm-a passed: 0/1" in text, text


def test_tabulate_counts_only_true():
    root = Path(tempfile.mkdtemp())
    run = root / "rewrite-dense" / "with_skill" / "run-1"
    run.mkdir(parents=True)
    (run / "output.md").write_text("Stop the pump.\n", encoding="utf-8")
    rows = [{"text": f"a{i}", "passed": True, "evidence": ""} for i in range(5)]
    rows[1]["passed"] = "false"
    grading = {"expectations": rows}
    (run / "grading.json").write_text(json.dumps(grading), encoding="utf-8")
    buf, argv = io.StringIO(), sys.argv
    sys.argv = ["tabulate_eval.py", str(root)]
    try:
        with contextlib.redirect_stdout(buf):
            tabulate_eval.main()
    finally:
        sys.argv = argv
        shutil.rmtree(root, ignore_errors=True)
    assert "  4  PFPPP  lint 0" in buf.getvalue(), buf.getvalue()


TESTS = [
    test_pair_rule,
    test_unpaired_floor,
    test_retry_and_invalid,
    test_other_copy,
    test_paired_drops_both_sides,
    test_timeout_and_broken_stream,
    test_crash_is_invalid_run,
    test_print_survives_cp1252,
    test_tally_single_vote_and_strings,
    test_tabulate_counts_only_true,
]


def main():
    failed = 0
    for test in TESTS:
        try:
            test()
        except Exception as e:
            failed += 1
            print("FAIL %s: %s" % (test.__name__, ascii(e)[:300]))
    if failed:
        print("%d of %d checks failed" % (failed, len(TESTS)))
        return 1
    print("tools self-test PASS (%d checks)" % len(TESTS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
