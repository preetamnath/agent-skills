#!/usr/bin/env python3
"""Prompt Codex to read Claude rules when tool operations reference matching paths.

The hook only needs a small amount of shell understanding.  In particular, it
must distinguish a file operand from a search pattern, a SQL expression, or a
shell value.  ``FileOperation`` is the boundary between that parsing and the
rule matcher below it.
"""

from __future__ import annotations

import ast
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import sys
import tempfile
from typing import Any, Iterable, NamedTuple


DEFAULT_STATE_ROOT = Path(tempfile.gettempdir()) / "codex-claude-rules"
SHELL_SEPARATORS = {"|", "||", "&&", ";", "(", ")", "{", "}"}
PATH_MAGIC = frozenset("*?[{")
READERS = frozenset({"cat", "head", "sed", "tail", "less", "more"})

# Keep commands whose arguments are not treated as paths explicit.
_NO_PATH_COMMANDS = frozenset(
    {
        "alias",
        "cd",
        "command",
        "echo",
        "env",
        "export",
        "false",
        "printf",
        "pwd",
        "set",
        "source",
        "test",
        "time",
        "true",
        "type",
        "unalias",
        "unset",
        "which",
    }
)
_SHELL_WRAPPERS = frozenset(
    {"builtin", "command", "exec", "nice", "nohup", "stdbuf", "sudo", "time"}
)
_READ_COMMANDS = READERS | frozenset(
    {
        "awk",
        "cut",
        "diff",
        "file",
        "find",
        "fd",
        "jq",
        "ls",
        "readlink",
        "sort",
        "tree",
        "uniq",
        "wc",
    }
)
_WRITE_COMMANDS = frozenset(
    {"cp", "install", "ln", "mkdir", "mktemp", "mv", "rm", "rmdir", "tee", "touch"}
)

# Option arity is command-specific; normalize ``--key=value`` and
# ``--key value`` under the same option key.
_OPTION_ARGUMENTS: dict[str, frozenset[str]] = {
    "cat": frozenset(),
    "head": frozenset({"-n", "--lines", "-c", "--bytes"}),
    "tail": frozenset({"-n", "--lines", "-c", "--bytes", "--pid", "-s", "--sleep-interval"}),
    # Parse sed's optional ``-i`` suffix separately so its script stays
    # positional, including BSD's explicit empty suffix form: ``-i ''``.
    "sed": frozenset({"-e", "--expression", "-f", "--file", "-l", "--line-length"}),
    "rg": frozenset(
        {
            "-e", "--regexp", "-f", "--file", "-g", "--glob", "--iglob",
            "--ignore-file", "--type", "--type-add", "--type-not", "--max-count",
            "-m", "-A", "-B", "-C", "--context", "--path-separator",
        }
    ),
    "grep": frozenset({"-e", "--regexp", "-f", "--file", "-m", "--max-count", "-A", "-B", "-C", "--context", "--include", "--exclude", "--exclude-dir"}),
    "egrep": frozenset({"-e", "--regexp", "-f", "--file", "-m", "--max-count", "-A", "-B", "-C", "--context", "--include", "--exclude", "--exclude-dir"}),
    "fgrep": frozenset({"-e", "--regexp", "-f", "--file", "-m", "--max-count", "-A", "-B", "-C", "--context", "--include", "--exclude", "--exclude-dir"}),
    "awk": frozenset({"-f", "--file", "-v", "--assign"}),
    "jq": frozenset({"-L", "--library-path", "-f", "--from-file", "--file", "--arg", "--argjson", "--slurpfile", "--rawfile"}),
    "find": frozenset(),
    "sqlite3": frozenset({"-cmd", "-init", "-separator", "-nullvalue", "-header", "-output", "-table", "-json", "-csv"}),
    "cp": frozenset({"-t", "--target-directory", "-S", "--suffix"}),
    "mv": frozenset({"-t", "--target-directory", "-S", "--suffix"}),
    "install": frozenset({"-t", "--target-directory", "-m", "--mode", "-S", "--suffix", "-o", "--owner", "-g", "--group"}),
    "ln": frozenset({"-t", "--target-directory", "-S", "--suffix"}),
    "mkdir": frozenset({"-m", "--mode", "-Z", "--context"}),
    "touch": frozenset({"-d", "--date", "-r", "--reference", "-t", "--time"}),
    "mktemp": frozenset({"-p", "--tmpdir", "-t"}),
    "tee": frozenset(),
    "rm": frozenset(),
    "rmdir": frozenset(),
}

# Keep this legacy union for importers; parsing uses command-specific tables.
_OPTIONS_WITH_ARGUMENTS = frozenset().union(*_OPTION_ARGUMENTS.values())

_FILE_OPTION_VALUES: dict[str, frozenset[str]] = {
    "sed": frozenset({"-f", "--file"}),
    "rg": frozenset({"-f", "--file"}),
    "grep": frozenset({"-f", "--file"}),
    "egrep": frozenset({"-f", "--file"}),
    "fgrep": frozenset({"-f", "--file"}),
    "awk": frozenset({"-f", "--file"}),
    "jq": frozenset({"-f", "--from-file", "--file"}),
    "psql": frozenset({"-f", "--file"}),
    "mysql": frozenset({"-f", "--file"}),
    "mariadb": frozenset({"-f", "--file"}),
}

_QUERY_FREE_OPTIONS: dict[str, frozenset[str]] = {
    "rg": frozenset({"--files"}),
}

_OPTIONAL_ARGUMENTS: dict[str, frozenset[str]] = {
    "sed": frozenset({"-i", "--in-place"}),
}


class PathScope(NamedTuple):
    path: str
    is_directory: bool


class Redirection(NamedTuple):
    target: str
    operator: str


class CommandOperands(NamedTuple):
    positionals: tuple[str, ...]
    option_values: dict[str, str]
    options: frozenset[str]
    redirections: tuple[Redirection, ...]


class FileOperation(NamedTuple):
    """Normalized explicit paths observed in one tool invocation.

    ``scopes`` is the union used by rule matching.  ``read_scopes`` and
    ``write_scopes`` are retained so post-tool-use can identify rule reads and
    so callers can inspect the operation without reparsing the command.
    ``dynamic`` means that part of the command depends on shell expansion or a
    variable.  Dynamic input never creates a repository-root scope.
    """

    scopes: frozenset[PathScope] = frozenset()
    read_scopes: frozenset[PathScope] = frozenset()
    write_scopes: frozenset[PathScope] = frozenset()
    read_paths: tuple[str, ...] = ()
    write_paths: tuple[str, ...] = ()
    reader_paths: tuple[str, ...] = ()
    glob_selectors: tuple[str, ...] = ()
    selector_scopes: tuple[tuple[str, PathScope], ...] = ()
    reader_globs: tuple[str, ...] = ()
    dynamic: bool = False
    parse_error: bool = False
    commands: tuple[tuple[str, ...], ...] = ()

    @property
    def paths(self) -> frozenset[PathScope]:
        """Compatibility alias for consumers that only need all scopes."""
        return self.scopes

    @property
    def all_scopes(self) -> frozenset[PathScope]:
        return self.scopes

    @property
    def ambiguous(self) -> bool:
        return self.dynamic or self.parse_error


def find_repo_root(cwd: Path) -> Path | None:
    try:
        current = cwd.resolve()
    except OSError:
        return None
    if not current.is_dir():
        current = current.parent
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return None


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        try:
            parsed = ast.literal_eval(value)
        except (SyntaxError, ValueError):
            return value[1:-1]
        return parsed if isinstance(parsed, str) else value[1:-1]
    return value


def parse_paths_frontmatter(rule_path: Path) -> list[str] | None:
    """Parse the supported YAML subset for Claude's `paths` list."""
    try:
        text = rule_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    try:
        closing = next(i for i, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration:
        return None

    frontmatter = lines[1:closing]
    paths: list[str] = []
    paths_indent: int | None = None
    found_paths = False
    for raw_line in frontmatter:
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip())
        if paths_indent is None:
            match = re.fullmatch(r"paths\s*:\s*(.*)", stripped)
            if not match:
                continue
            found_paths = True
            paths_indent = indent
            inline = match.group(1).strip()
            if inline:
                try:
                    parsed = ast.literal_eval(inline)
                except (SyntaxError, ValueError):
                    return None
                if not isinstance(parsed, (list, tuple)) or not all(
                    isinstance(item, str) and item for item in parsed
                ):
                    return None
                paths.extend(parsed)
            continue

        if indent <= paths_indent and not stripped.startswith("-"):
            break
        item_match = re.fullmatch(r"-\s+(.+)", stripped)
        if not item_match:
            return None
        item = _unquote(item_match.group(1))
        if not item:
            return None
        paths.append(item)

    return paths if found_paths and paths else None


def discover_rules(repo_root: Path) -> dict[Path, list[str]]:
    rules_dir = repo_root / ".claude" / "rules"
    if not rules_dir.is_dir():
        return {}
    try:
        resolved_rules_dir = rules_dir.resolve()
        resolved_rules_dir.relative_to(repo_root.resolve())
    except (OSError, ValueError):
        return {}
    rules: dict[Path, list[str]] = {}
    rule_paths: list[Path] = []
    for directory, _, filenames in os.walk(rules_dir, followlinks=False):
        rule_paths.extend(
            Path(directory) / filename
            for filename in filenames
            if filename.endswith(".md")
        )
    for rule_path in sorted(rule_paths):
        try:
            resolved_rule = rule_path.resolve()
            resolved_rule.relative_to(resolved_rules_dir)
        except (OSError, ValueError):
            continue
        patterns = parse_paths_frontmatter(rule_path)
        if patterns:
            rules[resolved_rule] = patterns
    return rules


def expand_braces(pattern: str) -> list[str]:
    """Expand comma-delimited braces, including nested braces."""
    opening = -1
    depth = 0
    for index, char in enumerate(pattern):
        if char == "{":
            if depth == 0:
                opening = index
            depth += 1
        elif char == "}" and depth:
            depth -= 1
            if depth == 0:
                body = pattern[opening + 1 : index]
                parts: list[str] = []
                part_start = 0
                inner_depth = 0
                for body_index, body_char in enumerate(body):
                    if body_char == "{":
                        inner_depth += 1
                    elif body_char == "}":
                        inner_depth -= 1
                    elif body_char == "," and inner_depth == 0:
                        parts.append(body[part_start:body_index])
                        part_start = body_index + 1
                parts.append(body[part_start:])
                if len(parts) == 1:
                    return [pattern]
                expanded: list[str] = []
                for part in parts:
                    expanded.extend(
                        expand_braces(pattern[:opening] + part + pattern[index + 1 :])
                    )
                return expanded
    return [pattern]


def glob_matches(path: str, pattern: str) -> bool:
    """Match a repository-relative POSIX path with ** segment semantics."""
    path_parts = tuple(part for part in path.removeprefix("./").split("/") if part)
    pattern_parts = tuple(
        part for part in pattern.removeprefix("./").split("/") if part
    )

    def match_parts(path_index: int, pattern_index: int) -> bool:
        if pattern_index == len(pattern_parts):
            return path_index == len(path_parts)
        pattern_part = pattern_parts[pattern_index]
        if pattern_part == "**":
            return match_parts(path_index, pattern_index + 1) or (
                path_index < len(path_parts)
                and match_parts(path_index + 1, pattern_index)
            )
        return (
            path_index < len(path_parts)
            and fnmatch.fnmatchcase(path_parts[path_index], pattern_part)
            and match_parts(path_index + 1, pattern_index + 1)
        )

    return match_parts(0, 0)


def _non_magic_prefix(path: str) -> str:
    parts: list[str] = []
    for part in path.removeprefix("./").split("/"):
        if not part:
            continue
        if any(char in part for char in PATH_MAGIC):
            break
        parts.append(part)
    return "/".join(parts)


def scope_matches(scope: PathScope, patterns: Iterable[str]) -> bool:
    for pattern in patterns:
        for expanded in expand_braces(pattern):
            if not scope.is_directory and glob_matches(scope.path, expanded):
                return True
            if scope.is_directory:
                prefix = _non_magic_prefix(expanded)
                if not prefix or scope.path in ("", "."):
                    return True
                if (
                    prefix == scope.path
                    or prefix.startswith(scope.path + "/")
                    or scope.path.startswith(prefix + "/")
                ):
                    return True
    return False


def _segment_pattern_overlap(left: str, right: str) -> bool:
    """Conservatively decide whether two one-segment globs can intersect."""
    if left == right:
        return True
    left_magic = any(char in left for char in "*?[")
    right_magic = any(char in right for char in "*?[")
    if not left_magic and not right_magic:
        return False
    if not left_magic:
        return fnmatch.fnmatchcase(left, right)
    if not right_magic:
        return fnmatch.fnmatchcase(right, left)

    # Reject disjoint fixed prefixes or suffixes; treat other glob forms as
    # possibly overlapping so prompting remains conservative.
    def fixed_edges(pattern: str) -> tuple[str, str]:
        magic_positions = [index for index, char in enumerate(pattern) if char in "*?["]
        if not magic_positions:
            return pattern, pattern
        first = magic_positions[0]
        last = magic_positions[-1]
        return pattern[:first], pattern[last + 1 :]

    left_prefix, left_suffix = fixed_edges(left)
    right_prefix, right_suffix = fixed_edges(right)
    if left_prefix and right_prefix and not (
        left_prefix.startswith(right_prefix) or right_prefix.startswith(left_prefix)
    ):
        return False
    if left_suffix and right_suffix and not (
        left_suffix.endswith(right_suffix) or right_suffix.endswith(left_suffix)
    ):
        return False
    return True


def _glob_patterns_overlap(left: str, right: str) -> bool:
    """Return whether two repository-relative glob selectors may overlap."""
    left_options = expand_braces(left)
    right_options = expand_braces(right)

    def parts(pattern: str) -> tuple[str, ...]:
        return tuple(part for part in pattern.removeprefix("./").split("/") if part)

    def overlap(left_parts: tuple[str, ...], right_parts: tuple[str, ...]) -> bool:
        memo: dict[tuple[int, int], bool] = {}

        def walk(left_index: int, right_index: int) -> bool:
            key = (left_index, right_index)
            if key in memo:
                return memo[key]
            if left_index == len(left_parts):
                result = right_index == len(right_parts) or (
                    right_index < len(right_parts) and right_parts[right_index] == "**"
                    and walk(left_index, right_index + 1)
                )
                memo[key] = result
                return result
            if right_index == len(right_parts):
                result = left_parts[left_index] == "**" and walk(left_index + 1, right_index)
                memo[key] = result
                return result
            left_part, right_part = left_parts[left_index], right_parts[right_index]
            if left_part == "**":
                result = walk(left_index + 1, right_index) or walk(left_index, right_index + 1)
            elif right_part == "**":
                result = walk(left_index, right_index + 1) or walk(left_index + 1, right_index)
            else:
                result = _segment_pattern_overlap(left_part, right_part) and walk(
                    left_index + 1, right_index + 1
                )
            memo[key] = result
            return result

        return walk(0, 0)

    return any(overlap(parts(left_option), parts(right_option)) for left_option in left_options for right_option in right_options)


def _selector_matches_pattern(selector: str, pattern: str) -> bool:
    if _glob_patterns_overlap(selector, pattern):
        return True
    # A glob below an explicit directory is still a meaningful read; the
    # intersection check above handles extension-specific rule globs.
    if not any(char in pattern for char in PATH_MAGIC):
        return selector == pattern or selector.startswith(pattern.rstrip("/") + "/")
    return False


def operation_matches(operation: FileOperation, patterns: Iterable[str]) -> bool:
    """Match exact scopes and selector-aware glob scopes."""
    patterns = tuple(patterns)
    selector_scopes = {scope for _, scope in operation.selector_scopes}
    for scope in operation.scopes:
        if scope not in selector_scopes and scope_matches(scope, patterns):
            return True
    return any(
        _selector_matches_pattern(selector, pattern)
        for selector, _ in operation.selector_scopes
        for pattern in patterns
    )


def _candidate_token(token: str) -> str | None:
    token = token.strip()
    if not token or token in SHELL_SEPARATORS or token.startswith("-"):
        return None
    if "=" in token and token.split("=", 1)[0].startswith("-"):
        token = token.split("=", 1)[1]
    token = token.lstrip("<>").rstrip(",;:")
    if not token or token.startswith(("$", "`")):
        return None
    if any(char in token for char in ("\n", "\r", "\x00")):
        return None
    return token


def _shell_tokenize(command: str) -> list[str] | None:
    try:
        # Keep braces inside a word so ``src/{one,two}.py`` stays intact.
        lexer = shlex.shlex(command, posix=True, punctuation_chars="|&;()<>")
        lexer.whitespace_split = True
        return list(lexer)
    except (ValueError, TypeError):
        return None


def _split_commands(tokens: Iterable[str]) -> tuple[list[tuple[str, ...]], bool]:
    """Split a shell token stream into simple commands.

    Operators are retained only as boundaries.  Control-flow words and shell
    redirection syntax are handled by the segment parser; they do not become
    path candidates.
    """
    commands: list[tuple[str, ...]] = []
    current: list[str] = []
    dynamic = False
    for token in tokens:
        if token in SHELL_SEPARATORS or token in {"<", ">", ">>"}:
            if token in {"<", ">", ">>"}:
                current.append(token)
                continue
            if current:
                commands.append(tuple(current))
                current = []
            continue
        if token in {"[", "]", "if", "then", "else", "elif", "fi", "for", "while", "until", "do", "done", "case", "esac", "in"}:
            dynamic = True
            if current:
                commands.append(tuple(current))
                current = []
            continue
        current.append(token)
    if current:
        commands.append(tuple(current))
    return commands, dynamic


def _contains_dynamic(token: str) -> bool:
    return any(marker in token for marker in ("$", "`", "\n", "\r", "\x00"))


def _command_name(tokens: tuple[str, ...]) -> tuple[str, int]:
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token in _SHELL_WRAPPERS:
            index += 1
            while index < len(tokens) and tokens[index].startswith("-"):
                index += 1
            continue
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.+", token):
            index += 1
            continue
        break
    if index >= len(tokens):
        return "", index
    return Path(tokens[index]).name, index


def _positional_tokens(
    tokens: tuple[str, ...],
    start: int,
    *,
    option_arguments: Iterable[str] = (),
    optional_arguments: Iterable[str] = (),
    stop_at_double_dash: bool = True,
) -> CommandOperands:
    """Parse one command's operands with explicit option arity."""
    positionals: list[str] = []
    option_values: dict[str, str] = {}
    options: set[str] = set()
    redirections: list[Redirection] = []
    option_arguments = frozenset(option_arguments)
    optional_arguments = frozenset(optional_arguments)
    index = start
    end_options = False
    while index < len(tokens):
        token = tokens[index]
        if token in {"<", ">", ">>", "&>", "&>>", "<>"}:
            if index + 1 < len(tokens):
                redirections.append(Redirection(tokens[index + 1], token))
                index += 2
            else:
                index += 1
            continue
        # shlex separates the descriptor in forms such as ``2>errors.log``.
        if token.isdigit() and index + 2 < len(tokens) and tokens[index + 1] in {"<", ">", ">>"}:
            redirections.append(Redirection(tokens[index + 2], f"{token}{tokens[index + 1]}"))
            index += 3
            continue
        if stop_at_double_dash and token == "--":
            end_options = True
            index += 1
            continue
        if not end_options and token.startswith("-") and token != "-":
            key = token
            embedded: str | None = None
            if token.startswith("--") and "=" in token:
                key, embedded = token.split("=", 1)
            elif token.startswith("-") and "=" in token and len(token) > 2:
                key, embedded = token.split("=", 1)
            options.add(key)
            if key in option_arguments and embedded is not None:
                option_values[key] = embedded
                index += 1
                continue
            if key in optional_arguments:
                if embedded is not None:
                    option_values[key] = embedded
                elif index + 1 < len(tokens) and tokens[index + 1] == "":
                    # BSD sed spells the no-backup suffix as ``-i ''``.
                    option_values[key] = ""
                    index += 2
                    continue
                else:
                    option_values[key] = ""
                index += 1
                continue
            if key in option_arguments and index + 1 < len(tokens):
                option_values[key] = tokens[index + 1]
                index += 2
                continue
            # Attached short-option values (for example ``-n10``) are
            # command-specific too.
            if len(key) > 2 and key[:2] in (option_arguments | optional_arguments):
                options.discard(key)
                key = key[:2]
                options.add(key)
                option_values[key] = key[2:] + token[len(key):]
                index += 1
                continue
            index += 1
            continue
        positionals.append(token)
        index += 1
    return CommandOperands(
        tuple(positionals), option_values, frozenset(options), tuple(redirections)
    )


def _path_scope(
    token: str,
    cwd: Path,
    repo_root: Path,
    *,
    allow_missing: bool = False,
    directory_hint: bool = False,
) -> PathScope | None:
    """Resolve one explicit path without allowing a path outside the repo."""
    token = _candidate_token(token)
    if token is None or _contains_dynamic(token):
        return None
    # A bare wildcard is a command pattern; accept a prefixed wildcard only
    # when its literal prefix names an existing directory.
    raw_path = Path(token)
    candidate = raw_path if raw_path.is_absolute() else cwd / raw_path
    has_magic = any(char in token for char in PATH_MAGIC)
    if has_magic:
        prefix = _non_magic_prefix(token)
        if not prefix:
            return None
        prefix_path = Path(prefix)
        prefix_candidate = (
            prefix_path if prefix_path.is_absolute() else cwd / prefix_path
        )
        try:
            prefix_resolved = prefix_candidate.resolve()
            root = repo_root.resolve()
            relative_prefix = prefix_resolved.relative_to(root)
        except (OSError, ValueError):
            return None
        if not prefix_resolved.is_dir():
            return None
        return PathScope(relative_prefix.as_posix() or ".", True)

    try:
        root = repo_root.resolve()
        resolved = candidate.resolve()
        relative = resolved.relative_to(root)
    except (OSError, ValueError):
        return None
    if resolved.is_file():
        return PathScope(relative.as_posix(), False)
    if resolved.is_dir():
        return PathScope(relative.as_posix() or ".", True)
    if not allow_missing:
        return None
    # ``resolve`` is non-strict; ``relative_to(root)`` still rejects escapes.
    return PathScope(relative.as_posix(), directory_hint)


def _path_selector(token: str, cwd: Path, repo_root: Path) -> str | None:
    """Return a repo-relative path-prefixed glob, if its prefix is safe."""
    token = _candidate_token(token)
    if token is None or not any(char in token for char in PATH_MAGIC):
        return None
    prefix = _non_magic_prefix(token)
    if not prefix:
        return None
    raw_path = Path(token)
    candidate = raw_path if raw_path.is_absolute() else cwd / raw_path
    prefix_path = Path(prefix)
    prefix_candidate = prefix_path if prefix_path.is_absolute() else cwd / prefix_path
    try:
        root = repo_root.resolve()
        prefix_resolved = prefix_candidate.resolve()
        if not prefix_resolved.is_dir():
            return None
        prefix_resolved.relative_to(root)
        relative = candidate.resolve().relative_to(root)
    except (OSError, ValueError):
        return None
    return relative.as_posix()


def _command_option_arguments(name: str) -> frozenset[str]:
    return _OPTION_ARGUMENTS.get(name, frozenset())


def _command_optional_arguments(name: str) -> frozenset[str]:
    return _OPTIONAL_ARGUMENTS.get(name, frozenset())


def _add_scope(
    destination: set[PathScope],
    token: str,
    cwd: Path,
    repo_root: Path,
    *,
    allow_missing: bool = False,
    directory_hint: bool = False,
    selector_scopes: list[tuple[str, PathScope]] | None = None,
) -> PathScope | None:
    scope = _path_scope(
        token,
        cwd,
        repo_root,
        allow_missing=allow_missing,
        directory_hint=directory_hint,
    )
    if scope is not None:
        destination.add(scope)
        if selector_scopes is not None:
            selector = _path_selector(token, cwd, repo_root)
            if selector is not None:
                selector_scopes.append((selector, scope))
    return scope


def _apply_redirections(
    redirections: Iterable[Redirection],
    cwd: Path,
    repo_root: Path,
    read_scopes: set[PathScope],
    write_scopes: set[PathScope],
    selector_scopes: list[tuple[str, PathScope]],
) -> None:
    for redirection in redirections:
        if redirection.operator.startswith("<"):
            _add_scope(
                read_scopes,
                redirection.target,
                cwd,
                repo_root,
                selector_scopes=selector_scopes,
            )
        elif redirection.operator.startswith(">") or ">" in redirection.operator:
            _add_scope(
                write_scopes,
                redirection.target,
                cwd,
                repo_root,
                allow_missing=True,
                selector_scopes=selector_scopes,
            )


def _reader_operands(
    command: str,
    tokens: tuple[str, ...],
    start: int,
    cwd: Path,
    repo_root: Path,
    read_scopes: set[PathScope],
    write_scopes: set[PathScope],
    reader_paths: list[str],
    reader_globs: list[str],
    selector_scopes: list[tuple[str, PathScope]],
    dynamic: list[bool],
) -> None:
    name = Path(command).name
    parsed = _positional_tokens(
        tokens,
        start,
        option_arguments=_command_option_arguments(name),
        optional_arguments=_command_optional_arguments(name),
    )
    positionals = list(parsed.positionals)
    option_values = parsed.option_values
    file_options = _FILE_OPTION_VALUES.get(name, frozenset())
    for option, value in option_values.items():
        if option not in file_options or not value:
            continue
        scope = _add_scope(
            read_scopes,
            value,
            cwd,
            repo_root,
            selector_scopes=selector_scopes,
        )
        selector = _path_selector(value, cwd, repo_root)
        if scope is not None and selector is None:
            reader_paths.append(value)
        elif selector is not None:
            reader_globs.append(selector)
    # grep/rg/jq/awk/sed place a query or program before file paths.
    if name in {"rg", "grep", "egrep", "fgrep"}:
        if positionals and not (
            ({"-e", "--regexp", "-f", "--file"} & parsed.options)
            or (_QUERY_FREE_OPTIONS.get(name, frozenset()) & parsed.options)
        ):
            positionals = positionals[1:]
    elif name in {"awk", "jq"}:
        if positionals and not ({"-f", "--file", "--from-file"} & parsed.options):
            positionals = positionals[1:]
    elif name == "sed":
        if positionals and not ({"-e", "--expression", "-f", "--file"} & parsed.options):
            positionals = positionals[1:]
    elif name == "find":
        # find's first positional is the search root; later words are expressions.
        positionals = positionals[:1]
    elif name == "git":
        # The caller handles git; retain a safe fallback for wrappers.
        positionals = [item for item in positionals if "/" in item or item.startswith(".")]
    elif name in {"sqlite3", "duckdb"}:
        positionals = positionals[:1]
    elif name in {"psql", "mysql", "mariadb"}:
        positionals = []
        for key in ("-f", "--file"):
            if key in option_values:
                positionals.append(option_values[key])

    for token in positionals:
        if _contains_dynamic(token):
            dynamic[0] = True
            continue
        if token in option_values.values() and token.startswith("-"):
            continue
        target_scopes = (
            write_scopes
            if name == "sed"
            and ("-i" in parsed.options or "--in-place" in parsed.options)
            else read_scopes
        )
        scope = _add_scope(
            target_scopes,
            token,
            cwd,
            repo_root,
            selector_scopes=selector_scopes,
        )
        selector = _path_selector(token, cwd, repo_root)
        if scope is not None and selector is None:
            reader_paths.append(token)
        elif selector is not None:
            reader_globs.append(selector)
    if any(_contains_dynamic(token) for token in tokens[start:]):
        dynamic[0] = True


def _write_operands(
    command: str,
    tokens: tuple[str, ...],
    start: int,
    cwd: Path,
    repo_root: Path,
    read_scopes: set[PathScope],
    write_scopes: set[PathScope],
    selector_scopes: list[tuple[str, PathScope]],
    dynamic: list[bool],
) -> None:
    name = Path(command).name
    parsed = _positional_tokens(
        tokens,
        start,
        option_arguments=_command_option_arguments(name),
        optional_arguments=_command_optional_arguments(name),
    )
    positionals = list(parsed.positionals)
    option_values = parsed.option_values
    if name in {"cp", "mv", "install", "ln"}:
        target_directory = option_values.get("-t") or option_values.get("--target-directory")
        if target_directory:
            sources = positionals
            _add_scope(
                write_scopes,
                target_directory,
                cwd,
                repo_root,
                allow_missing=True,
                directory_hint=True,
                selector_scopes=selector_scopes,
            )
            for token in sources:
                _add_scope(
                    read_scopes,
                    token,
                    cwd,
                    repo_root,
                    selector_scopes=selector_scopes,
                )
            if len(sources) == 0:
                dynamic[0] = True
        elif len(positionals) >= 2:
            sources, destinations = positionals[:-1], positionals[-1:]
            source_scopes: list[PathScope] = []
            for token in sources:
                scope = _add_scope(
                    read_scopes,
                    token,
                    cwd,
                    repo_root,
                    selector_scopes=selector_scopes,
                )
                if scope is not None:
                    source_scopes.append(scope)
            destination = destinations[0]
            directory_hint = (
                destination.endswith("/")
                or len(sources) > 1
                or (any(scope.is_directory for scope in source_scopes) and "-T" not in parsed.options)
            )
            _add_scope(
                write_scopes,
                destination,
                cwd,
                repo_root,
                allow_missing=True,
                directory_hint=directory_hint,
                selector_scopes=selector_scopes,
            )
        else:
            dynamic[0] = True
    elif name in {"touch", "mktemp"}:
        # touch creates missing files; match mktemp only when its template has
        # a concrete path prefix.
        for token in positionals:
            if _contains_dynamic(token):
                dynamic[0] = True
                continue
            _add_scope(
                write_scopes,
                token,
                cwd,
                repo_root,
                allow_missing=True,
                selector_scopes=selector_scopes,
            )
    elif name in {"mkdir", "rmdir"}:
        for token in positionals:
            _add_scope(
                write_scopes,
                token,
                cwd,
                repo_root,
                allow_missing=True,
                directory_hint=True,
                selector_scopes=selector_scopes,
            )
    elif name == "rm":
        for token in positionals:
            _add_scope(
                write_scopes,
                token,
                cwd,
                repo_root,
                selector_scopes=selector_scopes,
            )
    elif name == "tee":
        for token in positionals:
            _add_scope(
                write_scopes,
                token,
                cwd,
                repo_root,
                allow_missing=True,
                selector_scopes=selector_scopes,
            )
    if any(_contains_dynamic(token) for token in tokens[start:]):
        dynamic[0] = True


def _git_operands(
    tokens: tuple[str, ...],
    start: int,
    cwd: Path,
    repo_root: Path,
    read_scopes: set[PathScope],
    reader_paths: list[str],
    selector_scopes: list[tuple[str, PathScope]],
) -> None:
    if start >= len(tokens):
        return
    subcommand = tokens[start]
    if subcommand in {"diff", "grep", "log", "show", "ls-files"}:
        after_double_dash = False
        query_seen = False
        index = start + 1
        while index < len(tokens):
            token = tokens[index]
            if token == "--":
                after_double_dash = True
                index += 1
                continue
            if not after_double_dash and token.startswith("-"):
                index += 1
                continue
            if subcommand == "grep" and not query_seen and not after_double_dash:
                query_seen = True
                index += 1
                continue
            scope = _add_scope(
                read_scopes,
                token,
                cwd,
                repo_root,
                selector_scopes=selector_scopes,
            )
            if scope is not None and _path_selector(token, cwd, repo_root) is None:
                reader_paths.append(token)
            index += 1


def normalize_file_operation(
    command: str, cwd: Path, repo_root: Path
) -> FileOperation:
    """Normalize explicit file operands from a Bash command.

    The normalizer is intentionally conservative.  It records a known path,
    a path-prefixed glob's literal directory prefix, or an explicit write
    destination.  It never turns a bare glob, regex, SQL expression, or shell
    variable into the repository root.
    """
    tokens = _shell_tokenize(command)
    if tokens is None:
        return FileOperation(parse_error=True, dynamic=True)
    commands, shell_dynamic = _split_commands(tokens)
    read_scopes: set[PathScope] = set()
    write_scopes: set[PathScope] = set()
    read_paths: list[str] = []
    write_paths: list[str] = []
    reader_paths: list[str] = []
    reader_globs: list[str] = []
    selector_scopes: list[tuple[str, PathScope]] = []
    dynamic = [shell_dynamic]
    for segment in commands:
        name, start = _command_name(segment)
        if not name:
            dynamic[0] = True
            continue
        if any(_contains_dynamic(token) for token in segment[start:]):
            dynamic[0] = True
        parsed = _positional_tokens(
            segment,
            start + 1,
            option_arguments=_command_option_arguments(name),
            optional_arguments=_command_optional_arguments(name),
        )
        _apply_redirections(
            parsed.redirections,
            cwd,
            repo_root,
            read_scopes,
            write_scopes,
            selector_scopes,
        )
        if name == "git":
            _git_operands(
                segment,
                start + 1,
                cwd,
                repo_root,
                read_scopes,
                reader_paths,
                selector_scopes,
            )
            continue
        if name in _NO_PATH_COMMANDS:
            continue
        if name in _WRITE_COMMANDS:
            before_reads = set(read_scopes)
            before_writes = set(write_scopes)
            _write_operands(
                name,
                segment,
                start + 1,
                cwd,
                repo_root,
                read_scopes,
                write_scopes,
                selector_scopes,
                dynamic,
            )
            read_paths.extend(scope.path for scope in read_scopes - before_reads)
            write_paths.extend(scope.path for scope in write_scopes - before_writes)
            continue
        if name in _READ_COMMANDS or name in {"rg", "grep", "egrep", "fgrep", "sqlite3", "duckdb", "psql", "mysql", "mariadb"}:
            before_reads = set(read_scopes)
            _reader_operands(
                name,
                segment,
                start + 1,
                cwd,
                repo_root,
                read_scopes,
                write_scopes,
                reader_paths,
                reader_globs,
                selector_scopes,
                dynamic,
            )
            read_paths.extend(scope.path for scope in read_scopes - before_reads)
            continue
        if name in {"bash", "sh", "zsh", "fish", "xargs"}:
            # Do not infer paths from an unevaluated nested command.
            dynamic[0] = True
            continue
        # Unknown command semantics are not guessable. Redirections above are
        # still safe, but positional words do not become file scopes.
        dynamic[0] = True

    scopes = frozenset(read_scopes | write_scopes)
    return FileOperation(
        scopes=scopes,
        read_scopes=frozenset(read_scopes),
        write_scopes=frozenset(write_scopes),
        read_paths=tuple(dict.fromkeys(read_paths)),
        write_paths=tuple(dict.fromkeys(write_paths)),
        reader_paths=tuple(dict.fromkeys(reader_paths)),
        glob_selectors=tuple(dict.fromkeys(selector for selector, _ in selector_scopes)),
        selector_scopes=tuple(dict.fromkeys(selector_scopes)),
        reader_globs=tuple(dict.fromkeys(reader_globs)),
        dynamic=dynamic[0],
        commands=tuple(commands),
    )


def extract_scopes(command: str, cwd: Path, repo_root: Path) -> set[PathScope]:
    """Compatibility wrapper returning normalized operation scopes."""
    return set(normalize_file_operation(command, cwd, repo_root).scopes)


def normalize_apply_patch_operation(
    patch: str, cwd: Path, repo_root: Path
) -> FileOperation:
    """Normalize file paths declared by an apply_patch envelope."""
    write_scopes: set[PathScope] = set()
    write_paths: list[str] = []
    for line in patch.splitlines():
        match = re.fullmatch(r"\*\*\* (?:Add|Update|Delete) File: (.+)", line)
        if match is None:
            match = re.fullmatch(r"\*\*\* Move to: (.+)", line)
        if match is None:
            continue
        target = match.group(1).strip()
        if not target:
            continue
        before = len(write_scopes)
        _add_scope(
            write_scopes,
            target,
            cwd,
            repo_root,
            allow_missing=True,
        )
        if len(write_scopes) != before:
            write_paths.append(target)
    return FileOperation(
        scopes=frozenset(write_scopes),
        write_scopes=frozenset(write_scopes),
        write_paths=tuple(dict.fromkeys(write_paths)),
    )


def _context_key(payload: dict[str, Any]) -> str | None:
    identifier = payload.get("transcript_path") or payload.get("session_id")
    if not isinstance(identifier, str) or not identifier:
        return None
    return hashlib.sha256(identifier.encode("utf-8")).hexdigest()


def _state_path(payload: dict[str, Any], state_root: Path) -> Path | None:
    key = _context_key(payload)
    return state_root / f"{key}.json" if key else None


def _load_state(path: Path | None) -> dict[str, str]:
    if path is None:
        return {}
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeError):
        return {}
    if not isinstance(state, dict):
        return {}
    return {
        key: value
        for key, value in state.items()
        if isinstance(key, str) and isinstance(value, str)
    }


def _save_state(path: Path | None, state: dict[str, str]) -> None:
    if path is None:
        return
    try:
        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        temporary = path.with_suffix(f".{os.getpid()}.tmp")
        temporary.write_text(json.dumps(state, sort_keys=True), encoding="utf-8")
        temporary.replace(path)
    except OSError:
        return


def _rule_hash(rule_path: Path) -> str | None:
    try:
        return hashlib.sha256(rule_path.read_bytes()).hexdigest()
    except OSError:
        return None


def _command_from_payload(payload: dict[str, Any]) -> str | None:
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return None
    for key in ("command", "cmd"):
        command = tool_input.get(key)
        if isinstance(command, str):
            return command
    return None


def _operation_from_payload(
    payload: dict[str, Any], cwd: Path, repo_root: Path
) -> FileOperation | None:
    command = _command_from_payload(payload)
    if command is None:
        return None
    if payload.get("tool_name") == "apply_patch":
        return normalize_apply_patch_operation(command, cwd, repo_root)
    return normalize_file_operation(command, cwd, repo_root)


def _response_contains_rule(response: Any, rule_path: Path) -> bool:
    if not isinstance(response, str) or not response.strip():
        return False
    try:
        rule_text = rule_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return False
    rule_lines = rule_text.splitlines()
    body_start = 0
    if rule_lines and rule_lines[0].strip() == "---":
        try:
            body_start = next(
                index for index, line in enumerate(rule_lines[1:], 1) if line.strip() == "---"
            ) + 1
        except StopIteration:
            return False
    substantive_body = [line.strip() for line in rule_lines[body_start:] if line.strip()]
    response_lines = [line.strip() for line in response.splitlines() if line.strip()]
    if not substantive_body:
        return False

    # Require every substantive body line in order; a heading or frontmatter
    # line alone cannot suppress reinjection.
    response_index = 0
    for expected in substantive_body:
        try:
            response_index = response_lines.index(expected, response_index) + 1
        except ValueError:
            return False
    return True


def _path_token_refers_to(
    token: str, rule_path: Path, cwd: Path | None = None
) -> bool:
    raw = _candidate_token(token)
    if raw is None or any(char in raw for char in PATH_MAGIC):
        return False
    candidate = Path(raw)
    if not candidate.is_absolute() and cwd is not None:
        candidate = cwd / candidate
    try:
        return candidate.resolve() == rule_path.resolve()
    except OSError:
        return False


def _recognizable_rule_read(
    command: str,
    rule_path: Path,
    cwd: Path | None = None,
    repo_root: Path | None = None,
) -> bool:
    """Return true for exact paths, explicit rule globs, and control flow."""
    base = cwd or rule_path.parent
    root = repo_root or find_repo_root(base)
    if root is None:
        return False
    operation = normalize_file_operation(command, base, root)
    if any(_path_token_refers_to(token, rule_path, base) for token in operation.reader_paths):
        return True
    try:
        rule_relative = rule_path.resolve().relative_to(root.resolve()).as_posix()
    except (OSError, ValueError):
        return False
    if any(
        glob_matches(rule_relative, expanded)
        for selector in operation.reader_globs
        for expanded in expand_braces(selector)
    ):
        return True

    # A loop variable is dynamic, but its explicit reader glob remains
    # concrete evidence (``for r in .claude/rules/*.md; do cat "$r"``).
    tokens = _shell_tokenize(command)
    if tokens is None:
        return False
    commands, _ = _split_commands(tokens)
    has_reader = any(_command_name(segment)[0] in READERS for segment in commands)
    if not has_reader:
        return False
    for token in tokens:
        selector = _path_selector(token, base, root)
        if selector is not None and any(
            glob_matches(rule_relative, expanded) for expanded in expand_braces(selector)
        ):
            return True
    return False


def _process_pre_tool_use(
    payload: dict[str, Any], state_root: Path = DEFAULT_STATE_ROOT
) -> dict[str, Any] | None:
    cwd_value = payload.get("cwd")
    if not isinstance(cwd_value, str):
        return None
    cwd = Path(cwd_value)
    repo_root = find_repo_root(cwd)
    if repo_root is None:
        return None
    rules = discover_rules(repo_root)
    if not rules:
        return None

    state_path = _state_path(payload, state_root)
    state = _load_state(state_path)
    operation = _operation_from_payload(payload, cwd, repo_root)
    if operation is None:
        return None
    instructions: list[str] = []
    for rule_path, patterns in rules.items():
        if not operation_matches(operation, patterns):
            continue
        current_hash = _rule_hash(rule_path)
        if current_hash is None or state.get(str(rule_path)) == current_hash:
            continue
        instructions.append(f"Read and follow `{rule_path}`.")

    if not instructions:
        return None
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": "\n".join(instructions),
        }
    }


def process_pre_tool_use(
    payload: dict[str, Any], state_root: Path = DEFAULT_STATE_ROOT
) -> dict[str, Any] | None:
    try:
        return _process_pre_tool_use(payload, state_root)
    except Exception as error:
        _diagnostic("pre-tool-use", error)
        return None


def _process_post_tool_use(
    payload: dict[str, Any], state_root: Path = DEFAULT_STATE_ROOT
) -> None:
    """Record a rule hash only when a recognized read returns rule content."""
    command = _command_from_payload(payload)
    cwd_value = payload.get("cwd")
    if command is None or not isinstance(cwd_value, str):
        return
    cwd = Path(cwd_value)
    repo_root = find_repo_root(cwd)
    if repo_root is None:
        return
    rules = discover_rules(repo_root)
    if not rules:
        return
    state_path = _state_path(payload, state_root)
    state = _load_state(state_path)
    changed = False
    for rule_path in rules:
        if not _recognizable_rule_read(command, rule_path, cwd, repo_root) or not _response_contains_rule(
            payload.get("tool_response"), rule_path
        ):
            continue
        current_hash = _rule_hash(rule_path)
        if current_hash is not None and state.get(str(rule_path)) != current_hash:
            state[str(rule_path)] = current_hash
            changed = True
    if changed:
        _save_state(state_path, state)


def process_post_tool_use(
    payload: dict[str, Any], state_root: Path = DEFAULT_STATE_ROOT
) -> None:
    try:
        _process_post_tool_use(payload, state_root)
    except Exception as error:
        _diagnostic("post-tool-use", error)


def _process_post_compact(
    payload: dict[str, Any], state_root: Path = DEFAULT_STATE_ROOT
) -> None:
    state_path = _state_path(payload, state_root)
    if state_path is None:
        return
    try:
        state_path.unlink(missing_ok=True)
    except OSError:
        return


def process_post_compact(
    payload: dict[str, Any], state_root: Path = DEFAULT_STATE_ROOT
) -> None:
    try:
        _process_post_compact(payload, state_root)
    except Exception as error:
        _diagnostic("post-compact", error)


def _diagnostic(event: str, error: BaseException | str) -> None:
    """Write one bounded local diagnostic without touching hook stdout."""
    try:
        if isinstance(error, BaseException):
            detail = f"{type(error).__name__}: {error}"
        else:
            detail = str(error)
        detail = " ".join(detail.split())[:400]
        print(f"claude_rules: {event} failed open ({detail})", file=sys.stderr)
    except Exception:
        return


def main() -> int:
    events = {"pre-tool-use", "post-tool-use", "post-compact"}
    try:
        if len(sys.argv) != 2 or sys.argv[1] not in events:
            _diagnostic("argument parsing", "unknown event")
            return 0
        event = sys.argv[1]
        try:
            payload = json.load(sys.stdin)
        except (json.JSONDecodeError, OSError, UnicodeError) as error:
            _diagnostic("input parsing", error)
            return 0
        if not isinstance(payload, dict):
            _diagnostic("input parsing", "payload is not an object")
            return 0
        if event == "post-compact":
            process_post_compact(payload)
            return 0
        if event == "post-tool-use":
            process_post_tool_use(payload)
            return 0
        output = process_pre_tool_use(payload)
        if output is not None:
            print(json.dumps(output, separators=(",", ":")))
        return 0
    except Exception as error:
        _diagnostic("hook execution", error)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
