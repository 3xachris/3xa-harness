# Core

The four-skill discipline loop, shipped as the `harness-core` plugin.

## Model-invoked

Reachable by you or by the agent — each carries trigger phrasing so it fires when a task fits.

- **[workorder](./workorder/SKILL.md)** — Freeze a task's scope into a written order before building, then run it to done in one pass rather than returning at every obstacle.
- **[sensory-gate](./sensory-gate/SKILL.md)** — Hand images, audio, or video to a human in one batch, record its file hashes in the decision log, and archive rejected files in the reference-only `rejected-archive/<gate-folder>/`.
- **[decision-log](./decision-log/SKILL.md)** — One append-only log with a fixed index line per entry, plus the always-loaded pointer that makes a fresh session open it.
- **[honest-closeout](./honest-closeout/SKILL.md)** — Close out with evidence per acceptance line, independent verification for `DONE`, gate folders reconciled from the decision log, credited human input, and a chat message copied verbatim from the report. Owns the pack's reporting vocabulary.
