# Decision log — judgment cases

Three logs that were kept faithfully and still failed the cold read. Each is generalised; each ends in the rule it bought.

## 1. The rejection buried the need underneath it

An entry read, in full: *rejected — approach X doesn't fit*. The requirement that approach X had been proposed to solve was never written anywhere else, because at the time it was obvious to everyone in the room. Months later the requirement resurfaced as a fresh discovery, and the search that should have found it turned up only the rejection of a solution nobody remembered the purpose of.

**Rule:** a rejection is two facts — the approach that is out, and the problem that is still in. Log the second one somewhere it can be found on its own.

## 2. The log became a second copy of the source

One busy day produced a run of long entries, each restating in full the content of a document written the same day. The log grew faster than the work and became the thing people read, so the source stopped being maintained — and the copies drifted from it without anyone noticing which version was current.

**Rule:** entries point, they do not duplicate. Length in an entry is the signal that its content has a home somewhere else.

## 3. The entry with no index line was invisible to the scan

An entry was written as a plain paragraph — accurate, well-argued, no index line. A later pass that walked the log to answer *what has been decided, and where does each decision live* worked off the index lines and never saw it. The decision it recorded was made again, differently, six weeks later.

**Rule:** the index line is what makes an entry exist to anything other than a full read. It costs one line at write time and cannot be reconstructed reliably afterwards.

## 4. Splitting the file to get real frontmatter would have solved a problem nobody had

When the index line moved from a single blockquote to a YAML block, one proposal was to go further and split the log into one file per decision — that's the only way to get frontmatter Obsidian's Properties panel actually renders, since real frontmatter is a file-top concept and this log is one file with many headings. It was rejected: the log's whole value is reading a period's worth of decisions top to bottom to see how the thinking moved (§1), and a folder of one-line files scatters that into a directory listing with no order to read it in. The chosen format — a YAML-shaped fenced block under each heading — gets genuine, parser-grade structure without that cost; it loses only the Properties-panel rendering, which nothing here depended on.

**Rule:** matching a tool's ideal format is not free if it breaks the shape the format was chosen to serve. Take the piece of the convention that pays for itself (real YAML, not prose regex) and name the piece you're deliberately not taking (file-level frontmatter) rather than silently drifting toward it.
