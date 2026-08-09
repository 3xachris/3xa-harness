---
name: honest-closeout
description: Close a task with a report a reviewer can trust — every acceptance line answered with evidence or a recorded blocking reason, human corrections credited to whoever made them, refuted hypotheses kept, background processes proven stopped, and the chat message copied verbatim from the report. Use when reporting work as finished, writing a completion report, summarising what a session achieved, or handing a result to whoever reviews it.
---

# Honest Closeout

A closeout is read by someone deciding whether to trust the work without redoing it, and that decision runs on **evidence** — a path they can open, a number they can compare, a command they can re-run. Claims that arrive without evidence make the reviewer redo the work, which is the cost the report existed to save.

A result that failed, closed out with its full trail, is a good closeout: the trail is the deliverable in that case.

## 1. Reporting vocabulary

This is where the pack's reporting conventions are defined; other skills point here rather than restate them.

- **Status first.** Every message to the human opens with one word from a fixed set, so the state of the task is readable before the second word:

  | Word | The task is |
  |---|---|
  | `WORKING` | running; nothing needed from you |
  | `GATE-HOLD` | stopped at a review gate, waiting on your judgment |
  | `STOPPED` | stopped short — the two-strike rule handed the next move back to you |
  | `DONE` | every acceptance line passed with evidence and the report records independent functional verification outside the work's control |
  | `CLOSED-FAILED` | every acceptance line has evidence or a recorded blocking reason, but the target was not achieved |

  Choose from these five. Use `DONE` when every acceptance line passed and the report records at least one independent functional verification outside the work's control: a rerun in an environment this task does not control, an independent test process, an integration or contract check, or a post-deployment smoke test. Artifact hashes and environment-and-commit identity belong in a separate integrity-and-identity record: they establish which bytes and execution context were reviewed, not whether the result is functionally correct, and they never satisfy the `DONE` verification requirement. If all four functional verification forms are unavailable, report why each form is unavailable and use `CLOSED-FAILED` rather than `DONE`. Use `CLOSED-FAILED` when the trail is complete but the target was not achieved, and `STOPPED` when the two-strike rule ends the run. A state that fits none of them is `STOPPED`, with the reason on the next line.
- **The wait token.** A message that needs the human to act ends with one fixed token alone on the final line — `WAITING_FOR_HUMAN`. It is reserved for exactly that case, which is what keeps it meaning something when it appears.
- **Codes for state, sentences for claims.** The status word and the wait token compress *state* — what this task is doing right now — and compression suits state, because it has a fixed set of values and gets read on every message. A **claim about the world** is the opposite case: this dependency is unmaintained, that bug is fixed, the upstream project has a design flaw. Claims go in full sentences in the report body, however long the sentence needs to be. Compressed into a field — `severity: high`, `A1: read-side absent` — a claim loses the one property a reviewer reads it for: how much it is asserting. A reader can tell that *"the upstream project has a structural hole"* deserves a second look before anyone acts on it; nobody can tell that from a severity value. The audacity of a claim lives in its wording, and the wording is exactly what a code throws away.
- **`[UNVERIFIED]` marks the unchecked.** Version numbers, licence terms, quota limits, "this is fixed" — anything not confirmed at its source this session carries the tag inline, so a reviewer can tell a checked statement from a confident one.
- **Classification tags mark what a fix actually was.** `root-fix`, `patch`, `workaround` for what kind of change it was; `one-shot`, `recurring` for how often it has to run to keep working. Defined in full at §2, item 2, because they attach to acceptance lines the same way evidence does.

## 2. Write the report

For mechanical cross-checking, answer each frozen acceptance ID (`AC-1`, `AC-2`, and so on) on a line shaped like `- [PASS] AC-1: ... | evidence: path`. Record an independent functional check on a line shaped like `- Functional verification: what was run | evidence: path`. List each gate as `- [GATE] gate/path | disposition: approved | reviewer: name | archive: none` or with its archive path.

The report is a file on disk. The chat message is a copy of part of it, never a separate composition.

1. **Answer the acceptance list line by line**, reading it as amended — where the order carries amendment blocks, the amended text is the one being answered. Each line gets PASS or FAIL and the evidence it named — path, output, measurement. A line nobody can evidence is FAIL with the reason, which is information; a line summarised instead of answered is a gap.
2. **Classify what got fixed.** A line whose evidence reports something fixed or handled carries two tags: what kind of change it was, and how often it has to run to keep working. The first is `root-fix` (the actual cause is gone), `patch` (the symptom is suppressed and the cause is still there), or `workaround` (the order reached done by a different path, and the original problem was never touched). A `patch` line names the root-fix it stands in for, or states why none is scheduled yet, on the same line — a patch with neither is missing the information a reviewer needs to weigh it. A `workaround` does not close the line it appears on: routing around a problem reopens the problem, not the order, so a workaround line stays FAIL or BLOCKED until it is replaced by a root-fix or a patch. The second tag is `one-shot` or `recurring`, decided by one question — does this need to happen again to keep working? — never by how much effort the fix took. Both tags are additive to the line's existing shape: `verify_closeout.py`'s evidence match only requires `| evidence: <path>`; anything appended after it is invisible to a parser that never looked for it.
3. **Prove the `DONE` condition** by recording at least one independent functional verification outside the work's control: name the environment and rerun output, independent test process and output, integration or contract check, or deployment smoke-test result. Record artifact hashes and environment-and-commit identity separately as integrity-and-identity evidence; they identify the reviewed bytes and context but do not prove function. If all four functional forms are unavailable, state why the clean-environment rerun, independent test process, integration or contract check, and deployment smoke test are each unavailable, then use `CLOSED-FAILED` rather than `DONE`. A self-run command or a mutable local test is not that proof.
4. **Prove it with material this order hasn't already spent.** A `Functional verification` line that reruns exactly the input a prior round already used shows the result didn't regress — it cannot show the result is healthy, because whatever the input doesn't reach was never going to appear either way. Reserve `regression` for that rerun and never label it `Functional verification` on a `DONE` line; a regression check tests a floor that already held, `DONE` proof tests a fact that is true right now on new ground, and the two are not interchangeable evidence. Where fresh material for this line doesn't exist yet, producing it is part of the order, not a blocker to report around: name the pipeline that gets it, and verify that pipeline too — a producer only ever exercised by being forced to run is a producer nobody has actually tested. Keep a plain list, in the order's artifacts folder, of what material each acceptance line's verification spent; a later reviewer greps it to see whether a `DONE` claim quietly reused an input a previous closeout already burned.
5. **Answer the frozen order's other two claims**: that the work used only the materials the order allowed, and that it stayed out of the non-goals. Both are one line each, and both are the fields a reviewer would otherwise have to reconstruct from the diff.
6. **Record what people did**, compiled from the log entries written at the time rather than from what the session remembers. Every human stop, correction, or diagnosis appears with the person who supplied it, including permissions granted mid-build (a dependency installed, a setting changed) — the reviewer is deciding about a system whose state changed, and needs to know it did. Where a `decision-log` is running, its `correction` entries are the source this section is built from.
7. **Keep the refuted hypotheses.** What was tried and eliminated is the most reusable part of the report; the next attempt spends its budget on new ground instead of re-walking this one.
8. **Report the budget spent** against the fuse the order set — the count, the unit, and whether the fuse was reached. A build that stopped on its fuse and a build that finished are different results, and only this line tells them apart.
9. **Prove the background is clear.** Query the tooling for every background process this session started and account for each one. Anything meant to outlive the report is declared with a receipt a later session can check by itself: an absolute output path, a PID, or a log file's absolute path. A name only this session knows is not a receipt.
10. **Answer the gate register** from the gate-opening `decision` entries in the project's decision log. List every recorded gate folder, compare its recorded file hashes with the files shipped, and report the `rejected-archive/<gate-folder>/` path and its contents. This is the complete gate list for the task.
11. **Write the chat-summary section inside the report** — status word, the three-to-five line result, the paths a human needs to open, the wait token if action is needed.
12. **Send that section verbatim.** Copy it out of the file; a summary rewritten from memory late in a long session drifts, and drift runs toward the flattering version.
13. **Leave the log a pointer.** One `closeout` entry — the result in a line, the report's path as its Target — so the next session finds this report by reading the log rather than by knowing it exists. Run the `decision-log` skill for the entry format.

## 3. Completion criteria

Read the report as the reviewer: **for every acceptance line, can you point at the evidence without asking a question?**

Then six checks with a yes-or-no answer each:

- every background process this session started is named, with how it ended
- every gate folder recorded in the gate-opening `decision` entries is listed, its shipped files match the recorded hashes, and its rejected items are in the corresponding `rejected-archive/<gate-folder>/` reference-only archive
- the budget line reports a count against the fuse
- the log carries a `closeout` entry whose Target is this report
- every claim about anything outside this task's own artifacts appears as a sentence somewhere in the report, not only as a field value
- the chat message matches the report's summary section character for character

The two things that stay a judgment — that human contributions are credited to whoever supplied them, and that unconfirmed statements carry `[UNVERIFIED]` — cannot be checked by counting, because both ask about something that *should* be in the report and isn't. Re-read for those two specifically, comparing against the log entries rather than against your memory of the session.

## Report template

```markdown
# Closeout: <task name> — <DONE / CLOSED-FAILED / STOPPED>

**Order:** <path to the frozen order this was measured against>

## Chat summary (send this section verbatim)

<DONE | CLOSED-FAILED | STOPPED>
- <what got built / where it died / the numbers that matter>
- <paths a human needs to open>

<!-- WAITING_FOR_HUMAN belongs here only when this closeout needs a decision
     from the human — a CLOSED-FAILED or STOPPED result, or an open question.
     A DONE that needs nothing back ends without it. -->

## Acceptance

- [PASS] AC-1: <line> | evidence: <path / output / number>
- [PASS] AC-2: <line reporting a fix> | evidence: <path> | fix: <root-fix / patch / workaround>, <one-shot / recurring>
- [FAIL] <line> — <what blocked it>

## Independent functional verification

- <functional verification outside the work's control: rerun in an uncontrolled environment, independent test process, integration or contract check, or post-deployment smoke test; include the path / output / measurement>
- <when all four forms are unavailable, why the uncontrolled-environment rerun is unavailable>
- <when all four forms are unavailable, why the independent test process is unavailable>
- <when all four forms are unavailable, why the integration or contract check is unavailable>
- <when all four forms are unavailable, why the post-deployment smoke test is unavailable; this closeout uses `CLOSED-FAILED`, not `DONE`>

## Integrity and identity evidence

- <artifact hash and/or environment-and-commit identity; state that it identifies the reviewed bytes or execution context and is not functional verification>

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
