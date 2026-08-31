"""Tests for consistency between tool schemas and dispatch."""

import unittest
from unittest.mock import patch

from agent_protocol import Action, Observation
from tools import TOOL_SPECS
from tools.dispatcher import TOOL_MAP, execute_tool


class DispatcherTests(unittest.TestCase):
    def test_tool_map_matches_tool_schemas(self) -> None:
        self.assertEqual(set(TOOL_SPECS), set(TOOL_MAP))

    def test_execute_tool_forwards_arguments_and_returns_observation(self) -> None:
        received: dict[str, object] = {}
        expected = Observation(
            output="done",
            success=True,
            truncated=False,
            terminal=False,
            exit_code=0,
        )

        def fake_bash(command: str) -> Observation:
            received["command"] = command
            return expected

        action = Action(tool="bash", arguments={"command": "pytest -q"})
        with patch.dict(TOOL_MAP, {"bash": fake_bash}):
            actual = execute_tool(action)

        self.assertIs(actual, expected)
        self.assertEqual(received, {"command": "pytest -q"})


if __name__ == "__main__":
    unittest.main()
