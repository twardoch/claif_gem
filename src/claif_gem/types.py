# this_file: src/claif_gem/types.py
"""
Type definitions for the Claif Gemini provider.

This module defines the data structures used for configuring Gemini queries,
representing messages from the Gemini CLI, and encapsulating result metadata.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from claif.common import Message, MessageRole, TextBlock


@dataclass
class GeminiOptions:
    """
    Configuration options for interacting with the Gemini CLI.

    Attributes:
        auto_approve: If True, automatically approves actions without user confirmation.
        yes_mode: Similar to auto_approve, forces 'yes' to all prompts.
        cwd: The current working directory for the Gemini CLI process.
        system_prompt: An optional system-level prompt to guide Gemini's behavior.
        max_context_length: The maximum context length for the model in tokens.
        temperature: Controls the randomness of the output. Higher values mean more random.
        model: The specific Gemini model to use (e.g., 'gemini-pro').
        timeout: Maximum time in seconds to wait for a response from the CLI.
        verbose: If True, enables verbose logging for the Gemini CLI process.
        exec_path: Explicit path to the Gemini CLI executable. If None, it will be searched in PATH.
        images: A list of paths to image files to be included in the prompt (multimodal input).
        retry_count: Number of times to retry a failed query.
        retry_delay: Initial delay in seconds before retrying a failed query.
        no_retry: If True, disables all retry attempts for the query.
    """

    auto_approve: bool = True
    yes_mode: bool = True
    cwd: Optional[Union[str, Path]] = None
    system_prompt: Optional[str] = None
    max_context_length: Optional[int] = None
    temperature: Optional[float] = None
    model: Optional[str] = None
    timeout: Optional[int] = None
    verbose: bool = False
    exec_path: Optional[str] = None
    images: Optional[List[str]] = None
    retry_count: int = 3
    retry_delay: float = 1.0
    no_retry: bool = False


@dataclass
class GeminiMessage:
    """
    Represents a single message received from the Gemini CLI.

    Attributes:
        content: The textual content of the message as a list of TextBlocks.
        role: The role of the sender (e.g., 'assistant', 'user'). Defaults to 'assistant'.
    """

    content: Union[str, List[TextBlock]]
    role: str = "assistant"

    def __post_init__(self) -> None:
        """
        Post-initialization hook to normalize string content into a list of TextBlock.

        If the `content` is provided as a string, it is automatically wrapped
        into a list containing a single `TextBlock` for consistency with the
        core Claif Message format.
        """
        if isinstance(self.content, str):
            self.content = [TextBlock(text=self.content)]

    def to_claif_message(self) -> Message:
        """
        Converts the GeminiMessage to a generic Claif Message format.

        Returns:
            A Message object compatible with the core Claif framework.
        """
        # Map Gemini's role string to Claif's MessageRole enum.
        claif_role: MessageRole = MessageRole.ASSISTANT if self.role == "assistant" else MessageRole.USER
        return Message(
            role=claif_role,
            content=self.content,  # Now already in List[TextBlock] format
        )


@dataclass
class GeminiResponse:
    """
    Represents a structured response from the Gemini CLI, including metadata.

    This dataclass is intended for more detailed responses that might include
    information beyond just the content, such as model details or usage statistics.

    Attributes:
        content: The main textual content of the response.
        role: The role of the sender (e.g., 'assistant', 'user'). Defaults to 'assistant'.
        model: The specific Gemini model that generated the response.
        usage: A dictionary containing usage statistics (e.g., token counts).
        raw_response: The raw, unparsed response from the Gemini CLI, typically a dictionary.
    """

    content: str
    role: str = "assistant"
    model: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None
    raw_response: Optional[Dict[str, Any]] = None

    def to_claif_message(self) -> Message:
        """
        Converts the GeminiResponse to a generic Claif Message format.

        Returns:
            A Message object compatible with the core Claif framework.
        """
        # Map Gemini's role string to Claif's MessageRole enum.
        claif_role: MessageRole = MessageRole.ASSISTANT if self.role == "assistant" else MessageRole.USER
        return Message(role=claif_role, content=self.content)


@dataclass
class ResultMessage:
    """
    Represents a result message containing metadata about a query's execution.

    This is typically used to convey information about the success or failure
    of a query, its duration, and any associated error messages.

    Attributes:
        type: The type of the message, typically 'result'.
        duration: The duration of the query execution in seconds.
        error: A boolean indicating if an error occurred during the query.
        message: An optional descriptive message, especially useful for errors.
        session_id: A unique identifier for the session associated with the query.
    """

    type: str = "result"
    duration: Optional[float] = None
    error: bool = False
    message: Optional[str] = None
    session_id: Optional[str] = None
