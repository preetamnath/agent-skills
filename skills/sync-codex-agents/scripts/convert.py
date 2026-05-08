#!/usr/bin/env python3
"""Convert Claude agent .md files to Codex .toml format.

Reads agents/*.md from the repo, skips MCP-wrapper agents (tools list contains
mcp__codex__codex), and writes parallel .toml files to .tmp/codex-agents/.

Mapping:
  name        -> name (TOML basic string)
  description -> description (TOML basic string)
  body        -> developer_instructions (TOML literal multi-line string)

The model and tools frontmatter fields are dropped — Codex's agent format has
no equivalent.

Run from the repo root:
  python3 skills/sync-codex-agents/scripts/convert.py

Exit code is 0 on success, 1 on any post-check failure (TOML parse, missing
fields, suspiciously short body, MCP wrapper leak).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
AGENTS_DIR = REPO_ROOT / "agents"
OUTPUT_DIR = REPO_ROOT / ".tmp" / "codex-agents"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)
KEY_VALUE_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$")


class ConvertError(Exception):
    pass


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        raise ConvertError("no YAML frontmatter found")
    raw_fm, body = m.group(1), m.group(2)
    fields: dict[str, str] = {}
    for line in raw_fm.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        km = KEY_VALUE_RE.match(line)
        if not km:
            continue
        key, value = km.group(1), km.group(2).strip()
        if value.startswith('"') and value.endswith('"') and len(value) >= 2:
            value = value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
        fields[key] = value
    return fields, body.lstrip("\n")


def escape_toml_basic(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def render_toml(name: str, description: str, body: str) -> str:
    name_field = f'name = "{escape_toml_basic(name)}"'
    desc_field = f'description = "{escape_toml_basic(description)}"'
    if "'''" in body:
        # Body contains the literal-string terminator — fall back to multi-line
        # basic string with backslash escaping.
        escaped_body = body.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')
        instr_field = f'developer_instructions = """\n{escaped_body}\n"""'
    else:
        instr_field = f"developer_instructions = '''\n{body}\n'''"
    return f"{name_field}\n{desc_field}\n{instr_field}\n"


def is_mcp_wrapper(fields: dict[str, str]) -> bool:
    tools = fields.get("tools", "")
    return "mcp__codex__codex" in tools


def convert_file(src: Path, dst_dir: Path) -> tuple[Path, dict[str, str]] | None:
    text = src.read_text(encoding="utf-8")
    fields, body = parse_frontmatter(text)
    if is_mcp_wrapper(fields):
        return None
    name = fields.get("name")
    description = fields.get("description")
    if not name:
        raise ConvertError(f"{src.name}: missing 'name' in frontmatter")
    if not description:
        raise ConvertError(f"{src.name}: missing 'description' in frontmatter")
    if not body.strip():
        raise ConvertError(f"{src.name}: empty body")
    dst = dst_dir / f"{name}.toml"
    dst.write_text(render_toml(name, description, body), encoding="utf-8")
    return dst, {"name": name, "description": description, "body": body}


NAME_LINE_RE = re.compile(r'^name\s*=\s*"((?:[^"\\]|\\.)*)"\s*$', re.MULTILINE)
DESC_LINE_RE = re.compile(r'^description\s*=\s*"((?:[^"\\]|\\.)*)"\s*$', re.MULTILINE)
INSTR_LITERAL_RE = re.compile(
    r"^developer_instructions\s*=\s*'''\n(.*)\n'''\s*$",
    re.MULTILINE | re.DOTALL,
)
INSTR_BASIC_RE = re.compile(
    r'^developer_instructions\s*=\s*"""\n(.*)\n"""\s*$',
    re.MULTILINE | re.DOTALL,
)


def _unescape_basic(s: str) -> str:
    return s.replace('\\"', '"').replace("\\\\", "\\")


def post_check(dst: Path, expected: dict[str, str]) -> list[str]:
    """Deterministic post-checks. Returns a list of error messages (empty = OK)."""
    errors: list[str] = []
    text = dst.read_text(encoding="utf-8")

    name_m = NAME_LINE_RE.search(text)
    desc_m = DESC_LINE_RE.search(text)
    instr_m = INSTR_LITERAL_RE.search(text) or INSTR_BASIC_RE.search(text)

    if not name_m:
        errors.append(f"{dst.name}: missing or malformed 'name' line")
    if not desc_m:
        errors.append(f"{dst.name}: missing or malformed 'description' line")
    if not instr_m:
        errors.append(f"{dst.name}: missing or malformed 'developer_instructions' block")
    if errors:
        return errors

    name_val = _unescape_basic(name_m.group(1))
    desc_val = _unescape_basic(desc_m.group(1))
    instr_val = instr_m.group(1)

    if name_val != expected["name"]:
        errors.append(
            f"{dst.name}: name mismatch (expected {expected['name']!r}, got {name_val!r})"
        )
    if desc_val != expected["description"]:
        errors.append(f"{dst.name}: description does not round-trip")
    if dst.stem != expected["name"]:
        errors.append(
            f"{dst.name}: filename stem {dst.stem!r} != name {expected['name']!r}"
        )
    if not instr_val.strip():
        errors.append(f"{dst.name}: developer_instructions empty")
    if len(instr_val) < 0.8 * len(expected["body"]):
        errors.append(
            f"{dst.name}: developer_instructions shrank "
            f"({len(instr_val)} < 0.8 * {len(expected['body'])})"
        )
    if "mcp__codex__codex" in instr_val:
        errors.append(f"{dst.name}: MCP wrapper content leaked into output")
    return errors


def main() -> int:
    if not AGENTS_DIR.is_dir():
        print(f"error: {AGENTS_DIR} does not exist", file=sys.stderr)
        return 1
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    # Wipe existing outputs so stale agents (renamed/removed at source) don't
    # linger.
    for old in OUTPUT_DIR.glob("*.toml"):
        old.unlink()

    converted: list[Path] = []
    skipped: list[str] = []
    all_errors: list[str] = []

    for src in sorted(AGENTS_DIR.glob("*.md")):
        try:
            result = convert_file(src, OUTPUT_DIR)
        except ConvertError as e:
            all_errors.append(str(e))
            continue
        if result is None:
            skipped.append(src.name)
            continue
        dst, expected = result
        errors = post_check(dst, expected)
        if errors:
            all_errors.extend(errors)
        converted.append(dst)

    print(f"Converted: {len(converted)}")
    for p in converted:
        print(f"  {p.relative_to(REPO_ROOT)}")
    print(f"Skipped (MCP wrappers): {len(skipped)}")
    for n in skipped:
        print(f"  {n}")
    if all_errors:
        print(f"\nFAILED post-checks: {len(all_errors)}", file=sys.stderr)
        for e in all_errors:
            print(f"  {e}", file=sys.stderr)
        return 1
    print("\nAll post-checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
