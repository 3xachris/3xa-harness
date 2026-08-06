---
name: workorder
description: Freeze a task's scope into a written order before building, then run it to done in one pass — build, self-verify, self-fix, re-verify — closing with a passing result or a two-strike failure trail. Use when a task spans more than a few steps, when scope is drifting mid-build, when a request is too vague to start from, or when handing work to a subagent.
---

# Workorder

A **frozen order** is the contract the build runs against: written before the first edit, unchanged while the work runs, and the only thing acceptance is measured against. It is also the whole brief — what a subagent or a fresh session is handed when the work moves.

Scope stays where it was frozen, so the thing delivered is the thing agreed. And the work runs **to done in one pass** — obstacles get solved in the same session that hit them, so the human is asked once, at the start, rather than at every bump.

## 1. Write the order

Seven fields, plus the header line that freezes it.

1. **One sentence** — the whole task, in one. Two sentences means two orders, or a request still in fog: interview it sharp first, write the order after.
2. **Known facts** — what is already verified, each with its source (a prior report, a measurement, a file path). This field is what stops the build re-discovering what was settled last week.
3. **Materials** — the models, datasets, fonts, and dependencies this order may use, each with its licence and the date that licence was checked. Anything the order rules out is listed with the reason, so the check is not repeated either.
4. **Build spec** — every parameter pinned to *a file plus a name inside it*: a symbol in code, a key in a config, a named preset and the parameter within it for a render, a voice profile and its setting for audio. Whatever the domain, "the value we settled on" has to resolve to exactly one place someone else can open. Where a value genuinely lives only in a GUI, the pin is a written line in the order plus a screenshot in the artifacts folder — a copy someone can check, since the slider cannot be cited. The spec also names that **artifacts folder**, which holds the order, its gate folders, and its closeout, so the whole task is one place on disk.
5. **Budget fuse** — a number the work counts against, in whatever unit this task actually spends: renders, GPU-hours, API calls, install attempts, drafts, research passes. The count is kept as it goes, in the order's artifacts folder, because a number reconstructed at closeout is a number remembered rather than measured. Reaching the fuse ends the build and returns what exists so far.
6. **Acceptance** — objective lines someone else could check without asking what was meant. Each one names how it will be evidenced: a path, a command's output, a measured number.
7. **Non-goals** — what this order leaves alone, especially the neighbouring work it would be natural to drift into.

**Freezing** happens once, in writing, by the person who owns the outcome, and leaves the header line `[FROZEN <date> by <owner>]` on the order — the one artifact that says this document is now the contract.

**Amending** is how a frozen order changes, and it has a fixed shape: a dated `## Amendment <n> — <date>, <who authorised it>` block appended to the bottom of the order, naming the field it changes and the new text in full. The original field stays where it is; the amendment is what governs from that date. Every amendment gets a `decision-log` entry of Type `amendment`, so the trail of what the contract said when survives outside the file too. Changes of mind larger than a field or two are a new order.

## 2. Run the order

1. **Check the order against the disk first.** Paths, filenames, service states, versions — confirm each assumption the order rests on before the first edit. Where disk and order disagree, the disk wins: stop, name the conflict, and ask.
2. **Build the whole scope.** Every acceptance line is a deliverable; a line that turns out to be blocked is reported as blocked, with the rest finished in full.
3. **Self-verify**, walking the acceptance list line by line and attaching the evidence each line named.
4. **Self-fix and re-verify.** Stay in this loop until every line carries evidence. When a failure resists a first look, `staged-diagnosis` (the `harness-debug` add-on) is the ordered way through it.
5. **The two-strike rule**, defined here and referred to from elsewhere: a *sub-problem* is one acceptance line failing for one identified cause, and it takes a **strike** each time an attempt aimed at that cause leaves it still failing. At two strikes the loop ends — carry the full trail, including which hypotheses were refuted, back to the human, who decides the next move. A sub-problem that got fixed is closed and its strikes are gone; a new cause behind the same line starts at zero.
6. **Close out** with `honest-closeout`, whether the result passed or failed.

## 3. Completion criteria

The order is done when **every acceptance line has evidence attached to it**, line by line. Read the frozen order one more time beside the closeout and answer, line by line: is this line evidenced, blocked-and-reported, or neither? Only the third answer means there is still work to do.

The order itself is ready to freeze when all seven fields are filled and the header carries `[FROZEN <date> by <owner>]`; until that line exists, there is nothing to build against.

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
- Artifacts folder: <one path holding this order, its gate folders, and its closeout>

**Budget fuse:** <number> <unit — runs, GPU-hours, API calls, install attempts, drafts>. On reaching it: stop and return what exists.

**Acceptance**
- [ ] <checkable line> — evidenced by <path / command output / number>

**Non-goals**
- <what this order leaves alone>

## Amendment 1 — <date>, authorised by <who>
Field: <which of the seven>
New text: <the field in full, as it now reads>
```

## Judgment cases

Four ways orders have failed in practice, and the rule each one bought: [`CASES.md`](CASES.md).
