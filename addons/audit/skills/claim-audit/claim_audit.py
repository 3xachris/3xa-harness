#!/usr/bin/env python3
"""Candidate scanner for numeric claims written without a source.

Reads Markdown records -- a decision log, orders, closeouts, docs -- and lists
the lines that state a number as fact while carrying nothing a reader could
check it against. Every hit is a **candidate for a human to judge**, never a
verdict: false positives are expected and are not defects.

Needs Python 3.9+ on PATH. Standard library only, no configuration required to
start. See README, section "Record audits", for the config file and the
optional hook wiring.

Exit codes: 0 nothing to look at, 1 candidates for a human, 2 could not check.
"""
from __future__ import annotations
import argparse
import fnmatch
import hashlib
import json
import re
import sys
from pathlib import Path

MIN_PYTHON = (3, 9)  # Path.is_relative_to and dict ordering guarantees used below

CONFIG_NAME = ".harness-audit.json"
CONFIG_SECTION = "claim_audit"
KNOWN_KEYS = {
    "targets", "exclude", "baseline",
    "claim_patterns", "claim_patterns_replace_defaults",
    "source_patterns", "source_patterns_replace_defaults",
    "exempt_patterns", "exempt_patterns_replace_defaults",
}

# Defaults aim at the layout the README recommends (docs/decisions.md plus an
# artifacts folder per task). A project that keeps its records somewhere else
# changes `targets` and nothing else.
DEFAULT_TARGETS = [
    "docs/decisions.md",
    "docs/**/*.md",
    "artifacts/**/*.md",
]
DEFAULT_EXCLUDE = [
    "**/.git/**",
    "**/node_modules/**",
    "**/.venv/**",
    "**/venv/**",
    "**/dist/**",
    "**/build/**",
    "**/*.bak",
    "**/*_backup*",
]
DEFAULT_BASELINE = ".harness-audit-baseline.json"

# "This line states a number as fact." Units are deliberately broad: the check
# is cheap and a human reads the result.
DEFAULT_CLAIM_PATTERNS = [
    # A percent sign is not a word character, so a trailing \b after it can
    # never match mid-sentence -- "cuts latency by 35% and" went undetected
    # until a fixture with a known percentage claim reported clean. Units that
    # are punctuation get (?!\w); units that are letters keep \b.
    r"\b\d+(?:\.\d+)?\s*%(?!\w)",
    r"\b\d+(?:\.\d+)?\s*per\s?cent\w*\b",           # spelled out; "30 percent" read clean once
    r"\b\d+(?:\.\d+)?\s*(?:px|fps|ms|KB|MB|GB|TB|Hz|kHz)\b",
    r"\b\d+(?:\.\d+)?\s*(?:seconds?|secs?|minutes?|mins?|hours?|hrs?|days?|weeks?|months?|years?)\b",
    r"\b\d+(?:\.\d+)?\s*[x×](?![\w-])",             # bare multiplier: "4x", "1.5×"
    r"\b\d+(?:\.\d+)?\s*(?:times)\b",
    # One comparative may sit between the number and its noun: "900 more requests"
    # read clean while "900 requests" did not, and nothing warned that it would.
    r"\b\d+\s*(?:more|fewer|less|extra|additional|further)?\s*"
    r"(?:files?|lines?|entries|items?|cases?|runs?|calls?|users?|tests?|errors?"
    r"|warnings?|requests?|records?|rows?|commits?|issues?|attempts?|features?"
    r"|releases?|deploys?|incidents?|customers?|tickets?|PRs?)\b",
    r"\b\d+\s*[-–~]\s*\d+\b",
    r"\bv?\d+\.\d+(?:\.\d+)?\b",
    r"[$€£¥]\s?\d",
    # CJK units. This pack ships a Traditional Chinese README and both scripts
    # print a bilingual closing line, so a detector anchored only to Latin units
    # leaves its own documented audience with percent-signs and nothing else:
    # "returned 3 times", "2x faster", "saved 3 hours" all read clean in Chinese
    # while their English equivalents were caught.
    r"\d+(?:\.\d+)?\s*(?:秒|分鐘|小時|天|週|個月|年|次|倍|支|張|篇|筆|條|行|檔|份|個|人|頁|字)",
    r"\d+(?:\.\d+)?\s*(?:成|折)",
]

# "A reader could go and check this." Anything on this list makes the line pass.
# These are shape-only: a date, a verb, a ticket id cannot be checked against
# anything, so writing one is taken on trust and the docs say so.
DEFAULT_SOURCE_PATTERNS = [
    r"\b(?:19|20)\d{2}-\d{2}-\d{2}\b",             # ISO date
    r"https?://",                                  # URL
    r"\b(?:evidence|source|measured|benchmark|verified|checked|per)\s*[:=]",
    r"\b(?:measured|benchmarked|reproduced|profiled|counted|timed)\b",
    r"§\s?\d|\bsections?\s+\d",                     # cross-reference to a section
    r"\bAC-\d+\b",                                 # acceptance line reference
    r"\b[A-Z]{2,}-\d+\b",                          # ticket id
    r"#\d+\b",                                     # issue reference
]

# Path-shaped citations are the one source class a scanner CAN verify, so it
# does: a cited file counts as a source only when it exists. Shape alone let
# `see \`totally.made.up\`` silence a latency claim -- a fake filename was a
# free pass, and inventing one is easier than hedging. Existence is still not
# truth (the file may not support the number), but a citation that cannot even
# be opened is not a citation.
DEFAULT_VERIFIABLE_PATTERNS = [
    r"\b(?P<p1>[\w./\\-]+\.[A-Za-z0-9]{1,6}):\d+",   # path.ext:123
    r"`(?P<p2>[^`\s]*\.[A-Za-z0-9]{1,6})(?::\d+)?`", # `path.ext` / `path.ext:123`
    r"\[\[(?P<p3>[^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]",  # [[path]] WikiLink
    r"\[[^\]]+\]\((?P<p4>[^)#\s]+)(?:#[^)]*)?\)",    # [text](path) Markdown link
]

# Honest hedging is the behaviour this check wants, so it never flags it.
# The hedge words have to sit in front of a number to count. Matching them
# anywhere let ordinary prepositional English through: "the artifacts folder
# around this script" exempted a version claim on the same line, and a checker
# with a silent hole reports success it never performed.
DEFAULT_EXEMPT_PATTERNS = [
    r"\[UNVERIFIED\]",
    r"\b(?:TODO|TBD|FIXME)\b",
    r"\bunverified\b",
    # The rest have to stand next to the number they qualify. A hedge parked at
    # the far end of a paragraph exempts claims it never modified, and the
    # exemption list is the one thing an author can use to retire this check on
    # purpose -- so it gets the narrowest form that still recognises real hedging.
    # Either order: "estimated 40 minutes" and "40 minutes, estimated" are the
    # same concession. Only the distance is bounded.
    r"\b(?:draft|estimate[sd]?|assumed?|assumption|hypothes\w+|guess\w*)\b[^\n]{0,24}?\d",
    r"\d[^\n]{0,24}?\b(?:draft|estimate[sd]?|assumed?|assumption|hypothes\w+|guess\w*)\b",
    r"\b(?:approx\w*|roughly|about|around|circa|some|nearly|almost|up to)\s+~?\d",
    r"~\d",
]

# Structural lines that carry no prose claim of their own.
SKIP_LINE = re.compile(r"^\s*(?:\||#{1,6}\s|>\s*$|-{3,}\s*$|\*{3,}\s*$|:?-{2,}:?\s*\|)")

BOUNDARY_EN = "This checks form only. Whether a claim is true is for a human."
BOUNDARY_ZH = "這支只驗形式，內容對不對是人的事"
CANDIDATE_NOTE = (
    "Candidate detector, not a judge -- false positives are expected. "
    "Handle each one: add the source, mark it [UNVERIFIED], or delete the claim. "
    "Do not reset the baseline to make it quiet."
)


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
    """Return a problem description if the running interpreter is below
    MIN_PYTHON, else None. Takes an optional version_info so the check can be
    exercised without a second interpreter installed."""
    version_info = sys.version_info if version_info is None else version_info
    if tuple(version_info[:2]) < MIN_PYTHON:
        return (f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ required, "
                f"found {version_info[0]}.{version_info[1]}.")
    return None


class ConfigError(Exception):
    """A malformed config stops the run and says so. A check that silently
    falls back to defaults reports success it never performed."""


def load_config(root: Path, explicit: "Path | None") -> dict:
    path = explicit if explicit is not None else root / CONFIG_NAME
    if not path.is_file():
        if explicit is not None:
            raise ConfigError(f"config file not found: {path}")
        return {}
    try:
        whole = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ConfigError(f"config unreadable: {path} -- {exc}") from exc
    if not isinstance(whole, dict):
        raise ConfigError(f"config root must be an object: {path}")
    section = whole.get(CONFIG_SECTION, {})
    if not isinstance(section, dict):
        raise ConfigError(f"'{CONFIG_SECTION}' must be an object: {path}")
    # A typo'd key that quietly does nothing is a check you think you configured
    # and didn't: `target` instead of `targets` silently reverts to the defaults
    # and scans a directory you never asked about, then reports clean.
    unknown = sorted(set(section) - KNOWN_KEYS)
    if unknown:
        raise ConfigError(f"unknown key(s) in '{CONFIG_SECTION}': {', '.join(unknown)}. "
                          f"Known keys: {', '.join(sorted(KNOWN_KEYS))}")
    return section


def cited_path_exists(line: str, verifiable, root: Path, origin: Path) -> "bool | None":
    """Return True if the line cites a path that exists, False if it cites only
    paths that do not, None if it cites no path at all. Resolution tries the
    project root, then the citing file's own folder; a `:line` suffix and a
    URL-shaped token are handled before the lookup."""
    # Links are read from a copy with inline code spans blanked: a WikiLink
    # inside backticks is a quoted example of the syntax, not a live citation,
    # and reading it as one flagged a core skill's format documentation. The
    # backtick-path form keeps the raw line -- there the backticks are the
    # citation syntax itself.
    blanked = re.sub(r"`[^`]*`", " ", line)
    tokens = []
    for pattern in verifiable:
        keys = pattern.groupindex.keys()
        haystack = blanked if ("p3" in keys or "p4" in keys) else line
        for match in pattern.finditer(haystack):
            token = next((g for g in match.groupdict().values() if g), None)
            if token:
                tokens.append(token.strip().strip("\"'"))
    tokens = [t for t in tokens
              if t and not t.startswith(("http://", "https://", "mailto:"))
              # `.md` alone is prose naming an extension, not a file citation.
              and not re.fullmatch(r"\.[A-Za-z0-9]{1,6}", t)]
    if not tokens:
        return None
    for token in tokens:
        token = re.sub(r":\d+$", "", token)
        for base in (root, origin.parent):
            try:
                if (base / token).exists():
                    return True
            except OSError:
                continue
    return False


def compile_patterns(defaults: "list[str]", section: dict, key: str) -> "list[re.Pattern]":
    """Config patterns extend the built-ins unless the section says to replace
    them, so a project adding one unit of its own does not silently lose the
    rest of the detection."""
    extra = section.get(key, [])
    if not isinstance(extra, list) or any(not isinstance(x, str) for x in extra):
        raise ConfigError(f"'{key}' must be a list of regex strings")
    base = [] if section.get(f"{key}_replace_defaults") else list(defaults)
    out = []
    for raw in base + extra:
        try:
            out.append(re.compile(raw, re.IGNORECASE))
        except re.error as exc:
            raise ConfigError(f"'{key}' has an invalid regex {raw!r}: {exc}") from exc
    return out


def excluded(rel_posix: str, patterns: "list[str]") -> bool:
    return any(fnmatch.fnmatch(rel_posix, pat) for pat in patterns)


def collect(root: Path, targets: "list[str]", exclude: "list[str]") -> "tuple[list, dict]":
    """Return the files, and how many each glob matched.

    The per-glob count is reported because a glob that matches nothing is
    invisible otherwise: the run says "1 record scanned, 0 claims" and exits
    clean while the directory you asked about was never opened."""
    seen, out, per_glob = set(), [], {}
    for pattern in targets:
        matched = 0
        for path in sorted(root.glob(pattern)):
            if not path.is_file() or path.suffix.lower() != ".md":
                continue
            matched += 1
            rel = path.relative_to(root).as_posix()
            if rel in seen or excluded(rel, exclude):
                continue
            seen.add(rel)
            out.append(path)
        per_glob[pattern] = matched
    return out, per_glob


def line_key(text: str) -> str:
    """Baseline key = a hash of the line's content with whitespace removed.
    Keyed on content rather than line number: inserting a paragraph moves every
    line below it, and a line-number baseline reports all of them as new."""
    return hashlib.sha1("".join(text.split()).encode("utf-8")).hexdigest()[:12]


# A number of two or more characters carries an identity a single digit does
# not: "200", "3.9", "12.5" pick out one claim, "1" and "5" appear in every
# other sentence. Only distinctive numbers can say "this line restates that one".
DISTINCTIVE_NUMBER = re.compile(r"\d[\d.,]*\d")


def numbers_in(line: str) -> "set[str]":
    return {m.group(0).rstrip(".,") for m in DISTINCTIVE_NUMBER.finditer(line)
            if len(m.group(0).rstrip(".,")) >= 2}


def scan_text(text: str, claim, source, exempt, verifiable=None,
              root: "Path | None" = None, origin: "Path | None" = None) -> "tuple[list, list]":
    """Return (candidates, restatements).

    A **restatement** is a line whose every distinctive number already appears
    on a sourced line in the same file -- a checklist repeating a threshold the
    document pinned and justified earlier. It is still reported, in its own
    quieter list, because suppressing a finding outright is how a checker starts
    reporting clean runs it did not earn. It does not count as work to do."""
    rows, sourced_numbers = [], set()
    in_fence = False
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if line.startswith("```") or line.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence or not line or SKIP_LINE.match(line):
            continue
        if not any(p.search(line) for p in claim):
            continue
        if any(p.search(line) for p in exempt):
            continue
        cited = (cited_path_exists(line, verifiable, root, origin)
                 if verifiable and root and origin else None)
        if cited or (cited is None and any(p.search(line) for p in source)):
            # A verified citation, or a contextual signal on a line that cites
            # no path at all. A line whose only citation is a path that does
            # NOT exist falls through: naming a file nobody can open is not a
            # source, whatever else sits on the line.
            sourced_numbers |= numbers_in(line)
            continue
        rows.append((number, line[:160]))

    candidates, restatements = [], []
    for number, line in rows:
        marks = numbers_in(line)
        (restatements if marks and marks <= sourced_numbers else candidates).append(
            (number, line))
    return candidates, restatements


def scan_file(path: Path, claim, source, exempt, verifiable=None,
              root: "Path | None" = None) -> "tuple[list, list]":
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return [], []
    return scan_text(text, claim, source, exempt, verifiable, root, path)


def load_baseline(path: Path) -> "tuple[dict, str | None]":
    """Return (baseline, problem). An unreadable baseline is reported, never
    swallowed: read as empty, it turns every known line back into a new one and
    the run looks like a first run forever."""
    if not path.is_file():
        return {}, None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return {}, f"baseline {path.name} is unreadable ({exc}); comparing against nothing"
    if not isinstance(data, dict):
        return {}, f"baseline {path.name} is not an object; comparing against nothing"
    if any(isinstance(x, int) for v in data.values() if isinstance(v, list) for x in v):
        return {}, (f"baseline {path.name} is keyed by line number, which reports every line "
                    f"below an insertion as new. Rerun with --baseline to rebuild it")
    return data, None


def run_scan(root: Path, section: dict) -> dict:
    targets = section.get("targets") or DEFAULT_TARGETS
    exclude = list(DEFAULT_EXCLUDE) + list(section.get("exclude") or [])
    if not isinstance(targets, list):
        raise ConfigError("'targets' must be a list of glob strings")
    claim = compile_patterns(DEFAULT_CLAIM_PATTERNS, section, "claim_patterns")
    source = compile_patterns(DEFAULT_SOURCE_PATTERNS, section, "source_patterns")
    exempt = compile_patterns(DEFAULT_EXEMPT_PATTERNS, section, "exempt_patterns")
    verifiable = [re.compile(p, re.IGNORECASE) for p in DEFAULT_VERIFIABLE_PATTERNS]

    files, per_glob = collect(root, targets, exclude)
    result, restated = {}, {}
    for path in files:
        hits, repeats = scan_file(path, claim, source, exempt, verifiable, root)
        rel = path.relative_to(root).as_posix()
        if hits:
            result[rel] = hits
        if repeats:
            restated[rel] = repeats
    return {"files": files, "result": result, "restated": restated, "per_glob": per_glob,
            "baseline_path": root / (section.get("baseline") or DEFAULT_BASELINE)}


def diff_baseline(result: dict, baseline: dict) -> dict:
    new = {}
    for name, hits in result.items():
        known = set(baseline.get(name, []))
        fresh = [(n, t) for n, t in hits if line_key(t) not in known]
        if fresh:
            new[name] = fresh
    return new


def cmd_scan(args, root: Path, section: dict) -> int:
    scan = run_scan(root, section)
    files, result = scan["files"], scan["result"]
    if not files:
        print("[SKIP] no Markdown records matched the target globs; nothing to check")
        print("無法驗證，跳過")
        print("Set 'claim_audit.targets' in .harness-audit.json to your records' paths.")
        print(BOUNDARY_EN)
        return 2

    baseline_path = scan["baseline_path"]
    if args.baseline:
        payload = {name: sorted({line_key(t) for _, t in hits})
                   for name, hits in result.items()}
        baseline_path.write_text(json.dumps(payload, ensure_ascii=False, indent=1),
                                 encoding="utf-8")
        total = sum(len(v) for v in result.values())
        print(f"[OK] baseline written to {baseline_path.name} "
              f"({total} lines, keyed by content hash)")
        print("From now on only lines added after this point are reported.")
        return 0

    baseline, problem = load_baseline(baseline_path)
    if problem:
        print(f"[WARN] {problem}")
    total = sum(len(v) for v in result.values())
    new_only = diff_baseline(result, baseline) if baseline else result
    new_total = sum(len(v) for v in new_only.values())

    scope = "since baseline" if baseline else "no baseline yet -- all lines shown"
    print(f"[1/1] {len(files)} records scanned | {total} unsourced numeric claims"
          f" | {new_total} {scope}")
    empty_globs = [g for g, n in scan["per_glob"].items() if n == 0]
    if empty_globs:
        print(f"[WARN] {len(empty_globs)} target glob(s) matched no Markdown file and were "
              f"therefore not checked: {', '.join(empty_globs)}")
    print(CANDIDATE_NOTE)
    print()

    show = new_only if (baseline and not args.full) else result
    for name, hits in sorted(show.items(), key=lambda kv: -len(kv[1])):
        print(f"-- {name}  ({len(hits)})")
        for number, text in (hits if args.full else hits[:3]):
            print(f"   :{number}  {text}")
        if not args.full and len(hits) > 3:
            print(f"   ... {len(hits) - 3} more (--full shows all)")
        print()

    restated = scan["restated"]
    repeat_total = sum(len(v) for v in restated.values())
    if repeat_total:
        counted = "counted as work (--strict)" if args.strict else "not counted as work"
        print(f"-- restated, {counted} ({repeat_total})")
        print("   Every distinctive number on these lines is already sourced elsewhere in "
              "the same file -- a checklist repeating a threshold the document pinned "
              "earlier. Listed so the run stays honest about what it set aside.")
        for name, hits in sorted(restated.items()):
            for number, text in (hits if args.full else hits[:1]):
                print(f"   {name}:{number}  {text[:110]}")
            if not args.full and len(hits) > 1:
                print(f"   ... {len(hits) - 1} more in {name} (--full shows all)")
        print()

    fixable = new_total if baseline else total
    if args.strict:
        # Restatements are a judgment the tool made on its own. In strict mode
        # they come back into the count and the exit code, so CI can tell a run
        # that found nothing from a run that set things aside without being read.
        fixable += repeat_total
    print(f"Disposition: {fixable} line(s) to handle one by one; {repeat_total} restated "
          f"and {'included (--strict)' if args.strict else 'set aside'}; 0 need a recurring "
          f"re-run (this check is one pass over the records).")
    print(BOUNDARY_EN)
    print(BOUNDARY_ZH)
    return 1 if fixable else 0


def cmd_hook(root: Path, section: dict) -> int:
    """PostToolUse(Write|Edit) mode: read the hook payload on stdin, check the
    one file that changed, and report only lines added since the baseline.

    Fails open on every internal error -- this is an audit, not a door lock --
    but never silently: an error the human cannot see is a gate that looks like
    it is running and is not."""
    def emit(obj: dict) -> None:
        print(json.dumps(obj, ensure_ascii=False))

    reconfigure = getattr(sys.stdin, "reconfigure", None)
    if reconfigure is not None:
        # stdin needs the same treatment as stdout: on Windows it defaults to the
        # ANSI codepage, and a non-ASCII path in the payload raises before the
        # check ever runs.
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass

    try:
        payload = json.load(sys.stdin)
    except Exception as exc:  # noqa: BLE001 - report anything, block nothing
        emit({"systemMessage": f"[claim-audit] hook input unreadable, no check run: {exc}"})
        return 0

    tool_input = payload.get("tool_input") or {}
    tool_response = payload.get("tool_response") or {}
    raw = tool_response.get("filePath") or tool_input.get("file_path") or ""
    if not raw:
        return 0

    try:
        changed = Path(raw).resolve()
        if changed.suffix.lower() != ".md":
            return 0
        scan = run_scan(root, section)
        targets = {p.resolve() for p in scan["files"]}
        if changed not in targets:
            return 0
        rel = changed.relative_to(root).as_posix()
        hits = scan["result"].get(rel, [])
        if not hits:
            return 0
        baseline, problem = load_baseline(scan["baseline_path"])
        if problem:
            emit({"systemMessage": f"[claim-audit] {problem}"})
        known = set(baseline.get(rel, []))
        fresh = [(n, t) for n, t in hits if line_key(t) not in known]
        if not fresh:
            return 0
    except Exception as exc:  # noqa: BLE001 - see docstring
        emit({"systemMessage": f"[claim-audit] check failed, edit allowed through: {exc}"})
        return 0

    listed = "\n".join(f"  :{n}  {t[:160]}" for n, t in fresh[:8])
    more = f"\n  ... {len(fresh) - 8} more" if len(fresh) > 8 else ""
    body = (f"claim-audit: {len(fresh)} new line(s) in `{rel}` state a number as fact "
            f"with nothing to check it against:\n{listed}{more}\n{CANDIDATE_NOTE}")
    emit({
        "systemMessage": f"[claim-audit] {rel}: {len(fresh)} unsourced claim(s)",
        "suppressOutput": True,
        "hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": body},
    })
    return 0


def main(argv=None) -> int:
    ensure_utf8_stdout()
    problem = runtime_precheck()
    if problem:
        print(f"[RUNTIME] {problem}")
        print(BOUNDARY_EN)
        return 2

    parser = argparse.ArgumentParser(
        description="List numeric claims written without a source a reader could check")
    parser.add_argument("--root", type=Path, default=Path.cwd(),
                        help="project root the target globs are relative to")
    parser.add_argument("--config", type=Path, default=None,
                        help=f"config file (default: <root>/{CONFIG_NAME} when present)")
    parser.add_argument("--path", type=Path, default=None,
                        help="scan this file or folder instead of the configured targets")
    parser.add_argument("--full", action="store_true", help="print every candidate line")
    parser.add_argument("--strict", action="store_true",
                        help="count restatements as work, so a run that set lines aside "
                             "cannot exit 0 (use in CI)")
    parser.add_argument("--baseline", action="store_true",
                        help="record the current findings as the baseline and report only later additions")
    parser.add_argument("--hook", action="store_true",
                        help="PostToolUse mode: read a hook payload on stdin (see README)")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    if not root.is_dir():
        if args.hook:
            print(json.dumps({"systemMessage": f"[claim-audit] root not a directory: {root}"},
                             ensure_ascii=False))
            return 0
        print(f"[ERROR] root is not a directory: {root}")
        return 2
    try:
        section = load_config(root, args.config)
        if args.path is not None:
            target = args.path if args.path.is_absolute() else root / args.path
            if not target.exists():
                print(f"[ERROR] --path not found: {target}")
                return 2
            rel = target.resolve().relative_to(root).as_posix()
            section = dict(section)
            section["targets"] = [rel] if target.is_file() else [f"{rel}/**/*.md"]
        if args.hook:
            return cmd_hook(root, section)
        return cmd_scan(args, root, section)
    except ConfigError as exc:
        if args.hook:
            # Hook mode returns 0 for every failure, including a broken config.
            # Exit 2 is the harness's own blocking code, so a config typo would
            # start blocking edits -- the opposite of the fail-open promise, and
            # a far worse outcome than the unchecked write it was guarding.
            print(json.dumps({"systemMessage": f"[claim-audit] {exc} -- edit allowed through, "
                                               f"no check run"}, ensure_ascii=False))
            return 0
        print(f"[ERROR] {exc}")
        print("Fix the config, or delete it to fall back to the built-in defaults.")
        return 2


if __name__ == "__main__":
    sys.exit(main())
