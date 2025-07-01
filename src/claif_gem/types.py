"""Type definitions for CLAIF Gemini wrapper."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

from ..claif.common import Message, MessageRole


@dataclass
class GeminiOptions:
    """Options for Gemini queries."""
    auto_approve: bool = True
    yes_mode: bool = True
    cwd: Optional[Union[str, Path]] = None
    system_prompt: Optional[str] = None
    max_context_length: Optional[int] = None
    temperature: Optional[float] = None
    model: Optional[str] = None
    timeout: Optional[int] = None
    verbose: bool = False


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
class ResultMessage:
    """Result message with metadata."""
    type: str = "result"
    duration: Optional[float] = None
    error: bool = False
    message: Optional[str] = None
    session_id: Optional[str] = None