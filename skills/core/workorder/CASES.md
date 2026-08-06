# Workorder — judgment cases

Four ways a written order failed in practice. Each one is generalised; each ends in the rule it bought.

## 1. "Same as the final version" resolved to two files

A build spec pinned a parameter by describing it — *use the settings from the final render* — rather than by path. Two copies of that asset existed: one inside the project, one on the operator's desktop, differing in a way nobody had noticed. Two sessions running the same order produced different output and each proved itself correct against its own copy. Reconciling them cost more than the original build.

**Rule:** a parameter is pinned to *file plus symbol name*. A description of where a value lives is not a location.

## 2. The order that grew while it ran

Mid-build, an adjacent improvement looked cheap and got done alongside the ordered work. Review then faced one diff containing two changes, could not accept either independently, and sent both back. The improvement was genuinely good and still shipped a week later — as its own order, reviewed in an hour.

**Rule:** the frozen scope is the deliverable. Work found along the way gets written down as a candidate for a next order, not folded into this one. Widening is as much a scope break as narrowing.

## 3. The order that came back at every bump

A task hit an ambiguity two steps in, stopped, and asked. It hit another one step later, stopped, and asked again. Five round trips over two days for work that held perhaps four hours of building; each restart also paid to rebuild the context it had dropped.

**Rule:** run to done in one pass — resolve what is resolvable, state the assumption where a call has to be made, and finish everything that does not depend on the answer. Two failures on the *same* sub-problem is the signal to stop; a fresh question is not.

## 4. Acceptance measured a proxy, not the outcome

An order adopted a widely recommended practice and set its acceptance line to the metric that practice optimises — the artifact got smaller, so the line passed. What the change was meant to buy was *fewer downstream mistakes*, and that was never measured. Two weeks later the size had returned and the mistake rate had not moved; the practice had been graded on its own scoreboard the whole time.

**Rule:** an official recommendation is a hypothesis, not a result. Acceptance names the outcome the work is for — rework avoided, defects caught, time to ship — and treats the practice's own favourite number as supporting evidence at best.
