---
name: staged-diagnosis
description: Diagnose a hard error in six ordered stages — reproduce, minimise, hypothesise, instrument, fix, regression-test — where each stage produces the thing the next stage needs before it may start. Use on a crash, traceback, silent wrong answer, zero-byte or truncated output, intermittent flake, or a check that started failing between two known-good states.
---

# Staged Diagnosis

The six stages are ordered because each one produces the evidence the next one runs on, and a stage is finished when it has produced that thing. Each edit made before its stage has produced evidence is one the next investigation has to account for.

## The six stages

1. **Reproduce** — get to one command you can re-run that goes **red** on this failure: the trigger, its input, its environment flags, its machine state. *Produces:* that command, and the red result it gives. A path you can walk by hand is the weaker version of this and only acceptable while the automatic one is out of reach — everything downstream is measured by whether this goes green, so a loop you have to drive by hand slows every later stage. Where it fires only sometimes, run it repeatedly and record what varies; the shape of the intermittency is the strongest clue on offer.
2. **Minimise** — cut away everything the failure survives without, until it sits in one layer: the script, the service, the data, the encoding, the environment. *Produces:* the smallest case that still fails, and the layer it lives in.
3. **Hypothesise** — write the causal claim down in one sentence, in terms of that layer. *Produces:* a statement specific enough to be wrong. Check the project's own record of past failures first — a familiar shape is a precedent to apply, not a discovery to repeat.
4. **Instrument** — put the hypothesis in front of evidence: a log line, a printed value, a breakpoint, a checksum. *Produces:* a measurement that confirms or kills the claim. Edits belong after this stage, so that what gets changed is what the evidence pointed at.
5. **Fix** — change the confirmed cause and nothing beside it. *Produces:* one focused edit. When the fix would reach into frozen specification, another task's settled rules, or a shared module several callers depend on, stop and ask — the cheapest version of that conversation happens before the edit.
6. **Regression-test** — re-run the original trigger, then the checks around it. *Produces:* evidence the failure is gone and its neighbours still work, attached to the closeout.

## Loud failures only

Diagnosis runs on signal, so it depends on the code failing loudly: an error that stops and says what happened, rather than a fallback that quietly substitutes a default and lets the run continue looking healthy. When the investigation meets a swallowed exception or a silent default, that is a finding to record and usually to fix — the failure being diagnosed may be the second symptom of it.

## Where diagnosis stops

This order settles **objective** failures — crashes, wrong values, malformed or missing output, a check that returns FAIL. Those are self-fixed until they pass, and the passing evidence goes in the report.

Judgments of look, sound, taste, or tone are a different question, and a passing objective check is not an answer to it. Once the artifact is physically sound, that call belongs to a human. (With `harness-core` installed, `sensory-gate` runs that hand-off.)

## Completion criteria

Each stage names its output above; the diagnosis is done when **all six exist and can be shown** — the trigger, the minimal case, the written hypothesis, the measurement, the edit, and the regression evidence. Missing outputs are where a stage was skipped, and a skipped stage is where the next investigation will start.

Two failed attempts at the same cause end the run: hand over the whole trail, refuted hypotheses included, since they are what the next attempt spends its budget on not repeating. (With `harness-core` installed, `workorder` holds the full definition of the two-strike rule.)
