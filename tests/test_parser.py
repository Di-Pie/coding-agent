"""Tests for parsing model-generated JSON actions."""

import unittest

from agent_protocol import Action
from agent_protocol.parser import ActionParseError, parse_action


class ParseActionTests(unittest.TestCase):
    def test_parses_valid_action(self) -> None:
        action = parse_action(
            '{"tool": "open", "arguments": {"path": "src/main.py"}}'
        )

        self.assertEqual(
            action,
            Action(tool="open", arguments={"path": "src/main.py"}),
        )

    def test_accepts_optional_null_argument(self) -> None:
        action = parse_action(
            '{"tool": "open", '
            '"arguments": {"path": "src/main.py", "line_number": null}}'
        )

        self.assertIsNone(action.arguments["line_number"])

    def test_ignores_extra_top_level_fields(self) -> None:
        action = parse_action(
            '{"tool": "submit", "arguments": {}, "thought": "Done"}'
        )

        self.assertEqual(action, Action(tool="submit", arguments={}))

    def test_rejects_invalid_json_or_extra_text(self) -> None:
        invalid_responses = [
            "not JSON",
            '{"tool": "submit", "arguments": {}} trailing text',
        ]

        for response in invalid_responses:
            with self.subTest(response=response):
                with self.assertRaises(ActionParseError):
                    parse_action(response)

    def test_rejects_non_object_action(self) -> None:
        with self.assertRaisesRegex(ActionParseError, "JSON object"):
            parse_action("[]")

    def test_rejects_missing_or_invalid_envelope_fields(self) -> None:
        invalid_responses = [
            ('{"arguments": {}}', 'missing required field "tool"'),
            ('{"tool": 1, "arguments": {}}', '"tool" must be a string'),
            ('{"tool": "submit"}', 'missing required field "arguments"'),
            ('{"tool": "submit", "arguments": []}', '"arguments" must be an object'),
        ]

        for response, message in invalid_responses:
            with self.subTest(response=response):
                with self.assertRaisesRegex(ActionParseError, message):
                    parse_action(response)

    def test_rejects_unknown_tool(self) -> None:
        with self.assertRaisesRegex(ActionParseError, 'Unknown tool "banana"'):
            parse_action('{"tool": "banana", "arguments": {}}')

    def test_rejects_missing_required_argument(self) -> None:
        with self.assertRaisesRegex(ActionParseError, "missing required arguments: path"):
            parse_action('{"tool": "open", "arguments": {}}')

    def test_rejects_unknown_argument(self) -> None:
        with self.assertRaisesRegex(ActionParseError, "unknown arguments: banana"):
            parse_action(
                '{"tool": "open", '
                '"arguments": {"path": "src/main.py", "banana": true}}'
            )

    def test_rejects_incorrect_argument_type(self) -> None:
        with self.assertRaisesRegex(ActionParseError, 'argument "path" must be a string'):
            parse_action('{"tool": "open", "arguments": {"path": 1}}')

    def test_rejects_boolean_as_integer(self) -> None:
        with self.assertRaisesRegex(ActionParseError, '"line_number" must be an integer'):
            parse_action('{"tool": "goto", "arguments": {"line_number": true}}')


if __name__ == "__main__":
    unittest.main()
