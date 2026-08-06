# 3xa-harness

Discipline skills for agents doing long-running real work — the parts of the job that go wrong slowly.

Four skills form one loop around a task: **freeze** what it is, **gate** what only a human can judge, **log** the decisions as they happen, **close out** with evidence. Two optional add-ons sit beside it. MIT, no dependencies, installable in under a minute.

## What this is for

Short tasks forgive a lot. Work that runs for weeks fails in ways prompting doesn't reach:

- **Scope moves while the work runs.** What gets delivered is no longer what was agreed, and nobody can point at the moment it changed.
- **Sensory judgment gets simulated.** An agent looks at a render, decides it's fine, and builds three more steps on top of it. "Looks fine to a language model" and "looks fine to the person who has to ship it" are different claims.
- **Decisions evaporate.** A rejection or a correction gets said once, in a chat, and is gone at the next context reset — so the same mistake or the same argument comes back.
- **Reports outrun the evidence.** A summary written from memory at the end of a long session drifts, and drift runs toward the version where the work went well.

Each skill is one concrete, checkable mechanism: a frozen document, a folder to drag rejects into, an index line you can grep, a report the chat message is copied out of. An agent can follow them, and a human can verify from the same disk state whether it did.

## Install

Three plugins in one marketplace — take the core, add what you need.

```bash
claude plugin marketplace add https://github.com/3xachris/3xa-harness
claude plugin install harness-core@3xa-harness
```

| Plugin | What it adds |
|---|---|
| `harness-core` | The four-skill loop: `workorder`, `sensory-gate`, `decision-log`, `honest-closeout`. |
| `harness-debug` | `staged-diagnosis` — six ordered stages for the errors that resist a first look. |
| `harness-router` | `/ask-harness` — describe your situation, get told which skill fits. |

```bash
claude plugin install harness-debug@3xa-harness
claude plugin install harness-router@3xa-harness
```

Then describe the task normally — "freeze this before we start", "review this batch of renders", "log why we dropped approach X" — and the matching skill fires on its own. `/ask-harness` is the one you type.

**Other agents.** [skills.sh](https://skills.sh) reads the same repo — the core skills sit at `skills/core/<name>/SKILL.md` and every skill is declared in `.claude-plugin/`, both layouts it understands:

```bash
npx skills@latest add 3xachris/3xa-harness
```

**Pick one route.** The plugin is a managed bundle you subscribe to; skills.sh copies editable files you own. Installing both leaves you with every skill twice.

## What's inside

| Skill | One-line usage |
|---|---|
| [`workorder`](skills/core/workorder/SKILL.md) | Freeze the task first — one sentence, known facts, pinned parameters, a budget fuse, acceptance lines, non-goals — then run it to done in one pass instead of returning at every bump. |
| [`sensory-gate`](skills/core/sensory-gate/SKILL.md) | Batch images, audio, or video into one gate folder with an `NG/` subfolder; the agent holds there, and you reject by dragging a file into `NG/`. Nothing to write. |
| [`decision-log`](skills/core/decision-log/SKILL.md) | One append-only log, each entry opening with a fixed index line and pointing at where the detail lives — plus a one-line pointer in the file your project already loads every session, so the next agent opens the log without being told. |
| [`honest-closeout`](skills/core/honest-closeout/SKILL.md) | Every acceptance line answered with evidence, human corrections credited, background processes proven stopped, and the chat message copied verbatim out of the report. |
| [`staged-diagnosis`](addons/debug/skills/staged-diagnosis/SKILL.md) | Reproduce → minimise → hypothesise → instrument → fix → regression-test, each stage producing what the next one runs on. |
| [`/ask-harness`](addons/router/skills/ask-harness/SKILL.md) | The map: the loop, its on-ramps, and which skill answers the situation you're in. |

Each skill carries its rules, its steps, and a completion criterion you can check. The four core skills also ship a `CASES.md` — the incidents that bought each rule, generalised.

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

The writing standard is Matt Pocock's [`writing-for-agents`](https://github.com/mattpocock/skills): positive targets over prohibitions, one source of truth per meaning, completion criteria that are checkable and exhaustive. The staged-diagnosis order is a generalisation of the same repo's `/diagnosing-bugs`. Both MIT.

繁體中文版：[README.zh-TW.md](README.zh-TW.md)

## License

MIT — see [LICENSE](LICENSE). Use it, fork it, ship it in your own product.
