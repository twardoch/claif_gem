# this_file: claif_gem/src/claif_gem/client.py
"""Gemini client with OpenAI Responses API compatibility using gemini-cli."""

import os
import json
import time
import subprocess
from collections.abc import Iterator
from typing import Any, Union, Optional
from pathlib import Path

from openai import NOT_GIVEN, NotGiven
from openai.types import CompletionUsage
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionChunk,
    ChatCompletionMessage,
    ChatCompletionMessageParam,
)
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_chunk import Choice as ChunkChoice
from openai.types.chat.chat_completion_chunk import ChoiceDelta


class ChatCompletions:
    """Namespace for completions methods to match OpenAI client structure."""

    def __init__(self, parent: "GeminiClient"):
        self.parent = parent

    def create(
        self,
        *,
        messages: list[ChatCompletionMessageParam],
        model: str = "gemini-pro",
        frequency_penalty: float | None | NotGiven = NOT_GIVEN,
        function_call: Any | None | NotGiven = NOT_GIVEN,
        functions: list[Any] | None | NotGiven = NOT_GIVEN,
        logit_bias: dict[str, int] | None | NotGiven = NOT_GIVEN,
        logprobs: bool | None | NotGiven = NOT_GIVEN,
        max_tokens: int | None | NotGiven = NOT_GIVEN,
        n: int | None | NotGiven = NOT_GIVEN,
        presence_penalty: float | None | NotGiven = NOT_GIVEN,
        response_format: Any | None | NotGiven = NOT_GIVEN,
        seed: int | None | NotGiven = NOT_GIVEN,
        stop: str | None | list[str] | NotGiven = NOT_GIVEN,
        stream: bool | None | NotGiven = NOT_GIVEN,
        temperature: float | None | NotGiven = NOT_GIVEN,
        tool_choice: Any | None | NotGiven = NOT_GIVEN,
        tools: list[Any] | None | NotGiven = NOT_GIVEN,
        top_logprobs: int | None | NotGiven = NOT_GIVEN,
        top_p: float | None | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        # Additional parameters
        extra_headers: Any | None | NotGiven = NOT_GIVEN,
        extra_query: Any | None | NotGiven = NOT_GIVEN,
        extra_body: Any | None | NotGiven = NOT_GIVEN,
        timeout: float | NotGiven = NOT_GIVEN,
    ) -> ChatCompletion | Iterator[ChatCompletionChunk]:
        """Create a chat completion using Gemini CLI.

        This method provides compatibility with OpenAI's chat.completions.create API.
        """
        # Extract the last user message as the prompt
        prompt = ""
        system_prompt = ""
        
        for msg in messages:
            if isinstance(msg, dict):
                role = msg["role"]
                content = msg["content"]
            else:
                role = msg.role
                content = msg.content
                
            if role == "system":
                system_prompt = content
            elif role == "user":
                prompt = content  # Take the last user message
            elif role == "assistant":
                # For multi-turn conversations, append assistant responses
                if prompt:
                    prompt = f"{prompt}\n\nAssistant: {content}\n\nHuman: "
                    
        # Build gemini CLI command
        cmd = [self.parent._gemini_cli_path]
        
        # Add model if specified
        if model and model != "gemini-pro":
            cmd.extend(["--model", self._map_model_name(model)])
            
        # Add temperature if specified
        if temperature is not NOT_GIVEN:
            cmd.extend(["--temperature", str(temperature)])
            
        # Add max tokens if specified
        if max_tokens is not NOT_GIVEN:
            cmd.extend(["--max-output-tokens", str(max_tokens)])
            
        # Add system prompt if specified
        if system_prompt:
            # Some gemini-cli versions might support system prompts differently
            # For now, prepend to the prompt
            prompt = f"System: {system_prompt}\n\n{prompt}"
            
        # Add auto-approve flag to avoid interactive prompts
        cmd.append("-y")  # or --yes depending on gemini-cli version
        
        # Add the prompt
        cmd.append(prompt)
        
        # Handle streaming
        if stream is True:
            return self._create_stream(cmd, model)
        else:
            return self._create_sync(cmd, model)

    def _map_model_name(self, model: str) -> str:
        """Map OpenAI-style model names to Gemini model names."""
        model_map = {
            # Common mappings
            "gpt-4": "gemini-1.5-pro",
            "gpt-4-turbo": "gemini-1.5-pro", 
            "gpt-3.5-turbo": "gemini-1.5-flash",
            "gpt-3.5": "gemini-1.5-flash",
            # Pass through Gemini model names
            "gemini-pro": "gemini-1.5-pro",
            "gemini-pro-vision": "gemini-1.5-pro",
            "gemini-flash": "gemini-1.5-flash",
            "gemini-2.0-flash": "gemini-2.0-flash-exp",
        }
        
        # Return mapped model or pass through if not in map
        return model_map.get(model, model)

    def _create_sync(self, cmd: list[str], model: str) -> ChatCompletion:
        """Create a synchronous chat completion."""
        try:
            # Run gemini CLI
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.parent.timeout,
                check=True
            )
            
            # Extract response content
            content = result.stdout.strip()
            
            # Try to parse as JSON if it looks like JSON
            if content.startswith("{") or content.startswith("["):
                try:
                    data = json.loads(content)
                    # Extract text from JSON response if possible
                    if isinstance(data, dict):
                        content = data.get("text", data.get("response", str(data)))
                except json.JSONDecodeError:
                    pass  # Use raw content
                    
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"Gemini CLI timed out after {self.parent.timeout} seconds")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Gemini CLI error: {e.stderr}")
        except FileNotFoundError:
            raise RuntimeError(
                f"Gemini CLI not found at {cmd[0]}. "
                f"Please install it or set GEMINI_CLI_PATH environment variable."
            )
            
        # Create ChatCompletion response
        timestamp = int(time.time())
        response_id = f"chatcmpl-{timestamp}{os.getpid()}"
        
        # Estimate token counts (rough approximation)
        prompt_tokens = len(cmd[-1].split()) * 2  # Rough estimate
        completion_tokens = len(content.split()) * 2  # Rough estimate
        
        return ChatCompletion(
            id=response_id,
            object="chat.completion", 
            created=timestamp,
            model=model,
            choices=[
                Choice(
                    index=0,
                    message=ChatCompletionMessage(
                        role="assistant",
                        content=content,
                    ),
                    finish_reason="stop",
                    logprobs=None,
                )
            ],
            usage=CompletionUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            ),
        )

    def _create_stream(
        self, cmd: list[str], model: str
    ) -> Iterator[ChatCompletionChunk]:
        """Create a streaming chat completion."""
        # For now, implement a simple non-streaming fallback
        # In a real implementation, this would use gemini-cli's streaming mode if available
        response = self._create_sync(cmd, model)
        
        timestamp = int(time.time())
        chunk_id = f"chatcmpl-{timestamp}{os.getpid()}"
        
        # Initial chunk with role
        yield ChatCompletionChunk(
            id=chunk_id,
            object="chat.completion.chunk",
            created=timestamp,
            model=model,
            choices=[
                ChunkChoice(
                    index=0,
                    delta=ChoiceDelta(role="assistant", content=""),
                    finish_reason=None,
                    logprobs=None,
                )
            ],
        )
        
        # Content chunk
        yield ChatCompletionChunk(
            id=chunk_id,
            object="chat.completion.chunk",
            created=timestamp,
            model=model,
            choices=[
                ChunkChoice(
                    index=0,
                    delta=ChoiceDelta(content=response.choices[0].message.content),
                    finish_reason=None,
                    logprobs=None,
                )
            ],
        )
        
        # Final chunk
        yield ChatCompletionChunk(
            id=chunk_id,
            object="chat.completion.chunk",
            created=timestamp,
            model=model,
            choices=[
                ChunkChoice(
                    index=0,
                    delta=ChoiceDelta(),
                    finish_reason="stop",
                    logprobs=None,
                )
            ],
        )


class Chat:
    """Namespace for chat-related methods to match OpenAI client structure."""

    def __init__(self, parent: "GeminiClient"):
        self.parent = parent
        self.completions = ChatCompletions(parent)


class GeminiClient:
    """Gemini client compatible with OpenAI's chat completions API."""

    def __init__(
        self,
        api_key: str | None = None,
        cli_path: str | None = None,
        timeout: float = 600.0,
    ):
        """Initialize the Gemini client.

        Args:
            api_key: Google API key (defaults to env var) - passed to gemini CLI
            cli_path: Path to gemini CLI executable (defaults to searching PATH)
            timeout: Command timeout in seconds
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.timeout = timeout
        
        # Find gemini CLI path
        self._gemini_cli_path = self._find_gemini_cli(cli_path)
        
        # Set API key environment variable if provided
        if self.api_key:
            os.environ["GEMINI_API_KEY"] = self.api_key
            
        # Create namespace structure to match OpenAI client
        self.chat = Chat(self)

    def _find_gemini_cli(self, cli_path: str | None = None) -> str:
        """Find the gemini CLI executable."""
        if cli_path:
            # Use provided path
            path = Path(cli_path)
            if path.exists() and path.is_file():
                return str(path)
            else:
                raise FileNotFoundError(f"Gemini CLI not found at {cli_path}")
                
        # Check environment variable
        env_path = os.getenv("GEMINI_CLI_PATH")
        if env_path:
            path = Path(env_path)
            if path.exists() and path.is_file():
                return str(path)
                
        # Search common locations
        search_paths = [
            "gemini",  # In PATH
            "gemini-cli",  # Alternative name
            "/usr/local/bin/gemini",
            "/usr/bin/gemini",
            "~/.local/bin/gemini",
            "~/bin/gemini",
            # Windows paths
            "C:\\Program Files\\Gemini\\gemini.exe",
            "C:\\Program Files (x86)\\Gemini\\gemini.exe",
        ]
        
        for search_path in search_paths:
            path = Path(search_path).expanduser()
            if path.exists() and path.is_file():
                return str(path)
                
            # Also try with .exe extension on Windows
            if os.name == "nt" and not search_path.endswith(".exe"):
                exe_path = Path(f"{search_path}.exe").expanduser()
                if exe_path.exists() and exe_path.is_file():
                    return str(exe_path)
                    
        # Try to find in PATH
        import shutil
        gemini_path = shutil.which("gemini") or shutil.which("gemini-cli")
        if gemini_path:
            return gemini_path
            
        raise FileNotFoundError(
            "Gemini CLI not found. Please install it and ensure it's in your PATH, "
            "or set GEMINI_CLI_PATH environment variable, or pass cli_path parameter."
        )

    # Convenience method for backward compatibility
    def create(self, **kwargs) -> ChatCompletion:
        """Create a chat completion (backward compatibility method)."""
        return self.chat.completions.create(**kwargs)