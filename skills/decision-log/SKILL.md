---
name: decision-log
description: Maintain a single append-only decision log so an agent's decisions, rejections, and their reasons survive context resets and handoffs between sessions. Use on any long-running project where an agent makes decisions that a later session (or a different agent) needs to be able to find and trust without re-deriving them. Triggers on tasks involving project history, changelogs, "why did we decide X", session handoff, or any request to record a decision, rejection, or correction for future reference.
---

# Decision Log

Context resets. A fresh session (or a different agent) has no memory of why a decision was made, only what's written down. This skill defines a log format that a cold read can trust and search without opening every entry.

## 1. Vocabulary and rules

- **One file, append-only.** Past entries are never edited or deleted. Corrections get a new entry that references the old one — the log is a timeline, not a wiki page.
- **Every entry starts with an index line.** Directly under the entry's heading, the first line is a fixed-format index: `> Type: <decision|closeout|correction|info|handoff> | Target: <file path, or "none (pure process note)">`. A reader — human or machine — should be able to tell what kind of entry this is and where its real content lives without reading past this line.
- **Entries stay short.** A cap of roughly five lines per entry. The log records *that* a decision was made, its one-line reason, and *where* the full detail lives — it never becomes a second copy of that detail. If an entry is getting long, the content belongs in a proper document and the log entry should just point to it.
- **A running summary lives at the top of the file.** Kept current on every append, it lets a reader get the current state in one glance instead of scrolling through history to reconstruct it.
- **Volume splitting.** As a concrete anchor rather than a vague "too big": once the live file approaches a few hundred KB, several common file-read tools start truncating or erroring on it — that's the trigger to split, not a wall to wait until you hit. When it's time, older entries move to a dated archive file and the live file keeps only the current period. The live file's summary and the archive index both get updated at split time.

## 2. Workflow

1. **Log the moment a decision, rejection, correction, or handoff happens** — not at the end of a session from memory. Logging from memory after the fact is how entries drift from what actually happened.
2. **Entry gate**: before writing the entry, ask "does this decision have a file it belongs to?" If yes, put that path in the index line's Target field. If no — the decision would otherwise live only in this log entry and nowhere else — create or register that home now, in the same turn. A decision with no target anywhere is a decision a future search can't find.
3. **Rejection cascade**: rejecting a proposal does not delete the need behind it. When logging a rejection, log the underlying need as a separate, findable item (in a backlog, task list, or wherever open items live) — otherwise the need disappears along with the rejected proposal, and nobody notices until it's needed again.
4. **Keep the summary table honest.** Every append that changes the current state (open items, counts, current focus) updates the summary block at the top in the same edit — don't let the summary drift out of sync with the entries below it.
5. **Check file size on append.** If the live file has grown past the split threshold, perform the volume split as part of this same session's work, not as a separate deferred task.

## 3. Before you report this done

After writing an entry, re-read only its index line — not the body — and ask: could a cold reader, searching this log weeks from now with no memory of this session, tell what happened and where to look from that one line alone? If the answer is no, the entry isn't finished; fix the index line before moving on. This is the same test a fresh session will actually apply.

## Example entry

Copy this shape — the index line is the part that matters most:

```markdown
## 2026-08-06 Rejected the caching proposal, kept the underlying need
> Type: correction | Target: backlog.md#cache-invalidation

Rejected the write-through cache approach — added complexity the read
volume doesn't justify yet. The staleness problem it was solving is
still real: logged as an open item in backlog.md so it isn't lost with
the rejected approach.
```

## Judgment cases (generalized, no project-specific detail)

1. **A rejection buried its own need.** A proposal was rejected and logged as "rejected — approach X doesn't fit." The requirement the proposal was trying to solve was never logged anywhere else. Weeks later, nobody remembered the requirement existed, because it only ever lived inside the rejected proposal's shadow. Rule: log the rejection and the surviving need as two separate facts.
2. **The log became a second copy of the source.** One session wrote many long entries in a single day, each restating content that already existed in full in a source document. The log's job — a short pointer to the real content — was defeated by the log itself becoming the thing people read instead of the source. Rule: entries point; they don't duplicate.
3. **Missing index line, unfindable entry.** An entry was written as a plain paragraph with no index line. A later automated scan built to recover "what decisions were made and where" had to guess from keywords and missed it. Rule: the index line is what makes an entry machine-findable — write it at the time, don't rely on a scanner to reconstruct it later.
