---
name: handoff
description: Write one snapshot of the current state, organized by what the next reader needs rather than by what this session did, so a person or session with zero memory of the work can read it once and keep going — every open thread's status, every already-spent asset and how to start it, every cross-thread dependency, every unresolved debt, each answered or marked none. Use when a session is ending, a task is moving to another person or agent, a long break is coming, or a fresh session needs to inherit in-flight work without whoever was here to fill the gaps.
---

# Handoff

A handoff is read by someone who was not in the room — not a colleague filling gaps from memory of the conversation, a reader with none. `decision-log` is written for the cold read of one decision at a time, appended the moment it happens. A handoff is written for the cold read of the whole state at once: a single wide snapshot, taken the moment work changes hands, of what the log's entry-by-entry trail doesn't by itself add up to — everything true right now, in a shape built to survive the writer's own memory being gone at the other end.

## 1. The coverage checklist

Four categories, each answered or marked `none` — leaving one out reads identically to having checked it and found nothing, so only a written `none` proves the second:

- **Running work and its reasoning.** Every thread currently open, its status word from the fixed set (`WORKING`, `GATE-HOLD`, `STOPPED`, `DONE`, `CLOSED-FAILED` — defined in `honest-closeout`) and the one-line reason it sits there. Where a thread is a frozen `workorder`, point at the order instead of redescribing it.
- **Already-spent assets.** Anything paid for, provisioned, or installed that outlives this session — how to start it, and any red line attached to using it: a quota, a licence limit, an action it must never take.
- **Cross-thread dependencies.** Which open items block or feed which others, so the next reader doesn't start the wrong one first.
- **Unresolved debt.** Known problems nobody has closed, each with enough of a trail that the next reader can pick it up rather than rediscover that it exists.

## 2. Write for the reader, not the writer

The most common way a handoff fails: written as a log of what got done this session, in the order it happened. A narrative like that has no edge that stops it short of complete — it just stops wherever the writer's memory of the session runs out, and what's missing is exactly the part the writer wasn't touching when they sat down to write: someone else's open thread, an asset from three sessions back, a debt nobody's mentioned lately. Write against the four categories instead, and write each fact as itself rather than as something someone did — a fact stated plainly reads the same whether the cold reader arrives in an hour or in a month.

Don't restate what another artifact already carries. A `decision-log` entry, a frozen order, a report — point at its path. A handoff that copies one becomes a second copy that goes stale the moment the original changes, and the reader can no longer tell which one to trust. Copy nothing that already has an authoritative home.

## 3. Leave the pointer

After writing, append one `decision` entry to the project's decision log with the handoff document's path as its Target — the existing pointer mechanism, not a new one. A session that opens the log first, as `workorder` already tells it to, finds the handoff from there too. Run the `decision-log` skill for the entry format.

## 4. Completion criteria

- Every one of the four checklist categories carries an entry or an explicit `none`.
- No sentence names "this session," "I," "we," or a person by role — a leftover of narrative structure the checklist alone won't catch, so read for it specifically.
- Every fact that already lives in a decision-log entry, a frozen order, or a report appears here only as a path, not restated.
- Every open thread's status word is one of the fixed five, each with its one-line reason.
- The decision log carries an entry whose Target is this document.
- **The test the first five don't cover:** hand the document, alone, to someone who was not here, and have them state the single next action for one open thread using nothing else. If they can't, the checklist entry that thread lived under was answered too thinly, not left off — a self-read by the writer doesn't catch this, the same way a self-run test doesn't prove `honest-closeout`'s `DONE`.

## Handoff template

```markdown
# Handoff: <what's changing hands> (<YYYYMMDD>)

**Written for:** <the next reader — a fresh session, a named person, "whoever picks this up">

## Running work

- <thread> — <status word> — <one-line reason>. Order: <path, or "none">
- (none)

## Already-spent assets

- <asset> — start it: <command / path>. Red line: <quota / licence / irreversible action to avoid, or "none">
- (none)

## Dependencies

- <thread> blocks/feeds <thread> — <one-line reason>
- (none)

## Open debt

- <problem> — what's known so far, and where the trail lives
- (none)

## Pointers, not copies

- Decision log: <path>
- Orders / reports referenced above: <paths already listed inline, not repeated here>
```

## Judgment cases

Three handoffs that read as complete and were not: [`CASES.md`](CASES.md).
