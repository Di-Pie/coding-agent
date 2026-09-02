"""Tests for the stateful file-viewer tools."""

import tempfile
import unittest
from pathlib import Path

from tools import ToolContext, goto, open_file, scroll_down, scroll_up


class OpenFileTests(unittest.TestCase):
    def make_context(self, root: Path, *, window_size: int = 100) -> ToolContext:
        return ToolContext(root, root, window_size=window_size)

    def write_numbered_file(self, root: Path, total_lines: int) -> Path:
        path = root / "example.py"
        path.write_text(
            "\n".join(f"content {number}" for number in range(1, total_lines + 1)),
            encoding="utf-8",
        )
        return path

    def test_opens_first_full_window(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = self.write_numbered_file(root, 250)
            context = self.make_context(root)

            observation = open_file(context, path.name)

            self.assertTrue(observation.success)
            self.assertIn("  1:content 1", observation.output)
            self.assertIn("100:content 100", observation.output)
            self.assertIn("(150 more lines below)", observation.output)
            self.assertEqual(context.open_file, path.resolve())
            self.assertEqual(context.window_start, 1)

    def test_places_target_using_swe_agent_offset(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_numbered_file(root, 250)
            context = self.make_context(root)

            observation = open_file(context, "example.py", line_number=50)

            self.assertTrue(observation.success)
            self.assertEqual(context.window_start, 33)
            self.assertIn("(32 more lines above)", observation.output)
            self.assertIn(" 50:content 50", observation.output)
            self.assertIn("132:content 132", observation.output)
            self.assertIn("(118 more lines below)", observation.output)

    def test_clamps_final_window_to_end_of_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_numbered_file(root, 250)
            context = self.make_context(root)

            observation = open_file(context, "example.py", line_number=250)

            self.assertTrue(observation.success)
            self.assertEqual(context.window_start, 151)
            self.assertIn("151:content 151", observation.output)
            self.assertIn("250:content 250", observation.output)
            self.assertNotIn("more lines below", observation.output)

    def test_short_file_displays_every_line(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_numbered_file(root, 4)
            context = self.make_context(root)

            observation = open_file(context, "example.py", line_number=4)

            self.assertTrue(observation.success)
            self.assertEqual(context.window_start, 1)
            self.assertIn("1:content 1", observation.output)
            self.assertIn("4:content 4", observation.output)
            self.assertNotIn("more lines above", observation.output)
            self.assertNotIn("more lines below", observation.output)

    def test_empty_file_returns_header_only(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "empty.py"
            path.write_text("", encoding="utf-8")
            context = self.make_context(root)

            observation = open_file(context, path.name)

            self.assertTrue(observation.success)
            self.assertEqual(
                observation.output,
                f"[File: {path.resolve()} (0 lines total)]",
            )
            self.assertEqual(context.window_start, 1)

    def test_invalid_line_returns_failed_observation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_numbered_file(root, 4)
            context = self.make_context(root)

            observation = open_file(context, "example.py", line_number=5)

            self.assertFalse(observation.success)
            self.assertIn("line_number must be between 1 and 4", observation.error or "")
            self.assertIsNone(context.open_file)

    def test_path_failures_return_failed_observations(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = self.make_context(root)

            missing = open_file(context, "missing.py")
            directory_result = open_file(context, ".")
            unsafe = open_file(context, "../outside.py")

            self.assertFalse(missing.success)
            self.assertIn("file does not exist", missing.error or "")
            self.assertFalse(directory_result.success)
            self.assertIn("not a regular file", directory_result.error or "")
            self.assertFalse(unsafe.success)
            self.assertIn("inside the repository", unsafe.error or "")

    def test_invalid_utf8_returns_failed_observation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "binary.py"
            path.write_bytes(b"\xff")
            context = self.make_context(root)

            observation = open_file(context, path.name)

            self.assertFalse(observation.success)
            self.assertIn("open:", observation.error or "")

    def test_truncates_rendered_window(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_numbered_file(root, 20)
            context = ToolContext(root, root, max_output_chars=40)

            observation = open_file(context, "example.py")

            self.assertTrue(observation.success)
            self.assertTrue(observation.truncated)
            self.assertEqual(len(observation.output), 40)
            self.assertEqual(context.window_start, 1)

    def test_goto_renders_target_window(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_numbered_file(root, 250)
            context = self.make_context(root)
            open_file(context, "example.py")

            observation = goto(context, 50)

            self.assertTrue(observation.success)
            self.assertEqual(context.window_start, 33)
            self.assertIn("(32 more lines above)", observation.output)
            self.assertIn(" 50:content 50", observation.output)
            self.assertIn("132:content 132", observation.output)

    def test_goto_rejects_invalid_line_without_changing_window(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_numbered_file(root, 250)
            context = self.make_context(root)
            open_file(context, "example.py", line_number=50)

            observation = goto(context, 0)

            self.assertFalse(observation.success)
            self.assertIn("goto: line_number must be between", observation.error or "")
            self.assertEqual(context.window_start, 33)

    def test_scroll_down_and_up_preserve_overlap(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_numbered_file(root, 250)
            context = self.make_context(root)
            open_file(context, "example.py")

            down = scroll_down(context)

            self.assertTrue(down.success)
            self.assertEqual(context.window_start, 99)
            self.assertIn(" 99:content 99", down.output)
            self.assertIn("198:content 198", down.output)

            up = scroll_up(context)

            self.assertTrue(up.success)
            self.assertEqual(context.window_start, 1)
            self.assertIn("  1:content 1", up.output)
            self.assertIn("100:content 100", up.output)

    def test_scrolling_clamps_at_file_boundaries(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_numbered_file(root, 250)
            context = self.make_context(root)
            open_file(context, "example.py")

            scroll_up(context)
            self.assertEqual(context.window_start, 1)

            scroll_down(context)
            scroll_down(context)
            scroll_down(context)
            self.assertEqual(context.window_start, 151)

            final_window = scroll_down(context)
            self.assertEqual(context.window_start, 151)
            self.assertIn("250:content 250", final_window.output)
            self.assertNotIn("more lines below", final_window.output)

    def test_navigation_requires_an_open_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = self.make_context(root)

            results = [goto(context, 1), scroll_down(context), scroll_up(context)]

            for observation, tool_name in zip(
                results,
                ("goto", "scroll_down", "scroll_up"),
                strict=True,
            ):
                with self.subTest(tool=tool_name):
                    self.assertFalse(observation.success)
                    self.assertEqual(
                        observation.error,
                        f"{tool_name}: no file is currently open",
                    )

    def test_navigation_rereads_file_contents(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = self.write_numbered_file(root, 150)
            context = self.make_context(root)
            open_file(context, path.name)
            path.write_text("updated\ncontent", encoding="utf-8")

            observation = scroll_down(context)

            self.assertTrue(observation.success)
            self.assertEqual(context.window_start, 1)
            self.assertIn("1:updated", observation.output)
            self.assertIn("2:content", observation.output)


if __name__ == "__main__":
    unittest.main()
