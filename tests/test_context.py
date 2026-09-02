"""Tests for tool execution context initialization."""

import tempfile
import unittest
from pathlib import Path

from tools import ToolContext, ToolPathError


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

            with self.assertRaisesRegex(
                ToolPathError,
                "Repository root does not exist",
            ):
                ToolContext(missing, missing)

    def test_rejects_working_directory_outside_repository(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            repository_root = base / "repository"
            outside = base / "outside"
            repository_root.mkdir()
            outside.mkdir()

            with self.assertRaisesRegex(ToolPathError, "inside the repository"):
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

            with self.assertRaisesRegex(ToolPathError, "inside the repository"):
                ToolContext(repository_root, link)

    def test_rejects_open_file_outside_repository(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            repository_root = base / "repository"
            repository_root.mkdir()
            outside_file = base / "outside.py"
            outside_file.write_text("", encoding="utf-8")

            with self.assertRaisesRegex(ToolPathError, "inside the repository"):
                ToolContext(repository_root, repository_root, open_file=outside_file)

    def test_resolve_path_accepts_relative_string_and_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository_root = Path(directory)
            source_directory = repository_root / "src"
            source_directory.mkdir()
            context = ToolContext(repository_root, source_directory)

            expected = (source_directory / "main.py").resolve()
            self.assertEqual(context.resolve_path("main.py"), expected)
            self.assertEqual(context.resolve_path(Path("main.py")), expected)

    def test_resolve_path_accepts_absolute_path_inside_repository(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository_root = Path(directory)
            target = repository_root / "new.py"
            context = ToolContext(repository_root, repository_root)

            self.assertEqual(context.resolve_path(target), target.resolve())

    def test_resolve_path_allows_missing_target_inside_repository(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository_root = Path(directory)
            context = ToolContext(repository_root, repository_root)

            target = context.resolve_path("new/directory/file.py")

            expected = (repository_root / "new/directory/file.py").resolve()
            self.assertEqual(target, expected)
            self.assertFalse(target.exists())

    def test_resolve_path_rejects_parent_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository_root = Path(directory) / "repository"
            repository_root.mkdir()
            context = ToolContext(repository_root, repository_root)

            with self.assertRaisesRegex(ToolPathError, "inside the repository"):
                context.resolve_path("../outside.py")

    def test_resolve_path_rejects_absolute_path_outside_repository(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            repository_root = base / "repository"
            repository_root.mkdir()
            context = ToolContext(repository_root, repository_root)

            with self.assertRaisesRegex(ToolPathError, "inside the repository"):
                context.resolve_path(base / "outside.py")

    def test_resolve_path_rejects_symlink_escape(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            repository_root = base / "repository"
            outside = base / "outside"
            repository_root.mkdir()
            outside.mkdir()
            link = repository_root / "outside-link"
            link.symlink_to(outside, target_is_directory=True)
            context = ToolContext(repository_root, repository_root)

            with self.assertRaisesRegex(ToolPathError, "inside the repository"):
                context.resolve_path("outside-link/file.py")

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
                    message = f"{field} must be positive"
                    with self.assertRaisesRegex(ValueError, message):
                        ToolContext(
                            repository_root,
                            repository_root,
                            **{field: value},
                        )

    def test_validates_window_overlap(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository_root = Path(directory)

            with self.assertRaisesRegex(ValueError, "must be nonnegative"):
                ToolContext(
                    repository_root,
                    repository_root,
                    window_overlap=-1,
                )

            with self.assertRaisesRegex(ValueError, "smaller than window_size"):
                ToolContext(
                    repository_root,
                    repository_root,
                    window_size=10,
                    window_overlap=10,
                )


if __name__ == "__main__":
    unittest.main()
