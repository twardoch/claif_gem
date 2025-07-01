# this_file: src/claif_gem/types.py
"""Type definitions for CLAIF Gemini wrapper."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from claif.common import Message, MessageRole
except ImportError:
    from claif_gem._compat import Message, MessageRole


@dataclass
class GeminiOptions:
    """Options for Gemini queries."""

    auto_approve: bool = True
    yes_mode: bool = True
    cwd: str | Path | None = None
    system_prompt: str | None = None
    max_context_length: int | None = None
    temperature: float | None = None
    model: str | None = None
    timeout: int | None = None
    verbose: bool = False
    exec_path: str | None = None
    images: list[str] | None = None


@dataclass
class GeminiMessage:
    """A message from Gemini."""

    content: str
    role: str = "assistant"

    def to_claif_message(self) -> Message:
        """Convert to CLAIF message."""
        return Message(
            role=MessageRole.ASSISTANT,
            content=self.content,
        )


@dataclass
class GeminiResponse:
    """Response from Gemini CLI."""

    content: str
    role: str = "assistant"
    model: str | None = None
    usage: dict[str, Any] | None = None
    raw_response: dict[str, Any] | None = None

    def to_claif_message(self) -> Message:
        """Convert to CLAIF message."""
        role = MessageRole.ASSISTANT if self.role == "assistant" else MessageRole.USER
        return Message(role=role, content=self.content)


@dataclass
class ResultMessage:
    """Result message with metadata."""

    type: str = "result"
    duration: float | None = None
    error: bool = False
    message: str | None = None
    session_id: str | None = None
