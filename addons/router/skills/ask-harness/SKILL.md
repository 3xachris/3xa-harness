---
name: ask-harness
description: Ask which harness skill fits the situation you're in.
disable-model-invocation: true
---

# Ask Harness

You are somewhere in a piece of work and want to know which part of the pack applies. Describe the situation; this is the map to answer from.

Four skills form **one loop** around a single task. Two more sit outside it, reached by situation.

## The loop: frozen → built → judged → closed

The route almost all work travels, once per task.

1. **`workorder`** — the task gets written down and **frozen** before the first edit: one sentence, known facts, materials with their licences, pinned parameters, a budget fuse, acceptance lines, non-goals. Freezing is what makes "done" checkable later, and what keeps the work from growing while it runs.

2. **The build runs to done in one pass** — build, self-verify against the acceptance lines, self-fix, re-verify. This is part of `workorder`, not a skill of its own; it also defines the two-strike rule the other skills refer to.

3. **`sensory-gate`** — when the work produces something only eyes or ears can judge, the whole batch goes into one gate folder with an `NG/` subfolder, and the task holds there until you answer. Rejecting is a drag into `NG/` — the skill defines what the folder means and when. Skip this step and the human's sign-off is being simulated by the thing asking for it.

4. **`decision-log`** — running underneath the whole loop, not after it. Every decision, rejection, or correction gets a short entry with a fixed index line, pointing at where the detail lives. This is what a fresh session or a different agent reads when the context is gone.

5. **`honest-closeout`** — the report: every acceptance line answered with evidence, human corrections credited, refuted hypotheses kept, background processes proven stopped, and the chat message copied verbatim out of the file. It also defines the status words and the wait token the other skills use.

The four skills live in the **`harness-core`** plugin. Nothing here needs a repo, a tracker, or a language — the loop is the same for code, renders, audio, or writing.

## On-ramps

A situation that starts work and merges into the loop.

- **Something is broken** → **`staged-diagnosis`** (plugin: `harness-debug`). Six stages, each producing what the next one runs on: reproduce, minimise, hypothesise, instrument, fix, regression-test. Reach for it on the failure that resists a first look — the flake, the silent wrong answer, the regression between two known-good states. Its output is evidence, so it feeds straight into the closeout.

- **A fresh session is taking over** → open with **`decision-log`** rather than the code. The log holds the decisions the previous session made and the reasons that never made it into a diff.

- **You are being asked to approve something you cannot see** → the answer is a gate, not a better description. Ask for the batch in a gate folder and answer with `NG/`.

## Where the boundaries and the credits live

The pack's honest boundary — these are protocols, not enforcement — and the writing standard behind them are stated once, in the [README](https://github.com/3xachris/3xa-harness#honest-boundary).
