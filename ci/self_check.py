#!/usr/bin/env python3
"""Repository-owned, dependency-free checks for the Harness distribution.

This is deliberately narrower than the downstream audit add-on. It checks the
files that make this repository installable and runnable; it does not run
candidate scans and does not turn audit findings into security decisions.
"""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
PYTHON_SCRIPTS = (
    ROOT / "verify_closeout.py",
    ROOT / "addons" / "audit" / "skills" / "claim-audit" / "claim_audit.py",
    ROOT / "addons" / "audit" / "skills" / "repo-audit" / "repo_audit.py",
)
DEMO_COMMAND = (
    sys.executable,
    "verify_closeout.py",
    ".verification-demo/order.md",
    ".verification-demo/closeout.md",
    ".verification-demo/decisions.md",
    "--root",
    ".",
)
LINK_RE = re.compile(r"(?<!!)[^\S\r\n]*\[[^\]]+\]\(([^)\r\n]+)\)")


def repo_path(value: str) -> Path:
    """Resolve a repository-relative manifest path without leaving the repo."""

    path = (ROOT / value).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise ValueError(f"path escapes repository: {value}") from exc
    return path


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def tracked_repo_paths(pattern: str, errors: list[str]) -> tuple[Path, ...]:
    result = subprocess.run(
        ("git", "ls-files", "-z", "--", pattern),
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        errors.append(f"could not enumerate tracked files matching {pattern}")
        return ()
    return tuple(ROOT / relative for relative in result.stdout.split("\0") if relative)


def json_manifest_check(errors: list[str]) -> int:
    paths = tracked_repo_paths("*.json", errors)
    parse_errors = 0
    for path in paths:
        try:
            read_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            parse_errors += 1
            errors.append(f"JSON parse failed: {path.relative_to(ROOT)} ({exc})")
    print(f"JSON_MANIFESTS={len(paths)} PARSE_ERRORS={parse_errors}")
    return len(paths)


def declarations_from_manifest(path: Path) -> list[tuple[str, Path]]:
    """Return (plugin name, skill directory) declarations from one manifest.

    The root plugin manifests resolve their skill paths from the repository
    root. Add-on manifests resolve them from the add-on root, matching the
    source roots in the marketplace manifest.
    """

    data = read_json(path)
    if not isinstance(data, dict):
        return []

    if path == ROOT / ".claude-plugin" / "plugin.json":
        base = ROOT
        plugins = (data,)
    elif path == ROOT / ".claude-plugin" / "marketplace.json":
        base = ROOT
        plugins = tuple(data.get("plugins", ()))
    elif path.name == "plugin.json" and path.parent.name == ".claude-plugin":
        base = path.parent.parent
        plugins = (data,)
    else:
        return []

    declarations: list[tuple[str, Path]] = []
    for plugin in plugins:
        if not isinstance(plugin, dict):
            continue
        plugin_base = base
        if path == ROOT / ".claude-plugin" / "marketplace.json":
            plugin_base = repo_path(str(plugin.get("source", "./")))
        name = str(plugin.get("name", "<unnamed>"))
        for skill in plugin.get("skills", ()):
            declarations.append((name, (plugin_base / str(skill)).resolve()))
    return declarations


def manifest_target_check(errors: list[str]) -> tuple[int, int]:
    manifest_paths = list(
        tracked_repo_paths(
            ":(glob)**/.claude-plugin/plugin.json",
            errors,
        )
    )
    manifest_paths.append(ROOT / ".claude-plugin" / "marketplace.json")
    declarations: list[tuple[str, Path]] = []
    for manifest in manifest_paths:
        try:
            declarations.extend(declarations_from_manifest(manifest))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(
                f"manifest declaration read failed: {manifest.relative_to(ROOT)} ({exc})"
            )

    unique_targets = {target for _, target in declarations}
    broken = 0
    for plugin, target in declarations:
        try:
            target.relative_to(ROOT.resolve())
        except ValueError:
            errors.append(f"manifest target escapes repository: {plugin} -> {target}")
            broken += 1
            continue
        if not target.is_dir():
            errors.append(f"manifest target missing: {plugin} -> {target.relative_to(ROOT)}")
            broken += 1
        elif not (target / "SKILL.md").is_file():
            errors.append(f"SKILL.md missing: {plugin} -> {target.relative_to(ROOT)}")
            broken += 1

    print(
        "MANIFEST_DECLARATIONS="
        f"{len(declarations)} UNIQUE_SKILL_TARGETS={len(unique_targets)} "
        f"BROKEN_TARGETS={broken}"
    )
    return len(declarations), len(unique_targets)


def markdown_target(raw_target: str) -> Optional[str]:
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        target = target[1 : target.index(">")]
    else:
        target = target.split(None, 1)[0]
    target = unquote(target.split("#", 1)[0])
    if not target or target.startswith(("#", "/")):
        return None
    if target.startswith(("http://", "https://", "mailto:", "data:")):
        return None
    return target


def markdown_link_check(errors: list[str]) -> tuple[int, int]:
    checked = 0
    broken = 0
    for markdown in sorted(tracked_repo_paths("*.md", errors)):
        text = markdown.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            target = markdown_target(match.group(1))
            if target is None:
                continue
            checked += 1
            resolved = (markdown.parent / target).resolve()
            try:
                resolved.relative_to(ROOT.resolve())
            except ValueError:
                broken += 1
                errors.append(
                    f"Markdown link escapes repository: "
                    f"{markdown.relative_to(ROOT)} -> {target}"
                )
                continue
            if not resolved.exists():
                broken += 1
                errors.append(
                    f"broken Markdown link: {markdown.relative_to(ROOT)} -> {target}"
                )
    print(f"MARKDOWN_RELATIVE_LINKS={checked} BROKEN_LINKS={broken}")
    return checked, broken


def python_smoke_check(errors: list[str]) -> None:
    syntax_errors = 0
    import_errors = 0
    cli_errors = 0

    for path in PYTHON_SCRIPTS:
        try:
            source = path.read_text(encoding="utf-8")
            compile(source, str(path), "exec")
        except (OSError, SyntaxError) as exc:
            syntax_errors += 1
            errors.append(f"Python syntax failed: {path.relative_to(ROOT)} ({exc})")

        try:
            module_name = f"harness_self_check_{path.stem}"
            spec = importlib.util.spec_from_file_location(module_name, path)
            if spec is None or spec.loader is None:
                raise ImportError("module spec unavailable")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as exc:  # noqa: BLE001 - smoke check must name any import failure
            import_errors += 1
            errors.append(f"Python import failed: {path.relative_to(ROOT)} ({exc})")

        result = subprocess.run(
            (sys.executable, str(path), "--help"),
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0:
            cli_errors += 1
            details = (result.stderr or result.stdout).strip().splitlines()
            errors.append(
                f"Python CLI smoke failed: {path.relative_to(ROOT)} "
                f"(exit {result.returncode}: {details[-1] if details else 'no output'})"
            )

    print(
        "PYTHON_SMOKE="
        f"{len(PYTHON_SCRIPTS)} SCRIPTS "
        f"SYNTAX_ERRORS={syntax_errors} IMPORT_ERRORS={import_errors} CLI_ERRORS={cli_errors}"
    )


def demo_check(errors: list[str]) -> None:
    result = subprocess.run(
        DEMO_COMMAND,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        details = (result.stderr or result.stdout).strip().splitlines()
        errors.append(
            "verification demo failed "
            f"(exit {result.returncode}: {details[-1] if details else 'no output'})"
        )
    print(f"VERIFICATION_DEMO_EXIT={result.returncode}")


def main() -> int:
    errors: list[str] = []
    json_manifest_check(errors)
    manifest_target_check(errors)
    markdown_link_check(errors)
    python_smoke_check(errors)
    demo_check(errors)

    if errors:
        print("SELF_CHECK_FAIL")
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("SELF_CHECK_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
