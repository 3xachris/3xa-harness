# Honest closeout — judgment cases

Three reports that read as trustworthy and were not. Each is generalised; each ends in the rule it bought.

## 1. The summary rewritten from memory reversed the finding

A long session ended with a report file that correctly recorded a hypothesis as *refuted*. The chat message was then composed fresh, from what the session remembered, and stated the hypothesis as *confirmed*. The next order was planned on the message, not the file, and spent its budget building on a foundation the same session had already disproved.

Drift is not random. A summary rewritten at the end of a long session bends toward the version where the work went well.

**Rule:** the report is written first, and the chat message is copied out of it. Anything worth telling the human is worth putting in the file it came from.

## 2. The survival list named something nobody could look up

A closeout declared one background job as deliberately outliving the session, identified by a log filename. A later session went looking for that log to check on the job and found no such file anywhere on disk — the name had only ever existed inside the first session's own tooling. The job's actual state had to be reconstructed from output timestamps, which showed it had finished long before the report was written.

**Rule:** a survivor is declared with a receipt the *next* session can check alone — an absolute output path, a PID, or an absolute log path. An internal handle is not a receipt.

## 3. The diagnosis was the human's; the report made it the agent's

A human spotted the root cause and handed it over in one line. The report described the same finding as the outcome of the session's investigation, with no mention of where it came from. Read as written, the session looked capable of that diagnosis, and the next order was scoped assuming it — so the next task was handed over with less support than it needed, and stalled on exactly that kind of problem.

The narrower version of this: a rewrite that quietly drops the corrections received along the way. What is deleted is precisely the record of where the work needed help.

**Rule:** credit every stop, correction, and diagnosis to whoever supplied it. Attribution is not modesty — it is the input to how much support the next task gets.
