from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ModelConfig:
    name: str
    base_url: str
    temperature: float = 0.2
    context_length: int = 32_768


@dataclass(frozen=True)
class AgentConfig:
    max_steps: int = 30
    command_timeout: int = 120
    max_output_chars: int = 12_000


def load_config(path: Path) -> tuple[ModelConfig, AgentConfig]:
    """Load model and agent settings from a JSON configuration file."""
    data = json.loads(path.read_text(encoding="utf-8"))
    return ModelConfig(**data["model"]), AgentConfig(**data["agent"])

