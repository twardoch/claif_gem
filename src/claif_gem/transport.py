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
    """
    Manages communication with the Google Gemini command-line interface (CLI).

    This class handles the execution of Gemini CLI commands as a subprocess,
    manages environment variables, parses output, and implements retry logic
    for transient errors.
    """

    def __init__(self) -> None:
        """
        Initializes the GeminiTransport instance.

        A unique session ID is generated for tracking purposes.
        """
        self.process: Any | None = None
        self.session_id: str = str(uuid.uuid4())

    async def connect(self) -> None:
        """
        Establishes a connection for the transport.

        This method is a no-op for subprocess-based transports as the connection
        is established implicitly with each command execution.
        """
        pass

    async def disconnect(self) -> None:
        """
        Cleans up the transport by terminating any running Gemini CLI subprocess.

        Ensures that the process is properly terminated and its resources are released.
        Logs a debug message if an error occurs during termination.
        """
        if self.process:
            try:
                # Terminate the process and wait for it to exit
                self.process.terminate()
                await self.process.wait()
                self.process = None
            except Exception as e:
                # Log any errors encountered during process termination
                logger.debug(f"Error during Gemini CLI process disconnect: {e}")
                self.process = None

    async def send_query(self, prompt: str, options: GeminiOptions) -> AsyncIterator[GeminiMessage | ResultMessage]:
        """
        Sends a query to the Gemini CLI and yields responses as they are received.

        This method constructs the CLI command, sets up the environment, and
        executes the command as a subprocess. It includes retry logic for
        transient errors based on the provided options.

        Args:
            prompt: The user's prompt to send to the Gemini CLI.
            options: An instance of GeminiOptions containing configuration for the query.

        Yields:
            An asynchronous iterator of GeminiMessage or ResultMessage objects.
            GeminiMessage contains content from the Gemini CLI.
            ResultMessage indicates the status and duration of the query.
        """
        command: list[str] = self._build_command(prompt, options)
        env: dict[str, str] = self._build_env()

        if options.verbose:
            cmd_str: str = " ".join(command)
            logger.debug(f"Attempting to run Gemini CLI command: {cmd_str}")

        # Retrieve retry settings from options, with sensible defaults
        retry_count: int = getattr(options, "retry_count", 3)
        retry_delay: float = getattr(options, "retry_delay", 1.0)
        no_retry: bool = getattr(options, "no_retry", False)

        # If retries are explicitly disabled or the retry count is zero/negative,
        # execute the query once without any retry mechanism.
        if no_retry or retry_count <= 0:
            async for result in self._execute_query(command, env, options, prompt):
                yield result
            return

        # Define exceptions that are considered retryable. These typically indicate
        # temporary issues like network problems or service unavailability.
        retryable_exceptions = (
            OSError,  # Operating system errors, often related to process spawning
            TransportError,  # Custom transport-level errors
            ConnectionError,  # Network connection issues
            TimeoutError,  # Operation timed out
        )

        try:
            # Configure and execute the retry mechanism.
            # `stop_after_attempt` ensures a maximum number of attempts.
            # `wait_exponential` implements a back-off strategy to avoid overwhelming the service.
            # `retry_if_exception_type` specifies which exceptions trigger a retry.
            # `reraise=False` prevents `RetryError` from being re-raised, allowing custom handling.
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(retry_count + 1),
                wait=wait_exponential(multiplier=retry_delay, min=retry_delay, max=retry_delay * 10),
                retry=retry_if_exception_type(retryable_exceptions),
                reraise=False,
            ):
                with attempt:
                    logger.debug(f"Gemini query attempt {attempt.retry_state.attempt_number}/{retry_count}")

                    # Execute the query and collect all results.
                    # This is necessary to check if any output was received at all.
                    results: list[GeminiMessage | ResultMessage] = []
                    async for result in self._execute_query(command, env, options, prompt):
                        results.append(result)
                        yield result

                    # If no results were received after a successful command execution,
                    # it indicates an unexpected empty response, which is treated as an error.
                    if not results:
                        msg = "No response received from Gemini CLI"
                        raise TransportError(msg)

                    # If execution reaches here, at least one result was received,
                    # and the query is considered successful for this attempt.
                    return

        except RetryError as e:
            # This block is executed if all retry attempts fail.
            # It extracts the last encountered error and yields a ResultMessage indicating failure.
            last_error: Exception = e.__cause__ or e
            logger.error(f"All retry attempts failed for Gemini query: {last_error}")
            yield ResultMessage(
                error=True,
                message=f"Gemini query failed after {retry_count} retries: {last_error!s}",
                session_id=self.session_id,
            )

    async def _execute_query(
        self, command: list[str], env: dict[str, str], options: GeminiOptions, prompt: str
    ) -> AsyncIterator[GeminiMessage | ResultMessage]:
        """
        Executes the actual Gemini CLI subprocess and streams its output.

        This is an internal helper method used by `send_query`. It handles
        subprocess creation, communication, and initial parsing of stdout/stderr.

        Args:
            command: The list of command-line arguments for the Gemini CLI.
            env: A dictionary of environment variables for the subprocess.
            options: An instance of GeminiOptions containing query configuration.
            prompt: The original prompt sent to the Gemini CLI.

        Yields:
            An asynchronous iterator of GeminiMessage or ResultMessage objects.
            GeminiMessage contains parsed content from the CLI.
            ResultMessage indicates the status and duration of the execution.

        Raises:
            TransportError: If a retryable error occurs during subprocess execution
                            and retries are enabled.
        """
        try:
            import asyncio

            start_time: float = anyio.current_time()

            # Create the subprocess. Using `asyncio.create_subprocess_exec` for direct
            # subprocess management, capturing stdout and stderr.
            process = await asyncio.create_subprocess_exec(
                *command,
                env=env,
                cwd=options.cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            self.process = process

            # Wait for the process to complete and capture all its output.
            stdout_data, stderr_data = await process.communicate()

            duration: float = anyio.current_time() - start_time

            # Decode stdout and stderr, stripping any leading/trailing whitespace.
            stdout_output: str = stdout_data.decode("utf-8").strip() if stdout_data else ""
            stderr_output: str = stderr_data.decode("utf-8").strip() if stderr_data else ""

            # Check the process's return code for non-zero (error) status.
            if process.returncode != 0:
                error_msg: str = stderr_output or "Unknown error occurred during Gemini CLI execution."
                
                # Define indicators for retryable errors. These are typically transient
                # issues that might resolve on subsequent attempts.
                retryable_indicators: list[str] = [
                    "timeout", "connection", "network", "quota", "exhausted", 
                    "rate limit", "too many requests", "503", "502", "429"
                ]
                is_retryable: bool = any(indicator in error_msg.lower() for indicator in retryable_indicators)
                
                # Determine if retries are disabled via options.
                no_retry: bool = getattr(options, "no_retry", False)

                # If the error is retryable and retries are not disabled,
                # raise a TransportError to trigger the retry mechanism in `send_query`.
                if is_retryable and not no_retry:
                    msg: str = f"Gemini CLI error (retryable): {error_msg}"
                    raise TransportError(msg)
                else:
                    # If the error is not retryable or retries are disabled,
                    # yield a ResultMessage indicating a permanent failure.
                    yield ResultMessage(
                        error=True,
                        message=f"Gemini CLI error: {error_msg}",
                        duration=duration,
                        session_id=self.session_id,
                    )
                    return

            # If the command executed successfully, attempt to parse its stdout.
            if stdout_output:
                # First, try to parse the output as JSON. This is expected for structured responses.
                try:
                    data: dict[str, Any] = json.loads(stdout_output)
                    # If the JSON contains a "content" key, assume it's a GeminiMessage.
                    if isinstance(data, dict) and "content" in data:
                        yield GeminiMessage(
                            content=data["content"],
                            role=data.get("role", "assistant"),  # Default role to 'assistant'
                        )
                    else:
                        # If JSON is valid but doesn't match expected structure, treat as plain text.
                        yield GeminiMessage(content=stdout_output)
                except json.JSONDecodeError:
                    # If JSON parsing fails, treat the entire output as plain text content.
                    yield GeminiMessage(content=stdout_output)

            # After processing all output, yield a final ResultMessage indicating success.
            yield ResultMessage(
                duration=duration,
                session_id=self.session_id,
            )

        except Exception as e:
            # Catch any unexpected exceptions during execution and log them.
            logger.error(f"An unexpected transport error occurred: {e}")
            # Re-raise specific exceptions that are meant to be handled by the retry logic.
            if isinstance(e, OSError | TransportError | ConnectionError | TimeoutError):
                raise
            # For all other exceptions, yield a ResultMessage indicating an error.
            yield ResultMessage(
                error=True,
                message=str(e),
                session_id=self.session_id,
            )

    def _build_command(self, prompt: str, options: GeminiOptions) -> list[str]:
        """
        Constructs the command-line argument list for the Gemini CLI subprocess.

        This method intelligently handles the executable path (whether it's a simple
        command name or a full path with spaces) and appends various options
        based on the provided GeminiOptions.

        Args:
            prompt: The user's prompt to be included in the command.
            options: An instance of GeminiOptions containing command-line arguments.

        Returns:
            A list of strings representing the full command to be executed.
        """
        cli_path: str = self._find_cli(options.exec_path)

        # Determine how to split the command based on whether cli_path is a direct
        # file path or a command string that might contain arguments (e.g., "deno run").
        path_obj: Path = Path(cli_path)
        if path_obj.exists() and path_obj.is_file():
            # If it's an existing file, treat it as a single executable path.
            command: list[str] = [cli_path]
        elif " " in cli_path:
            # If it contains spaces but isn't a direct file, assume it's a command
            # with arguments and split it using shlex for proper handling of quotes.
            command = shlex.split(cli_path)
        else:
            # Otherwise, treat it as a simple command name (e.g., "gemini").
            command = [cli_path]

        # Append various options to the command list based on GeminiOptions.
        if options.auto_approve or options.yes_mode:
            command.append("-y")  # Equivalent to --yes or --yolo mode in some CLIs

        if options.verbose:
            command.append("-d")  # Equivalent to --debug mode

        if options.model:
            command.extend(["-m", options.model])

        if options.temperature is not None:
            command.extend(["-t", str(options.temperature)])

        if options.system_prompt:
            command.extend(["-s", options.system_prompt])

        if options.max_context_length:
            command.extend(["--max-context", str(options.max_context_length)])

        # Add the main prompt argument.
        command.extend(["-p", prompt])

        # Add image paths if provided.
        if options.images:
            for image_path in options.images:
                command.extend(["-i", image_path])

        return command

    def _build_env(self) -> dict[str, str]:
        """
        Constructs the environment variables dictionary for the Gemini CLI subprocess.

        This method ensures that the `claif` binary directory is added to the PATH
        (if available) and sets specific environment variables required by the
        Gemini SDK and Claif framework.

        Returns:
            A dictionary of environment variables.
        """
        try:
            # Attempt to import and use `inject_claif_bin_to_path` from `claif.common.utils`
            # to ensure the Claif binaries are discoverable by the subprocess.
            from claif.common.utils import inject_claif_bin_to_path
            env: dict[str, str] = inject_claif_bin_to_path()
        except ImportError:
            # If `claif.common.utils` is not available, fall back to the current environment.
            env = os.environ.copy()

        # Set specific environment variables for the Gemini SDK and Claif provider identification.
        env["GEMINI_SDK"] = "1"
        env["CLAIF_PROVIDER"] = "gemini"
        return env

    def _find_cli(self, exec_path: str | None = None) -> str:
        """
        Locates the Gemini CLI executable.

        It uses a simplified 3-mode logic:
        1. If `exec_path` is provided, it attempts to use that directly.
        2. Otherwise, it searches for "gemini" in standard executable locations.

        Args:
            exec_path: An optional explicit path to the Gemini CLI executable.

        Returns:
            The absolute path to the Gemini CLI executable.

        Raises:
            TransportError: If the Gemini CLI executable cannot be found or accessed.
        """
        try:
            # Use `find_executable` from `claif.common` to locate the executable.
            return find_executable("gemini", exec_path)
        except InstallError as e:
            # Wrap InstallError in TransportError for consistency within the transport layer.
            raise TransportError(f"Gemini CLI executable not found: {e}") from e
