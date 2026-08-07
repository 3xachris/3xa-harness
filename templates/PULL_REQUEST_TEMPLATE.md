<!--
Copy into .github/PULL_REQUEST_TEMPLATE.md in your own project, or paste
this per PR. Fill every placeholder from the frozen order and closeout
this PR is shipping — the sections below mirror honest-closeout's report
template so the same lines answer both.
-->

## Order

Frozen order: `<path to order.md>`

## Acceptance

<!-- Copy every AC-n line from the closeout's Acceptance section, verbatim. -->

- [PASS] AC-1: `<line>` | evidence: `<path / output / number>`

## Independent functional verification

<!--
Copy the "Functional verification: ... | evidence: ..." line(s) from the
closeout. A PR whose order claims DONE but carries none of these is not
ready to merge as DONE — see honest-closeout's DONE definition.
-->

## Gate register

<!-- One line per gate this PR's work went through, or "None". -->

- [GATE] `<gate/path>` | disposition: approved | reviewer: `<name>` | archive: `<path|none>`

## Closeout

Full report: `<path to closeout.md>`
