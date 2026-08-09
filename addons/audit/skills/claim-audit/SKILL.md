---
name: claim-audit
description: List the lines in a project's records that state a number as fact with nothing a reader could check it against, then handle each one by adding the source, marking it [UNVERIFIED], or deleting the claim. Use when writing or reviewing a decision log, workorder, closeout, or spec that a later session will trust; when a report's numbers came from memory rather than measurement; or when setting up a check that catches unsourced claims at the moment they are written.
---

# Claim Audit

A record is read by someone deciding whether to act without re-deriving it. A number they can trace — to a path, a date, a measurement, a run — costs them one look. A number that arrives bare costs them the whole derivation, which is the work the record existed to save. So the checkable form is:

**Every number written into a record either carries a source, or is marked as unverified.**

The script [`claim_audit.py`](claim_audit.py) finds the lines that satisfy neither. It is a **candidate detector, not a judge**: it reads shape, not meaning, so some of what it returns will be fine as written.

How noisy that is, measured rather than asserted — one run over this repository, reproducible with `python addons/audit/skills/claim-audit/claim_audit.py --root . --full`: 21 Markdown records scanned in about a tenth of a second, 2 lines left for a human, 3 more auto-classified as restatements (§3, *The fifth disposition*), and both human-judged lines were false positives on review — budget lines declaring a fuse rather than reporting a measurement. So the per-run reading cost here was five lines, and the finding count was zero. That is one small documentation-heavy repo that had already been cleaned against this tool, not a precision figure for yours; run it on your own records before deciding how much attention it deserves, and before binding it to anything (§5). The first run on an older project is the expensive one — that is what the baseline (§4) exists for.

## 1. What counts as a source

A line passes when it carries any of these, on the same line as the number:

| Signal | Example | Checked how |
|---|---|---|
| A path with a line number | `verify_closeout.py:16` | **the file must exist** |
| A filename in backticks | ``the limit lives in `config.json` `` | **the file must exist** |
| A link, or a WikiLink | `[[docs/decisions.md#2026-08-01 Picked the cache]]` | **the file must exist** |
| A date | `2026-08-07` | shape only |
| A field naming its origin | `evidence: artifacts/run.log`, `source: docs/spec.md` | shape only |
| A measurement verb | measured, benchmarked, reproduced, profiled, counted, timed | shape only |
| A reference id | `AC-3`, `#412`, `PROJ-88`, `§4` | shape only |

The split matters. Path-shaped citations are the one source class a scanner *can* verify, so it does: the named file is resolved against the project root and the citing file's folder, and a line whose only citation names a file nobody can open is **not sourced** — writing `` see `plausible-name.md` `` was otherwise a cheaper silencer than hedging, since it cost nothing and weakened nothing. A dead citation poisons its line even when a shape-only signal sits beside it: a claim that leans on a file that is not there has a worse problem than a missing verb. The shape-only rows cannot be checked against anything — a date, a verb, a ticket id are taken on trust, which is a stated boundary, not an oversight; verifying that a cited file *supports* the number is reading, and reading is the human's half.

And a line is left alone entirely when it is honestly hedged — `[UNVERIFIED]`, TODO, TBD, FIXME, or a word like *estimated*, *assumed*, *roughly* standing next to the number it qualifies. Hedging is the behaviour this check wants; flagging it would teach the opposite lesson.

**The exemption list is also the bypass**, and it is worth naming rather than discovering: an agent that learns "adding *estimated* silences this" can retire the check one word at a time. Two things narrow it and neither closes it. A hedge only counts next to the number it modifies, so it cannot be parked at the far end of a paragraph. And a hedged number reads as hedged to the next human, which is the honest outcome the rule wanted — *"roughly 40% faster"* is a weaker claim than *"40% faster"*, and weakening the claim is a real concession, not a free pass. What remains is a judgment nothing mechanical will make for you: **hedging that is not true is a lie the check cannot see**, and it belongs on the review list beside anything else a reader has to take on trust.

The exact built-in patterns are four lists at the top of the script — `DEFAULT_CLAIM_PATTERNS`, `DEFAULT_SOURCE_PATTERNS`, `DEFAULT_VERIFIABLE_PATTERNS`, `DEFAULT_EXEMPT_PATTERNS` — plus the existence rule above. Read them before arguing with a result; they are short and they are the whole specification.

**The unit is the line, and that is a real limit on what it catches.** A source signal anywhere on a line covers every number on it, so a long unwrapped paragraph that cites one file gets a free pass on the other four numbers in the same sentence. Fenced code blocks and table rows are skipped entirely. What comes back is a floor, not the complete list — treat a clean run as "nothing obvious", never as "every number here is sourced".

## 2. Run it

```bash
python claim_audit.py --root .
```

With no config it reads `docs/decisions.md`, `docs/**/*.md`, and `artifacts/**/*.md` — the layout the pack's README recommends. A project that keeps its records elsewhere sets `claim_audit.targets` in `.harness-audit.json` at the project root, and changes nothing else:

```json
{ "claim_audit": { "targets": ["notes/**/*.md", "rfcs/**/*.md"] } }
```

`claim_patterns`, `source_patterns`, and `exempt_patterns` accept extra regexes that **add to** the built-ins, so a project can teach it one domain unit without losing the rest of the detection. Exit codes: `0` nothing to handle, `1` candidates for a human, `2` could not check (bad config, no matching files, interpreter too old).

## 3. Handle every hit, one of three ways

Nothing about a hit is decided until a person or an agent looks at it. There are exactly three dispositions, and each one is an edit:

1. **Add the source** — the number came from somewhere; name where. This is the outcome that makes the record worth more than it was.
2. **Mark it `[UNVERIFIED]`** — the number is real but unconfirmed at its origin this session. The tag is what lets a reader tell a checked statement from a confident one.
3. **Delete the claim** — it was never load-bearing, and prose survives without it.

A fourth answer, *"false positive, and here is why"*, is legitimate and belongs written down beside the run — a version number in a shell command, a budget line declaring a fuse rather than reporting a measurement. Write the reason, not just the verdict: an unexplained dismissal is indistinguishable from an unread one.

### The fifth disposition, which the tool makes for you

A line whose every distinctive number already appears on a **sourced line in the same file** is reported as a **restatement** and does not count as work. This is a checklist repeating a threshold the document pinned and justified earlier — the pack's own `decision-log` skill states its 200 KB split limit once with a reason (its `SKILL.md`, section 1) and repeats it in a step list, and asking for a second citation would teach padding. A number has to be two characters or more to carry this identity: `1` and `5` are in every other sentence, and matching on them would let anything wash anything.

**It is a whitewash surface and you should know its shape.** Unlike a hedge, a restatement does not weaken the claim at all — the sentence stays fully confident and simply leaves the work list. Anyone who can add one sourced line mentioning the same number can retire a bare claim elsewhere in that file. Three things bound it: restatements are always printed, under their own heading, with the count in the summary line; they are scoped to one file; and `--strict` folds them back into the candidate list and the exit code, which is the setting to use in CI if you would rather have the noise than the hole.

```bash
python claim_audit.py --root . --strict
```

## 4. The baseline, and the one way to misuse it

```bash
python claim_audit.py --root . --baseline
```

This records the current findings, keyed by a hash of each line's content, and from then on the tool reports only lines added afterwards. Content keys, not line numbers: inserting a paragraph shifts every line below it, and a position-keyed baseline reports all of them as new.

The baseline exists so that an existing project can adopt this check without a thousand-line backlog blocking the first run. It is a record of what has been judged — **not a mute button**. Re-running `--baseline` to clear a set of findings you have not looked at converts a working check into a green light, and the next reader has no way to tell which it was.

It writes to `.harness-audit-baseline.json` at the project root, or wherever `claim_audit.baseline` points. **Commit it.** A baseline outside version control is a per-machine file: every teammate's first run hands them the whole backlog, everyone re-baselines to get past it, and the check is dead inside a week. Committed, it becomes a reviewable artifact — a diff that adds twenty hashes is someone declaring twenty claims judged, and that is a thing a reviewer can ask about. The same argument says don't commit `.harness-audit-history.jsonl` or `.harness-audit-references.json`: those are regenerated every run and carry no decisions.

## 5. Optional: have it run itself

A check that needs someone to remember it is a check that eventually doesn't run. The script can be bound to whatever fires when a file is written in your harness, so the author sees the finding while the claim is still in their hands. In Claude Code that is a `PostToolUse` hook — see the README section *Record audits* for the exact block. The binding is optional project wiring; the script is meant to be runnable by a person or CI without it.

In hook mode the script fails **open**: any internal error lets the edit through, and reports the error rather than swallowing it. This is an audit, not a door lock, and a gate that looks like it is running while silently doing nothing is worse than no gate.

## 6. Completion criteria

Every candidate from the run has one of four things attached: a source, an `[UNVERIFIED]` tag, a deletion, or a written reason it was dismissed. Check it by re-running: the count of lines a human still owes an answer for is zero, and the baseline was not rewritten to get there.

Then read one flagged line the way a stranger would, and ask what they would have to do to check it. If the answer is still "ask the author", the source you added names a person, not a place.

## Judgment cases

Four ways this check has failed in practice, and the rule each one bought: [`CASES.md`](CASES.md).
