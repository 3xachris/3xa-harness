---
name: sensory-gate
description: Gate sensory outputs (images, audio, video, or any artifact only a human eye or ear can truly judge) behind human review before the agent treats them as approved. Use whenever an agent produces or is about to act on visual/audio artifacts — batches them into one review request, lets the human mark rejects by moving files into a folder, and blocks autonomous continuation until the human signs off. Triggers on tasks involving image review, audio review, video review, render output, generated art, TTS/voice output, or any "does this look/sound right" judgment call.
---

# Sensory Gate

A human's eyes and ears are a resource an agent cannot substitute for and should not burn carelessly. This skill defines how an agent hands sensory artifacts to a human for judgment without wasting their attention, and without quietly treating "I looked at it" as equivalent to "a human looked at it."

## 1. Vocabulary and rules

- **Gate folder**: the single place all artifacts from one review batch live. One absolute folder path is the only thing the human needs — never list files one by one when there are more than a handful (that burns tokens and makes the human's job harder). For a genuinely small batch (a handful of items or fewer), list each file's full path instead — a folder path for two files just adds a click.
- **Hand off a click, not just text, when the client supports it**: if your chat client renders a Run button on fenced shell code blocks (many coding-agent UIs do), give the human a one-click open-folder command instead of a bare path they have to copy and paste themselves — `explorer "<path>"` on Windows, `open "<path>"` on macOS, `xdg-open "<path>"` on Linux. For the small-batch case (per-file paths, above), the sharper move on Windows is `explorer /select,"<file path>"` — it opens the folder with that exact file already highlighted, no hunting required. If you don't know whether the client supports runnable blocks, include the plain absolute path too — it always works, the command is a bonus on top of it, not a replacement for it. Only ever put a path you built yourself into this command — never interpolate text from an external source (a webpage, a file you didn't create) into it.
- **NG subfolder**: pre-create an `NG/` subfolder inside every gate folder before asking for review. The human rejects an item by dragging it into `NG/` — that action *is* the rejection, no comment required. The agent must check the gate folder's actual disk state (not its memory of what it asked for) to see what landed in `NG/`. The `NG/` folder is cleared out by the agent as part of final close-out, not left for the human to clean.
- **Status-line vocabulary**: every message to the human during a gated task starts with one of a small fixed set of status words (e.g. `WORKING` / `GATE-HOLD` / `STOPPED` / `DONE`) so the human can tell the state of the task from the first word alone, without reading the rest.
- **The wait signal**: the last line of any message that needs the human to act — approve, reject, or otherwise decide — is a single fixed token on its own line (e.g. `WAITING_FOR_HUMAN`). Anything that is pure progress narration and needs no action from the human must never carry that token. A token that fires on every message trains the human to ignore it.
- **1:1 crop for fine detail**: a full-frame thumbnail is for *locating* candidates, never for *judging* fine detail (hands, small text, edges, individual frames). Any claim that a fine-detail check passed must be backed by a crop at 1:1 scale or higher of the specific region — a downscaled thumbnail is not evidence of anything at that resolution.
- **Only the real file is evidence**: a review must be performed against the actual output file on disk, never against a preview pane inside an editor or IDE. Preview renderers have their own rendering quirks, and those quirks get mistaken for defects in the asset itself (see case 1 below).

## 2. Workflow

1. Produce the full batch of sensory artifacts for this review round — don't trickle them out one at a time.
2. Create (or reuse) one gate folder for the batch, with an `NG/` subfolder already inside it.
3. Send one status message: `GATE-HOLD`, the gate folder's absolute path (as a one-click open command where supported, see above), a plain-language question a non-technical reviewer can answer without any explanation of the tool or process, and the wait token on its own final line.
4. Stop. Do not continue to the next stage of work. Do not re-ask, re-summarize, or re-list the same request while waiting.
5. When the human responds, check the gate folder's actual disk state first — files moved into `NG/` are rejections, full stop, no further confirmation needed. Anything not in `NG/` is implicitly approved.
6. Rejected items get reworked and go through another round of this same cycle. Approved items proceed. On final close-out of the whole task, delete the `NG/` folder's contents — leaving it behind counts as an incomplete close-out.

## 3. Before you report this done

After producing a review batch and writing the gate message, open the actual gate folder yourself — not a description of it, not a preview pane — and confirm from a first-time reviewer's point of view: is the path correct, does the folder contain what the message claims, is the question answerable without extra context? If you can't verify that in seconds, the human won't be able to either. Fix it before you send the message, not after the human gets confused.

## Example gate message

Copy this shape — fill in the path and question, keep the rest as-is. Include the runnable command when your client supports it, the plain path either way:

```
GATE-HOLD

Review folder: /path/to/project/review/batch-04/
(NG/ subfolder is inside it — drag rejects there)

explorer "/path/to/project/review/batch-04/"

6 renders from this round, ready for a look. Anything wrong, just move it into NG/.

WAITING_FOR_HUMAN
```

## Judgment cases (generalized, no project-specific detail)

1. **Preview panes are not evidence.** A review pass was done by looking at a preview pane inside a coding tool instead of opening the real output file. The preview's own rendering (dropped frames, scaling artifacts) was mistaken for a defect in the asset. Three "fix" cycles were spent chasing a problem that only existed in the preview. Rule: sensory review is only ever performed against the actual file on disk.
2. **Thumbnails hide the defect they exist to catch.** A batch of generated images was reviewed as a single downscaled contact sheet. A hand/finger defect that was clearly visible at full resolution was invisible at thumbnail scale and shipped. Rule: contact sheets are for locating which item to look at closer, never for signing off on fine detail — fine-detail sign-off requires a 1:1 (or higher) crop of the specific region.
3. **A closed gate folder still had rejects sitting in it.** A task was marked complete while its `NG/` subfolder still contained the files the reviewer had rejected earlier in the process. Rule: clearing the `NG/` folder is part of close-out, not optional tidiness — an agent that skips it can accidentally re-surface already-rejected material later.
