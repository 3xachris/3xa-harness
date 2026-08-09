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
5. **Budget fuse** — a number the work counts against, in whatever unit this task actually spends: renders, GPU-hours, API calls, install attempts, drafts, research passes. The count is kept as it goes, in the order's artifacts folder, because a number reconstructed at closeout is a number remembered rather than measured. Reaching the fuse ends the build with a `STOPPED` message and returns what exists so far.
6. **Acceptance** — objective lines someone else could check without asking what was meant. Each one names how it will be evidenced: a path, a command's output, a measured number. The `DONE` condition is defined by `honest-closeout`, including its required verification outside the work's control.
7. **Non-goals** — what this order leaves alone, especially the neighbouring work it would be natural to drift into.

**Freezing** happens once, in writing, by the person who owns the outcome, and leaves the header line `[FROZEN <date> by <owner>]` on the order — the one artifact that says this document is now the contract. Where the project also tracks capability tiers, the tier picked in §4 rides the same header line.

**Amending** is how a frozen order changes, and it has a fixed shape: a dated `## Amendment <n> — <date>, <who authorised it>` block appended to the bottom of the order, naming the field it changes and the new text in full. The original field stays where it is; the amendment is what governs from that date. Every amendment gets a `decision-log` entry of Type `amendment`, so the trail of what the contract said when survives outside the file too. Changes of mind larger than a field or two are a new order.

## 2. Run the order

For mechanical cross-checking, give every acceptance line a stable ID such as `AC-1` and keep that ID in the closeout answer. The verifier reads lines shaped like `- [ ] AC-1: ...`.

1. **Check the order against the disk first**, and open the project's decision log while you are there — it holds what was settled before this order existed. Paths, filenames, service states, versions: confirm each assumption the order rests on before the first edit. Messages from here on open with `WORKING`. Treat the disk as the factual authority: when it disagrees with the order, stop, name the conflict, and ask before deciding how to proceed.
2. **Build the whole scope**, keeping the budget count in the artifacts folder as you spend it — one line per unit spent, written when it is spent. Every acceptance line is a deliverable; a line that turns out to be blocked is reported as blocked, with the rest finished in full.
3. **Self-verify**, walking the acceptance list line by line and attaching the evidence each line named. Apply the `honest-closeout` `DONE` condition before treating the order as ready for that status.
4. **Self-fix and re-verify.** Stay in this loop until every line carries evidence. When a failure resists a first look, use the core diagnosis loop: reproduce it (a repeatable failure), minimise it (the smallest failing case), state a checkable hypothesis (a prediction), instrument the relevant path (evidence), fix it (the failure is gone), and regression-test it (the failure stays gone). If installed, `staged-diagnosis` is the expanded version of this same loop.
5. **The two-strike rule**, defined here and referred to from elsewhere: a *sub-problem* is one acceptance line failing for one identified cause, and it takes a **strike** each time an attempt aimed at that cause leaves it still failing. At two strikes the loop ends with a `STOPPED` message — carry the full trail, including which hypotheses were refuted, back to the human, who decides the next move. A sub-problem that got fixed is closed and its strikes are gone; a new cause behind the same line starts at zero only after you state its distinct, checkable prediction: what it predicts that the previous cause cannot, or what observation the previous cause cannot explain.
6. **Close out** with `honest-closeout`, whether the result passed or failed.

## 3. Completion criteria

The order is ready for closeout when every acceptance line is classified line by line as passed with evidence, failed with evidence, or blocked with a recorded reason. Use the `honest-closeout` status definitions: `DONE` when every line passed and the required verification outside the work's control is recorded, `CLOSED-FAILED` when the trail is complete but the target was not achieved, and `STOPPED` when the two-strike rule ended the run. Read the frozen order beside the closeout and confirm that every line has one of those classifications.

The order itself is ready to freeze when all seven fields are filled and the header carries `[FROZEN <date> by <owner>]`; until that line exists, there is nothing to build against.

## 4. Pick the tier before freezing

Freezing an order also means picking what capability the work runs at — the project's own name for whichever tier costs the most to run: a stronger model, a more expensive agent mode, a senior reviewer's own attention. The axis that decides which one it gets isn't difficulty — it's whether this line of work has been walked before. **Pathfinding** — the failure modes aren't known yet and there's no successful sample to point at: a tool built from nothing, an unproven external API, a task shaped like nothing this project has finished — takes the strongest tier available, because a lighter one spends its budget re-discovering the same unknowns a stronger one would have seen through faster. **Known-road** — the path has already been walked: the tool exists and has been exercised, a first sample already shipped, the spec is settled — takes the standard tier, because what's left is executing a known shape, not discovering one. A single line of work changes tier as it matures: pathfinding opens it, and once a sample exists, the next order on that same line drops to known-road. Sending known-road capability to open a path burns it on unknowns it can't see past; sending pathfinding capability at quiet, already-proven work burns it on nothing.

Where the project tracks this, the picked tier rides the freeze header alongside the owner: `[FROZEN <date> by <owner>, <tier>]`.

**Check the order itself before raising the tier mid-run.** A run that's stuck usually reads as needing more capability; just as often it needs a better-written order. Check, in order: does the order state a checkable success criterion? does it say when to reach for which tool? does it name a stop condition? does it say how the result gets verified? Any one of those missing is the order's gap, not the model's — a stronger tier pointed at an unclear target just follows the unclear target with more conviction. Fix the gap and rerun at the same tier before escalating; escalate only once all four are confirmed present and the run still stalled.

## 5. Hand it to whoever runs it next

When a frozen order moves to another agent, another session, or another contractor, what they need is the order itself plus four facts a document alone doesn't carry: who they are for this task, what tier the work runs at, where the order lives, and the instruction to run it as frozen. Nothing else — the order already says what to build, and restating any of it in the handoff message creates a second copy that can drift from the first without anyone noticing which one changed.

```text
You are <role>. Tier: <tier>. Read
<path to the frozen order>
Run it as frozen.
```

The one exception is a fact that genuinely can't wait for an amendment — a service that's already running and must not be touched, say. That goes on its own added line, never folded into a restatement of the order's spec.

## 6. Archive on close

An order that's still running lives wherever the project keeps active work — one place, named once and reused, the same way `docs/decisions.md` is one place for decisions rather than one per task; an `orders/active/` folder moving to `orders/archive/` is a common shape for it. The closeout that reaches `DONE` or `CLOSED-FAILED` moves the order into that archive location in the same pass: archiving is part of closing out, not a chore closing out leaves for later, and a closeout that leaves its order sitting in the active location isn't finished, whatever its acceptance lines say. A `STOPPED` order isn't a closeout — the two-strike rule handed the decision back to the human — so it stays in the active location until whatever the human decides next produces a `DONE`, a `CLOSED-FAILED`, or a superseding order that carries it to archive instead.

An order with no natural end — a standing instruction that repeats rather than completes, governing a recurring role instead of a single task — never archives by date. It going stale on the calendar doesn't mean it closed; only a closeout, or a later order that names it superseded, moves it. Sort by that question before filing anything old: did this order finish, or does it just keep running?

## Order template

```markdown
# Order: <name> (<slug>_<YYYYMMDD>)   [FROZEN <date> by <owner>, <tier — optional>]

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
- [ ] AC-1: <checkable line> | evidence: <path / command output / number>

**Non-goals**
- <what this order leaves alone>

## Amendment 1 — <date>, authorised by <who>
Field: <which of the seven>
New text: <the field in full, as it now reads>
```

## Judgment cases

Six ways orders have failed in practice, and the rule each one bought: [`CASES.md`](CASES.md).
