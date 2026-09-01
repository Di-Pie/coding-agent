"""Tests for tool execution context initialization."""

import tempfile
import unittest
from pathlib import Path

from tools import ToolContext


class ToolContextTests(unittest.TestCase):
    def test_resolves_relative_working_directory_inside_repository(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository_root = Path(directory)
            source_directory = repository_root / "src"
            source_directory.mkdir()

            context = ToolContext(repository_root, Path("src"))

            self.assertEqual(context.repository_root, repository_root.resolve())
            self.assertEqual(context.working_directory, source_directory.resolve())

    def test_resolves_relative_open_file_from_working_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository_root = Path(directory)
            source_directory = repository_root / "src"
            source_directory.mkdir()
            source_file = source_directory / "main.py"
            source_file.write_text("print('hello')\n", encoding="utf-8")

            context = ToolContext(
                repository_root,
                Path("src"),
                open_file=Path("main.py"),
            )

            self.assertEqual(context.open_file, source_file.resolve())

    def test_rejects_missing_repository_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing"

            with self.assertRaisesRegex(ValueError, "Repository root does not exist"):
                ToolContext(missing, missing)

    def test_rejects_working_directory_outside_repository(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            repository_root = base / "repository"
            outside = base / "outside"
            repository_root.mkdir()
            outside.mkdir()

            with self.assertRaisesRegex(ValueError, "inside the repository"):
                ToolContext(repository_root, outside)

    def test_rejects_working_directory_symlink_outside_repository(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            repository_root = base / "repository"
            outside = base / "outside"
            repository_root.mkdir()
            outside.mkdir()
            link = repository_root / "outside-link"
            link.symlink_to(outside, target_is_directory=True)

            with self.assertRaisesRegex(ValueError, "inside the repository"):
                ToolContext(repository_root, link)

    def test_rejects_open_file_outside_repository(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            repository_root = base / "repository"
            repository_root.mkdir()
            outside_file = base / "outside.py"
            outside_file.write_text("", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "inside the repository"):
                ToolContext(repository_root, repository_root, open_file=outside_file)

    def test_rejects_nonpositive_limits(self) -> None:
        invalid_values = {
            "window_start": 0,
            "window_size": 0,
            "command_timeout": 0,
            "max_output_chars": 0,
        }

        with tempfile.TemporaryDirectory() as directory:
            repository_root = Path(directory)
            for field, value in invalid_values.items():
                with self.subTest(field=field):
                    with self.assertRaisesRegex(ValueError, f"{field} must be positive"):
                        ToolContext(
                            repository_root,
                            repository_root,
                            **{field: value},
                        )


if __name__ == "__main__":
    unittest.main()
