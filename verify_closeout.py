#!/usr/bin/env python3
"""Candidate verifier for a frozen workorder and its closeout report.

Needs Python 3.9+ on PATH. If `python` is not found at all, this script
cannot run to tell you that -- check `python --version` before building any
order/closeout/gate artifacts around it. See README, section "Executable
closeout check" > "Before the first artifact", for the five-question manual
fallback you can run by eye when no runtime is available.
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

MIN_PYTHON = (3, 9)  # Path.is_relative_to (used below) needs 3.9+

ACCEPTANCE_RE = re.compile(r"^- \[ \] (AC-\d+):", re.MULTILINE)
ANSWER_RE = re.compile(r"^- \[(?:PASS|FAIL|BLOCKED)\] (AC-\d+):.*\| evidence:\s*(\S+)", re.MULTILINE)

# Legacy decision-log format (pre-2026-08-07): a prose blockquote index line under each
# heading. Kept forever, never removed -- the log is append-only, so old entries stay
# exactly as written (decision-log SKILL.md, section "Older logs keep working").
GATE_OPEN_RE = re.compile(r"^> Gate: (\S+) \| Batch: (\S+) \| Files: (.+)$", re.MULTILINE)
GATE_DISPOSITION_RE = re.compile(r"^> Gate disposition: (\S+) \| Reviewer: (\S+) \| Scope: (.+?) \| Archive: (\S+)$", re.MULTILINE)
CLOSEOUT_RE = re.compile(r"^> Type: closeout \| Target: (\S+)$", re.MULTILINE)

# Current decision-log format: a fenced ```yaml``` block under each heading (not literal
# file-top frontmatter -- see decision-log SKILL.md section 1 for why). Parsed with a
# minimal flat key:value reader, not a YAML library, to keep this script dependency-free.
YAML_BLOCK_RE = re.compile(r"^```yaml\r?\n(.*?)^```\s*$", re.MULTILINE | re.DOTALL)


def parse_yaml_block(block: str) -> dict:
    """Read a flat key: value block -- scalars, quoted strings, and [a, b] inline lists.
    Deliberately not a full YAML parser: the schema (decision-log SKILL.md section 5)
    never nests, so this covers it without adding a dependency."""
    fields = {}
    for line in block.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            value = [item.strip().strip('"').strip("'") for item in inner.split(",") if item.strip()]
        elif len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        fields[key] = value
    return fields


def parse_decision_log(text: str):
    """Return (opened gate ids, {disposition id: (reviewer, scope, archive)}, [closeout
    source paths]) by reading both the legacy blockquote format and the current fenced
    yaml format, so an entry written under either convention is accounted for."""
    opened = {match.group(1) for match in GATE_OPEN_RE.finditer(text)}
    dispositions = {match.group(1): match.groups()[1:] for match in GATE_DISPOSITION_RE.finditer(text)}
    closeout_targets = [match.group(1) for match in CLOSEOUT_RE.finditer(text)]

    for match in YAML_BLOCK_RE.finditer(text):
        fields = parse_yaml_block(match.group(1))
        if {"gate", "batch", "files"} <= fields.keys():
            opened.add(fields["gate"])
        if {"disposition", "reviewer", "scope", "archive"} <= fields.keys():
            dispositions[fields["disposition"]] = (fields["reviewer"], fields["scope"], fields["archive"])
        if fields.get("type") == "closeout" and fields.get("source"):
            closeout_targets.append(fields["source"])

    return opened, dispositions, closeout_targets

BOUNDARY = "\u9019\u652f\u53ea\u9a57\u5f62\u5f0f\uff0c\u5167\u5bb9\u5c0d\u4e0d\u5c0d\u662f\u4eba\u7684\u4e8b"
RUNTIME_FALLBACK = ("\u74b0\u5883\u4e0d\u53ef\u7528\uff0c\u8acb\u6539\u8d70\u624b\u52d5\u6838\u5c0d"
                     "\uff08\u898b README\u300cBefore the first artifact\u300d\uff09")

def on_disk(value: str, root: Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path

def ensure_utf8_stdout() -> None:
    """Best-effort UTF-8 reconfigure so the bilingual status lines below do
    not crash a non-UTF-8 console (Windows cp950/cp437) -- a real local
    failure class, not a hypothetical one. Silently no-ops where the stream
    does not support reconfiguring (e.g. when output is already redirected
    through something that fixes its own encoding)."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (OSError, ValueError):
                pass

def runtime_precheck(version_info=None) -> str | None:
    """Return a problem description if the running interpreter is below
    MIN_PYTHON, else None. Takes an optional version_info so the check is
    exercised directly in a regression test without needing a second, older
    interpreter installed."""
    version_info = sys.version_info if version_info is None else version_info
    if tuple(version_info[:2]) < MIN_PYTHON:
        return (f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ required, "
                f"found {version_info[0]}.{version_info[1]}.")
    return None

def main() -> int:
    ensure_utf8_stdout()
    problem = runtime_precheck()
    if problem:
        print(f"[RUNTIME] {problem}")
        print(RUNTIME_FALLBACK)
        print(BOUNDARY)
        return 2
    parser = argparse.ArgumentParser(description="Check machine-readable links between a workorder, closeout, and decision log")
    parser.add_argument("order", type=Path)
    parser.add_argument("report", type=Path)
    parser.add_argument("decision_log", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    root = args.root.resolve()
    paths = {"order": args.order.resolve(), "report": args.report.resolve(), "decision log": args.decision_log.resolve()}
    texts = {}
    for label, path in paths.items():
        if not path.is_file():
            print(f"[ERROR] {label} not found: {path}")
            return 3
        texts[label] = path.read_text(encoding="utf-8")

    acceptance = ACCEPTANCE_RE.findall(texts["order"])
    answers = {match.group(1): match.group(2) for match in ANSWER_RE.finditer(texts["report"])}
    if not acceptance or not answers:
        print("Unable to verify, skipped: structured fields are missing")
        print("\u7121\u6cd5\u9a57\u8b49\uff0c\u8df3\u904e")
        print(BOUNDARY)
        return 2

    missing = [item for item in acceptance if item not in answers]
    print(f"[1/5] acceptance answered one by one: {'[WARN] ' + ', '.join(missing) if missing else '[OK] all answered'}")
    evidence = [match.group(2) for match in ANSWER_RE.finditer(texts["report"])]
    absent = [item for item in evidence if not on_disk(item, root).exists()]
    print(f"[2/5] evidence paths exist: {'[WARN] ' + ', '.join(absent) if absent else '[OK] all exist'}")

    # Read the closing state from anywhere in the report. An earlier version matched only
    # one heading shape, so a report that worded its state differently was treated as
    # "not DONE" and this check passed silently — the exact claim it exists to catch.
    done = bool(re.search("DONE", texts["report"])) and not re.search("CLOSED-FAILED", texts["report"])
    # A report with no closing state at all is a warning, never a pass. For a checker,
    # failing open is the worst failure mode: it reports success by saying nothing.
    state_unknown = not re.search("DONE|CLOSED-FAILED|STOPPED", texts["report"])
    functional = re.findall(r"^- Functional verification:\s*(.+?)\s*\| evidence:\s*(\S+)$", texts["report"], re.MULTILINE)
    independent = any(not re.search(r"hash|environment|commit|identity", description, re.I) for description, _ in functional)
    functional_warning = done and not independent
    absent_functional = [path for _, path in functional if not on_disk(path, root).exists()]
    functional_label = ("[WARN] closing state not found in report" if state_unknown
                        else "[WARN] missing" if functional_warning
                        else "[OK] recorded" if functional
                        else "[--] not required (state is not DONE)")
    if absent_functional:
        functional_label += f"; missing evidence: {', '.join(absent_functional)}"
    print(f"[3/5] independent functional verification for DONE: {functional_label}")

    opened, dispositions, closeout_targets = parse_decision_log(texts["decision log"])
    listed = {match.group(1): match.groups()[1:] for match in re.finditer(r"^- \[GATE\] (\S+) \| disposition: (\S+) \| reviewer: (\S+) \| archive: (\S+)$", texts["report"], re.MULTILINE)}
    gate_warnings = []
    for gate in opened:
        if gate not in dispositions or gate not in listed:
            gate_warnings.append(gate)
            continue
        # Compare like with like: the log side carries (reviewer, scope, archive) and the
        # report side carries (disposition, reviewer, archive). An earlier version lined
        # these up wrong, so well-formed input warned every time.
        if dispositions[gate][0] != listed[gate][1] or dispositions[gate][2] != listed[gate][2]:
            gate_warnings.append(gate)
        archive = dispositions[gate][2]
        if archive != "none" and not on_disk(archive, root).exists():
            gate_warnings.append(gate)
    print(f"[4/5] gate dispositions: {'[WARN] ' + ', '.join(gate_warnings) if gate_warnings else '[OK] all accounted for'}")

    report_path = paths["report"]
    report_target = report_path.relative_to(root).as_posix() if report_path.is_relative_to(root) else report_path.as_posix()
    log_label = "[OK] closeout entry points to report" if report_target in closeout_targets or report_path.as_posix() in closeout_targets else "[WARN] no matching closeout entry"
    print(f"[5/5] decision log pointer: {log_label}")
    print(BOUNDARY)
    # Three exit states: 0 clean, 1 candidate warnings for a human to judge, 2 could not
    # verify. Warnings and a clean run once shared exit 0, which left CI with no signal
    # and contradicted the separate code the skipped case already had.
    any_warning = bool(missing) or bool(absent) or state_unknown or functional_warning or bool(gate_warnings) or "[WARN]" in log_label
    return 1 if any_warning else 0

if __name__ == "__main__":
    sys.exit(main())
