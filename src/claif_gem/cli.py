# this_file: src/claif_gem/cli.py
"""Fire-based CLI for Claif Gemini wrapper."""

import asyncio
import os
import sys
import time

import fire
from loguru import logger

from claif.common import (
    Provider,
    ResponseMetrics,
    format_metrics,
    format_response,
    load_config,
)
from claif_gem.client import query
from claif_gem.types import GeminiOptions


def _print(message: str) -> None:
    """Simple print function for output."""


def _print_error(message: str) -> None:
    """Print error message."""


def _print_success(message: str) -> None:
    """Print success message."""


def _print_warning(message: str) -> None:
    """Print warning message."""


class GeminiCLI:
    """Claif Gemini CLI with Fire interface."""

    def __init__(self, config_file: str | None = None, verbose: bool = False):
        """Initialize CLI with optional config file."""
        self._config = load_config(config_file)
        if verbose:
            self._config.verbose = True
        logger.debug("Initialized Gemini CLI")

    def query(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float | None = None,
        system: str | None = None,
        auto_approve: bool = True,
        yes_mode: bool = True,
        max_context: int | None = None,
        timeout: int | None = None,
        output_format: str = "text",
        show_metrics: bool = False,
        images: str | None = None,
        exec: str | None = None,
    ) -> None:
        """Execute a query to Gemini.

        Args:
            prompt: The prompt to send
            model: Model to use (e.g., 'gemini-pro')
            temperature: Sampling temperature (0-1)
            system: System prompt
            auto_approve: Auto-approve mode
            yes_mode: Yes mode for confirmations
            max_context: Maximum context length
            timeout: Timeout in seconds
            output_format: Output format (text, json)
            show_metrics: Show response metrics
            images: Comma-separated image paths or URLs
            exec: Executable path or method (bun/deno/npx)
        """
        # Process images
        image_paths = None
        if images:
            image_paths = self._process_images(images)
        options = GeminiOptions(
            model=model,
            temperature=temperature,
            system_prompt=system,
            auto_approve=auto_approve,
            yes_mode=yes_mode,
            max_context_length=max_context,
            timeout=timeout,
            verbose=self._config.verbose,
            images=image_paths,
            exec_path=exec,
        )

        start_time = time.time()

        try:
            # Run async query
            messages = asyncio.run(self._query_async(prompt, options))

            # Format and display response
            for message in messages:
                formatted = format_response(message, output_format)
                _print(formatted)

            # Show metrics if requested
            if show_metrics:
                duration = time.time() - start_time
                metrics = ResponseMetrics(
                    duration=duration,
                    provider=Provider.GEMINI,
                    model=model or "default",
                )
                _print("\n" + format_metrics(metrics))

        except Exception as e:
            _print_error(str(e))
            if self._config.verbose:
                logger.exception("Full error details")
            sys.exit(1)

    async def _query_async(self, prompt: str, options: GeminiOptions) -> list:
        """Execute async query and collect messages."""
        messages = []
        async for message in query(prompt, options):
            messages.append(message)
        return messages

    def stream(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float | None = None,
        system: str | None = None,
        auto_approve: bool = True,
        yes_mode: bool = True,
    ) -> None:
        """Stream responses from Gemini with live display.

        Args:
            prompt: The prompt to send
            model: Model to use
            temperature: Sampling temperature (0-1)
            system: System prompt
            auto_approve: Auto-approve mode
            yes_mode: Yes mode for confirmations
        """
        options = GeminiOptions(
            model=model,
            temperature=temperature,
            system_prompt=system,
            auto_approve=auto_approve,
            yes_mode=yes_mode,
            verbose=self._config.verbose,
        )

        try:
            asyncio.run(self._stream_async(prompt, options))
        except KeyboardInterrupt:
            _print_warning("Stream interrupted")
        except Exception as e:
            _print_error(str(e))
            if self._config.verbose:
                logger.exception("Full error details")
            sys.exit(1)

    async def _stream_async(self, prompt: str, options: GeminiOptions) -> None:
        """Stream responses with live display."""
        async for message in query(prompt, options):
            # Print content for streaming display
            if isinstance(message.content, str):
                pass
            elif isinstance(message.content, list):
                for block in message.content:
                    if hasattr(block, "text"):
                        pass

    def health(self) -> None:
        """Check Gemini service health."""
        try:
            _print("Checking Gemini health...")

            # Simple health check
            result = asyncio.run(self._health_check())

            if result:
                _print_success("Gemini service is healthy")
            else:
                _print_error("Gemini service is not responding")
                sys.exit(1)

        except Exception as e:
            _print_error(f"Health check failed: {e}")
            sys.exit(1)

    async def _health_check(self) -> bool:
        """Perform health check."""
        try:
            options = GeminiOptions(timeout=10)
            message_count = 0

            async for _ in query("Hello", options):
                message_count += 1
                if message_count > 0:
                    return True

            return message_count > 0
        except Exception:
            return False

    def models(self) -> None:
        """List available Gemini models."""
        _print("Available Gemini Models:")
        _print("  • gemini-pro (default)")
        _print("  • gemini-pro-vision")
        _print("  • gemini-ultra")
        _print("\nNote: Model availability depends on your API access level.")

    def config(self, action: str = "show", **kwargs) -> None:
        """Manage Gemini configuration.

        Args:
            action: Action to perform (show, set)
            **kwargs: Configuration values for 'set' action
        """
        if action == "show":
            _print("Gemini Configuration:")
            gemini_config = self._config.providers.get(Provider.GEMINI, {})

            if isinstance(gemini_config, dict):
                for key, value in gemini_config.items():
                    _print(f"  {key}: {value}")
            else:
                _print(f"  enabled: {gemini_config.enabled}")
                _print(f"  model: {gemini_config.model}")
                _print(f"  timeout: {gemini_config.timeout}")

        elif action == "set":
            if not kwargs:
                _print_error("No configuration values provided")
                return

            # Update configuration
            for key, value in kwargs.items():
                _print_success(f"Set {key} = {value}")

            msg = "Note: Configuration changes are temporary. Update config file for persistence."
            _print_warning(msg)

        else:
            _print_error(f"Unknown action: {action}")
            _print("Available actions: show, set")

    def install(self) -> None:
        """Install Gemini provider (npm package + bundling + installation).

        This will:
        1. Install bun if not available
        2. Install the latest @google/gemini-cli package
        3. Bundle it into a standalone executable
        4. Install the executable to ~/.local/bin (or equivalent)
        """
        from claif_gem.install import install_gemini

        _print("Installing Gemini provider...")
        result = install_gemini()

        if result["installed"]:
            _print_success("Gemini provider installed successfully!")
            _print_success("You can now use the 'gemini' command from anywhere")
        else:
            error_msg = result.get("message", "Unknown error")
            _print_error(f"Failed to install Gemini provider: {error_msg}")
            if result.get("failed"):
                failed_str = ", ".join(result["failed"])
                _print_error(f"Failed components: {failed_str}")
            sys.exit(1)

    def uninstall(self) -> None:
        """Uninstall Gemini provider (remove bundled executable).

        This will remove the bundled Gemini executable from the install
        directory.
        """
        from claif_gem.install import uninstall_gemini

        _print("Uninstalling Gemini provider...")
        result = uninstall_gemini()

        if result["uninstalled"]:
            _print_success("Gemini provider uninstalled successfully!")
        else:
            error_msg = result.get("message", "Unknown error")
            _print_error(f"Failed to uninstall Gemini provider: {error_msg}")
            if result.get("failed"):
                failed_str = ", ".join(result["failed"])
                _print_error(f"Failed components: {failed_str}")
            sys.exit(1)

    def status(self) -> None:
        """Show Gemini provider installation status."""
        try:
            from claif.common.install import find_executable, get_install_dir
        except ImportError:
            _print_error("Install utilities not available")
            return

        _print("Gemini Provider Status")
        _print("")

        # Check bundled executable
        install_dir = get_install_dir()
        bundled_path = install_dir / "gemini"

        if bundled_path.exists():
            _print_success(f"Bundled executable: {bundled_path}")
        else:
            _print_warning("Bundled executable: Not installed")

        # Check external executable
        try:
            external_path = find_executable("gemini")
            _print_success(f"Found executable: {external_path}")
        except Exception:
            _print_error("No external gemini executable found")

        # Show install directory in PATH status
        path_env = os.environ.get("PATH", "")
        if str(install_dir) in path_env:
            _print_success("Install directory in PATH")
        else:
            _print_warning(f"Install directory not in PATH: {install_dir}")
            path_cmd = 'export PATH="$HOME/.local/bin:$PATH"'
            _print(f"  Add to PATH with: {path_cmd}")

    def _process_images(self, images: str) -> list[str]:
        """Process comma-separated image paths or URLs.

        Args:
            images: Comma-separated image paths or URLs

        Returns:
            List of image file paths (downloads URLs to temp files)
        """
        import tempfile
        import urllib.request
        from pathlib import Path

        image_list = [img.strip() for img in images.split(",") if img.strip()]
        processed_paths = []

        for img in image_list:
            if img.startswith(("http://", "https://")):
                # Download URL to temp file
                try:
                    suffix = Path(img).suffix or ".jpg"
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                        logger.debug(f"Downloading image from {img}")
                        with urllib.request.urlopen(img) as response:
                            tmp_file.write(response.read())
                        processed_paths.append(tmp_file.name)
                        logger.debug(f"Downloaded to {tmp_file.name}")
                except Exception as e:
                    _print_error(f"Failed to download image {img}: {e}")
                    continue
            else:
                # Local file path
                path = Path(img).expanduser().resolve()
                if path.exists():
                    processed_paths.append(str(path))
                else:
                    _print_error(f"Image file not found: {img}")
                    continue

        return processed_paths


def main():
    """Main entry point for Fire CLI."""
    fire.Fire(GeminiCLI)
