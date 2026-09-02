"""Shared execution state for tool calls within one agent run."""

from dataclasses import dataclass
from pathlib import Path

DEFAULT_WINDOW_SIZE = 100
DEFAULT_OVERLAP_LINES = 2


class ToolPathError(ValueError):
    """Raised when a tool path is invalid or unsafe."""


@dataclass
class ToolContext:
    """Mutable repository state and execution limits shared by tools."""

    repository_root: Path
    working_directory: Path
    open_file: Path | None = None
    window_start: int = 1
    window_size: int = DEFAULT_WINDOW_SIZE
    window_overlap: int = DEFAULT_OVERLAP_LINES
    command_timeout: int = 120
    max_output_chars: int = 12_000

    def __post_init__(self) -> None:
        """Normalize paths and reject an invalid initial execution state."""
        repository_root = self.repository_root.resolve()
        if not repository_root.exists():
            raise ToolPathError("Repository root does not exist.")
        if not repository_root.is_dir():
            raise ToolPathError("Repository root is not a directory.")

        working_directory = self.working_directory
        if not working_directory.is_absolute():
            working_directory = repository_root / working_directory
        working_directory = working_directory.resolve()

        if not working_directory.exists():
            raise ToolPathError("Working directory does not exist.")
        if not working_directory.is_dir():
            raise ToolPathError("Working directory is not a directory.")
        if not working_directory.is_relative_to(repository_root):
            raise ToolPathError("Working directory must be inside the repository.")

        self.repository_root = repository_root
        self.working_directory = working_directory

        if self.open_file is not None:
            open_file = self.resolve_path(self.open_file)

            if not open_file.exists():
                raise ToolPathError("Open file does not exist.")
            if not open_file.is_file():
                raise ToolPathError("Open file must be a regular file.")

            self.open_file = open_file

        if self.window_start <= 0:
            raise ValueError("window_start must be positive.")
        if self.window_size <= 0:
            raise ValueError("window_size must be positive.")
        if self.command_timeout <= 0:
            raise ValueError("command_timeout must be positive.")
        if self.max_output_chars <= 0:
            raise ValueError("max_output_chars must be positive.")
        if self.window_overlap < 0:
            raise ValueError("window_overlap must be nonnegative.")
        if self.window_overlap >= self.window_size:
            raise ValueError("window_overlap must be smaller than window_size.")

    def resolve_path(self, path: str | Path) -> Path:
        """Resolve a path relative to the working directory and enforce containment."""

        candidate_path = Path(path)

        if not candidate_path.is_absolute():
            candidate_path = self.working_directory / candidate_path

        resolved_path = candidate_path.resolve()

        if not resolved_path.is_relative_to(self.repository_root):
            raise ToolPathError(f"Path must be inside the repository: {path}")

        return resolved_path
