"""Data models used by the agent protocol."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Action:
    """One tool invocation parsed from a model's JSON response."""

    tool: str
    arguments: dict[str, object]
