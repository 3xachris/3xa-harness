---
name: sensory-gate
description: Hand images, audio, video, or any artifact only a human eye or ear can judge to a human, in one batch, and hold there until they answer — rejections made by dragging a file into an NG folder, approval implied by everything left outside it. Use when producing renders, generated art, TTS or voice output, edited video, or anything whose acceptance rests on "does this look or sound right".
---

# Sensory Gate

A human's eyes and ears are the scarcest resource in the loop, and the one an agent cannot stand in for. "I looked at it and it seems fine" is a different claim from "a human looked at it", and only the second one closes a sensory question.

This skill spends that attention well: one batch, one folder, one question, one action to answer it.

## 1. The gate

- **Gate folder** — one folder holding everything from this review round. Above a handful of items, the folder's absolute path is the entire ask; at three items or fewer, list each file's own absolute path, because opening a folder to find two files adds a click for nothing.
- **`NG/` subfolder** — created inside the gate folder *before* the human is asked. Dragging a file into `NG/` **is** the rejection; no comment, no form, no reply needed. Everything still outside `NG/` at answer time is approved. Read the folder's real contents on disk to learn the verdict — the disk is where the human answered.
- **One-click open.** Where the chat client renders a run button on shell code blocks, hand over a runnable command — `explorer "<path>"` on Windows, `open "<path>"` on macOS, `xdg-open "<path>"` on Linux — alongside the plain path, which works everywhere. For a small batch, `explorer /select,"<file>"` opens the folder with that file already highlighted. Build the command only from paths you constructed yourself; text from a webpage or a file of unknown origin belongs in a message, never inside a command the human will run.
- **A question a stranger could answer.** The prompt is about the artifact, in plain language, with no vocabulary from the pipeline that made it: *"Six renders — anything wrong, drag it into NG."*
- **Isolate what is being judged.** Send the cleanest form of the thing in question — the raw voice take rather than the finished mix, the single frame rather than the sequence — so the human's answer lands on the artifact instead of on everything wrapped around it.
- **Real pipeline, real file.** What reaches the gate is what the production path actually produces, opened from disk. An editor's preview pane renders with its own quirks, and those quirks get reported as defects in the asset; a shortcut build gets judged and then can't be reproduced.
- **1:1 for fine detail.** A contact sheet locates which item to look at. Signing off on hands, small text, edges, or single frames takes a crop at full scale or greater of that exact region — at thumbnail scale the defect and its absence look identical.

The status word and the wait token that frame the gate message are defined in [`honest-closeout`](../honest-closeout/SKILL.md).

## 2. Run the gate

1. Produce the **whole batch** for this round before asking. Trickling artifacts out one at a time turns one review into six interruptions.
2. Create the gate folder with `NG/` already inside it.
3. Send one message: `GATE-HOLD`, the runnable open command and the plain path, the plain-language question, and the wait token on its own last line.
4. **Hold.** The next thing this task does is read the human's answer. Re-asking, re-summarising, or starting the next stage while the gate is open all spend the human's attention on the same request twice.
5. When they answer, read the gate folder from disk. Files inside `NG/` are rejected, full stop — that action was the verdict and it needs no confirming question.
6. Rework the rejects into the next round; approved items move on. At final closeout, empty `NG/` yourself, so nothing already rejected can resurface in a later batch.

## 3. Completion criteria

Before sending, **open the gate folder yourself** — the folder, not your memory of writing to it — and check three things: the path in the message resolves, the folder holds exactly what the message says it holds, and the question is answerable by someone who knows nothing about how the files were made. A gate the sender cannot verify in ten seconds is one the human will answer with a question instead of a decision.

## Gate message

```
GATE-HOLD

Review folder: /path/to/project/review/batch-04/
(drag anything wrong into the NG/ folder inside it)

explorer "/path/to/project/review/batch-04/"

6 renders from this round. Anything you don't like, drag it into NG/ — that's all I need.

WAITING_FOR_HUMAN
```

## Judgment cases

Three gates that passed and should not have: [`CASES.md`](CASES.md).
