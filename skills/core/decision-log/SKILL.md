---
name: decision-log
description: Keep one append-only log where decisions, rejections, and corrections survive a context reset — each entry carrying a fixed index line a later session can search, and pointing at where the full detail lives instead of copying it. Read it first when picking up a project you have no memory of; write to it when recording why something was chosen or dropped, when handing over to a fresh session or another agent, or when answering "why did we do it this way" months later.
---

# Decision Log

A fresh session inherits what was written down and nothing else. The log carries a decision across that boundary, so it is written for the **cold read**: someone who was not there, searching months later, with no memory to fill the gaps. What that reader needs above all is to tell, from a scan, which entry holds what they came for.

## 1. Shape of the log

- **One file, append-only.** The log is a timeline: past entries stay as written, and a change of mind arrives as a new entry that references the old one. Reading it top to bottom shows how the thinking moved, which is usually the question being asked.
- **Every entry opens with an index line**, directly under its heading, in a fixed format:
  `> Type: <decision|amendment|rejection|correction|closeout> | Target: <path to where the detail lives, or "none (process note)">`
  Five types, each with something that writes it: a choice made (`decision`), a frozen scope changed (`amendment`, from `workorder`), a human turning an artifact down (`rejection`, from `sensory-gate`), a human correcting the work (`correction`), a task finished and reported (`closeout`, from `honest-closeout`). A type nothing produces is a type the format check spends its strictness guarding for no one.
  This line is what makes an entry findable by machine and skimmable by human. Write it at the time — it is the one part of an entry that cannot be reconstructed afterwards.
- **Entries point.** Roughly five lines: what was decided, the one-line reason, and where the full detail lives. When an entry starts growing, the content belongs in a real document and the entry belongs pointing at it.
- **A running summary sits at the top** — open items, current focus, counts — updated in the same edit as the entry below it. It gives the current state in one glance, and stays trustworthy for exactly as long as that pairing holds.
- **Split at a threshold you set in advance** — 200 KB unless you have a measured reason for another number. The point is having a line at all: file-reading tools truncate a long log silently, and a log you believe you read in full is worse than one you know you didn't. At the line, older entries move to a dated archive, the live file keeps the current period, and both the summary and the archive index are updated in the same pass.

## 2. Install the pointer, once per project

A log that nothing points at is read by whoever already knew it was there. What makes it reach a session that has no memory of this one is a line in the file that project loads every time — `CLAUDE.md`, `AGENTS.md`, or whatever the harness always reads:

```markdown
## Decision log

`docs/decisions.md` — the decisions, rejections, and corrections made on this project,
newest last. Read it before starting work here.
```

Install that line the first time this project gets a log, and the read side runs itself from then on: every session loads the pointer, and the pointer names the file and the moment to open it. Where a project already carries such a section, add to it rather than starting a second one.

## 3. Log the moment

1. **Write the entry as the decision happens.** Recall at the end of a long session smooths over the parts that were contested — which are the parts a later reader came for.
2. **Give the decision a home.** Before writing, ask where the detail belongs: a spec, a config, a design doc, a backlog item. That path goes in the index line's Target field. When no home exists yet, create it in this same turn — a decision whose only home is one log line is a decision the next search will not surface.
3. **Log the surviving need beside a rejection.** Turning down a proposal leaves the problem it addressed standing. Record that problem as its own findable item — a backlog entry, an open question, a ticket — so it outlives the approach that failed to solve it.
4. **Check the file size on the way out.** If the live file has crossed 200 KB, split it now, in this session.

## 4. Completion criteria

The log holds when all four are true, checked over the whole file after appending rather than over the entry just written:

- every `##` heading is followed by a line matching `^> Type: (decision|amendment|rejection|correction|closeout) \| Target: ` — greppable
- every Target other than `none` resolves to something that exists on disk — greppable
- the running summary's open items match the entries below it — a read of one block against the headings
- the project's always-loaded file names the log — a look at one file

## Entry shape

```markdown
## 2026-08-06 Dropped the write-through cache, kept the staleness problem

> Type: correction | Target: backlog.md#cache-invalidation

Write-through cache rejected — complexity the current read volume doesn't
earn. The staleness it was solving is still real and is now an open item in
backlog.md, so it survives the approach that was meant to fix it.
```

## Judgment cases

Three logs that were kept faithfully and still failed the cold read: [`CASES.md`](CASES.md).
