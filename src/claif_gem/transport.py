# this_file: claif_gem/src/claif_gem/transport.py
"""Transport layer for Claif Gemini CLI communication."""

import json
import os
import shlex
import uuid
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

import anyio
from claif.common import InstallError, TransportError, find_executable
from loguru import logger
from tenacity import (
    AsyncRetrying,
    RetryError,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from claif_gem.types import GeminiMessage, GeminiOptions, ResultMessage


class GeminiTransport:
    """Transport for communicating with Gemini CLI."""

    def __init__(self):
        self.process: Any | None = None
        self.session_id = str(uuid.uuid4())

    async def connect(self) -> None:
        """Initialize transport (no-op for subprocess)."""

    async def disconnect(self) -> None:
        """Cleanup transport."""
        if self.process:
            try:
                self.process.terminate()
                await self.process.wait()
            except Exception as e:
                # Disconnect errors during cleanup are usually not critical
                logger.debug(f"Error during disconnect (expected during cleanup): {e}")
            finally:
                self.process = None

    async def send_query(self, prompt: str, options: GeminiOptions) -> AsyncIterator[GeminiMessage | ResultMessage]:
        """Send query to Gemini and yield responses."""
        command = self._build_command(prompt, options)
        env = self._build_env()

        if options.verbose:
            cmd_str = " ".join(command)
            logger.debug(f"Running command: {cmd_str}")

        # Get retry settings from options or use defaults
        retry_count = getattr(options, "retry_count", 3)
        retry_delay = getattr(options, "retry_delay", 1.0)

        # If retry is disabled, execute once without retry
        if retry_count <= 0:
            async for result in self._execute_query(command, env, options, prompt):
                yield result
            return

        # Define retry exceptions
        retry_exceptions = (
            OSError,  # Process spawn failures
            TransportError,
            ConnectionError,
            TimeoutError,
        )

        try:
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(retry_count),
                wait=wait_exponential(multiplier=retry_delay, min=retry_delay, max=retry_delay * 10),
                retry=retry_if_exception_type(retry_exceptions),
                reraise=True,
            ):
                with attempt:
                    logger.debug(f"Gemini query attempt {attempt.retry_state.attempt_number}/{retry_count}")

                    # Collect all results to check if we got any
                    results = []
                    async for result in self._execute_query(command, env, options, prompt):
                        results.append(result)
                        yield result

                    # If we got no results, that's an error
                    if not results:
                        msg = "No response received from Gemini CLI"
                        raise TransportError(msg)

                    return

        except RetryError as e:
            last_error = e.__cause__ or e
            logger.error(f"All retry attempts failed for Gemini query: {last_error}")
            yield ResultMessage(
                error=True,
                message=f"Gemini query failed after {retry_count} retries: {last_error!s}",
                session_id=self.session_id,
            )

    async def _execute_query(
        self, command: list[str], env: dict[str, str], options: GeminiOptions, prompt: str
    ) -> AsyncIterator[GeminiMessage | ResultMessage]:
        """Execute the actual query subprocess."""
        try:
            import asyncio

            start_time = anyio.current_time()

            # Use asyncio subprocess instead of anyio
            process = await asyncio.create_subprocess_exec(
                *command,
                env=env,
                cwd=options.cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            self.process = process

            # Wait for process and get all output at once
            stdout_data, stderr_data = await process.communicate()

            duration = anyio.current_time() - start_time

            # Decode the output
            stdout_output = stdout_data.decode("utf-8").strip() if stdout_data else ""
            stderr_output = stderr_data.decode("utf-8").strip() if stderr_data else ""

            # Check for errors
            if process.returncode != 0:
                error_msg = stderr_output or "Unknown error"
                # Check if it's a retryable error
                if any(indicator in error_msg.lower() for indicator in ["timeout", "connection", "network"]):
                    msg = f"Gemini CLI error (retryable): {error_msg}"
                    raise TransportError(msg)
                else:
                    yield ResultMessage(
                        error=True,
                        message=f"Gemini CLI error: {error_msg}",
                        duration=duration,
                        session_id=self.session_id,
                    )
                    return

            # Parse output
            if stdout_output:
                # Try to parse as JSON first
                try:
                    data = json.loads(stdout_output)
                    if isinstance(data, dict) and "content" in data:
                        yield GeminiMessage(
                            content=data["content"],
                            role=data.get("role", "assistant"),
                        )
                    else:
                        # Fallback to plain text
                        yield GeminiMessage(content=stdout_output)
                except json.JSONDecodeError:
                    # Plain text response
                    yield GeminiMessage(content=stdout_output)

            # Send result message
            yield ResultMessage(
                duration=duration,
                session_id=self.session_id,
            )

        except Exception as e:
            logger.error(f"Transport error: {e}")
            # Re-raise for retry logic if it's a retryable exception
            if isinstance(e, OSError | TransportError | ConnectionError | TimeoutError):
                raise
            yield ResultMessage(
                error=True,
                message=str(e),
                session_id=self.session_id,
            )

    def _build_command(self, prompt: str, options: GeminiOptions) -> list[str]:
        """Build command line arguments."""
        cli_path = self._find_cli(options.exec_path)

        # Check if this is a single file path (possibly with spaces) or a command with arguments
        path_obj = Path(cli_path)
        if path_obj.exists():
            # This is a file path, treat as single argument even if it has spaces
            command = [cli_path]
        elif " " in cli_path:
            # This is a command with arguments (e.g., "deno run script.js")
            command = shlex.split(cli_path)
        else:
            # Simple command name
            command = [cli_path]

        # Add options
        if options.auto_approve or options.yes_mode:
            command.append("-y")  # --yolo mode

        if options.verbose:
            command.append("-d")  # --debug mode

        if options.model:
            command.extend(["-m", options.model])

        if options.temperature is not None:
            command.extend(["-t", str(options.temperature)])

        if options.system_prompt:
            command.extend(["-s", options.system_prompt])

        if options.max_context_length:
            command.extend(["--max-context", str(options.max_context_length)])

        # Add prompt
        command.extend(["-p", prompt])

        # Add images if supported (Note: Gemini CLI may not support this yet)
        if options.images:
            for image_path in options.images:
                command.extend(["-i", image_path])

        return command

    def _build_env(self) -> dict:
        """Build environment variables."""
        try:
            from claif.common.utils import inject_claif_bin_to_path

            env = inject_claif_bin_to_path()
        except ImportError:
            env = os.environ.copy()

        env["GEMINI_SDK"] = "1"
        env["CLAIF_PROVIDER"] = "gemini"
        return env

    def _find_cli(self, exec_path: str | None = None) -> str:
        """Find Gemini CLI executable using simplified 3-mode logic.

        Args:
            exec_path: Optional explicit path provided by user

        Returns:
            Path to the executable

        Raises:
            TransportError: If executable cannot be found
        """
        try:
            return find_executable("gemini", exec_path)
        except InstallError as e:
            raise TransportError(str(e)) from e
