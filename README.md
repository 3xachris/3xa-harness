<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/hero-dark.png">
  <img alt="3xa-harness" src="assets/hero-light.png">
</picture>

# 3xa-harness

Discipline skills for agents doing long-running real work — the parts of the job that go wrong slowly.

Five skills form one loop around a task: **freeze** what it is, **gate** what only a human can judge, **log** the decisions as they happen, **hand off** the state when work changes hands, **close out** with evidence. One optional add-on sits beside it. MIT, no dependencies, installable in under a minute.

## Pick your weight first

You don't have to adopt the full loop to get value from this repo. Answer five questions about the task in front of you:

```text
New task
│
├─ Could it outlive this conversation, or be picked up by another session?
├─ Is the boundary still unsettled — scope that could keep growing?
├─ Is it handed to someone else (subagent, contractor, teammate)?
├─ Would getting it wrong be expensive to undo?
├─ Does a human have to look at or listen to the result?
│
├─ All no
│   └─ Light: one decision-log entry — what changed, why, where the
│      detail lives. No order, no closeout.
│
└─ Any yes
    └─ Core: workorder + decision-log + honest-closeout
       ├─ work changes hands            → add handoff
       └─ renders / audio / video to judge → add sensory-gate
```

Each condition is unpacked in [When to open the loop](#when-to-open-the-loop). Then take only the weight you answered for:

| Weight | What you take | Where |
|---|---|---|
| **Light** | Nothing to install — the practice is one log entry per change. To carry the skill itself, install the core plugin (unused skills stay silent) or copy `skills/core/decision-log/` alone into your agent's skill directory; there is no decision-log-only plugin. | [The light path](#the-light-path) |
| **Core** | The `harness-core` plugin — the five-skill loop, fired per task by shape. | [Install](#install) |
| **Validation** | Core, plus running `verify_closeout.py` before trusting a closeout. | [Executable closeout check](#executable-closeout-check) |
| **CI** | Validation, plus the GitHub Actions template on every PR that touches an artifacts folder. | [Integration templates](#integration-templates) |

`sensory-gate` only enters when there is something a human must see or hear — a full-path task with no media never opens a gate.

## What this is for

Short tasks forgive a lot. Work that runs for weeks fails in ways prompting doesn't reach:

- **Scope moves while the work runs.** What gets delivered is no longer what was agreed, and nobody can point at the moment it changed.
- **Sensory judgment gets simulated.** An agent looks at a render, decides it's fine, and builds three more steps on top of it. "Looks fine to a language model" and "looks fine to the person who has to ship it" are different claims.
- **Decisions evaporate.** A rejection or a correction gets said once, in a chat, and is gone at the next context reset — so the same mistake or the same argument comes back.
- **State doesn't survive the handover.** Work moves to a fresh session or another person, and what they inherit is whatever's left in one person's memory — which is exactly the part that doesn't travel. The next session re-discovers the state instead of continuing from it.
- **Reports outrun the evidence.** A summary written from memory at the end of a long session drifts, and drift runs toward the version where the work went well.

Each skill is one concrete, checkable mechanism: a frozen document, a folder to drag rejects into, an index line you can grep, a report the chat message is copied out of. An agent can follow them, and a human can verify from the same disk state whether it did.

## When to open the loop

Whether to freeze a `workorder` and run the full loop is a question about the task's **shape**, not its size — a big mechanical job and a five-line fix can land on either side of it. Open the loop when the task has any of these properties:

- **It can outlive this conversation.** The work might not finish in one sitting, or a different session — yours tomorrow, or someone else's — will pick it up. A frozen order is what that session reads instead of asking you to remember.
- **The boundary isn't settled yet.** The request is still fuzzy, or "while I'm in here" work keeps looking tempting. Freezing forces the boundary to exist before the first edit.
- **It's handed to someone else.** A subagent, a contractor, a teammate — the order is the whole brief they get, in place of the conversation that produced it.
- **Getting it wrong is expensive to undo.** A schema migration, a deleted dataset, a published release — anything a `git revert` doesn't cleanly fix.
- **A human has to look at or listen to the result.** Renders, voice takes, edited video — `sensory-gate`'s reason to exist, and a workorder is what gives that review a fixed acceptance line to close against.

None of these is "this will take a while": a long, single-sitting refactor that's easy to revert and nobody else will touch doesn't need any of it, no matter how many files it touches. A one-line config change that a different session inherits tomorrow does.

## The light path

Not opening the loop doesn't mean leaving nothing behind. When none of the five properties above apply, skip the order, the budget fuse, and the closeout report — but still write the one `decision-log` entry: what changed, the one-line reason, where the detail lives. That's the fact a cold read actually needs; the workorder's other six fields exist to protect things a five-minute fix doesn't have — scope that could drift, evidence a stranger needs to trust.

All-or-nothing breaks both directions: skip everything, and the small fix that quietly became the big one never got framed as one; require everything, and small fixes get done off the books to dodge the paperwork, which is worse than no paperwork at all. The one log entry is the part worth keeping under any weight.

If a "light" task turns out bigger than it looked — three files in, still finding new edges — that's the signal to stop and write the order retroactively, not to keep going bare.

## Install

Two plugins in one marketplace — take the core, add what you need.

Inside a Claude Code conversation:

```
/plugin marketplace add 3xachris/3xa-harness
/plugin install harness-core@3xa-harness
```

Or from a terminal, same result:

```bash
claude plugin marketplace add https://github.com/3xachris/3xa-harness
claude plugin install harness-core@3xa-harness
```

Codex users can install the same five core skills by copying their folders into the user skill directory:

```powershell
$dest = Join-Path $HOME '.agents\skills'
New-Item -ItemType Directory -Force $dest | Out-Null
Copy-Item skills\core\workorder,skills\core\sensory-gate,skills\core\decision-log,skills\core\handoff,skills\core\honest-closeout -Destination $dest -Recurse -Force
Get-ChildItem $dest\workorder,$dest\sensory-gate,$dest\decision-log,$dest\handoff,$dest\honest-closeout -Filter SKILL.md
```

The final command should list five `SKILL.md` files. Start a new Codex session and describe a matching task to confirm the skill is discovered and invoked.

OpenCode users clone the whole repo into the OpenCode skills directory — not just the inner `skills/` folder, the full repo, so the path comes out `~/.opencode/skills/3xa-harness/skills/core/<skill-name>/SKILL.md`:

```sh
git clone https://github.com/3xachris/3xa-harness.git ~/.opencode/skills/3xa-harness
```

OpenCode auto-discovers every `SKILL.md` under `~/.opencode/skills/`; no config file changes needed. Restart OpenCode for it to pick the skills up.

| Plugin | What it adds |
|---|---|
| `harness-core` | The five-skill loop: `workorder`, `sensory-gate`, `decision-log`, `handoff`, `honest-closeout`. |
| `harness-debug` | `staged-diagnosis` — the expanded version of the core diagnosis loop for errors that resist a first look. |

```bash
claude plugin install harness-debug@3xa-harness
```

Then describe the task normally — "freeze this before we start", "review this batch of renders", "log why we dropped approach X" — and the matching skill fires on its own. Every skill here is model-invoked.

**Other agents.** [skills.sh](https://skills.sh) reads the same repo — the core skills sit at `skills/core/<name>/SKILL.md` and every skill is declared in `.claude-plugin/`, both layouts it understands:

```bash
npx skills@latest add 3xachris/3xa-harness
```

*Unverified in this environment* — the sandbox this README was written in blocks outbound `npm`/`node` traffic at the network layer, so this exact command has not been run end to end here; it follows the form `skills.sh` documents for adding a GitHub repo by `owner/repo`. If it fails for you the way it did here, the error is `npm error code EACCES` / `FetchError ... registry.npmjs.org`, and it means your network, not this repo — the Claude plugin and Codex routes above don't go through npm at all.

**Pick one route: Claude plugin, Codex user skills, OpenCode, or skills.sh.** Each route installs the same skills; choosing more than one leaves every skill twice.

## Executable closeout check

### Before the first artifact

Check this before building anything, not after: [`verify_closeout.py`](verify_closeout.py) needs Python 3.9+ on `PATH`. Confirm it once, before the first order exists:

```bash
python --version
```

If that command fails, or reports a version below 3.9, don't build the artifacts folder around this script — the script itself won't be able to start to tell you that later. Run the same five checks by eye instead:

1. Every `AC-n` in the order has a matching `- [PASS/FAIL/BLOCKED] AC-n` line in the closeout.
2. Every path after `| evidence:` opens.
3. If the closeout's status is `DONE`, a `- Functional verification: ... | evidence: ...` line exists, its evidence path opens, and its description is more than a hash or environment claim.
4. Every gate opening in the decision log — a fenced `yaml` block with a `gate` key, or the legacy `> Gate: ...` line — has a matching disposition (a `disposition` key, or the legacy `> Gate disposition: ...` line); the closeout's `[GATE]` line agrees with that disposition's reviewer and archive; and a non-`none` archive path opens.
5. The decision log has a closeout entry pointing at this report — `type: closeout` with `source: <path to this report>` in the new format, or `> Type: closeout | Target: <path to this report>` in the legacy one.

Running the script catches slips in this by hand faster; it does not replace judging whether the content is right, on a runtime or off one.

The pack includes `verify_closeout.py`, a standalone Python 3 script because Python is commonly present on developer and CI machines and its standard library keeps this check dependency-free. Run it with one frozen order, one closeout report, and the decision log:

```bash
python verify_closeout.py artifacts/order.md artifacts/closeout.md docs/decisions.md --root .
```

It checks that acceptance IDs are answered one by one, evidence paths exist, `DONE` has an independent functional verification, every opened gate has a named disposition and archive path when needed, and the decision log points to this report. This is a first-class handoff check: run it locally or in CI before asking a human to trust the closeout. Findings are candidate warnings for a human; they are not an automatic content verdict. A legacy report without the structured fields prints `Unable to verify, skipped` and exits differently from a completed check. The final line always states: this script checks form only; whether the content is correct is for a human.

Claude Code hook binding is optional project wiring; the script itself is intended to be run by a person or CI.

| Skill | Failure it closes |
|---|---|
| [`workorder`](skills/core/workorder/SKILL.md) | Scope drift — freeze the task and its acceptance lines before the first edit, run it to done in one pass. |
| [`sensory-gate`](skills/core/sensory-gate/SKILL.md) | Simulated judgment — batch what only a human can see or hear into one reviewable folder. |
| [`decision-log`](skills/core/decision-log/SKILL.md) | Evaporating decisions — one append-only log a cold session reads before the code. |
| [`handoff`](skills/core/handoff/SKILL.md) | State that dies at the handover — one wide snapshot at the moment work changes hands. |
| [`honest-closeout`](skills/core/honest-closeout/SKILL.md) | Reports outrunning evidence — every claim answered with a path a human can open. |
| [`staged-diagnosis`](addons/debug/skills/staged-diagnosis/SKILL.md) | Errors that resist a first look — six stages, each producing what the next runs on. |

Each skill carries its rules, its steps, and a completion criterion you can check — the formats, fixed fields, and exact paths live in each `SKILL.md`, not here. The five core skills also ship a `CASES.md` — the incidents that bought each rule, generalised.

For `DONE`, independent functional verification is deliberately separate from two other questions: hashes establish that the reviewed files are the same files, and environment identity establishes where they ran. Neither proves that the feature works. A sensory gate records the reviewer, batch, and approved scope in the decision log.

## Bring it into an existing project

Keep the harness records beside the project records, for example:

```text
your-project/
├── AGENTS.md                    # or CLAUDE.md: the always-loaded pointer
├── docs/decisions.md            # one append-only decision log
└── artifacts/
    └── checkout-20260807/
        ├── order.md
        ├── closeout.md
        └── gate/review-01/
```

The `decision-log` skill makes a new session find the records automatically: add this once to the file your agent always loads:

```markdown
## Decision log

`docs/decisions.md` — the decisions, rejections, and corrections for this project, newest last. Read it before starting work here.
```

Put the order, gate folders, evidence, and closeout under one artifacts folder. Existing issues and pull requests become evidence paths or links in the order and closeout; test reports become the evidence for the relevant `AC-n` line and, when run independently, the `Functional verification` line. The decision log records the gate opening, human disposition, corrections, and a final `closeout` pointer to the report. Run the verifier with the order, closeout, log, and project root:

```bash
python verify_closeout.py artifacts/checkout-20260807/order.md artifacts/checkout-20260807/closeout.md docs/decisions.md --root .
```

## Works well with Obsidian — recommended, not required

`decision-log` and `handoff` are plain Markdown: a YAML block under each entry, and `[[path/from/root/file.md#Heading]]` WikiLinks between entries. Nothing here needs an app — an agent reads the files directly, and a human reads the same text cold, with or without a renderer. Opening the same folder as an Obsidian vault adds two things that are otherwise hand-maintained: renaming a file updates every `[[...]]` that pointed at it, and the backlinks panel shows which entries reference a given one. Both are read-only conveniences on files this pack already writes — no Obsidian-specific syntax (no Dataview queries, no Templater scripts) ever appears in them, so nothing breaks if you don't install it.

Recommended because it's a large existing user base your team may already be on, not because any skill here depends on it. Every skill, and `verify_closeout.py`, behave identically with or without Obsidian in the loop. Commercial/team use of Obsidian carries its own licensing terms, separate from this repo's MIT license — check [obsidian.md/pricing](https://obsidian.md/pricing) before adopting it for a team; any plain-text or Markdown editor reads these files just as well if that doesn't fit.

## Integration templates

Three files under [`templates/`](templates/) wire the pack into the places a PR actually gets reviewed — copy them in, don't rebuild them:

| Template | Copy it to |
|---|---|
| [`PULL_REQUEST_TEMPLATE.md`](templates/PULL_REQUEST_TEMPLATE.md) | `.github/PULL_REQUEST_TEMPLATE.md` — mirrors `honest-closeout`'s report sections, so the same acceptance and verification lines answer both the PR and the closeout. |
| [`ISSUE_TEMPLATE_workorder-request.md`](templates/ISSUE_TEMPLATE_workorder-request.md) | `.github/ISSUE_TEMPLATE/workorder-request.md` — captures a task's rough shape, plus a checklist against "When to open the loop", before anyone freezes it into an order. |
| [`ci-verify-closeout.yml`](templates/ci-verify-closeout.yml) | `.github/workflows/verify-closeout.yml` — runs `verify_closeout.py` on every PR that touches an artifacts folder. Copied verbatim it checks this repo's own `.verification-demo/`; edit the three paths in the run step to point at your project. |

The CI template deliberately does not fail the build on a warning — `verify_closeout.py`'s exit code 1 is a candidate finding for a human, matching the "Honest boundary" section below, not a merge gate. The template's own comments say what to remove if a team wants a hard gate instead.

## Minimal end-to-end example

The checked-in files under [`.verification-demo/`](.verification-demo/) are one small task wired from order to gate to closeout. They are intentionally ordinary Markdown so they can be copied into an existing project:

```text
.verification-demo/
├── order.md
├── closeout.md
├── decisions.md
├── evidence/verification.txt
└── gate/review-01/approved.txt
```

The order freezes `AC-1` and `AC-2` with the same `AC-n` marker that the closeout answers. The log opens and disposes `review-01`, then points to the closeout. The closeout records the independent test, the gate approval, and evidence paths. Run this exact regression example from the repository root:

```bash
python verify_closeout.py .verification-demo/order.md .verification-demo/closeout.md .verification-demo/decisions.md --root .
```

It should parse the structured fields and finish with exit code `0`; the final boundary line still means that a human judges the content.

## It's working if

Signals you can check in your own work, without opening a `SKILL.md`:

- The agent asks its questions **at the start**, in one round, instead of stopping every twenty minutes for a decision it could have raised up front.
- A review request arrives as **one folder and one plain question**, and answering it takes a drag rather than a paragraph.
- A fresh session opens the decision log **before** it opens the code, and stops re-litigating things you settled last week.
- A completion report tells you where the evidence is for each thing it claims — and says plainly when something failed, instead of arriving polished with the failure sanded off.
- You find yourself checking the disk to verify a claim, and the disk agrees.

## Honest boundary

These are protocols, not enforcement. Nothing here blocks a step from being skipped — they work because they're specific enough to follow and checkable enough that skipping shows. Physically enforcing a gate is a hook in your own project, and it's worth writing.

## Credits

The writing standard is Matt Pocock's [`writing-for-agents`](https://github.com/mattpocock/skills): positive targets over prohibitions, one source of truth per meaning, completion criteria that are checkable and exhaustive. The staged-diagnosis order is a generalisation of the same repo's `/diagnosing-bugs`; `handoff` generalises the same repo's `handoff` and `claude-handoff` commands into a model-invoked, checklist-driven skill. All MIT.

繁體中文版：[README.zh-TW.md](README.zh-TW.md)

## License

MIT — see [LICENSE](LICENSE). Use it, fork it, ship it in your own product.
