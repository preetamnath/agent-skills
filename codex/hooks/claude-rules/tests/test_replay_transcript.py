from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).parents[1] / "replay_transcript.py"
SPEC = importlib.util.spec_from_file_location("replay_transcript", SCRIPT)
assert SPEC and SPEC.loader
replay_transcript = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = replay_transcript
SPEC.loader.exec_module(replay_transcript)


REPO_ROOT = Path("/Users/preetamnath/Desktop/code/OakPostPurchase")
TRANSCRIPT = Path(
    "/Users/preetamnath/.codex/sessions/2026/08/17/"
    "rollout-2026-08-17T10-02-08-01a00dfd-bd81-7c02-8b97-518fe8297ea5.jsonl"
)
FIXTURE = Path(__file__).parent / "fixtures/cartking-regressions.json"


class ReplayTranscriptTest(unittest.TestCase):
    def test_extracts_zsh_lc_and_file_url_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            transcript = Path(directory) / "events.jsonl"
            records = [
                {"type": "event_msg", "payload": {"type": "message"}},
                {
                    "ordinal": 42,
                    "type": "event_msg",
                    "payload": {
                        "type": "item_completed",
                        "item": {
                            "type": "CommandExecution",
                            "id": "exec-1",
                            "command": ["/bin/zsh", "-lc", "sed -n '1p' README.md"],
                            "cwd": "file:///tmp/example%20repo",
                            "exit_code": 0,
                        },
                    },
                },
            ]
            transcript.write_text(
                "\n".join(json.dumps(record) for record in records) + "\n",
                encoding="utf-8",
            )
            events = list(replay_transcript.iter_command_events(transcript))

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].ordinal, 42)
        self.assertEqual(events[0].event_id, "exec-1")
        self.assertEqual(events[0].command, "sed -n '1p' README.md")
        self.assertEqual(events[0].cwd, Path("/tmp/example repo"))

    def test_cartking_fixture_matches_expected_rule_basenames(self) -> None:
        if not (REPO_ROOT / ".git").exists():
            self.skipTest(f"OakPostPurchase checkout not present: {REPO_ROOT}")
        cases = replay_transcript.load_fixture(FIXTURE)
        matches = replay_transcript.replay_fixture(FIXTURE, REPO_ROOT)
        self.assertEqual(len(matches), len(cases))
        for case, match in zip(cases, matches):
            actual = sorted(Path(path).name for path in match.rule_paths)
            expected = sorted(case["expected_rules"])
            self.assertEqual(actual, expected, case["name"])

    def test_archive_replays_all_126_bash_events_with_no_matches(self) -> None:
        if not TRANSCRIPT.exists():
            self.skipTest(f"archived transcript not present: {TRANSCRIPT}")
        if not (REPO_ROOT / ".git").exists():
            self.skipTest(f"OakPostPurchase checkout not present: {REPO_ROOT}")
        report = replay_transcript.replay_transcript(TRANSCRIPT, REPO_ROOT)
        self.assertEqual(report.command_count, 126)
        replay_transcript.assert_expected(report, expect_no_matches=True)

    def test_expected_rule_assertion_accepts_basename_and_rejects_missing(self) -> None:
        if not (REPO_ROOT / ".git").exists():
            self.skipTest(f"OakPostPurchase checkout not present: {REPO_ROOT}")
        matching = replay_transcript.ReplayReport(
            transcript=FIXTURE,
            repo_root=REPO_ROOT,
            events=(
                replay_transcript.match_command(
                    replay_transcript.CommandEvent(
                        ordinal=None,
                        event_id="sanity",
                        command="sed -n '1p' frontend/index.html",
                        cwd=REPO_ROOT,
                        exit_code=0,
                    ),
                    REPO_ROOT,
                ),
            ),
        )
        replay_transcript.assert_expected(
            matching, expected_rule_basenames=["app-shell-parity.md"]
        )
        with self.assertRaises(AssertionError):
            replay_transcript.assert_expected(
                matching, expected_rule_basenames=["missing.md"]
            )


if __name__ == "__main__":
    unittest.main()
