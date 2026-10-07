# Fixture: coined jargon (explain-to-the-PM input)

Give the tester ONLY the summary below. The label list and the fact list at
the bottom are for the grader.

---

Status for the week. The shim path is live for 40% of traffic and p95 is
holding under 300 ms. We hit the ghost-write bug twice on Tuesday. Both
times the Monday job replayed the missing rows within the hour, so no
customer saw a gap. The cache warmer is still in review. Next week we move
the shim path to 100% unless the ghost-write bug shows up again. If it
does, we hold at 40% and ship the cache warmer first.

---

## Coined labels (grader only — each must be handled)

These four names were made up by the author. The summary never defines
them. For each label, the output passes when it says at first use what the
summary supports about the thing, in plain words, and keeps or replaces the
name. A meaning that the summary does not state is invented and fails that
label. A label used bare, with no explanation, fails. A closing note that
says all names are undefined, without using the context that exists, fails
the first three labels.

1. the shim path — supported: it carries 40% of the traffic now and goes
   to 100% next week, so it is something new being rolled out.
2. the ghost-write bug — supported: it happened twice on Tuesday and left
   rows missing, which the Monday job then replayed.
3. the Monday job — supported: it replayed the missing rows within the
   hour, so it is a job that re-copies missing rows.
4. the cache warmer — the summary says only that it is in review and ships
   first if the bug returns. Nothing says what it does. The pass is to keep
   the name and say that the summary does not define it. Any stated
   function ("fills the cache before traffic arrives") is invented and
   fails.

## Fact list (grader only — all 7 must survive)

1. The shim path serves 40% of traffic.
2. p95 latency is holding under 300 ms.
3. The ghost-write bug happened twice on Tuesday.
4. Both times the Monday job replayed the missing rows within the hour.
5. No customer saw a gap.
6. The cache warmer is still in review.
7. Next week the shim path goes to 100% unless the bug shows up again; if
   it does, the team holds at 40% and ships the cache warmer first. The
   condition must stay attached to the rollout.
