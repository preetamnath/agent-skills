#!/usr/bin/env python3
"""Replay Codex Bash events through the Claude-rule file matcher.

The archived transcript is an event log, not a shell script.  This harness
extracts completed ``CommandExecution`` events, unwraps Codex's
``/bin/zsh -lc`` command shape, converts ``file://`` working directories, and
asks the matcher which repository rules would have applied before each Bash
command.  It never executes transcript commands.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any, Iterable, Iterator
from urllib.parse import unquote, urlparse


MODULE_PATH = Path(__file__).with_name("claude_rules.py")
SPEC = importlib.util.spec_from_file_location("codex_claude_rules", MODULE_PATH)
if SPEC is None or SPEC.loader is None:  # pragma: no cover - packaging failure
    raise ImportError(f"cannot load matcher from {MODULE_PATH}")
claude_rules = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(claude_rules)


DEFAULT_TRANSCRIPT = Path(
    "/Users/preetamnath/.codex/sessions/2026/08/17/"
    "rollout-2026-08-17T10-02-08-01a00dfd-bd81-7c02-8b97-518fe8297ea5.jsonl"
)


@dataclass(frozen=True)
class CommandEvent:
    """One completed Bash command extracted from a Codex transcript."""

    ordinal: int | None
    event_id: str | None
    command: str
    cwd: Path
    exit_code: int | None


@dataclass(frozen=True)
class ReplayMatch:
    """Matcher result for one transcript command."""

    event: CommandEvent
    rule_paths: tuple[str, ...]
    scopes: tuple[str, ...]
    dynamic: bool
    parse_error: bool


@dataclass(frozen=True)
class ReplayReport:
    """Stable summary returned by :func:`replay_transcript`."""

    transcript: Path
    repo_root: Path
    events: tuple[ReplayMatch, ...]

    @property
    def command_count(self) -> int:
        return len(self.events)

    @property
    def matched_events(self) -> tuple[ReplayMatch, ...]:
        return tuple(item for item in self.events if item.rule_paths)

    @property
    def matched_rule_paths(self) -> tuple[str, ...]:
        return tuple(
            sorted({rule for item in self.events for rule in item.rule_paths})
        )


def _file_url_to_path(value: str) -> Path:
    """Convert a Codex ``file://`` cwd or a normal path to ``Path``."""
    parsed = urlparse(value)
    if parsed.scheme != "file":
        return Path(value)
    if parsed.netloc not in ("", "localhost"):
        raise ValueError(f"unsupported file URL host: {parsed.netloc}")
    return Path(unquote(parsed.path))


def _shell_command(command: Any) -> str | None:
    """Unwrap Codex's command argv without executing it.

    Codex normally records ``["/bin/zsh", "-lc", command]``.  The fallback
    accepts another ``*-c`` shell form, while rejecting an argv that is not
    demonstrably a shell command so the replay cannot silently invent input.
    """
    if isinstance(command, str):
        return command
    if not isinstance(command, list) or not all(isinstance(item, str) for item in command):
        return None
    if len(command) >= 3 and command[1] in {"-c", "-lc"}:
        return command[2]
    return None


def _command_event(record: dict[str, Any]) -> CommandEvent | None:
    if record.get("type") != "event_msg":
        return None
    payload = record.get("payload")
    if not isinstance(payload, dict) or payload.get("type") != "item_completed":
        return None
    item = payload.get("item")
    if not isinstance(item, dict) or item.get("type") != "CommandExecution":
        return None
    command = _shell_command(item.get("command"))
    cwd_value = item.get("cwd")
    if command is None or not isinstance(cwd_value, str):
        return None
    try:
        cwd = _file_url_to_path(cwd_value)
    except ValueError:
        return None
    exit_code = item.get("exit_code")
    return CommandEvent(
        ordinal=record.get("ordinal") if isinstance(record.get("ordinal"), int) else None,
        event_id=item.get("id") if isinstance(item.get("id"), str) else None,
        command=command,
        cwd=cwd,
        exit_code=exit_code if isinstance(exit_code, int) else None,
    )


def iter_command_events(transcript: Path) -> Iterator[CommandEvent]:
    """Yield completed shell command events in transcript order.

    Malformed or unrelated JSONL records are ignored.  The hook's input log
    can contain prompts, world state, tool results, and other event types; only
    completed shell commands are replayable pre-tool events.
    """
    with transcript.open(encoding="utf-8") as stream:
        for line in stream:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict):
                event = _command_event(record)
                if event is not None:
                    yield event


def _relative_rule_path(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except (OSError, ValueError):
        return str(path)


def match_command(event: CommandEvent, repo_root: Path) -> ReplayMatch:
    operation = claude_rules.normalize_file_operation(event.command, event.cwd, repo_root)
    rules = claude_rules.discover_rules(repo_root)
    matched = tuple(
        sorted(
            _relative_rule_path(rule_path, repo_root)
            for rule_path, patterns in rules.items()
            if claude_rules.operation_matches(operation, patterns)
        )
    )
    scopes = tuple(
        sorted(
            f"{scope.path}{'/' if scope.is_directory and scope.path != '.' else ''}"
            for scope in operation.scopes
        )
    )
    return ReplayMatch(
        event=event,
        rule_paths=matched,
        scopes=scopes,
        dynamic=operation.dynamic,
        parse_error=operation.parse_error,
    )


def replay_transcript(transcript: Path, repo_root: Path) -> ReplayReport:
    """Replay every completed shell command without running any command."""
    transcript = transcript.expanduser().resolve()
    repo_root = repo_root.expanduser().resolve()
    events = tuple(match_command(event, repo_root) for event in iter_command_events(transcript))
    return ReplayReport(transcript=transcript, repo_root=repo_root, events=events)


def load_fixture(path: Path) -> list[dict[str, Any]]:
    """Load command cases from the small JSON fixture format."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("cases"), list):
        raise ValueError("fixture must contain a cases array")
    cases = payload["cases"]
    if not all(isinstance(case, dict) for case in cases):
        raise ValueError("fixture cases must be objects")
    return cases


def replay_fixture(path: Path, repo_root: Path) -> list[ReplayMatch]:
    matches: list[ReplayMatch] = []
    repo_root = repo_root.expanduser().resolve()
    for case in load_fixture(path):
        command = case.get("command")
        cwd_value = case.get("cwd", ".")
        if not isinstance(command, str) or not isinstance(cwd_value, str):
            raise ValueError("fixture case requires string command and cwd")
        cwd = Path(cwd_value)
        if not cwd.is_absolute():
            cwd = repo_root / cwd
        matches.append(
            match_command(
                CommandEvent(
                    ordinal=None,
                    event_id=case.get("name") if isinstance(case.get("name"), str) else None,
                    command=command,
                    cwd=cwd.resolve(),
                    exit_code=None,
                ),
                repo_root,
            )
        )
    return matches


def _expected_rule_basename(rule_path: str) -> str:
    return Path(rule_path).name


def assert_expected(
    report: ReplayReport,
    *,
    expected_rule_basenames: Iterable[str] = (),
    expect_no_matches: bool = False,
) -> None:
    """Raise ``AssertionError`` for CLI/test assertions.

    ``--expect-rule`` means the named basename must appear at least once.  It
    does not require the entire transcript to match only that rule.  Use
    ``--expect-no-matches`` for a strict empty-match regression check.
    """
    expected = set(expected_rule_basenames)
    actual = {_expected_rule_basename(path) for path in report.matched_rule_paths}
    missing = sorted(expected - actual)
    if missing:
        raise AssertionError(f"expected rule basenames not observed: {', '.join(missing)}")
    if expect_no_matches and report.matched_rule_paths:
        raise AssertionError(
            "expected no matches, got: " + ", ".join(report.matched_rule_paths)
        )


def _json_report(report: ReplayReport, verbose: bool) -> dict[str, Any]:
    events = report.events if verbose else report.matched_events
    return {
        "transcript": str(report.transcript),
        "repo_root": str(report.repo_root),
        "command_count": report.command_count,
        "matched_event_count": len(report.matched_events),
        "matched_rules": list(report.matched_rule_paths),
        "events": [
            {
                "ordinal": item.event.ordinal,
                "id": item.event.event_id,
                "command": item.event.command,
                "cwd": str(item.event.cwd),
                "exit_code": item.event.exit_code,
                "scopes": list(item.scopes),
                "dynamic": item.dynamic,
                "parse_error": item.parse_error,
                "matched_rules": list(item.rule_paths),
            }
            for item in events
        ],
    }


def _print_human(report: ReplayReport, verbose: bool) -> None:
    print(f"Transcript: {report.transcript}")
    print(f"Repository: {report.repo_root}")
    print(f"Bash CommandExecution events: {report.command_count}")
    print(f"Events with matched rules: {len(report.matched_events)}")
    if report.matched_rule_paths:
        print("Matched rules:")
        for rule in report.matched_rule_paths:
            print(f"  - {rule}")
    else:
        print("Matched rules: none")
    if verbose:
        print("Events:")
        for item in report.events:
            rules = ", ".join(item.rule_paths) if item.rule_paths else "none"
            ordinal = "?" if item.event.ordinal is None else str(item.event.ordinal)
            print(f"  [{ordinal}] {rules} :: {item.event.command}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "transcript",
        nargs="?",
        type=Path,
        default=DEFAULT_TRANSCRIPT,
        help=f"Codex JSONL transcript (default: {DEFAULT_TRANSCRIPT})",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        required=True,
        help="repository root whose .claude/rules files are matched",
    )
    parser.add_argument("--json", action="store_true", help="emit a JSON summary")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="include every event (JSON) or every command (human output)",
    )
    parser.add_argument(
        "--expect-rule",
        action="append",
        default=[],
        metavar="BASENAME",
        help="assert that a matched rule basename appears at least once; repeatable",
    )
    parser.add_argument(
        "--expect-no-matches",
        action="store_true",
        help="assert that no repository rules match any replayed command",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        report = replay_transcript(args.transcript, args.repo_root)
        assert_expected(
            report,
            expected_rule_basenames=args.expect_rule,
            expect_no_matches=args.expect_no_matches,
        )
    except (OSError, ValueError, AssertionError) as error:
        parser.error(str(error))
    if args.json:
        print(json.dumps(_json_report(report, args.verbose), indent=2, sort_keys=True))
    else:
        _print_human(report, args.verbose)
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised by CLI tests
    raise SystemExit(main())
