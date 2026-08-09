# Claim audit — judgment cases

Four ways this check failed while looking like it worked. Each is generalised; each ends in the rule it bought.

## 1. The gate existed; the trigger didn't

The check was written, tested, and documented with a line in the project's own guide: *run this after every edit to a source-of-truth document*. The author then edited a source-of-truth document and did not run it. Nobody had removed the gate — it simply required someone to remember, and remembering is the thing the gate was built to replace.

**Rule:** attach the check to an action that is already happening — a write, a commit, a pull request. A check whose trigger is human memory has the reliability of human memory, which is the number the check was supposed to improve.

## 2. The baseline keyed by position

The baseline was stored as a set of line numbers per file, so that only claims added after adoption would be reported. Then someone inserted two paragraphs near the top of a document, and every recorded line below the insertion shifted — the tool reported the entire rest of the file as newly added. The "only report what's new" feature broke on the first edit after every baseline, and it broke quietly: the output looked like a real finding list.

**Rule:** key a baseline on content, not position. Line numbers move for reasons that have nothing to do with what the line says.

## 3. The exemption that swallowed a real claim

Hedge words — *about*, *around*, *roughly* — were exempt, because honestly hedged numbers are the behaviour the check wants. The words were matched anywhere on the line. A sentence reading *"don't build the artifacts folder around this script"* therefore exempted a hard version requirement stated in the same sentence, and the claim went unreported for as long as that wording stood. The hole was found only when the same claim was flagged in a translated copy of the file and not in the original — the asymmetry was the tell.

**Rule:** an exemption has to be tied to the thing it exempts. A hedge exempts the number it modifies, so it must sit next to a number to count. And a checker that reports success it never performed is the worst failure mode available to a checker — worse than one that is merely noisy.

## 4. Resetting the baseline to make it quiet

A run returned a long list. Rather than work the list, someone re-ran the baseline command, which recorded all of it as known and returned the tool to silence. Nothing was fixed and nothing was recorded as dismissed, so the next reader saw a clean run and had no way to tell it from a project where the claims had actually been sourced.

**Rule:** the baseline records what has been *judged*, never what should stop being mentioned. Where a finding is dismissed, the reason is written down next to the run — an unexplained dismissal and an unread finding leave the same trace, which is none.
