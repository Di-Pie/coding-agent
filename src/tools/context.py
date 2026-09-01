"""Shared execution state for tool calls within one agent run."""

from dataclasses import dataclass
from pathlib import Path

DEFAULT_WINDOW_SIZE = 100


@dataclass
class ToolContext:
    """Mutable repository state and execution limits shared by tools."""

    repository_root: Path
    working_directory: Path
    open_file: Path | None = None
    window_start: int = 1
    window_size: int = DEFAULT_WINDOW_SIZE
    command_timeout: int = 120
    max_output_chars: int = 12_000

    def __post_init__(self) -> None:
        """Normalize paths and reject an invalid initial execution state."""
        repository_root = self.repository_root.resolve()
        if not repository_root.exists():
            raise ValueError("Repository root does not exist.")
        if not repository_root.is_dir():
            raise ValueError("Repository root is not a directory.")

        working_directory = self.working_directory
        if not working_directory.is_absolute():
            working_directory = repository_root / working_directory
        working_directory = working_directory.resolve()

        if not working_directory.exists():
            raise ValueError("Working directory does not exist.")
        if not working_directory.is_dir():
            raise ValueError("Working directory is not a directory.")
        if not working_directory.is_relative_to(repository_root):
            raise ValueError("Working directory must be inside the repository.")

        self.repository_root = repository_root
        self.working_directory = working_directory

        if self.open_file is not None:
            open_file = self.open_file
            if not open_file.is_absolute():
                open_file = working_directory / open_file
            open_file = open_file.resolve()

            if not open_file.exists():
                raise ValueError("Open file does not exist.")
            if not open_file.is_file():
                raise ValueError("Open file must be a regular file.")
            if not open_file.is_relative_to(repository_root):
                raise ValueError("Open file must be inside the repository.")

            self.open_file = open_file

        if self.window_start <= 0:
            raise ValueError("window_start must be positive.")
        if self.window_size <= 0:
            raise ValueError("window_size must be positive.")
        if self.command_timeout <= 0:
            raise ValueError("command_timeout must be positive.")
        if self.max_output_chars <= 0:
            raise ValueError("max_output_chars must be positive.")
