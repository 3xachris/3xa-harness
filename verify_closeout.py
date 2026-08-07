#!/usr/bin/env python3
"""Candidate verifier for a frozen workorder and its closeout report."""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

ACCEPTANCE_RE = re.compile(r"^- \[ \] (AC-\d+):", re.MULTILINE)
ANSWER_RE = re.compile(r"^- \[(?:PASS|FAIL|BLOCKED)\] (AC-\d+):.*\| evidence:\s*(\S+)", re.MULTILINE)
GATE_OPEN_RE = re.compile(r"^> Gate: (\S+) \| Batch: (\S+) \| Files: (.+)$", re.MULTILINE)
GATE_DISPOSITION_RE = re.compile(r"^> Gate disposition: (\S+) \| Reviewer: (\S+) \| Scope: (.+?) \| Archive: (\S+)$", re.MULTILINE)
CLOSEOUT_RE = re.compile(r"^> Type: closeout \| Target: (\S+)$", re.MULTILINE)

BOUNDARY = "\u9019\u652f\u53ea\u9a57\u5f62\u5f0f\uff0c\u5167\u5bb9\u5c0d\u4e0d\u5c0d\u662f\u4eba\u7684\u4e8b"

def on_disk(value: str, root: Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path

def main() -> int:
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

    # 2026-08-07 顧問線實跑修正：原本只認 "# Closeout: ...DONE" 一種標題寫法，換個寫法就判成非 DONE，
    # 於是「宣稱完成卻沒有獨立功能驗證」照樣過關——正是本題要擋的東西。改為認全文的狀態詞。
    done = bool(re.search("DONE", texts["report"])) and not re.search("CLOSED-FAILED", texts["report"])
    # 2026-08-07 顧問線實跑補：標題格式不合時 done=False 會讓本題靜默略過並印 [OK]，
    # 對驗證器而言 fail-open 是最危險的失效。全文找不到任何結案狀態詞＝警示，不當通過。
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

    opened = {match.group(1) for match in GATE_OPEN_RE.finditer(texts["decision log"])}
    dispositions = {match.group(1): match.groups()[1:] for match in GATE_DISPOSITION_RE.finditer(texts["decision log"])}
    listed = {match.group(1): match.groups()[1:] for match in re.finditer(r"^- \[GATE\] (\S+) \| disposition: (\S+) \| reviewer: (\S+) \| archive: (\S+)$", texts["report"], re.MULTILINE)}
    gate_warnings = []
    for gate in opened:
        if gate not in dispositions or gate not in listed:
            gate_warnings.append(gate)
            continue
        # 2026-08-07 顧問線實跑修正：原本拿 log 的 Reviewer 去比報告的 disposition、
        # 拿 Scope 去比 archive，欄位錯位導致格式正確的輸入也永遠誤報。
        # log 端 groups = (Reviewer, Scope, Archive)；報告端 = (disposition, reviewer, archive)。
        if dispositions[gate][0] != listed[gate][1] or dispositions[gate][2] != listed[gate][2]:
            gate_warnings.append(gate)
        archive = dispositions[gate][2]
        if archive != "none" and not on_disk(archive, root).exists():
            gate_warnings.append(gate)
    print(f"[4/5] gate dispositions: {'[WARN] ' + ', '.join(gate_warnings) if gate_warnings else '[OK] all accounted for'}")

    report_path = paths["report"]
    report_target = report_path.relative_to(root).as_posix() if report_path.is_relative_to(root) else report_path.as_posix()
    closeout_targets = [match.group(1) for match in CLOSEOUT_RE.finditer(texts["decision log"])]
    log_label = "[OK] closeout entry points to report" if report_target in closeout_targets or report_path.as_posix() in closeout_targets else "[WARN] no matching closeout entry"
    print(f"[5/5] decision log pointer: {log_label}")
    print(BOUNDARY)
    # 2026-08-07 顧問線實跑修正：原本無條件 return 0，有警示與全過同碼，CI 收不到任何訊號，
    # 也與「跳過要用不同碼」的設計自相矛盾。三態＝0 全過／1 有候選警示（人判，非退件）／2 無法驗證。
    any_warning = bool(missing) or bool(absent) or state_unknown or functional_warning or bool(gate_warnings) or "[WARN]" in log_label
    return 1 if any_warning else 0

if __name__ == "__main__":
    sys.exit(main())
