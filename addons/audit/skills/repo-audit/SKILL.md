---
name: repo-audit
description: Check a project's own records and code for the decay that accumulates without anyone noticing — a log past its split threshold, pointers that no longer resolve, corrections piling up on one cause, debt signals in source, documents nothing references any more — and report each finding with the file, the line, and the edit that closes it. Use when picking up a project cold, before a release, when the records feel out of date, when deciding whether a cleanup is worth its cost, or on a recurring schedule.
---

# Repo Audit

Records rot in the direction nobody is looking. A log grows past the size where tools read it whole; a `source:` points at a file that got renamed; the third local fix lands on a cause that deserved one real fix; a document stops being referenced and nobody notices it is now folklore. None of these announce themselves, and all of them are measurable.

The script [`repo_audit.py`](repo_audit.py) runs five such measurements and prints one report. It answers questions about **form** — does this resolve, is this over the line, how many times has this happened. It answers nothing about meaning, and says so in the report rather than leaving the reader to assume otherwise.

## 1. What it measures

| Check | Question | Reads |
|---|---|---|
| **size** | Is anything past the limit set for its class, and what grew since last time? | file sizes; the decision log against its own split threshold |
| **pointers** | Does every reference resolve? | `source:` keys in the log's YAML blocks, `[[WikiLinks]]` and their headings, `\| evidence:` paths, relative Markdown links |
| **corrections** | Is one cause collecting patches instead of a fix? | `correction` and `amendment` entries in the log, grouped by `root_cause` or tag |
| **signals** | Where does the code carry the shapes debt travels in? | swallowed exceptions, disabled checks, temporary markers, hand-sync comments, dates baked into shared constants, deprecated-but-imported modules |
| **references** | What has nothing referred to lately? | tracked documents against the set of files that would cite them |

**Three of the five read this pack's own record formats and need them to exist.** Size, pointers, and corrections resolve `decision-log` entries — the fenced YAML blocks, their `source:` keys, and `type: correction` with a `root_cause` or a tag. On a project with no such log they have nothing to read, and each says so by name in part 5 of the report rather than returning a clean result. Signals and references read generic file properties and work on any repository. Whether that split makes the tool worth having depends on which records your project actually keeps — the decision test in the README section *Record audits* is the place that question is answered, not here.

## 2. Run it

```bash
python repo_audit.py --root . --report artifacts/repo-audit.md
```

With no config it assumes the layout the README recommends — `docs/decisions.md`, `docs/**`, `artifacts/**`, source under the usual extensions. Everything else is one file at the project root:

```json
{
  "repo_audit": {
    "decision_log": "notes/decisions.md",
    "size_targets": [{ "glob": "notes/**/*.md", "limit_kb": 80 }],
    "stale_days": 180,
    "patch_threshold": 3
  }
}
```

**The thresholds are yours.** The defaults are round numbers chosen to be visible, not measured facts about your project: 200 KB for the log split is the figure `decision-log` names, three corrections on one cause is where a patch count starts arguing for a root fix, 180 days is a guess about how long a live document goes unreferenced. Change them the first time one of them is wrong, and say why in the log. A threshold nobody set is a threshold nobody believes.

Exit codes: `0` nothing found, `1` findings for a human, `2` could not check — a malformed config, or no records and no source matching the globs at all. `--only size,pointers` narrows a run. A signal that is wrong for your codebase — a project built on deliberate fallbacks will light up `SWALLOWED-ERROR` on every file — goes in `disable_signals` by id, and the report then states in part 5 that this run says nothing about it. Turning a check off is allowed; turning it off silently is not.

An unknown key in the config stops the run with exit `2` rather than being ignored. A typo'd setting that quietly does nothing is a check you think you configured and didn't.

## 3. Read the report

The report is written for whoever has to act on it, which is usually an agent working through it item by item. Five parts, in this order:

1. **Broken as found** — facts about the records: a path that does not resolve, a file past a limit someone set, a count past a threshold someone set. Establishing these needs no interpretation. Closing several of them still needs a *decision* — "correct the path, or point it at whatever replaced the target" is a fork, not an edit — and the row says so rather than dressing a choice up as a fix.
2. **Look before acting** — the code signals. A regex cannot tell a deliberate fallback from an accidental one, so each row is a place to look, and the looking is the work. These are kept out of the first table on purpose: a disabled validation flag and an oversized Markdown file do not belong at the same weight, and flattening them is how a report gets read once and never again.
3. **Volume** — how much was scanned and how much came back, so a reader can price the work before starting rather than discovering halfway that the job is a hundred files.
4. **Standing checks** — measurements that never finish, because what they measure keeps moving. These belong in CI or on a schedule; clearing today's findings does not close them.
5. **What this run could not measure** — every limit that applied to *this run*, including any check that read an empty input set and therefore reported nothing without proving anything.

Part 5 is the part to read first when the report is empty. A clean report from a check that had nothing to read is not a clean project.

What it actually looks like, trimmed from a run over a small deliberately-broken project:

```markdown
## Broken as found

| id | autonomy | what | where | what closes it |
|---|---|---|---|---|
| `PTR-SOURCE` | needs-decision | a decision-log entry points at a file that is not on disk | `docs/decisions.md:16 -> docs/missing-doc.md` | create the document the decision belongs in, or correct the path |
| `PTR-EVIDENCE` | needs-decision | an evidence path in a report does not exist | `artifacts/task-01/closeout.md:6 -> artifacts/task-01/absent.log` | attach the evidence file, or mark the line FAIL with the reason it has none |
| `PATCH-COUNT` | needs-decision | 3 corrections share one cause ('retry-storm'), at or over the escalation threshold of 3 | `docs/decisions.md:16,27,38` | stop patching and freeze a workorder against the cause itself |

## Look before acting

| id | autonomy | what | where | what closes it |
|---|---|---|---|---|
| `DATED-CONSTANT` | needs-decision | a date baked into a constant, in a module other files import | `src/service.py:2  RELEASE_DIR = "out/2026-01-05_release" [imported by 1: src/client.py]` | take the date from a parameter or the run's own clock |

## Volume

| check | scanned | result |
|---|---|---|
| pointers: references resolved | 10 | 4 broken |
| corrections: entries grouped by cause | 4 | 1 causes, 1 ungrouped |
| signals: source files scanned | 2 | SWALLOWED-ERROR=1, CHECK-DISABLED=2, DATED-CONSTANT=1 |
```

Note what the `where` column carries: the file, the line, and enough of the actual text to judge without opening it — a whole source line rather than the matched fragment, and for an imported module, who imports it.

**Two axes, because they answer different questions.** Which table a row sits in is *certainty* — is this established, or is it a shape that often means something. The `autonomy` column is *whether you may act alone* — `mechanical` is one edit whose right answer is already determined, `needs-decision` is a fork someone has to pick. They are close to orthogonal: a broken relative link is established and mechanical, while a missing evidence path is equally established and firmly needs-decision, because the two branches are "produce the evidence" and "mark a delivered closeout FAIL". An agent working the report acts on `mechanical` rows and brings the rest back.

Both axes are the tool's opinion about form, not about your project. A `mechanical` row can still be the wrong thing to do in a context the script cannot see.

## 4. What it deliberately does not answer

- **Whether a finding matters.** A regex cannot tell a deliberate fallback from an accidental one. Signals narrow where to look; they never constitute a work list on their own.
- **Whether a stale document should be retired.** That needs a second condition — that something else now covers what it does — and that is a reading, not a count. The check supplies the count.
- **How long a marker has been sitting there.** File modification time answers "when was this file last touched", which runs opposite to the question: the busiest files look the freshest. Only version control answers it, and this script does not shell out to one.
- **Whether an untagged correction belongs to an existing group.** Corrections group by `root_cause` or tag, written at the time. One written without either groups with nothing, and the report says how many.
- **Anything about meaning, taste, or correctness.** Nothing here reads a render, listens to audio, or judges whether a decision was right.

Each of these appears in the report itself, in the run's own words, so the reader is never left assuming that what the run found is all there is.

## 5. Completion criteria

The run is finished when every row in *Broken as found* and *Look before acting* has been closed, converted into an order, or dismissed with a written reason — and re-running produces a report whose findings table you recognise as the leftovers you chose to leave.

Then check the run itself, because the failure mode here is a check that cannot fail: read the *Volume* table and confirm every check scanned a non-zero number of things. A row reading zero means a glob points somewhere the project isn't, and the clean result beside it means nothing at all.

## Judgment cases

Four checks that ran, reported, and were believed while measuring something other than what they claimed: [`CASES.md`](CASES.md).
