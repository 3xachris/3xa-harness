---
name: decision-log
description: Keep one append-only log where decisions, rejections, and corrections survive a context reset — each entry carrying a fixed index line a later session can search, and pointing at where the full detail lives instead of copying it. Read it first when picking up a project you have no memory of; write to it when recording why something was chosen or dropped, when handing over to a fresh session or another agent, or when answering "why did we do it this way" months later.
---

# Decision Log

A fresh session inherits what was written down and nothing else. The log carries a decision across that boundary, so it is written for the **cold read**: someone who was not there, searching months later, with no memory to fill the gaps. What that reader needs above all is to tell, from a scan, which entry holds what they came for.

## 1. Shape of the log

- **One file with two layers.** The entry layer is append-only: once written, an entry stays as written, and a change of mind arrives as a new entry that references the old one. The summary layer is a maintained field at the top and is overwritten as the current state changes. Reading the entries top to bottom shows how the thinking moved, which is usually the question being asked.
- **Every entry opens with a fenced YAML block**, directly under its heading:
  ````markdown
  ## 2026-08-07 Dropped the write-through cache

  ```yaml
  type: decision
  status: closed
  tags: [architecture]
  source: docs/backlog.md
  ```
  ````
  Four keys, always present: `type` — one of `decision` (a choice made), `amendment` (a frozen scope changed, from `workorder`), `rejection` (a human turning an artifact down, from `sensory-gate`), `correction` (a human correcting the work), `closeout` (a task finished and reported, from `honest-closeout`). A value nothing produces is a value the format check spends its strictness guarding for no one. `status` — `open` if this entry leaves something for a later entry to close (a gate awaiting disposition, a decision flagged for revisit), `closed` if the entry is self-contained. Set once, at write time, like every other part of the entry — an entry that later gets closed is closed by a *new* entry pointing back at this one with a WikiLink (§4), never by editing this block. `tags` — free-form labels for grouping and filtering, `[]` if none apply. `source` — path from the project root to where the full detail lives, or the bare word `none`.
  A gate or a closeout entry carries extra keys beyond these four (§5) — same idea as Obsidian properties, where `tags`/`aliases`/`cssclasses` are the defaults and anything else you add is still a property.
  This block is what makes an entry parseable by machine and skimmable by human. Write it at the time — it is the one part of an entry that cannot be reconstructed afterwards.
- **Not literal file frontmatter.** Real YAML/Obsidian frontmatter is a file-level concept — one block, at the very top of the file. This log is one file with many entries, so what sits under each heading is a YAML-shaped fenced block, not something Obsidian's Properties panel will render specially. It is still genuine YAML: parseable with a real parser instead of an ad hoc line regex, and it carries the same four keys the frontmatter convention specifies (`type`/`status`/`tags`/`source`) so a decision that later graduates into its own note file needs no field rework, just the `---` delimiters swapped in. See `CASES.md` if you're deciding whether to split this file into one-note-per-decision instead — that trade is real, and not the one this format makes.
- **Entries point.** Roughly five lines below the block: what was decided, the one-line reason, and where the full detail lives. When an entry starts growing, the content belongs in a real document and the entry belongs pointing at it.
- **Update the summary layer** — open items, current focus, counts — in the same edit as the entry below it. It gives the current state in one glance, and stays trustworthy for exactly as long as that pairing holds.
- **Split at a threshold you set in advance** — 200 KB unless you have a measured reason for another number. The point is having a line at all: file-reading tools truncate a long log silently, and a log you believe you read in full is worse than one you know you didn't. At the line, older entries move to a dated archive, the live file keeps the current period, and both the summary and the archive index are updated in the same pass.

## 2. Install the pointer, once per project

A log that nothing points at is read by whoever already knew it was there. What makes it reach a session that has no memory of this one is a line in the project's always-loaded file — `AGENTS.md`, `CLAUDE.md`, or the equivalent file required by the agent harness:

```markdown
## Decision log

`docs/decisions.md` — the decisions, rejections, and corrections made on this project,
newest last. Read it before starting work here.
```

Install that line the first time this project gets a log, and the read side runs itself from then on: every session loads the pointer, and the pointer names the file and the moment to open it. Where a project already carries such a section, add to it rather than starting a second one.

## 3. Log the moment

1. **Write the entry as the decision happens.** Recall at the end of a long session smooths over the parts that were contested — which are the parts a later reader came for.
2. **Give the decision a home.** Before writing, ask where the detail belongs: a spec, a config, a design doc, a backlog item. That path goes in the block's `source` key. When no home exists yet, create it in this same turn — a decision whose only home is one log entry is a decision the next search will not surface.
3. **Log a `correction` the moment a human corrects the work** — a stop, a diagnosis you were handed, a call you got wrong and were told so. The entry names what changed and who supplied it, because this is the source the closeout's account of human input is built from, and it cannot be reconstructed later from a session's memory of itself.
4. **Log the surviving need beside a rejection.** Turning down a proposal leaves the problem it addressed standing. Record that problem as its own findable item — a backlog entry, an open question, a ticket — so it outlives the approach that failed to solve it.
5. **Check the file size on the way out.** If the live file has crossed 200 KB, split it now, in this session.

## 4. Cross-reference with WikiLinks

An entry that resolves, supersedes, or explains another one names it with a WikiLink instead of a loose description — `[[docs/decisions.md#2026-08-01 Picked the read-through cache]]` for another file, `[[#2026-08-01 Picked the read-through cache]]` for a heading in this same file. Always the relative path from the project root plus the `.md` extension, never a bare note name: this file is read with zero dependencies (nothing here requires an app installed to be readable), so a link has to stay resolvable by a plain `grep` for the target heading text, not only by a vault index. Obsidian, if installed, additionally renders it clickable and updates it automatically when the target file is renamed; without Obsidian, `[[x]]` still reads as "the entry titled x has the detail" to a human or an LLM scanning the raw file, and the reader follows it by searching for the heading text — one grep, not a broken promise.

Use it for what plain prose can't carry as a fact: a `status: closed` decision points at the entry that closed it; a `rejection` points at the backlog item its surviving need lives in (§3.4); a `handoff` points at the decision-log entries it's built from rather than restating them (`handoff` skill, §"Write for the reader, not the writer").

## 5. Entry shape, including gates and closeouts

A gate open and its later human disposition carry extra keys beyond the four core ones, because there is more to record than what/where:

````markdown
## 2026-08-07 Opened review gate

```yaml
type: decision
status: open
tags: [gate]
source: artifacts/order.md
gate: review-01
batch: review-01
files: render.png=sha256-...
```

The status endpoint batch is ready for human review.
````

````markdown
## 2026-08-07 Approved review gate

```yaml
type: decision
status: closed
tags: [gate]
source: artifacts/gate/review-01/approved.txt
disposition: review-01
reviewer: Ada
scope: all files in batch
archive: none
```

Ada approved the reviewed batch. Closes [[#2026-08-07 Opened review gate]].
````

The opening entry is written before review, the disposition entry after the human answer — two entries, not one edited in place, because the log is append-only (§1). A rejected batch uses the existing `rejected-archive/<gate-folder>/` path in `archive`.

A closeout entry needs only the four core keys — `source` is the path to the report:

````markdown
## 2026-08-07 Closed demo verification

```yaml
type: closeout
status: closed
tags: []
source: artifacts/closeout.md
```

The task passed its acceptance lines and independent test.
````

A plain decision, unremarkable in shape:

````markdown
## 2026-08-06 Dropped the write-through cache, kept the staleness problem

```yaml
type: decision
status: closed
tags: [architecture]
source: docs/backlog.md
```

Write-through cache rejected — complexity the current read volume doesn't
earn. The staleness it was solving is still real and is now an open item in
backlog.md, so it survives the approach that was meant to fix it.
````

## 6. Older logs keep working

Some entries in a long-running log will predate this format — a plain `> Type: decision | Target: docs/backlog.md` index line, or gate lines shaped `> Gate: ... | Batch: ... | Files: ...` and `> Gate disposition: ... | Reviewer: ... | Scope: ... | Archive: ...`. Append-only means those entries stay exactly as written (§1): don't rewrite them into frontmatter to make the file look consistent. A log with old-format entries above and new-format entries below is the expected shape of a log that's been running since before this convention existed, not a defect. `verify_closeout.py` reads both forms in the same pass.

## 7. Completion criteria

The log holds when all four are true, checked over the whole file after appending rather than over the entry just written:

- every `##` heading is followed, within a few lines, by either a fenced `yaml` code block whose first key is `type` with one of the five values, or (in an entry old enough to predate this convention, §6) a line matching `^> Type: (decision|amendment|rejection|correction|closeout) \| Target: ` — greppable either way
- every `source` (or legacy `Target`) other than `none` resolves to something that exists on disk — greppable
- the running summary's open items match the entries below it — a read of one block against the headings
- the project's always-loaded file names the log — a look at one file

## Judgment cases

Four logs that were kept faithfully and still failed the cold read, or nearly took a wrong turn in the name of tidiness: [`CASES.md`](CASES.md).
