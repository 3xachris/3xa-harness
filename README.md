# 3xa-harness

Two Agent Skills, distilled from running an AI agent on a real, long-lived production workflow for months. Both are free, MIT-licensed, and installable in under a minute.

## The problem this solves

Running an AI agent on a long project surfaces two recurring failure modes that generic prompting doesn't fix:

- **Sensory judgment gets faked.** An agent looks at an image, listens to audio, or watches a render, decides it's fine, and moves on — but "looks fine to a language model" and "looks fine to the person who actually has to live with the output" are not the same claim. By the time a human notices, the agent has already built three more steps on top of the bad asset.
- **Decisions evaporate.** A rejection, a correction, a "why did we do it this way" gets said once in a chat and then never again. The next session — or the next agent — has no way to find it, so it either repeats the same mistake or repeats the same argument.

`sensory-gate` and `decision-log` are the two mechanisms that fixed these for us. They're not vague prompting advice — each one has a concrete, checkable shape: a folder to look at, a token to grep for, an index line a cold read can trust. An agent can actually follow them, and a human can verify from the same disk state whether it did.

**Honest boundary**: what's here is discipline, not enforcement. Nothing in this repo stops an agent from skipping a step — these are protocols an agent follows because they're well-specified, not because a hook is blocking it from doing otherwise. If you want the same mechanisms backed by an actual hook that blocks continuation until the gate folder's real state is checked, that's the kind of thing that lives in the paid layer below, not this one.

## What's inside

| Skill | One-line usage |
|---|---|
| [`sensory-gate`](skills/sensory-gate/SKILL.md) | Tell the agent to batch its image/audio/video output into a gate folder with a pre-made `NG/` subfolder — it stops and waits; you reject something by dragging it into `NG/`, nothing else needed. |
| [`decision-log`](skills/decision-log/SKILL.md) | Tell the agent to log a decision, rejection, or correction — it appends a short, indexed entry to one running file that a cold read (a future session, a different agent) can trust without re-deriving anything. |

Each skill is self-contained: vocabulary/format rules, a step-by-step workflow, and a closing requirement that the agent verify its own output from a first-time user's point of view before calling the task done.

## Install

This is a standard [Agent Skills](https://docs.claude.com/en/docs/claude-code/skills) plugin marketplace — one repo, works the same way for Claude Code and any other Agent Skills–compatible tool.

```bash
claude plugin marketplace add https://github.com/3xachris/3xa-harness
claude plugin install 3xa-harness@3xa-harness
```

Then just describe a task that matches — "review this batch of renders" or "log why we dropped approach X" — and the matching skill triggers on its own.

## License

MIT — see [LICENSE](LICENSE). Use it, fork it, ship it in your own product.

## Status

This is the free, general-purpose layer. It documents the two mechanisms in full — no functionality is held back here. A separate, paid layer (case studies from real incidents, additional workflow modules, and tooling) exists for teams that want the fuller system; it is not part of this repository.
