# Repo audit — judgment cases

Four checks that ran, reported, and were believed, while measuring something other than what they claimed. Each is generalised; each ends in the rule it bought.

## 1. The check that could not fail

A symmetry check confirmed that when document A declares an interface to document B, B declares one back. It scanned the relevant section of each document and looked for the other document's name. It reported every pair as consistent, seven files, forty-two edges, one hundred percent.

The section it read contained two different statements: the interfaces a document declares, *and* a list of the documents it explicitly has no interface with — each of those also naming the other document. Read as one blob, both counted as "declared". The check had no input that could produce a failure, and its perfect score was the only symptom.

**Rule:** before trusting a green check, feed it a case you know is broken. A check that has never returned a failure has not been shown to be capable of one.

## 2. The scanner that read its own output

The report listed every tracked document by name, as reports do. The next run scanned the project — including the folder its own reports go in — and found every tracked document referenced, by its own previous report. Reachability went from a real number to a perfect one in a single cycle, and stayed there.

The same shape appeared twice more from different directions: an audit table elsewhere in the project listed the same names, and then a single document mentioned one tracked file as a *counter-example*, which the check counted as a reference like any other.

**Rule:** exclude the tool's own output and source from its inputs — and when a reference check keeps drifting green, the bug is usually not in finding references but in the definition of what counts as one. Tighten the definition rather than adding another exclusion; a blacklist of filenames is a list that only ever grows.

## 3. The proxy that pointed backwards

The plan was to report code comments marked *temporary* that had sat untouched for more than a month, using file modification time as the age. It returned nothing, in a codebase with a year-old temporary shim sitting in a file everyone edits weekly.

Modification time answers "when was this file last changed", not "how long has this line said this". The most actively maintained files — the ones where a stale shim does the most damage — are exactly the ones that never look old. The metric was not merely weak; it ranked in the opposite direction from the question.

**Rule:** before using a proxy, say out loud what it actually measures and check that its ordering matches the question's. Where the honest answer is "this cannot be measured here", the report says so, and does not substitute a suggestion to review it periodically.

## 4. Documents written to turn a check green

One check measured how many long-lived notes were reachable from the project's live documents. Eight were not. The cheapest way to a perfect score was obvious: write eight short documents referencing them.

The eight would have had no readers and no content beyond satisfying the count. The call that stopped it was blunt — *generating eight documents so the scanner goes green is degrading the product to suit the checker; the scanner should learn what it doesn't need to care about.* The exemption list that replaced them requires a category and a written reason per entry, enforced by the script, which refuses to start if either is missing.

**Rule:** a check is a proxy for quality, never the specification. When the cheapest way to pass is to change the product rather than fix the problem, the check is wrong and needs to be taught what to ignore — in writing, with a reason, so the exemption list cannot quietly become the thing that only grows.
