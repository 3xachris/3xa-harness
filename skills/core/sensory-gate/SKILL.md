---
name: sensory-gate
description: Hand images, audio, video, or any artifact only a human eye or ear can judge to a human, in one batch, and hold there until they answer — rejections made by dragging a file into a rejects folder, approval implied by everything left outside it. Use when producing renders, generated art, TTS or voice output, edited video, or anything whose acceptance rests on "does this look or sound right".
---

# Sensory Gate

"I looked at it and it seems fine" is a different claim from "a human looked at it", and only the second one closes a sensory question. Spend that attention well: one batch, one folder, one question, one action to answer it.

## 1. The gate

- **Gate folder** — one folder holding everything from this review round. How you hand it over depends only on size:

  | Batch | What the message carries |
  |---|---|
  | 4 or more | The gate folder's absolute path, alone |
  | 3 or fewer | Each file's own absolute path, listed |
- **`rejects/` subfolder** — created inside the gate folder *before* the human is asked. Dragging a file into `rejects/` **is** the rejection; no comment, no form, no reply needed. Read the folder's real contents on disk to learn the verdict — the disk is where the human answered.
- **Approval needs an answer, not just an empty `rejects/`.** An empty folder means "nothing rejected" only once the human has replied; before that it means "not looked at yet", and the two are indistinguishable from disk alone. So the gate opens on the reply and reads the folder second. When the reply names rejects in words instead of moving files — *"the third one is wrong"* — that is a rejection: move those files into `rejects/` yourself, say which ones you moved, and carry on from the same state the drag would have produced.
- **One-click open.** Where the chat client renders a run button on shell code blocks, hand over a runnable command — `explorer "<path>"` on Windows, `open "<path>"` on macOS, `xdg-open "<path>"` on Linux — alongside the plain path, which works everywhere. For a small batch, `explorer /select,"<file>"` opens the folder with that file already highlighted.
- **Commands are built from your own paths.** Everything inside a command handed to a human is a path this task constructed. Text from a webpage, a document, or any file of unknown origin goes in the message body, where running it is not one click away.
- **A question a stranger could answer.** The prompt is about the artifact, in plain language, with no vocabulary from the pipeline that made it: *"Six renders — anything wrong, drag it into rejects."*
- **Isolate what is being judged.** Send the cleanest form of the thing in question — the raw voice take rather than the finished mix, the single frame rather than the sequence — so the human's answer lands on the artifact instead of on everything wrapped around it.
- **Real pipeline, real file.** What reaches the gate is what the production path actually produces, opened from disk. An editor's preview pane renders with its own quirks, and those quirks get reported as defects in the asset; a shortcut build gets judged and then can't be reproduced.
- **1:1 for fine detail.** A contact sheet locates which item to look at. Signing off on hands, small text, edges, or single frames takes a crop at full scale or greater of that exact region — at thumbnail scale the defect and its absence look identical.

The status words this message uses — `GATE-HOLD` to open the gate, `WAITING_FOR_HUMAN` to close the message — belong to the pack's reporting vocabulary. Run the `honest-closeout` skill for it; that skill owns the definitions and this one uses them.

## 2. Run the gate

1. Produce the **whole batch** for this round before asking — one round of attention, spent once.
2. Create the gate folder with `rejects/` already inside it, inside this task's artifacts folder — that is what makes "every gate folder this task opened" something the closeout can list rather than remember.
3. Send one message: `GATE-HOLD`, the runnable open command and the plain path, the plain-language question, and the wait token on its own last line.
4. **Hold.** The next thing this task does is read the human's answer. One request, sent once, is the whole ask.
5. When they answer, read the gate folder from disk. Files inside `rejects/` are rejected, full stop — that action was the verdict and it needs no confirming question. Rejects named in words get moved into `rejects/` by you, so the folder and the verdict agree.
6. **Record the verdict where it survives the folder.** Each rejected item gets one `rejection` entry in the project's decision log — what was turned down, the reason if one was given, and the gate folder as its Target. A verdict that exists only as a file's location stops existing the moment the folder is cleaned, and the human's judgment is the most expensive thing in this whole loop to have to ask for twice. Run the `decision-log` skill for the entry format.
7. Rework the rejects into the next round; approved items move on. At final closeout, empty `rejects/` yourself, so nothing already rejected can resurface in a later batch.

## 3. Completion criteria

Before sending, **open the gate folder yourself** — the folder, not your memory of writing to it — and check four things: the path in the message resolves; `rejects/` exists and is empty; the file count in the folder equals the count the message claims; and every noun in the question names something visible in the artifact itself or present in the original request.

## Gate message

```
GATE-HOLD

Review folder: /path/to/project/review/batch-04/
(drag anything wrong into the rejects/ folder inside it)

explorer "/path/to/project/review/batch-04/"

6 renders from this round. Anything you don't like, drag it into rejects/ — that's all I need.

WAITING_FOR_HUMAN
```

## Judgment cases

Three gates that passed and should not have: [`CASES.md`](CASES.md).
