from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).parents[1] / "claude_rules.py"
SPEC = importlib.util.spec_from_file_location("claude_rules", SCRIPT)
assert SPEC and SPEC.loader
claude_rules = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(claude_rules)


class ClaudeRulesHookTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "repo"
        self.root.mkdir()
        (self.root / ".git").mkdir()
        self.rules = self.root / ".claude" / "rules"
        self.rules.mkdir(parents=True)
        self.state = Path(self.temporary.name) / "state"
        self.session = "session-one"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_source(self, relative: str, text: str = "source\n") -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def write_rule(self, name: str, patterns: list[str], body: str = "Rule body") -> Path:
        path = self.rules / name
        path.parent.mkdir(parents=True, exist_ok=True)
        rendered = "\n".join(f'  - "{pattern}"' for pattern in patterns)
        path.write_text(f"---\npaths:\n{rendered}\n---\n{body}\n", encoding="utf-8")
        return path.resolve()

    def payload(
        self,
        command: str,
        cwd: Path | None = None,
        tool_name: str = "Bash",
    ) -> dict[str, object]:
        return {
            "session_id": self.session,
            "transcript_path": f"/tmp/{self.session}.jsonl",
            "cwd": str(cwd or self.root),
            "tool_name": tool_name,
            "tool_input": {"command": command},
        }

    def run_hook(self, command: str, cwd: Path | None = None) -> str | None:
        output = claude_rules.process_pre_tool_use(self.payload(command, cwd), self.state)
        if output is None:
            return None
        return output["hookSpecificOutput"]["additionalContext"]

    def run_post(self, command: str, response: object, cwd: Path | None = None) -> None:
        payload = self.payload(command, cwd)
        payload["tool_response"] = response
        claude_rules.process_post_tool_use(payload, self.state)

    def test_exact_match_and_meta_no_match(self) -> None:
        self.write_source("backend/events.py")
        rule = self.write_rule("backend.md", ["backend/events.py"])
        self.assertEqual(
            self.run_hook("sed -n '1,80p' backend/events.py"),
            f"Read and follow `{rule}`.",
        )
        self.assertIsNone(self.run_hook("git status --short"))
        self.assertIsNone(self.run_hook("echo COUNT(*)"))

    def test_git_diff_pathspec_matches_explicit_app_shell_file(self) -> None:
        self.write_source("frontend/index.html")
        rule = self.write_rule("app-shell.md", ["frontend/index.html"])
        operation = claude_rules.normalize_file_operation(
            "git diff -- frontend/index.html", self.root, self.root
        )
        self.assertIn(
            claude_rules.PathScope("frontend/index.html", False), operation.read_scopes
        )
        self.assertEqual(
            self.run_hook("git diff -- frontend/index.html"),
            f"Read and follow `{rule}`.",
        )
        self.assertIsNone(self.run_hook("git status --short"))

    def test_multi_file_union(self) -> None:
        self.write_source("frontend/one.tsx")
        self.write_source("backend/two.py")
        frontend = self.write_rule("frontend.md", ["frontend/**/*.tsx"])
        backend = self.write_rule("backend.md", ["backend/**/*.py"])
        result = self.run_hook("cat frontend/one.tsx backend/two.py")
        self.assertEqual(
            result,
            f"Read and follow `{backend}`.\nRead and follow `{frontend}`.",
        )

    def test_apply_patch_uses_declared_write_paths_only(self) -> None:
        self.write_source("frontend/index.html")
        self.write_source("src/old.py")
        self.write_source("src/delete.py")
        shell_rule = self.write_rule("shell.md", ["frontend/index.html"])
        types_rule = self.write_rule("types.md", ["src/**/*.d.ts"])
        python_rule = self.write_rule("python.md", ["src/**/*.py"])
        patch = """*** Begin Patch
*** Update File: frontend/index.html
@@
-old
+new text mentioning src/ignored.py
*** Add File: src/new.d.ts
+export {};
*** Delete File: src/delete.py
*** Update File: src/old.py
*** Move to: src/moved.py
@@
-old
+new
*** End Patch"""
        operation = claude_rules.normalize_apply_patch_operation(
            patch, self.root, self.root
        )
        self.assertEqual(
            operation.write_scopes,
            {
                claude_rules.PathScope("frontend/index.html", False),
                claude_rules.PathScope("src/new.d.ts", False),
                claude_rules.PathScope("src/delete.py", False),
                claude_rules.PathScope("src/old.py", False),
                claude_rules.PathScope("src/moved.py", False),
            },
        )
        output = claude_rules.process_pre_tool_use(
            self.payload(patch, tool_name="apply_patch"), self.state
        )
        self.assertEqual(
            output["hookSpecificOutput"]["additionalContext"],
            f"Read and follow `{python_rule}`.\n"
            f"Read and follow `{shell_rule}`.\n"
            f"Read and follow `{types_rule}`.",
        )

    def test_apply_patch_no_match_and_malformed_envelope(self) -> None:
        self.write_rule("frontend.md", ["frontend/**/*.tsx"])
        for patch in (
            "*** Begin Patch\n*** Add File: meta/research/note.md\n+x\n*** End Patch",
            "*** Begin Patch\n*** Add File: ../outside.py\n+x\n*** End Patch",
            "*** Begin Patch\n+frontend/example.tsx\n*** End Patch",
        ):
            self.assertIsNone(
                claude_rules.process_pre_tool_use(
                    self.payload(patch, tool_name="apply_patch"), self.state
                )
            )

    def test_no_target_does_not_match_root(self) -> None:
        self.write_rule("all.md", ["**/*.md"])
        self.assertIsNone(self.run_hook("rg --hidden 'needle'"))
        self.assertIsNone(self.run_hook("rg 'needle' '*.md'"))
        self.assertIsNone(self.run_hook("sqlite3 ':memory:' 'SELECT COUNT(*)'"))

    def test_unknown_commands_do_not_guess_path_operands(self) -> None:
        self.write_source("src/input.py")
        self.write_rule("python.md", ["src/**/*.py"])
        for command in (
            "custom-linter src/input.py",
            f"codex exec -C {self.root} 'edit src/input.py'",
        ):
            operation = claude_rules.normalize_file_operation(
                command, self.root, self.root
            )
            self.assertFalse(operation.scopes, command)
            self.assertIsNone(self.run_hook(command), command)

    def test_regex_bare_glob_and_sql_tokens_do_not_create_root(self) -> None:
        self.write_rule("all.md", ["**/*.md"])
        for command in (
            "grep -E 'foo.*bar'",
            "rg 'src/.*\\.py'",
            "cat '*.md'",
            "psql -c 'SELECT COUNT(*) FROM things'",
        ):
            operation = claude_rules.normalize_file_operation(command, self.root, self.root)
            self.assertNotIn(claude_rules.PathScope(".", True), operation.scopes, command)
            self.assertIsNone(self.run_hook(command), command)

    def test_path_prefixed_glob_uses_literal_directory(self) -> None:
        self.write_source("frontend/src/existing.tsx")
        rule = self.write_rule("frontend.md", ["frontend/**/*.tsx"])
        self.assertEqual(self.run_hook("rg Widget 'frontend/src/**/*.tsx'"), f"Read and follow `{rule}`.")
        operation = claude_rules.normalize_file_operation("rg Widget 'frontend/src/**/*.tsx'", self.root, self.root)
        self.assertEqual(operation.scopes, {claude_rules.PathScope("frontend/src", True)})

    def test_command_specific_option_arity_preserves_operands(self) -> None:
        source = self.write_source("src/input.py")
        rule = self.write_rule("src.md", ["src/input.py"])
        for command in (
            "sed -e 's/input/output/' src/input.py",
            "sed -f src/input.py src/input.py",
            "rg -e input src/input.py",
            "rg -f src/input.py src/input.py",
            "mkdir -p new-dir",
            "rm -r src",
        ):
            operation = claude_rules.normalize_file_operation(command, self.root, self.root)
            self.assertTrue(operation.scopes, command)
        self.assertEqual(self.run_hook("sed -e 's/input/output/' src/input.py"), f"Read and follow `{rule}`.")
        self.assertTrue(source.exists())

    def test_sed_in_place_forms_are_writes(self) -> None:
        self.write_source("src/input.py")
        rule = self.write_rule("src.md", ["src/input.py"])
        for command in (
            "sed -i 's/input/output/' src/input.py",
            "sed -i.bak 's/input/output/' src/input.py",
            "sed --in-place 's/input/output/' src/input.py",
            "sed -i '' 's/input/output/' src/input.py",
        ):
            operation = claude_rules.normalize_file_operation(command, self.root, self.root)
            self.assertIn(claude_rules.PathScope("src/input.py", False), operation.write_scopes)
            self.assertNotIn(claude_rules.PathScope("src/input.py", False), operation.read_scopes)
        self.assertEqual(
            self.run_hook("sed -i 's/input/output/' src/input.py"),
            f"Read and follow `{rule}`.",
        )

    def test_rg_files_treats_all_positionals_as_targets(self) -> None:
        self.write_source("src/input.py")
        rule = self.write_rule("src.md", ["src/input.py"])
        operation = claude_rules.normalize_file_operation("rg --files src", self.root, self.root)
        self.assertIn(claude_rules.PathScope("src", True), operation.read_scopes)
        self.assertEqual(self.run_hook("rg --files src"), f"Read and follow `{rule}`.")
        self.assertIsNone(self.run_hook("rg --files"))

    def test_file_valued_options_are_read_scopes(self) -> None:
        self.write_source("patterns.txt")
        self.write_source("src/input.py")
        rule = self.write_rule("patterns.md", ["patterns.txt"])
        source_rule = self.write_rule("src.md", ["src/input.py"])
        operation = claude_rules.normalize_file_operation(
            "rg -f patterns.txt src/input.py", self.root, self.root
        )
        self.assertIn(claude_rules.PathScope("patterns.txt", False), operation.read_scopes)
        for command in (
            "sed -f patterns.txt src/input.py",
            "rg -f patterns.txt src/input.py",
            "grep --file=patterns.txt input src/input.py",
            "awk -f patterns.txt src/input.py",
            "jq -f patterns.txt src/input.py",
            "jq --file patterns.txt src/input.py",
        ):
            self.assertIn(
                claude_rules.PathScope("patterns.txt", False),
                claude_rules.normalize_file_operation(command, self.root, self.root).read_scopes,
                command,
            )
        self.assertEqual(
            self.run_hook("rg -f patterns.txt src/input.py"),
            f"Read and follow `{rule}`.\nRead and follow `{source_rule}`.",
        )

    def test_partial_shared_response_does_not_mark_rule_loaded(self) -> None:
        first = self.write_rule("first.md", ["src/one.py"], "Shared line\nFirst unique")
        second = self.write_rule("second.md", ["src/two.py"], "Shared line\nSecond unique")
        self.write_source("src/one.py")
        self.write_source("src/two.py")
        command = f"cat {first} {second}"
        self.run_post(command, "Shared line\nFirst unique\n")
        self.assertIsNone(self.run_hook("cat src/one.py"))
        self.assertIsNotNone(self.run_hook("cat src/two.py"))

    def test_redirection_destination_is_a_write_scope_even_when_missing(self) -> None:
        rule = self.write_rule("output.md", ["build/report.md"])
        operation = claude_rules.normalize_file_operation("printf report > build/report.md", self.root, self.root)
        self.assertIn(claude_rules.PathScope("build/report.md", False), operation.write_scopes)
        self.assertEqual(self.run_hook("printf report > build/report.md"), f"Read and follow `{rule}`.")
        self.assertEqual(self.run_hook("printf report >> build/report.md"), f"Read and follow `{rule}`.")

    def test_equals_options_use_normalized_keys(self) -> None:
        source = self.write_source("src/input.py")
        destination_rule = self.write_rule("out.md", ["out/input.py"])
        operation = claude_rules.normalize_file_operation(
            "cp --target-directory=out src/input.py", self.root, self.root
        )
        self.assertIn(claude_rules.PathScope("out", True), operation.write_scopes)
        self.assertEqual(
            self.run_hook("cp --target-directory=out src/input.py"),
            f"Read and follow `{destination_rule}`.",
        )
        self.assertTrue(source.exists())

    def test_recursive_copy_and_move_destinations_are_directories(self) -> None:
        self.write_source("source/nested/value.py")
        rule = self.write_rule("destination.md", ["destination/**/*.py"])
        for command in ("cp -r source destination", "mv -r source destination"):
            operation = claude_rules.normalize_file_operation(command, self.root, self.root)
            self.assertIn(claude_rules.PathScope("destination", True), operation.write_scopes)
        self.assertEqual(self.run_hook("cp -r source destination"), f"Read and follow `{rule}`.")

    def test_selector_extension_does_not_match_unrelated_rule_glob(self) -> None:
        self.write_source("src/value.ts")
        self.write_source("src/value.py")
        typescript = self.write_rule("typescript.md", ["src/**/*.ts"])
        self.write_rule("python.md", ["src/**/*.py"])
        self.assertEqual(self.run_hook("cat src/*.ts"), f"Read and follow `{typescript}`.")

    def test_post_tool_use_records_explicit_rule_globs_and_control_flow_reads(self) -> None:
        first = self.write_rule("first.md", ["src/one.py"], "First rule body")
        second = self.write_rule("second.md", ["src/two.py"], "Second rule body")
        self.write_source("src/one.py")
        self.write_source("src/two.py")
        response = first.read_text(encoding="utf-8") + second.read_text(encoding="utf-8")
        self.run_post("cat .claude/rules/*.md", response)
        self.assertIsNone(self.run_hook("cat src/one.py"))
        self.assertIsNone(self.run_hook("cat src/two.py"))

        # The reader operand is dynamic, but its explicit glob identifies
        # rules whose response evidence can be trusted.
        claude_rules.process_post_compact(self.payload("true"), self.state)
        self.run_post("for rule in .claude/rules/*.md; do cat \"$rule\"; done", response)
        self.assertIsNone(self.run_hook("cat src/one.py"))
        self.assertIsNone(self.run_hook("cat src/two.py"))

    def test_new_destinations_for_copy_move_touch(self) -> None:
        source = self.write_source("src/input.py")
        copy_rule = self.write_rule("generated.md", ["generated.py"])
        self.assertEqual(self.run_hook(f"cp {source} generated.py"), f"Read and follow `{copy_rule}`.")
        self.assertEqual(self.run_hook(f"mv {source} generated.py"), f"Read and follow `{copy_rule}`.")
        touch_rule = self.write_rule("notes.md", ["notes/new.md"])
        self.assertEqual(self.run_hook("touch notes/new.md"), f"Read and follow `{touch_rule}`.")

    def test_compound_rule_reads_record_state(self) -> None:
        first = self.write_rule("first.md", ["src/one.py"], "First rule body")
        second = self.write_rule("second.md", ["src/two.py"], "Second rule body")
        self.write_source("src/one.py")
        self.write_source("src/two.py")
        command = f"cat {first} && sed -n '1,80p' {second}"
        response = first.read_text(encoding="utf-8") + second.read_text(encoding="utf-8")
        self.run_post(command, response)
        self.assertIsNone(self.run_hook("cat src/one.py"))
        self.assertIsNone(self.run_hook("cat src/two.py"))

    def test_post_compact_clears_session_hashes(self) -> None:
        self.write_source("src/one.py")
        rule = self.write_rule("src.md", ["src/one.py"])
        self.run_post(f"cat {rule}", rule.read_text(encoding="utf-8"))
        self.assertIsNone(self.run_hook("cat src/one.py"))
        claude_rules.process_post_compact(self.payload("true"), self.state)
        self.assertIsNotNone(self.run_hook("cat src/one.py"))

    def test_malformed_input_and_top_level_errors_fail_open(self) -> None:
        script = str(SCRIPT)
        for event, stdin in (("pre-tool-use", "{"), ("pre-tool-use", "[]"), ("unknown", "{}")):
            result = subprocess.run(
                [sys.executable, script, event],
                input=stdin,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertLessEqual(len(result.stderr), 512)
        with mock.patch.object(claude_rules, "discover_rules", side_effect=RuntimeError("boom")):
            self.assertIsNone(claude_rules.process_pre_tool_use(self.payload("cat src/one.py"), self.state))

    def test_existing_baseline_behaviors(self) -> None:
        source = self.write_source("backend/events.py")
        rule = self.write_rule("backend.md", ["backend/events.py"])
        self.assertEqual(self.run_hook("cat backend/events.py"), f"Read and follow `{rule}`.")
        self.run_post(f"cat {rule}", rule.read_text(encoding="utf-8"))
        self.assertIsNone(self.run_hook("cat backend/events.py"))
        rule.write_text(rule.read_text(encoding="utf-8") + "Changed\n", encoding="utf-8")
        self.assertEqual(self.run_hook("cat backend/events.py"), f"Read and follow `{rule}`.")
        self.assertTrue(source.exists())


if __name__ == "__main__":
    unittest.main()
