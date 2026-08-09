#!/usr/bin/env python3
"""Health check over a project's own records and code, written for the agent
that has to act on the result.

Six checks, each reading either this pack's own record formats (the decision
log's YAML blocks, `| evidence:` lines, WikiLinks) or a generic file property
(size, modification time, whether a reference resolves). Nothing here judges
meaning: every finding names the file, the line, and the edit that closes it,
so a reader can price the work before starting it.

Needs Python 3.9+ on PATH. Standard library only. See README, section "Record
audits", for the config file.

Exit codes: 0 nothing found, 1 findings for a human, 2 could not check.
"""
from __future__ import annotations
import argparse
import datetime
import fnmatch
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

MIN_PYTHON = (3, 9)

CONFIG_NAME = ".harness-audit.json"
CONFIG_SECTION = "repo_audit"

DEFAULTS = {
    "decision_log": "docs/decisions.md",
    "log_split_kb": 200,          # decision-log SKILL.md, section 1: split at 200 KB
    "size_targets": [
        {"glob": "docs/**/*.md", "limit_kb": 100},
        {"glob": "artifacts/**/*.md", "limit_kb": 100},
        {"glob": "skills/**/SKILL.md", "limit_kb": 40},
    ],
    "link_scan": ["docs/**/*.md", "artifacts/**/*.md"],
    "code_globs": ["**/*.py", "**/*.js", "**/*.ts", "**/*.jsx", "**/*.tsx",
                   "**/*.go", "**/*.rb", "**/*.sh"],
    "patch_threshold": 3,
    "reference_track": ["skills/**/SKILL.md", "docs/rules/**/*.md"],
    "reference_cited_by": ["artifacts/**/*.md", "docs/**/*.md", "reports/**/*.md"],
    "stale_days": 180,
    "history": ".harness-audit-history.jsonl",
    "reference_ledger": ".harness-audit-references.json",
    "disable_signals": [],
    "exclude": [],
}

# Excluded everywhere. Backups and this tool's own output are the two inputs
# that quietly invalidate a repo check: a 500 KB pre-split backup drags a size
# average until one outlier reads as a systemic failure, and a report that
# lists every tracked filename makes every tracked file look "referenced" on
# the next run.
BASE_EXCLUDE = [
    "**/.git/**", "**/node_modules/**", "**/.venv/**", "**/venv/**",
    "**/__pycache__/**", "**/dist/**", "**/build/**", "**/vendor/**",
    "**/*.bak", "**/*_backup*", "**/*_bak*", "**/*.orig",
    "**/.harness-audit-*", "**/repo-audit*.md", "**/repo_audit*.md",
    # Backstop for installs that copy the skill folders somewhere else, where
    # the plugin-root anchor below no longer finds a `.claude-plugin/`.
    "**/claim_audit.py", "**/repo_audit.py",
]

# The scanner must not scan itself, or its sibling. This script carries a table
# of the very patterns it looks for, so reading its own source turns every
# pattern definition into a finding -- the first run reported its own
# `TODO|FIXME` regex as work marked temporary.
#
# Anchor on the plugin, not on this file's folder. An earlier version excluded
# only `Path(__file__).parent`; when the two scripts were later moved into their
# own skill folders to make folder-copy installs work, each stopped excluding
# the other and the same bug came back wearing a different shape. The nearest
# ancestor holding `.claude-plugin/` is the unit that means "this tool".
def _self_root() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in (here, *here.parents):
        if (candidate / ".claude-plugin").is_dir():
            return candidate
    return here


SELF_DIR = _self_root()

DATE_IN_NAME = re.compile(r"(20\d{2})[-_]?(\d{2})[-_]?(\d{2})")
YAML_BLOCK = re.compile(r"^```yaml\r?\n(.*?)^```\s*$", re.MULTILINE | re.DOTALL)
HEADING = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
WIKILINK = re.compile(r"\[\[([^\]|#]+)?(?:#([^\]|]+))?(?:\|[^\]]*)?\]\]")
MD_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
EVIDENCE = re.compile(r"\|\s*evidence:\s*(\S+)")
LEGACY_TARGET = re.compile(r"^>\s*Type:\s*(\w+)\s*\|\s*Target:\s*(\S+)\s*$", re.MULTILINE)

BOUNDARY_EN = "This checks form only. Whether the content is right is for a human."
BOUNDARY_ZH = "這支只驗形式，內容對不對是人的事"

# Each signal is a shape that tends to accompany debt, not a defect in itself.
# `multiline` regexes are matched with DOTALL; the rest line by line.
SIGNALS = [
    {"id": "SWALLOWED-ERROR",
     "name": "exception swallowed into an empty value",
     "why": "a failure that returns a default reports success it never had",
     "fix": "let it raise, or handle it explicitly and say what was substituted",
     "re": r"except[^\n:]*:\s*\n(?:[^\n]*\n){0,3}?\s*\w+\s*=\s*(?:\"\"|''|None|\[\]|\{\})\s*$"
           r"|catch\s*\([^)]*\)\s*\{\s*(?:return\s*(?:null|undefined|\[\]|\{\})\s*;?)?\s*\}",
     "multiline": True},
    {"id": "CHECK-DISABLED",
     "name": "something that reads as a check switched off in place",
     "why": "a disabled check still looks like a passing one from the outside",
     # Never phrase this as "re-enable it". A reviewer following that instruction
     # on a debug flag turns debug on in production -- the recommendation did
     # more damage than the finding. Say what to establish, not what to do.
     "fix": "confirm whether this is a check or a normal switch; if it is a check, "
            "re-enable it or delete it and record why in the decision log",
     # DEBUG/VERBOSE/TRACE flags are excluded: `DEBUG_ENABLED = False` is the
     # correct production value, and it matched only because the name ends in a
     # word that looks like a check.
     "re": r"log_only\s*=\s*[Tt]rue"
           r"|(?<![Bb][Uu][Gg])(?<![Ss][Ee])(?<![Cc][Ee])\b(?<!DEBUG_)(?<!VERBOSE_)(?<!TRACE_)"
           r"[A-Za-z_]*[Ee]nabled\s*=\s*(?:[Ff]alse|0)\b"
           r"|SKIP_[A-Z_]+\s*=\s*[Tt]rue"
           r"|\.skip\(|\bxit\(|\bxdescribe\(|@unittest\.skip|# *type: *ignore|eslint-disable",
     "exclude_re": r"(?i)\b(?:debug|verbose|trace|telemetry|analytics)\w*\s*=\s*(?:false|0)\b"},
    {"id": "TEMPORARY-MARKER",
     "name": "work marked temporary",
     "why": "a marker nobody counted is a marker nobody returns to",
     "fix": "close it, or turn it into a dated entry in the decision log",
     "re": r"\b(?:TODO|FIXME|HACK|XXX)\b|\btemporar\w+\b|\bfor now\b|\bplaceholder\b|\bMVP\b"},
    {"id": "MANUAL-SYNC",
     "name": "two places a comment says must be kept in sync by hand",
     "why": "hand-kept duplicates drift, and the comment is the only thing holding them",
     "fix": "derive one from the other, or assert they match at start-up",
     "re": r"keep(?:s|ing)? in sync|must match|mirror(?:ed|s) in|copied from|duplicated? (?:in|of)"},
    {"id": "DATED-CONSTANT",
     "name": "a date baked into a constant, in a module other files import",
     "why": "a one-off script may hardcode a date; a shared module that does is a trap",
     "fix": "take the date from a parameter or the run's own clock",
     "re": r"^[ \t]*([A-Z][A-Z0-9_]{2,})\s*=[^\n=]*?[\"'/\\_-](20\d{2}-?\d{2}-?\d{2})",
     "referenced_only": True},
    {"id": "ARCHIVED-BUT-LIVE",
     "name": "marked deprecated or archived, still referenced by other files",
     "why": "dead code others still call is the version of dead code that bites",
     "fix": "finish the removal, or drop the marker and own it as current",
     "re": r"\b(?:deprecated|obsolete|archived|do not use)\b",
     "referenced_only": True},
]


def ensure_utf8_stdout() -> None:
    """Best-effort UTF-8 reconfigure so the output below does not crash a
    non-UTF-8 console (Windows cp950/cp437) -- a real local failure class, not a
    hypothetical one. No-ops where the stream cannot be reconfigured."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (OSError, ValueError):
                pass


def runtime_precheck(version_info=None) -> "str | None":
    version_info = sys.version_info if version_info is None else version_info
    if tuple(version_info[:2]) < MIN_PYTHON:
        return (f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ required, "
                f"found {version_info[0]}.{version_info[1]}.")
    return None


class ConfigError(Exception):
    """A malformed config stops the run and says so. Falling back to defaults
    without a word would report a check that never ran the way it looked."""


def load_config(root: Path, explicit: "Path | None") -> dict:
    cfg = dict(DEFAULTS)
    path = explicit if explicit is not None else root / CONFIG_NAME
    if not path.is_file():
        if explicit is not None:
            raise ConfigError(f"config file not found: {path}")
        return cfg
    try:
        whole = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ConfigError(f"config unreadable: {path} -- {exc}") from exc
    if not isinstance(whole, dict):
        raise ConfigError(f"config root must be an object: {path}")
    section = whole.get(CONFIG_SECTION, {})
    if not isinstance(section, dict):
        raise ConfigError(f"'{CONFIG_SECTION}' must be an object: {path}")
    unknown = sorted(set(section) - set(DEFAULTS))
    if unknown:
        raise ConfigError(f"unknown key(s) in '{CONFIG_SECTION}': {', '.join(unknown)}")
    cfg.update(section)
    return cfg


def excluded(rel: str, extra: "list[str]") -> bool:
    return any(fnmatch.fnmatch(rel, pat) for pat in BASE_EXCLUDE + extra)


def is_self(path: Path, root: Path) -> bool:
    resolved = path.resolve()
    return SELF_DIR != root and SELF_DIR.is_relative_to(root) and resolved.is_relative_to(SELF_DIR)


def collect(root: Path, globs, extra_exclude) -> "list[Path]":
    seen, out = set(), []
    for pattern in globs or []:
        for path in sorted(root.glob(pattern)):
            if not path.is_file() or is_self(path, root):
                continue
            rel = path.relative_to(root).as_posix()
            if rel in seen or excluded(rel, extra_exclude):
                continue
            seen.add(rel)
            out.append(path)
    return out


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def parse_yaml_block(block: str) -> dict:
    """Read a flat key: value block -- scalars, quoted strings, and [a, b] inline
    lists. Deliberately not a full YAML parser: the decision-log schema never
    nests, so this covers it without adding a dependency (same reader as
    verify_closeout.py)."""
    fields = {}
    for line in block.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            value = [i.strip().strip('"').strip("'") for i in inner.split(",") if i.strip()]
        elif len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        fields[key] = value
    return fields


def log_entries(text: str) -> "list[dict]":
    """Return one record per decision-log entry that carries a YAML block,
    with the line number of the block so a finding can point at it."""
    out = []
    for match in YAML_BLOCK.finditer(text):
        fields = parse_yaml_block(match.group(1))
        fields["_line"] = text.count("\n", 0, match.start()) + 1
        out.append(fields)
    return out


CODE_SPAN = re.compile(r"`[^`]*`")


def prose_lines(text: str):
    """Yield (line number, line with examples removed) for every line that is
    actually asserting a link.

    A document that teaches a link format is full of illustrations of it --
    fenced templates, and `[[path/from/root/file.md]]` in backticks. Read
    literally, every example is a broken link, and the first run of this check
    reported thirteen of them and nothing else. An example of a link is not a
    link: fenced blocks are skipped whole, inline code spans are blanked out.

    The decision log's own YAML blocks are fenced and are read separately, by
    log_entries(), which parses them on purpose."""
    in_fence = False
    for number, raw in enumerate(text.splitlines(), 1):
        stripped = raw.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        yield number, CODE_SPAN.sub(" ", raw)


def is_placeholder(value: str) -> bool:
    """True for `<path>`, `x`, `...` and other stand-ins for a real path. A
    placeholder is what a template writes where the reader supplies a value."""
    value = value.strip()
    if not value or "<" in value or ">" in value or "..." in value:
        return True
    return "/" not in value and "." not in value


def file_date(path: Path) -> datetime.date:
    """Date a citation carries: the stamp in its filename when it has one,
    otherwise the file's mtime. A filename stamp is the stronger signal --
    mtime moves every time anything in the file is touched."""
    match = DATE_IN_NAME.search(path.name)
    if match:
        try:
            return datetime.date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        except ValueError:
            pass
    return datetime.date.fromtimestamp(path.stat().st_mtime)


# --------------------------------------------------------------------------
# Check A -- size and growth
# --------------------------------------------------------------------------

def check_size(root: Path, cfg: dict, findings: list, volume: list, boundaries: list,
               standing: list) -> None:
    targets = cfg["size_targets"]
    if not isinstance(targets, list):
        raise ConfigError("'size_targets' must be a list of {glob, limit_kb} objects")

    scanned, over, misconfigured = 0, [], []
    for spec in targets:
        if not isinstance(spec, dict) or "glob" not in spec or "limit_kb" not in spec:
            raise ConfigError(f"each size target needs 'glob' and 'limit_kb': {spec}")
        limit = float(spec["limit_kb"]) * 1024
        group = collect(root, [spec["glob"]], cfg["exclude"])
        breached = [p for p in group if p.stat().st_size > limit]
        scanned += len(group)
        # When most of a group breaches its limit, the limit is the finding.
        # Reporting it once per file inflates the count a reader is using to
        # price the work, and points at the wrong thing: nothing is wrong with
        # those files, something is wrong with the number they were measured by.
        if group and len(breached) > len(group) / 2 and len(group) > 1:
            misconfigured.append((spec["glob"], len(breached), len(group), limit))
            continue
        for path in breached:
            over.append((path.relative_to(root).as_posix(), path.stat().st_size, limit))

    log_path = root / cfg["decision_log"]
    split_limit = float(cfg["log_split_kb"]) * 1024
    if log_path.is_file():
        size = log_path.stat().st_size
        scanned += 1
        if size > split_limit:
            findings.append({
                "id": "SIZE-LOG", "what": "the decision log is past its split threshold",
                "where": f"{cfg['decision_log']} ({size / 1024:.1f} KB > {split_limit / 1024:.1f} KB)",
                "fix": "move older entries to a dated archive, keep the current period live, "
                       "and update the summary and archive index in the same pass",
                "decision": True,
            })

    for glob, breached, total, limit in misconfigured:
        findings.append({
            "id": "SIZE-THRESHOLD",
            "what": f"{breached} of {total} files under this glob are over the limit, so the "
                    f"limit is what looks wrong, not the files",
            "where": f"{glob} (limit {limit / 1024:.1f} KB)",
            "fix": "set 'limit_kb' for this glob to a number this project can hold to, and "
                   "record why in the decision log; do not split documents to satisfy it",
            "decision": True,
        })
    for name, size, limit in sorted(over, key=lambda x: -x[1])[:20]:
        findings.append({
            "id": "SIZE-OVER", "what": "file is over the size limit set for its class",
            "where": f"{name} ({size / 1024:.1f} KB > {limit / 1024:.1f} KB)",
            "fix": "split it, or raise the limit in .harness-audit.json and say why in the log",
            "decision": True,
        })
    if len(over) > 20:
        boundaries.append(f"size: {len(over) - 20} further over-limit files not listed "
                          f"(the first 20 are above)")

    # Trend needs a previous run to compare against; the first run only records.
    history_path = root / cfg["history"]
    current = {}
    for spec in targets:
        for path in collect(root, [spec["glob"]], cfg["exclude"]):
            current[path.relative_to(root).as_posix()] = path.stat().st_size
    if log_path.is_file():
        current[cfg["decision_log"]] = log_path.stat().st_size

    previous = None
    if history_path.is_file():
        lines = [l for l in read(history_path).splitlines() if l.strip()]
        if lines:
            try:
                previous = json.loads(lines[-1])
            except json.JSONDecodeError as exc:
                # Say it. Treating an unreadable history as "no history" quietly
                # turns every run into a first run, and the trend never appears.
                boundaries.append(f"size: the last line of {cfg['history']} is not readable "
                                  f"JSON ({exc}); this run has no growth comparison. Delete "
                                  f"or repair that line to restore the trend")
    try:
        with history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"at": datetime.datetime.now().isoformat(timespec="seconds"),
                                     "sizes": current}, ensure_ascii=False) + "\n")
    except OSError as exc:
        boundaries.append(f"size: trend history could not be written ({exc}); "
                          f"this run has no growth comparison for the next one")

    if previous and isinstance(previous.get("sizes"), dict):
        grown = [(k, v - previous["sizes"][k]) for k, v in current.items()
                 if k in previous["sizes"] and v - previous["sizes"][k] > 0]
        grown.sort(key=lambda x: -x[1])
        volume.append(("size: files that grew since the last run", len(grown),
                       ", ".join(f"{k} +{d / 1024:.1f} KB" for k, d in grown[:3]) or "-"))
    else:
        boundaries.append("size: no previous run recorded, so this run reports absolute "
                          "sizes only -- growth appears from the second run onward")

    # The volume row must agree with the findings above it. Collapsing a
    # misconfigured group into one SIZE-THRESHOLD row once left its breached
    # files out of this count, so the report said "5 of 6 over the limit" in
    # one table and "0 over limit" in the next -- a reader who catches a
    # checker contradicting itself is right to stop trusting both numbers.
    collapsed = sum(breached for _, breached, _, _ in misconfigured)
    detail = f"{len(over) + collapsed} over limit"
    if misconfigured:
        detail += (f", {collapsed} of them under {len(misconfigured)} "
                   f"suspect threshold(s) -- see SIZE-THRESHOLD")
    volume.append(("size: files measured against a limit", scanned, detail))
    standing.append("size and growth -- re-run to see the trend; a single run has no direction")


# --------------------------------------------------------------------------
# Check B -- pointers that do not resolve
# --------------------------------------------------------------------------

def check_pointers(root: Path, cfg: dict, findings: list, volume: list,
                   boundaries: list, standing: list) -> None:
    log_path = root / cfg["decision_log"]
    checked = broken = 0

    def resolve(value: str, origin: Path) -> bool:
        value = value.strip().strip("`\"'")
        if not value or value.lower() in ("none", "-"):
            return True
        if value.startswith(("http://", "https://", "#", "mailto:")):
            return True
        candidate = (root / value).resolve()
        if candidate.exists():
            return True
        sibling = (origin.parent / value).resolve()
        return sibling.exists()

    if log_path.is_file():
        text = read(log_path)
        for entry in log_entries(text):
            source = entry.get("source")
            if isinstance(source, str):
                checked += 1
                if not resolve(source, log_path):
                    broken += 1
                    findings.append({
                        "id": "PTR-SOURCE",
                        "what": "a decision-log entry points at a file that is not on disk",
                        "where": f"{cfg['decision_log']}:{entry['_line']} -> {source}",
                        "fix": "create the document the decision belongs in, or correct the "
                               "path; an entry whose only home is the log is a decision the "
                               "next search will not surface",
                        "decision": True,
                    })
        for match in LEGACY_TARGET.finditer(text):
            checked += 1
            if not resolve(match.group(2), log_path):
                broken += 1
                line = text.count("\n", 0, match.start()) + 1
                findings.append({
                    "id": "PTR-SOURCE",
                    "what": "a legacy decision-log entry points at a file that is not on disk",
                    "where": f"{cfg['decision_log']}:{line} -> {match.group(2)}",
                    "fix": "correct the Target path; legacy entries stay as written otherwise",
                })
    else:
        boundaries.append(f"pointers: no decision log at {cfg['decision_log']}, so entry "
                          f"sources and correction grouping were not checked -- set "
                          f"'decision_log' in {CONFIG_NAME} if it lives elsewhere")

    scan_files = collect(root, cfg["link_scan"], cfg["exclude"])
    if log_path.is_file() and log_path not in scan_files:
        scan_files.append(log_path)

    heading_cache: "dict[Path, set]" = {}

    def headings_of(path: Path) -> set:
        if path not in heading_cache:
            heading_cache[path] = {h.strip().lower() for h in HEADING.findall(read(path))}
        return heading_cache[path]

    for path in scan_files:
        rel = path.relative_to(root).as_posix()
        text = read(path)
        for number, line in prose_lines(text):
            for match in WIKILINK.finditer(line):
                target, anchor = match.group(1), match.group(2)
                if target and is_placeholder(target):
                    continue
                checked += 1
                where = (root / target).resolve() if target else path
                if target and not where.exists():
                    broken += 1
                    findings.append({
                        "id": "PTR-WIKILINK",
                        "what": "a WikiLink names a file that is not on disk",
                        "where": f"{rel}:{number} -> [[{target}]]",
                        "fix": "correct the path, or remove the link if the target was merged away",
                    })
                    continue
                if anchor and where.is_file() and anchor.strip().lower() not in headings_of(where):
                    broken += 1
                    findings.append({
                        "id": "PTR-WIKILINK",
                        "what": "a WikiLink names a heading that does not exist in the target",
                        "where": f"{rel}:{number} -> [[{target or ''}#{anchor}]]",
                        "fix": "match the heading text exactly -- a WikiLink is followed by "
                               "grepping for it, so a near-miss is a dead link",
                    })
            for match in EVIDENCE.finditer(line):
                if is_placeholder(match.group(1)):
                    continue
                checked += 1
                if not resolve(match.group(1), path):
                    broken += 1
                    findings.append({
                        "id": "PTR-EVIDENCE",
                        "what": "an evidence path in a report does not exist",
                        "where": f"{rel}:{number} -> {match.group(1)}",
                        "fix": "attach the evidence file, or mark the line FAIL with the "
                               "reason it has none",
                        "decision": True,
                    })
            for match in MD_LINK.finditer(line):
                target = match.group(1).split("#", 1)[0]
                if (not target or target.startswith(("http://", "https://", "mailto:"))
                        or is_placeholder(target)):
                    continue
                checked += 1
                if not resolve(target, path):
                    broken += 1
                    findings.append({
                        "id": "PTR-LINK",
                        "what": "a relative Markdown link does not resolve",
                        "where": f"{rel}:{number} -> {target}",
                        "fix": "correct the path, or point it at whatever replaced the target",
                    })

    volume.append(("pointers: references resolved", checked,
                   f"{broken} broken" if checked else "nothing to resolve"))
    if not checked:
        boundaries.append("pointers: no entry source, WikiLink, evidence path, or relative "
                          "link was found in the scanned files, so this check reported "
                          "nothing because it read nothing -- not because the links are good")
    boundaries.append("pointers: a link that resolves is not a link that says what the "
                      "reader needs -- only existence is checked")
    standing.append("pointer integrity -- links rot on every rename, so this belongs in CI "
                    "rather than in one cleanup pass")


# --------------------------------------------------------------------------
# Check C -- corrections piling up on one cause
# --------------------------------------------------------------------------

def check_corrections(root: Path, cfg: dict, findings: list, volume: list,
                        boundaries: list, standing: list) -> None:
    log_path = root / cfg["decision_log"]
    if not log_path.is_file():
        volume.append(("corrections: entries grouped", 0, "skipped, no decision log"))
        return

    threshold = int(cfg["patch_threshold"])
    groups = defaultdict(list)
    ungrouped = 0
    total = 0
    for entry in log_entries(read(log_path)):
        if entry.get("type") not in ("correction", "amendment"):
            continue
        total += 1
        key = entry.get("root_cause")
        keys = [key] if isinstance(key, str) and key else []
        if not keys:
            tags = entry.get("tags")
            keys = [t for t in tags if t] if isinstance(tags, list) else []
        if not keys:
            ungrouped += 1
            continue
        for k in keys:
            groups[k].append(entry["_line"])

    for key, lines in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        if len(lines) >= threshold:
            findings.append({
                "id": "PATCH-COUNT",
                "what": f"{len(lines)} corrections share one cause ('{key}'), at or over the "
                        f"escalation threshold of {threshold}",
                "where": f"{cfg['decision_log']}:" + ",".join(str(l) for l in lines[:6])
                         + (" ..." if len(lines) > 6 else ""),
                "fix": "stop patching and freeze a workorder against the cause itself; "
                       "each further local fix adds a strike to the same line",
                "decision": True,
            })

    volume.append(("corrections: entries grouped by cause", total,
                   f"{len(groups)} causes, {ungrouped} ungrouped"))
    if ungrouped:
        boundaries.append(f"corrections: {ungrouped} correction/amendment entries carry no "
                          f"tag and no root_cause key, so they group with nothing -- add one "
                          f"of those keys when writing the entry, not afterwards")
    standing.append("correction counting -- the count only rises as entries are written, so "
                    "this is a recurring read of the log, not a one-off fix")


# --------------------------------------------------------------------------
# Check D -- debt signals in code
# --------------------------------------------------------------------------

def check_signals(root: Path, cfg: dict, findings: list, volume: list,
                  boundaries: list, standing: list) -> None:
    files = collect(root, cfg["code_globs"], cfg["exclude"])
    if not files:
        volume.append(("signals: source files scanned", 0, "no code matched code_globs"))
        return

    bodies = {path: read(path) for path in files}
    stems = {path.stem: path for path in files}
    referenced = defaultdict(set)
    for path, body in bodies.items():
        for stem, target in stems.items():
            if target == path or len(stem) < 3:
                continue
            if (re.search(rf"^\s*(?:from\s+{re.escape(stem)}\s+import|import\s+{re.escape(stem)})\b",
                          body, re.MULTILINE)
                    or re.search(rf"""['"/\\]{re.escape(stem)}(?:\.\w+)?['"]""", body)):
                referenced[target].add(path.relative_to(root).as_posix())

    disabled = set(cfg.get("disable_signals") or [])
    unknown = disabled - {s["id"] for s in SIGNALS}
    if unknown:
        raise ConfigError(f"unknown id(s) in 'disable_signals': {', '.join(sorted(unknown))}")

    counts = {}
    for signal in SIGNALS:
        if signal["id"] in disabled:
            boundaries.append(f"signals: {signal['id']} is switched off in "
                              f"{CONFIG_NAME}, so this run says nothing about it")
            continue
        pattern = re.compile(signal["re"],
                             re.MULTILINE | (re.DOTALL if signal.get("multiline") else 0))
        hits, seen = [], set()
        for path, body in bodies.items():
            if signal.get("referenced_only") and not referenced.get(path):
                continue
            rel = path.relative_to(root).as_posix()
            lines = body.splitlines()
            for match in pattern.finditer(body):
                line = body.count("\n", 0, match.start()) + 1
                # One line, one finding per signal. Two keywords from the same
                # pattern on one line -- "TODO: temporary shim" -- is one thing
                # to look at, and counting it twice inflates the total a reader
                # is using to price the work.
                if (rel, line) in seen:
                    continue
                seen.add((rel, line))
                # Quote the whole line, not the matched span: a regex that stops
                # at a capture group prints `X = "out/2026-01-05` with the quote
                # unclosed, and truncated evidence costs the report more trust
                # than the finding earns.
                whole = lines[line - 1].strip() if line <= len(lines) else match.group(0)
                if signal.get("exclude_re") and re.search(signal["exclude_re"], whole):
                    continue
                extra = ""
                if signal.get("referenced_only"):
                    users = sorted(referenced.get(path, ()))
                    extra = (f" [imported by {len(users)}: "
                             f"{', '.join(users[:3])}{' ...' if len(users) > 3 else ''}]")
                hits.append((rel, line, whole[:110] + extra))
        counts[signal["id"]] = len(hits)
        for rel, line, snippet in hits[:5]:
            findings.append({
                "id": signal["id"], "what": f"{signal['name']} -- {signal['why']}",
                "where": f"{rel}:{line}  {snippet}",
                "fix": signal["fix"], "look_first": True,
            })
        if len(hits) > 5:
            boundaries.append(f"signals: {signal['id']} has {len(hits) - 5} further hits "
                              f"not listed (5 shown); re-run with the id to see the rest")

    volume.append(("signals: source files scanned", len(files),
                   ", ".join(f"{k}={v}" for k, v in counts.items() if v) or "no hits"))
    boundaries.append("signals: these are shapes that often accompany debt, not defects -- a "
                      "regex cannot tell a deliberate fallback from an accidental one, so "
                      "every hit needs one look before it becomes work")
    boundaries.append("signals: how long a marker has sat there is not measured. File mtime "
                      "answers 'when was this file last touched', which runs opposite to the "
                      "question -- the busiest files look the freshest. Only version control "
                      "answers it, and this script does not shell out to one")
    standing.append("debt signals -- new code adds new signals, so this is a recurring scan")


# --------------------------------------------------------------------------
# Check E -- what nothing has referenced lately
# --------------------------------------------------------------------------

def check_references(root: Path, cfg: dict, findings: list, volume: list,
                     boundaries: list, standing: list) -> None:
    tracked = collect(root, cfg["reference_track"], cfg["exclude"])
    if not tracked:
        volume.append(("references: documents tracked", 0, "nothing matched reference_track"))
        return

    tracked_set = {p.resolve() for p in tracked}
    citing = [p for p in collect(root, cfg["reference_cited_by"], cfg["exclude"])
              if p.resolve() not in tracked_set]
    if not citing:
        # With nothing to cite from, every tracked document is trivially
        # "never cited" -- a check run against an empty input set, reporting
        # verdicts it has no evidence for. Say the input was empty instead.
        volume.append(("references: documents tracked", len(tracked),
                       "not judged, citation set is empty"))
        boundaries.append("references: nothing matched 'reference_cited_by', so no document "
                          "could be found cited and none was reported. Point that glob at "
                          "the folders where work refers to these documents")
        return
    stale_days = int(cfg["stale_days"])
    today = datetime.date.today()

    bodies = [(p, read(p), file_date(p)) for p in citing]
    ledger, never, stale = {}, [], []
    for path in tracked:
        rel = path.relative_to(root).as_posix()
        name = path.name
        # A skill folder is usually cited by its folder name, not by SKILL.md.
        # The bare name needs word boundaries: a folder called `thing` matched
        # the word "Nothing" and reported itself cited by the very document that
        # says nothing references it. Paths and filenames are distinctive enough
        # to match plainly; a bare stem is not.
        label = path.parent.name if name.upper() == "SKILL.MD" else path.stem
        label_re = (re.compile(rf"(?<![\w-]){re.escape(label)}(?![\w-])")
                    if len(label) > 2 else None)
        cites = [(date, p.relative_to(root).as_posix())
                 for p, body, date in bodies
                 if rel in body or name in body or (label_re and label_re.search(body))]
        if not cites:
            ledger[rel] = {"last": None, "by": None, "count": 0}
            never.append(rel)
            continue
        cites.sort(reverse=True)
        last, by = cites[0]
        ledger[rel] = {"last": last.isoformat(), "by": by, "count": len(cites),
                       "age_days": (today - last).days}
        if (today - last).days > stale_days:
            stale.append((rel, last, (today - last).days))

    for rel in never[:10]:
        findings.append({
            "id": "REF-NEVER", "what": "nothing in the citation set references this document",
            "where": rel,
            "fix": "cite it from the work that uses it, or retire it -- but retiring also "
                   "needs the second condition below, which this check cannot answer",
            "decision": True,
        })
    for rel, last, age in sorted(stale, key=lambda x: -x[2])[:10]:
        findings.append({
            "id": "REF-STALE",
            "what": f"last referenced {age} days ago, past the {stale_days}-day mark",
            "where": f"{rel} (last cited by {ledger[rel]['by']}, {last.isoformat()})",
            "fix": "confirm it is still the live version, or fold it into whatever replaced it",
            "decision": True,
        })

    try:
        (root / cfg["reference_ledger"]).write_text(
            json.dumps({"generated": today.isoformat(), "stale_days": stale_days,
                        "ledger": ledger}, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError as exc:
        boundaries.append(f"references: ledger could not be written ({exc})")

    volume.append(("references: documents tracked", len(tracked),
                   f"{len(never)} never cited, {len(stale)} stale, "
                   f"{len(citing)} citing files read"))
    boundaries.append("references: never-cited does not mean retire. Retiring needs a second "
                      "condition -- that something else now covers what this document does -- "
                      "and that is a reading, not a count. This check supplies the count only")
    boundaries.append("references: a citation is detected by the document's path, filename, or "
                      "folder name appearing in the text. A document referred to only by "
                      "description is invisible here")
    standing.append("reference ledger -- the ledger is rewritten every run and is only "
                    "meaningful over time")


# --------------------------------------------------------------------------
# Report
# --------------------------------------------------------------------------

def render(root: Path, cfg: dict, findings, volume, boundaries, standing) -> str:
    out = []
    w = out.append
    w("# Repo audit")
    w("")
    w(f"Root: `{root}` | decision log: `{cfg['decision_log']}` | "
      f"generated by `repo_audit.py`, standard library only.")
    w("")
    w("Every number below was measured during this run. Findings are split by what they "
      "cost you to act on: the first table is wrong on its face, the second is a shape "
      "that *often* means something and needs one look before it becomes work. Some rows "
      "name an edit; the rest name a decision with two branches, and the report says which "
      "it is rather than calling both a fix.")
    w("")

    broken = [f for f in findings if not f.get("look_first")]
    look = [f for f in findings if f.get("look_first")]

    def table(rows):
        # Two axes, because they are not the same question and a reader needs
        # both. Certainty ("is this established?") decides which table a row is
        # in. Autonomy ("may I do this alone?") decides whether an agent acts or
        # asks -- and the first reader of this report is usually an agent
        # sorting exactly that. Leaving autonomy implicit made every reader
        # re-derive it row by row.
        w("| id | autonomy | what | where | what closes it |")
        w("|---|---|---|---|---|")
        for item in rows:
            where = item["where"].replace("|", "\\|")
            autonomy = "needs-decision" if item.get("decision") or item.get("look_first") \
                else "mechanical"
            w(f"| `{item['id']}` | {autonomy} | {item['what']} | `{where}` | {item['fix']} |")
        w("")

    w("## Broken as found")
    w("")
    if broken:
        w("Each of these is a fact about the records: a path that does not resolve, a file "
          "past a limit someone set, a count past a threshold someone set. Nothing here "
          "needs interpretation to establish — though several need a decision to close.")
        w("")
        table(broken)
    else:
        w("Nothing. Read the volume table before reading that as good news: a check that "
          "scanned zero things also finds nothing.")
        w("")

    w("## Look before acting")
    w("")
    if look:
        w("Signals, not defects. A regex cannot tell a deliberate fallback from an "
          "accidental one, so each row is a place to look, and the looking is the work. "
          "Do not convert this table into a task list without reading the code first.")
        w("")
        table(look)
    else:
        w("No signals matched, or none were enabled.")
        w("")

    w("## Volume")
    w("")
    w("| check | scanned | result |")
    w("|---|---|---|")
    for label, count, detail in volume:
        w(f"| {label} | {count} | {detail} |")
    w("")

    w("## Standing checks, not one-off fixes")
    w("")
    w("These stay true after the findings above are cleared: each one measures a state that "
      "keeps changing, so it earns a place in CI or a periodic run rather than a cleanup pass.")
    w("")
    for item in standing:
        w(f"- {item}")
    w("")

    w("## What this run could not measure")
    w("")
    for item in boundaries:
        w(f"- {item}")
    w("- semantics: whether a decision, a rule, or a claim is *correct* is not checked "
      "anywhere in this script. Every check here answers a question about form.")
    w("- taste: nothing here looks at a render, listens to audio, or judges tone.")
    w("- scale: this run read what the globs matched and nothing else. The volume table "
      "is the coverage figure -- there is no separate measure of how much of the project "
      "went unread, and no way for this script to tell a real repository from a fixture.")
    w("- path case: on a case-insensitive filesystem (Windows, macOS by default) a "
      "reference resolves regardless of case, so a link that passes here can still break "
      "on a case-sensitive CI runner.")
    w("")

    w("## Disposition")
    w("")
    w(f"{len(broken)} finding(s) broken as found, {len(look)} signal(s) needing a look "
      f"first. {len(standing)} check(s) are recurring by nature and never close. "
      f"{len(boundaries) + 2} stated limit(s) on what this run measured. "
      f"Nothing beyond what each row states is implied by this report.")
    w("")
    w(BOUNDARY_EN)
    w(BOUNDARY_ZH)
    return "\n".join(out)


def main(argv=None) -> int:
    ensure_utf8_stdout()
    problem = runtime_precheck()
    if problem:
        print(f"[RUNTIME] {problem}")
        print(BOUNDARY_EN)
        return 2

    parser = argparse.ArgumentParser(
        description="Check a project's own records and code for form failures an agent can act on")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--config", type=Path, default=None,
                        help=f"config file (default: <root>/{CONFIG_NAME} when present)")
    parser.add_argument("--report", type=Path, default=None,
                        help="also write the report to this path")
    parser.add_argument("--only", default=None,
                        help="comma-separated subset of: size,pointers,corrections,signals,references")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    if not root.is_dir():
        print(f"[ERROR] root is not a directory: {root}")
        return 2

    checks = [("size", check_size), ("pointers", check_pointers),
              ("corrections", check_corrections), ("signals", check_signals),
              ("references", check_references)]
    if args.only:
        wanted = {x.strip() for x in args.only.split(",") if x.strip()}
        unknown = wanted - {name for name, _ in checks}
        if unknown:
            print(f"[ERROR] unknown check(s): {', '.join(sorted(unknown))}")
            return 2
        checks = [(name, fn) for name, fn in checks if name in wanted]

    findings, volume, boundaries, standing = [], [], [], []
    try:
        cfg = load_config(root, args.config)
        # The report this run is about to write must not be an input to the next
        # one. Left in, it feeds the reference check a document that names every
        # tracked file, so on the second run everything looks cited and the
        # orphan this check exists to surface disappears -- CASES.md case 2,
        # reproduced by the exact command the README prints. A name pattern is
        # not enough: the path is whatever --report was given, so it is excluded
        # by its own path.
        if args.report is not None:
            target = args.report if args.report.is_absolute() else root / args.report
            try:
                cfg["exclude"] = list(cfg["exclude"]) + [
                    target.resolve().relative_to(root).as_posix()]
            except ValueError:
                pass  # written outside the scanned tree; nothing to exclude
        for _, fn in checks:
            fn(root, cfg, findings, volume, boundaries, standing)
    except ConfigError as exc:
        print(f"[ERROR] {exc}")
        print("Fix the config, or delete it to fall back to the built-in defaults.")
        print(BOUNDARY_EN)
        return 2

    if not any(count for _, count, _ in volume):
        print("Unable to verify, skipped: no records or source files matched the "
              "configured globs")
        print("無法驗證，跳過")
        print(f"Point '{CONFIG_SECTION}' in {CONFIG_NAME} at this project's own layout.")
        print(BOUNDARY_EN)
        return 2

    report = render(root, cfg, findings, volume, boundaries, standing)
    print(report)
    if args.report is not None:
        path = args.report if args.report.is_absolute() else root / args.report
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(report + "\n", encoding="utf-8")
        print(f"\n[OK] report written to {path}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
