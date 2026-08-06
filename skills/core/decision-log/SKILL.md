---
name: decision-log
description: Keep one append-only log where decisions, rejections, and corrections survive a context reset — each entry carrying a fixed index line a later session can search, and pointing at where the full detail lives instead of copying it. Read it first when picking up a project you have no memory of; write to it when recording why something was chosen or dropped, when handing over to a fresh session or another agent, or when answering "why did we do it this way" months later.
---

# Decision Log

A fresh session inherits what was written down and nothing else. The log is what carries a decision across that boundary — so it is written for the **cold read**: someone who was not there, searching months later, with no memory to fill the gaps.

That reader has one requirement above all others. They must be able to tell, from a scan, which entry holds what they came for.

## 1. Shape of the log

- **One file, append-only.** The log is a timeline: past entries stay as written, and a change of mind arrives as a new entry that references the old one. Reading it top to bottom shows how the thinking moved, which is usually the question being asked.
- **Every entry opens with an index line**, directly under its heading, in a fixed format:
  `> Type: <decision|amendment|correction|closeout|handoff|info> | Target: <path to where the detail lives, or "none (process note)">`
  This line is what makes an entry findable by machine and skimmable by human. It is written at the time; a scanner built later to reconstruct it from prose will guess, and will miss entries.
- **Entries point.** Roughly five lines: what was decided, the one-line reason, and where the full detail lives. When an entry starts growing, the content belongs in a real document and the entry belongs pointing at it.
- **A running summary sits at the top** — open items, current focus, counts — updated in the same edit as the entry below it. It gives the current state in one glance, and it is trustworthy only as long as it is never updated separately from the entries.
- **Split at 200 KB.** File-reading tools start truncating a live log well before it feels large, and a silently truncated log is worse than a missing one. 200 KB is the number to act on, not to wait for: older entries move to a dated archive, the live file keeps the current period, and both the summary and the archive index are updated in the same pass.

## 2. Read first, then log the moment

1. **Open the log before the work**, whenever you are picking up a project this session did not start. The entries hold the decisions and the reasons that never made it into a diff, and reading them takes a fraction of the time spent re-deriving them.
2. **Write the entry as the decision happens.** Recall at the end of a long session smooths over the parts that were contested — which are the parts a later reader came for.
3. **Give the decision a home.** Before writing, ask where the detail belongs: a spec, a config, a design doc, a backlog item. That path goes in the index line's Target field. When no home exists yet, create it in this same turn — a decision whose only home is one log line is a decision the next search will not surface.
4. **Log the surviving need beside a rejection.** Turning down a proposal leaves the problem it addressed standing. Record that problem as its own findable item — a backlog entry, an open question, a ticket — so it outlives the approach that failed to solve it.
5. **Check the file size on the way out.** If the live file has crossed 200 KB, split it now, in this session.

## 3. Completion criteria

The log holds when **every `##` heading in it is followed by a line matching `^> Type: (decision|amendment|correction|closeout|handoff|info) \| Target: ` and every Target other than `none` resolves to something that exists on disk.** Both halves are greppable, so this is a check to run rather than a feeling to have — run it over the whole file after appending, not only over the entry you just wrote.

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
