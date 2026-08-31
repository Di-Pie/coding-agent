"""Data models used by the agent protocol."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Action:
    """One tool invocation parsed from a model's JSON response."""

    tool: str
    arguments: dict[str, object]


@dataclass(frozen=True)
class Observation:
    """Structured result of executing one action."""

    output: str
    success: bool
    truncated: bool
    # Whether the agent runtime loop should terminate.
    terminal: bool
    exit_code: int | None = None
    error: str | None = None

    def __post_init__(self) -> None:
        if self.success and self.error is not None:
            raise ValueError("A successful observation cannot contain an error.")

        if not self.success and self.error is None:
            raise ValueError("An unsuccessful observation must contain an error.")

        if self.terminal and not self.success:
            raise ValueError("A terminal observation must be successful.")

        if self.exit_code is not None:
            exit_succeeded = self.exit_code == 0
            if self.success != exit_succeeded:
                raise ValueError(
                    "Observation success must agree with its process exit code."
                )
