# this_file: src/claif_gem/_compat/__init__.py
"""Compatibility layer for when claif package is not available."""

from dataclasses import dataclass
from enum import Enum


class Provider(Enum):
    """Provider enumeration."""

    GEMINI = "gemini"


class MessageRole(Enum):
    """Message role enumeration."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class Message:
    """A message in the conversation."""

    role: MessageRole
    content: str


@dataclass
class ClaifOptions:
    """Options for CLAIF queries."""

    model: str | None = None
    temperature: float | None = None
    system_prompt: str | None = None
    timeout: int | None = None
    verbose: bool = False


@dataclass
class ResponseMetrics:
    """Response metrics."""

    duration: float
    provider: Provider
    model: str


@dataclass
class Config:
    """Configuration class."""

    verbose: bool = False
    providers: dict = None

    def __post_init__(self):
        if self.providers is None:
            self.providers = {}


class TransportError(Exception):
    """Transport-related errors."""


def load_config(config_file: str | None = None) -> Config:
    """Load configuration."""
    return Config()


def format_response(message: Message, output_format: str = "text") -> str:
    """Format a message for display."""
    if output_format == "json":
        import json

        return json.dumps({"role": message.role.value, "content": message.content})
    return message.content


def format_metrics(metrics: ResponseMetrics) -> str:
    """Format metrics for display."""
    return f"[dim]Duration: {metrics.duration:.2f}s | Provider: {metrics.provider.value} | Model: {metrics.model}[/dim]"
