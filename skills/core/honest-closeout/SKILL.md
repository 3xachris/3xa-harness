---
name: honest-closeout
description: Close a task with a report a reviewer can trust — every acceptance line answered with evidence, human corrections credited to whoever made them, refuted hypotheses kept, background processes proven stopped, and the chat message copied verbatim from the report. Use when reporting work as finished, writing a completion report, summarising what a session achieved, or handing a result to whoever reviews it.
---

# Honest Closeout

A closeout is read by someone deciding whether to trust the work without redoing it. That decision runs on **evidence** — a path they can open, a number they can compare, a command they can re-run. Claims that arrive without evidence make the reviewer redo the work, which is the cost the report existed to save.

A result that failed, closed out with its full trail, is a good closeout: the trail is the deliverable in that case.

## 1. Reporting vocabulary

This is where the pack's reporting conventions are defined; other skills point here rather than restate them.

- **Status first.** Every message to the human opens with one word from a fixed set, so the state of the task is readable before the second word:

  | Word | The task is |
  |---|---|
  | `WORKING` | running; nothing needed from you |
  | `GATE-HOLD` | stopped at a review gate, waiting on your judgment |
  | `STOPPED` | stopped short — a budget fuse, a two-strike failure, a conflict to resolve |
  | `DONE` | finished and closed out |

  Fixed set means fixed: a word invented for one message costs the human the glance the convention exists to buy.
- **The wait token.** A message that needs the human to act ends with one fixed token alone on the final line — `WAITING_FOR_HUMAN`. Messages that are pure progress narration end without it. The token keeps its meaning exactly as long as it fires only when action is genuinely needed; on every message, it is noise the human learns to skip.
- **`[UNVERIFIED]` marks the unchecked.** Version numbers, licence terms, quota limits, "this is fixed" — anything not confirmed at its source this session carries the tag inline, so a reviewer can tell a checked statement from a confident one.

## 2. Write the report

The report is a file on disk. The chat message is a copy of part of it, never a separate composition.

1. **Answer the acceptance list line by line.** Each line gets PASS or FAIL and the evidence it named — path, output, measurement. A line nobody can evidence is FAIL with the reason, which is information; a line summarised instead of answered is a gap.
2. **Record what people did**, compiled from the log entries written at the time rather than from what the session remembers. Every human stop, correction, or diagnosis appears with the person who supplied it, including permissions granted mid-build (a dependency installed, a setting changed) — the reviewer is deciding about a system whose state changed, and needs to know it did. Where a `decision-log` is running, its `correction` entries are the source this section is built from.
3. **Keep the refuted hypotheses.** What was tried and eliminated is the most reusable part of the report; the next attempt spends its budget on new ground instead of re-walking this one.
4. **Report the budget spent** against the fuse the order set — the count, the unit, and whether the fuse was reached. A build that stopped on its fuse and a build that finished are different results, and only this line tells them apart.
5. **Prove the background is clear.** Query the tooling for every background process this session started and account for each one. Anything meant to outlive the report is declared with a receipt a later session can check by itself: an absolute output path, a PID, or a log file's absolute path. A name only this session knows is not a receipt.
6. **Write the chat-summary section inside the report** — status word, the three-to-five line result, the paths a human needs to open, the wait token if action is needed.
7. **Send that section verbatim.** Copy it out of the file; a summary rewritten from memory late in a long session drifts, and drift runs toward the flattering version.

## 3. Completion criteria

Read the report as the reviewer: **for every acceptance line, can you point at the evidence without asking a question?** Then check these four, each of which is a yes or a no: every background process this session started is accounted for; every human contribution names who supplied it; every statement not confirmed at its source this session carries `[UNVERIFIED]`; and the budget line reports a count against the fuse. Finally, the chat message matches the report's summary section character for character — a message that differs is not this report's summary.

## Report template

```markdown
# Closeout: <task name> — <PASSED / FAILED (closed) / STOPPED at budget>

## Chat summary (send this section verbatim)

DONE
- <what got built / where it died / the numbers that matter>
- <paths a human needs to open>
WAITING_FOR_HUMAN

## Acceptance

- [PASS] <line> — evidence: <path / output / number>
- [FAIL] <line> — <what blocked it>

## Build record

- <key steps and turning points>
- <hypotheses refuted along the way>
- Budget: <count> of <fuse> <unit> — <fuse reached / not reached>

## Human input

- <each stop, correction, or diagnosis + who supplied it; permissions granted mid-build. "None" if none.>

## Background processes

- <each one started this session and how it ended; survivors with path / PID / log path. "None" if none.>

## Left open

- <unresolved threads and suggested next orders; the call is the human's>
```

## Judgment cases

Three closeouts that read as trustworthy and were not: [`CASES.md`](CASES.md).
