"""Tests for agent-protocol data-model invariants."""

import unittest

from agent_protocol import Observation


class ObservationTests(unittest.TestCase):
    def test_accepts_success_without_process(self) -> None:
        observation = Observation(
            output="No matches found.",
            success=True,
            truncated=False,
            terminal=False,
        )

        self.assertIsNone(observation.exit_code)
        self.assertIsNone(observation.error)

    def test_accepts_successful_process(self) -> None:
        observation = Observation(
            output="15 tests passed",
            success=True,
            truncated=False,
            terminal=False,
            exit_code=0,
        )

        self.assertEqual(observation.exit_code, 0)

    def test_accepts_failed_process(self) -> None:
        observation = Observation(
            output="1 test failed",
            success=False,
            truncated=False,
            terminal=False,
            exit_code=1,
            error="Command exited with status 1.",
        )

        self.assertEqual(observation.exit_code, 1)

    def test_accepts_launch_or_timeout_failure(self) -> None:
        observation = Observation(
            output="partial output",
            success=False,
            truncated=False,
            terminal=False,
            error="Command timed out.",
        )

        self.assertIsNone(observation.exit_code)

    def test_rejects_error_on_success(self) -> None:
        with self.assertRaisesRegex(ValueError, "cannot contain an error"):
            Observation(
                output="done",
                success=True,
                truncated=False,
                terminal=False,
                error="unexpected",
            )

    def test_rejects_failure_without_error(self) -> None:
        with self.assertRaisesRegex(ValueError, "must contain an error"):
            Observation(
                output="",
                success=False,
                truncated=False,
                terminal=False,
            )

    def test_rejects_failed_terminal_observation(self) -> None:
        with self.assertRaisesRegex(ValueError, "must be successful"):
            Observation(
                output="submission failed",
                success=False,
                truncated=False,
                terminal=True,
                error="Could not submit changes.",
            )

    def test_rejects_success_that_disagrees_with_exit_code(self) -> None:
        with self.assertRaisesRegex(ValueError, "agree with its process exit code"):
            Observation(
                output="failed",
                success=True,
                truncated=False,
                terminal=False,
                exit_code=1,
            )

    def test_rejects_failure_that_disagrees_with_exit_code(self) -> None:
        with self.assertRaisesRegex(ValueError, "agree with its process exit code"):
            Observation(
                output="",
                success=False,
                truncated=False,
                terminal=False,
                exit_code=0,
                error="unexpected failure",
            )


if __name__ == "__main__":
    unittest.main()
