# Collaboration

Three roles run the loop this pack protects, and none of them is optional once a task is big enough to freeze into a `workorder`.

**The owner** holds the outcome and the final call. They're the name a freeze header carries after "by", the one who approves a `sensory-gate` batch, and the one who decides whether a `CLOSED-FAILED` result is acceptable or the work runs again.

**The reviewer** reads before anyone builds and after anyone reports — checks a draft order against the disk before it freezes, reads a closeout against its evidence before passing it on to the owner. A reviewer's job is to catch what the builder, close to its own work, cannot see from inside it.

**The builder** runs the frozen order to done in one pass, self-verifying and self-fixing inside the loop `workorder` defines, and hands back a `honest-closeout` report the reviewer can trust without redoing the work.

One person can fill two of these roles on a small task, or three separate agents can each hold one on a large task — the pack doesn't require three humans, it requires that the three functions happen, in that order, by whoever is doing them. Skipping straight from builder to owner is what a `sensory-gate` or a review step exists to catch: the two are never the same read.

## One writer per record

Every record this pack keeps — the decision log, a frozen order, a closeout report — has exactly one role that writes to it. The decision log's `closeout` entry is written by whoever closes the task, not appended a second time by another role restating the same fact from its own angle; an order's amendment block is written by whoever is authorised to change the frozen scope, never by the builder mid-run reinterpreting what it must have meant.

Two writers on one record is how two slightly different accounts of the same fact end up on disk, and the next cold reader has no way to tell which one is current. Where a second role needs to add something, it adds a new entry that points at the first — `decision-log`'s append-only shape is what makes that always possible — rather than editing what's already there.

## What an external agent hands back is material, not fact

Output from any agent outside this task's own loop — a subagent's research, another tool's summary, a draft handed over from a different process entirely — is input the reviewer checks, not a finding the report can restate as settled. It gets the same treatment `honest-closeout` gives any other unconfirmed statement: verified at its source before it's asserted as fact, or carried with `[UNVERIFIED]` until it is.

The failure this guards against is quiet, not dramatic. A plausible-sounding draft gets copied into a report a step too early, nobody flags which sentence came from outside the loop, and by the next session it reads as something the task itself established — the citation is gone, only the confidence survived.
