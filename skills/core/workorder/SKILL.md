---
name: workorder
description: Freeze a task's scope into a written order before building, then run it to done in one pass — build, self-verify, self-fix, re-verify — closing with a passing result or a two-strike failure trail. Use when a task spans more than a few steps, when scope is drifting mid-build, when a request is too vague to start from, or when handing work to a subagent.
---

# Workorder

A **frozen order** is the contract the build runs against: written before the first edit, unchanged while the work runs, and the only thing acceptance is measured against. Anything outside it stays outside it.

Two behaviours make an order worth writing. Scope stays where it was frozen, so the thing delivered is the thing agreed. And the work runs **to done in one pass** — obstacles get solved in the same session that hit them, so the human is asked once, at the start, rather than at every bump.

## 1. Write the order

Seven fields. An order is ready when all seven are filled and the human freezing it has read them.

1. **One sentence** — the whole task, in one. Two sentences means two orders, or a request still in fog: interview it sharp first, write the order after.
2. **Known facts** — what is already verified, each with its source (a prior report, a measurement, a file path). This field is what stops the build re-discovering what was settled last week.
3. **Materials** — the models, datasets, fonts, and dependencies this order may use, each with its licence and the date that licence was checked. Anything the order rules out is listed with the reason, so the check is not repeated either.
4. **Build spec** — parameters pinned to *file plus symbol name*, so "the value we settled on" resolves to exactly one place on disk.
5. **Budget fuse** — a number the work counts against: runs, GPU-hours, API calls, install attempts. Reaching it ends the build and returns what exists so far.
6. **Acceptance** — objective lines someone else could check without asking what was meant. Each one names how it will be evidenced: a path, a command's output, a measured number.
7. **Non-goals** — what this order leaves alone, especially the neighbouring work it would be natural to drift into.

**Freezing** happens once, in writing, by the person who owns the outcome. From then on the order is read-only: a change of mind is a new order or an explicit amendment, both of which leave a trace.

## 2. Run the order

1. **Check the order against the disk first.** Paths, filenames, service states, versions — confirm each assumption the order rests on before the first edit. Where disk and order disagree, the disk wins: stop, name the conflict, and ask. Assumptions cost seconds to check and hours to unwind.
2. **Build the whole scope.** Every acceptance line is a deliverable; a line that turns out to be blocked is reported as blocked, with the rest finished in full.
3. **Self-verify**, walking the acceptance list line by line and attaching the evidence each line named.
4. **Self-fix and re-verify.** Stay in this loop until every line carries evidence. This loop *is* the work — a build that returns at the first failing check has done half a job.
5. **Two strikes on the same sub-problem** ends the loop: carry the full trail — what was tried, what was observed, which hypotheses were refuted — back to the human, who decides the next move. A sub-problem that got fixed is closed and counts as nothing; only an unfixed repeat is a strike.
6. **Close out** with `honest-closeout`, whether the result passed or failed. A failure closed out with its full trail is a good closeout.

## 3. Completion criteria

The order is done when **every acceptance line has evidence attached to it** — not most lines, and not a summary that stands in for the lines. Read the frozen order one more time beside the closeout and answer, line by line: is this line evidenced, blocked-and-reported, or neither? Only the third answer means there is still work to do.

## Order template

```markdown
# Order: <name> (<slug>_<YYYYMMDD>)   [FROZEN <date> by <owner>]

**One sentence:** <the whole task>

**Known facts**
- <verified fact> — source: <report / measurement / path>

**Materials**
- Allowed: <asset> — <licence>, checked <date>
- Ruled out: <asset> — <reason>

**Build spec**
- <parameter> = <value>, pinned at <file>#<symbol>

**Budget fuse:** <number> <unit>. On reaching it: stop and return what exists.

**Acceptance**
- [ ] <checkable line> — evidenced by <path / command output / number>

**Non-goals**
- <what this order leaves alone>
```

## Judgment cases

Three ways orders have failed in practice, and the rule each one bought: [`CASES.md`](CASES.md).
