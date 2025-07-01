# this_file: src/claif_gem/transport.py
"""Transport layer for Gemini CLI communication."""

import json
import os
import shutil
import sys
import uuid
from collections.abc import AsyncIterator
from pathlib import Path

import anyio
from anyio.streams.text import TextReceiveStream
from loguru import logger

try:
    from claif.common import TransportError
except ImportError:
    from claif_gem._compat import TransportError
from claif_gem.types import GeminiMessage, GeminiOptions, ResultMessage


class GeminiTransport:
    """Transport for communicating with Gemini CLI."""

    def __init__(self):
        self.process: anyio.Process | None = None
        self.session_id = str(uuid.uuid4())

    async def connect(self) -> None:
        """Initialize transport (no-op for subprocess)."""
        pass

    async def disconnect(self) -> None:
        """Cleanup transport."""
        if self.process:
            try:
                self.process.terminate()
                await self.process.wait()
            except Exception as e:
                logger.warning(f"Error during disconnect: {e}")
            finally:
                self.process = None

    async def send_query(self, prompt: str, options: GeminiOptions) -> AsyncIterator[GeminiMessage | ResultMessage]:
        """Send query to Gemini and yield responses."""
        command = self._build_command(prompt, options)
        env = self._build_env()

        if options.verbose:
            logger.debug(f"Running command: {' '.join(command)}")

        try:
            start_time = anyio.current_time()

            async with await anyio.open_process(
                command,
                env=env,
                cwd=options.cwd,
                stdout=anyio.subprocess.PIPE,
                stderr=anyio.subprocess.PIPE,
            ) as process:
                self.process = process

                # Read output
                stdout_stream = TextReceiveStream(process.stdout)
                stderr_stream = TextReceiveStream(process.stderr)

                stdout_lines = []
                stderr_lines = []

                async with anyio.create_task_group() as tg:

                    async def read_stdout():
                        async for line in stdout_stream:
                            stdout_lines.append(line)

                    async def read_stderr():
                        async for line in stderr_stream:
                            stderr_lines.append(line)

                    tg.start_soon(read_stdout)
                    tg.start_soon(read_stderr)

                # Wait for process to complete
                await process.wait()

                duration = anyio.current_time() - start_time

                # Check for errors
                if process.returncode != 0:
                    error_msg = "".join(stderr_lines) or "Unknown error"
                    yield ResultMessage(
                        error=True,
                        message=f"Gemini CLI error: {error_msg}",
                        duration=duration,
                        session_id=self.session_id,
                    )
                    return

                # Parse output
                output = "".join(stdout_lines).strip()

                if output:
                    # Try to parse as JSON first
                    try:
                        data = json.loads(output)
                        if isinstance(data, dict) and "content" in data:
                            yield GeminiMessage(
                                content=data["content"],
                                role=data.get("role", "assistant"),
                            )
                        else:
                            # Fallback to plain text
                            yield GeminiMessage(content=output)
                    except json.JSONDecodeError:
                        # Plain text response
                        yield GeminiMessage(content=output)

                # Send result message
                yield ResultMessage(
                    duration=duration,
                    session_id=self.session_id,
                )

        except Exception as e:
            logger.error(f"Transport error: {e}")
            yield ResultMessage(
                error=True,
                message=str(e),
                session_id=self.session_id,
            )

    def _build_command(self, prompt: str, options: GeminiOptions) -> list[str]:
        """Build command line arguments."""
        cli_path = self._find_cli()
        command = [cli_path]

        # Add options
        if options.auto_approve:
            command.append("-a")

        if options.yes_mode:
            command.append("-y")

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

        return command

    def _build_env(self) -> dict:
        """Build environment variables."""
        env = os.environ.copy()
        env["GEMINI_SDK"] = "1"
        env["CLAIF_PROVIDER"] = "gemini"
        return env

    def _find_cli(self) -> str:
        """Find Gemini CLI executable."""
        # Check if specified in environment
        if cli_path := os.environ.get("GEMINI_CLI_PATH"):
            if Path(cli_path).exists():
                return cli_path

        # Search in PATH
        if cli := shutil.which("gemini"):
            return cli

        # Search common locations
        search_paths = [
            Path.home() / ".local" / "bin" / "gemini",
            Path("/usr/local/bin/gemini"),
            Path("/opt/gemini/bin/gemini"),
        ]

        # Add npm global paths
        if sys.platform == "win32":
            npm_prefix = os.environ.get("APPDATA", "")
            if npm_prefix:
                search_paths.append(Path(npm_prefix) / "npm" / "gemini.cmd")
        else:
            search_paths.extend(
                [
                    Path.home() / ".npm-global" / "bin" / "gemini",
                    Path("/usr/local/lib/node_modules/.bin/gemini"),
                ]
            )

        for path in search_paths:
            if path.exists():
                return str(path)

        msg = "Gemini CLI not found. Please install it or set GEMINI_CLI_PATH environment variable."
        raise TransportError(msg)
