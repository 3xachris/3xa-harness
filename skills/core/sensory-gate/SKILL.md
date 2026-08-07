---
name: sensory-gate
description: Hand images, audio, video, or any artifact only a human eye or ear can judge to a human, in one batch, and hold there until an identified reviewer records the approved batch scope — rejections made by dragging a file into a rejects folder. Use when producing renders, generated art, TTS or voice output, edited video, or anything whose acceptance rests on "does this look or sound right".
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
- **Gate identity** — when the gate folder is created and before the review message is sent, append one `decision` entry to the project's decision log with the gate folder as its Target and a file list containing each review file's relative path and SHA-256 hash. That entry is the gate register and binds the human-reviewed batch to the later shipped batch.
- **Approval needs an identified answer, not just an empty `rejects/`.** An empty folder means "nothing rejected" only once the human has replied; before that it means "not looked at yet", and the two are indistinguishable from disk alone. So the gate opens on the reply and reads the folder second. The reply supplies the reviewer's name or handle and says whether the reviewer approves the whole batch or only named files; record that scope and the batch identifier in the decision log. A short reply is enough, and dragging files remains the rejection action. When the reply names rejects in words instead of moving files — *"the third one is wrong"* — that is a rejection: move those files into `rejects/` yourself, say which ones you moved, and carry on from the same state the drag would have produced.
- **One-click open.** Where the chat client renders a run button on shell code blocks, hand over a runnable command — `explorer "<path>"` on Windows, `open "<path>"` on macOS, `xdg-open "<path>"` on Linux — alongside the plain path, which works everywhere. For a small batch, `explorer /select,"<file>"` opens the folder with that file already highlighted.
- **Commands are built from your own paths.** Everything inside a command handed to a human is a path this task constructed. Text from a webpage, a document, or any file of unknown origin goes in the message body, where running it is not one click away.
- **A question a stranger could answer.** The prompt is about the artifact, in plain language, with no vocabulary from the pipeline that made it: *"Six renders — anything wrong, drag it into rejects."*
- **Isolate what is being judged.** Send the cleanest form of the thing in question — the raw voice take rather than the finished mix, the single frame rather than the sequence — so the human's answer lands on the artifact instead of on everything wrapped around it.
- **Real pipeline, real file.** What reaches the gate is what the production path actually produces, opened from disk. An editor's preview pane renders with its own quirks, and those quirks get reported as defects in the asset; a shortcut build gets judged and then can't be reproduced.
- **1:1 for fine detail.** A contact sheet locates which item to look at. Signing off on hands, small text, edges, or single frames takes a crop at full scale or greater of that exact region — at thumbnail scale the defect and its absence look identical.

The status words this message uses — `GATE-HOLD` to open the gate, `WAITING_FOR_HUMAN` to close the message — belong to the pack's reporting vocabulary. Run the `honest-closeout` skill for it; that skill owns the definitions and this one uses them.

## 2. Run the gate

Write the gate register with `> Gate: <gate-folder> | Batch: <batch-id> | Files: <relative-path=sha256, ...>` before review. After the human answer, append `> Gate disposition: <gate-folder> | Reviewer: <name> | Scope: <all files in batch|approved file list> | Archive: <path|none>`.

1. Produce the **whole batch** for this round before asking — one round of attention, spent once.
2. Create the gate folder with `rejects/` already inside it, inside this task's artifacts folder. Before sending the review message, append the gate-opening `decision` entry described above and verify that its file list and SHA-256 hashes describe the files on disk.
3. Send one message: `GATE-HOLD`, the runnable open command and the plain path, the plain-language question, a request for the reviewer's name or handle plus approval of the whole batch or named files, and the wait token on its own last line.
4. **Hold.** The next thing this task does is read the human's answer. One request, sent once, is the whole ask.
5. When they answer, read the gate folder from disk. Files inside `rejects/` are rejected, full stop — that action was the verdict and it needs no confirming question. Rejects named in words get moved into `rejects/` by you, so the folder and the verdict agree. If the reply does not identify the reviewer and approval scope, keep the gate open and ask for those two facts.
6. **Record an approval where it survives the folder.** After the answer is identified, append one `decision` entry with the reviewer name or handle, the gate folder's batch identifier, and approval scope: `all files in batch` or the explicit approved file list. An empty `rejects/` corroborates the recorded approval; it is never the approval itself. Run the `decision-log` skill for the entry format.
7. **Record the rejection where it survives the folder.** Each rejected item gets one `rejection` entry in the project's decision log — what was turned down, the reason if one was given, and the gate folder as its Target. Then move the rejected item to the task artifacts folder's `rejected-archive/<gate-folder>/`; that archive is reference-only, and later production batches use newly produced files rather than archived inputs. Run the `decision-log` skill for the entry format.
8. Rework the rejected requirement into newly produced files for the next round; approved items move on. The original rejected files remain in the reference-only archive.

## 3. Completion criteria

Before sending, **open the gate folder yourself** — the folder, not your memory of writing to it — and check five things: the path in the message resolves; `rejects/` exists and is empty; the file count in the folder equals the count the message claims; the gate-opening decision entry records the same files and SHA-256 hashes; and every noun in the question names something visible in the artifact itself or present in the original request.

## Gate message

```
GATE-HOLD

Review folder: /path/to/project/review/batch-04/
(drag anything wrong into the rejects/ folder inside it)

explorer "/path/to/project/review/batch-04/"

6 renders from this round. Reply with your name or handle and whether you approve the whole batch or named files. Anything you don't like, drag it into rejects/ — that's all I need.

WAITING_FOR_HUMAN
```

## Judgment cases

Three gates that passed and should not have: [`CASES.md`](CASES.md).
