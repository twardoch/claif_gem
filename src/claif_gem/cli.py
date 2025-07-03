# this_file: src/claif_gem/cli.py
"""Fire-based CLI for Claif Gemini wrapper."""

import asyncio
import os
import sys
import time
from typing import Any, Dict, List, Union

import fire
from claif.common import (
    Provider,
    ResponseMetrics,
    format_metrics,
    format_response,
    load_config,
)
from loguru import logger

from claif_gem.client import query
from claif_gem.types import GeminiOptions


from rich.console import Console
from rich.theme import Theme

# Define a custom theme for consistent output styling
cli_theme = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "danger": "bold red",
    "success": "bold green",
    "debug": "dim white"
})
console = Console(theme=cli_theme)

def _print(message: str) -> None:
    """Prints a general message to the console."""
    console.print(message)

def _print_error(message: str) -> None:
    """Prints an error message to the console in red."""
    console.print(f"[danger]Error:[/danger] {message}")

def _print_success(message: str) -> None:
    """Prints a success message to the console in green."""
    console.print(f"[success]Success:[/success] {message}")

def _print_warning(message: str) -> None:
    """Prints a warning message to the console in yellow/magenta."""
    console.print(f"[warning]Warning:[/warning] {message}")


class GeminiCLI:
    """
    Command-Line Interface (CLI) for interacting with the Claif Gemini provider.

    This class provides a Fire-based interface to various Gemini functionalities,
    including querying, streaming, health checks, model listing, configuration
    management, and installation/uninstallation of the Gemini CLI.
    """

    def __init__(self, config_file: str | None = None, verbose: bool = False) -> None:
        """
        Initializes the GeminiCLI instance.

        Args:
            config_file: Optional path to a configuration file.
            verbose: If True, enables verbose logging for debugging purposes.
        """
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
        no_retry: bool = False,
    ) -> None:
        """
        Executes a query to the Gemini LLM and displays the response.

        This method orchestrates the entire query process, including option parsing,
        image processing, asynchronous execution, and result formatting.

        Args:
            prompt: The textual prompt to send to the Gemini model.
            model: Optional. The specific Gemini model to use (e.g., 'gemini-pro').
            temperature: Optional. Controls the randomness of the output (0.0 to 1.0).
            system: Optional. A system-level prompt to guide the model's behavior.
            auto_approve: If True, automatically approves actions without user confirmation.
            yes_mode: If True, forces 'yes' to all confirmation prompts.
            max_context: Optional. The maximum context length for the model in tokens.
            timeout: Optional. Maximum time in seconds to wait for a response.
            output_format: The desired format for the output ('text' or 'json').
            show_metrics: If True, displays performance metrics of the query.
            images: Optional. A comma-separated string of local image paths or URLs.
                    URLs will be downloaded to temporary files.
            exec: Optional. Explicit path to the Gemini CLI executable or a command
                  (e.g., 'bun run'). If None, the executable is searched in PATH.
            no_retry: If True, disables all retry attempts for the query.
        """
        # Initialize image paths to None; it will be populated if 'images' argument is provided.
        image_paths: List[str] | None = None
        if images:
            # Process the comma-separated image string into a list of paths.
            image_paths = self._process_images(images)

        # Create a GeminiOptions object from the provided arguments and configuration.
        options: GeminiOptions = GeminiOptions(
            model=model,
            temperature=temperature,
            system_prompt=system,
            auto_approve=auto_approve,
            yes_mode=yes_mode,
            max_context_length=max_context,
            timeout=timeout,
            verbose=self._config.verbose,  # Inherit verbose setting from CLI config
            images=image_paths,
            exec_path=exec,
            no_retry=no_retry,
        )

        start_time: float = time.time()  # Record the start time for metrics calculation.

        try:
            # Execute the asynchronous query and collect all messages.
            messages: List[Message] = asyncio.run(self._query_async(prompt, options))

            # Iterate through the received messages and format/display them.
            for message in messages:
                formatted_output: str = format_response(message, output_format)
                _print(formatted_output)

            # If requested, calculate and display response metrics.
            if show_metrics:
                duration: float = time.time() - start_time
                metrics: ResponseMetrics = ResponseMetrics(
                    duration=duration,
                    provider=Provider.GEMINI,
                    model=model or "default",  # Use "default" if no specific model was provided.
                )
                _print("\n" + format_metrics(metrics))

        except Exception as e:
            # Catch any exceptions during the query process, print an error message,
            # and exit with a non-zero status code to indicate failure.
            _print_error(str(e))
            if self._config.verbose:
                # If verbose mode is enabled, print the full traceback for debugging.
                logger.exception("Full error details for Gemini query failure:")
            sys.exit(1)

    async def _query_async(self, prompt: str, options: GeminiOptions) -> List[Message]:
        """
        Executes an asynchronous Gemini query and collects all messages.

        Args:
            prompt: The prompt to send to the Gemini model.
            options: Configuration options for the Gemini query.

        Returns:
            A list of Message objects received from the Gemini CLI.
        """
        messages: List[Message] = []
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
        exec: str | None = None,
        no_retry: bool = False,
    ) -> None:
        """
        Streams responses from the Gemini LLM and displays them live.

        This method is suitable for long-running queries where incremental
        updates are desired.

        Args:
            prompt: The textual prompt to send to the Gemini model.
            model: Optional. The specific Gemini model to use (e.g., 'gemini-pro').
            temperature: Optional. Controls the randomness of the output (0.0 to 1.0).
            system: Optional. A system-level prompt to guide the model's behavior.
            auto_approve: If True, automatically approves actions without user confirmation.
            yes_mode: If True, forces 'yes' to all confirmation prompts.
            exec: Optional. Explicit path to the Gemini CLI executable or a command.
            no_retry: If True, disables all retry attempts for the query.
        """
        options: GeminiOptions = GeminiOptions(
            model=model,
            temperature=temperature,
            system_prompt=system,
            auto_approve=auto_approve,
            yes_mode=yes_mode,
            verbose=self._config.verbose,
            exec_path=exec,
            no_retry=no_retry,
        )

        try:
            asyncio.run(self._stream_async(prompt, options))
        except KeyboardInterrupt:
            _print_warning("Stream interrupted by user.")
        except Exception as e:
            _print_error(str(e))
            if self._config.verbose:
                logger.exception("Full error details for Gemini stream failure:")
            sys.exit(1)

    async def _stream_async(self, prompt: str, options: GeminiOptions) -> None:
        """
        Asynchronously streams responses from the Gemini CLI and prints them.

        Args:
            prompt: The prompt to send to the Gemini model.
            options: Configuration options for the Gemini query.
        """
        async for message in query(prompt, options):
            # Print content for streaming display
            if isinstance(message.content, str):
                _print(message.content)
            elif isinstance(message.content, list):
                for block in message.content:
                    if hasattr(block, "text"):
                        _print(block.text)
            # Add a newline after each message for better readability in stream mode
            _print("")

    def health(self) -> None:
        """
        Checks the health and responsiveness of the Gemini service.

        This performs a simple query to the Gemini CLI to verify that it is
        properly installed, configured, and able to return a response.
        """
        try:
            _print("Checking Gemini service health...")

            # Execute a simple asynchronous health check query.
            is_healthy: bool = asyncio.run(self._health_check())

            if is_healthy:
                _print_success("Gemini service is healthy and responding.")
            else:
                _print_error("Gemini service is not responding or health check failed.")
                sys.exit(1)

        except Exception as e:
            _print_error(f"Health check failed due to an unexpected error: {e}")
            if self._config.verbose:
                logger.exception("Full error details for health check failure:")
            sys.exit(1)

    async def _health_check(self) -> bool:
        """
        Performs the actual asynchronous health check query.

        Sends a minimal query to the Gemini CLI with a short timeout.

        Returns:
            True if a response is received, False otherwise.
        """
        try:
            # Set a short timeout for the health check query.
            options: GeminiOptions = GeminiOptions(timeout=10)
            message_count: int = 0

            # Iterate through messages from a simple query. If any message is received,
            # the service is considered healthy.
            async for _ in query("Hello", options):
                message_count += 1
                # If at least one message is received, consider it a success and return.
                if message_count > 0:
                    return True

            # If the loop completes without receiving any messages, return False.
            return message_count > 0
        except Exception:
            # Catch any exceptions during the health check and return False, indicating failure.
            return False

    def models(self) -> None:
        """
        Lists available Gemini models.

        Note: The list of models is currently hardcoded. In a more robust
        implementation, this list would be dynamically retrieved from the
        Gemini API to ensure it is always up-to-date.
        """
        _print("Available Gemini Models:")
        _print("  • gemini-pro (default)")
        _print("  • gemini-pro-vision")
        _print("  • gemini-ultra")
        _print("\nNote: Model availability depends on your API access level.")

    def config(self, action: str = "show", **kwargs: Any) -> None:
        """
        Manages the Gemini provider configuration.

        This method allows users to view the current configuration or update
        temporary configuration settings for the Gemini provider.

        Args:
            action: The action to perform. Can be 'show' to display current
                    configuration, or 'set' to update configuration values.
            **kwargs: Key-value pairs representing configuration settings to update
                      when `action` is 'set'.
        """
        if action == "show":
            _print("Gemini Configuration:")
            # Retrieve Gemini-specific configuration from the loaded config.
            gemini_config: Union[Dict[str, Any], Any] = self._config.providers.get(Provider.GEMINI, {})

            if isinstance(gemini_config, dict):
                # If the configuration is a dictionary, iterate and print key-value pairs.
                for key, value in gemini_config.items():
                    _print(f"  {key}: {value}")
            else:
                # If it's an object (e.g., a dataclass), access its attributes directly.
                _print(f"  enabled: {getattr(gemini_config, 'enabled', 'N/A')}")
                _print(f"  model: {getattr(gemini_config, 'model', 'N/A')}")
                _print(f"  timeout: {getattr(gemini_config, 'timeout', 'N/A')}")

        elif action == "set":
            if not kwargs:
                _print_error("No configuration values provided for 'set' action.")
                return

            # Attempt to update configuration values.
            for key, value in kwargs.items():
                # This directly modifies the in-memory config object.
                # For persistent changes, the underlying config file would need to be updated.
                setattr(self._config.providers[Provider.GEMINI], key, value)
                _print_success(f"Set {key} = {value}")

            msg: str = "Note: Configuration changes made with 'set' are temporary and apply only to the current session. To make changes persistent, update your configuration file directly."
            _print_warning(msg)

        else:
            _print_error(f"Unknown action: {action}")
            _print("Available actions for 'config': show, set")

    def install(self) -> None:
        """
        Installs the Gemini provider, including its npm package and bundling.

        This method performs the following steps:
        1. Checks for and installs 'bun' if it's not already available.
        2. Installs the latest `@google/gemini-cli` npm package.
        3. Bundles the installed package into a standalone executable.
        4. Installs the executable to a well-known local binary directory (e.g., `~/.local/bin`).

        Upon successful installation, it provides instructions on how to add the
        installation directory to the system's PATH for easy access.

        Raises:
            SystemExit: If the installation fails at any step.
        """
        from claif_gem.install import install_gemini

        _print("Attempting to install Gemini provider...")
        result: Dict[str, Any] = install_gemini()

        if result.get("installed"):
            _print_success("Gemini provider installed successfully!")
            _print_success("You can now use the 'gemini' command from anywhere.")
            _print("\nTo ensure the 'gemini' command is always available, add the installation directory to your system's PATH. For most Unix-like systems, you can add the following line to your shell's profile file (e.g., ~/.bashrc, ~/.zshrc, or ~/.profile):\n")
            _print(f"  export PATH=\"{result.get('install_dir', '~/.local/bin')}:$PATH\"")
            _print("\nAfter adding, run 'source ~/.bashrc' (or your respective profile file) to apply the changes.")
        else:
            error_msg: str = result.get("message", "Unknown installation error.")
            _print_error(f"Failed to install Gemini provider: {error_msg}")
            if result.get("failed"):
                failed_components: str = ", ".join(result["failed"])
                _print_error(f"Failed components: {failed_components}")
            sys.exit(1)

    def uninstall(self) -> None:
        """
        Uninstalls the Gemini provider by removing its bundled executable.

        This method attempts to remove the Gemini CLI executable from the
        installation directory. It does not remove the npm package itself.

        Raises:
            SystemExit: If the uninstallation fails.
        """
        from claif_gem.install import uninstall_gemini

        _print("Attempting to uninstall Gemini provider...")
        result: Dict[str, Any] = uninstall_gemini()

        if result.get("uninstalled"):
            _print_success("Gemini provider uninstalled successfully!")
        else:
            error_msg: str = result.get("message", "Unknown uninstallation error.")
            _print_error(f"Failed to uninstall Gemini provider: {error_msg}")
            if result.get("failed"):
                failed_components: str = ", ".join(result["failed"])
                _print_error(f"Failed components: {failed_components}")
            sys.exit(1)

    def status(self) -> None:
        """
        Displays the installation status of the Gemini provider.

        This method checks for the presence of the bundled Gemini executable
        and any externally found Gemini executables. It also verifies if the
        installation directory is included in the system's PATH.
        """
        try:
            from claif.common.install import find_executable, get_install_dir
        except ImportError:
            _print_error("Installation utilities are not available. Please ensure 'claif' is properly installed.")
            return

        _print("\n[bold underline]Gemini Provider Status[/bold underline]")

        # Check for the bundled executable within the expected install directory.
        install_dir: Path = get_install_dir()
        bundled_path: Path = install_dir / "gemini"

        if bundled_path.exists():
            _print_success(f"Bundled executable found: [green]{bundled_path}[/green]")
        else:
            _print_warning("Bundled executable: [yellow]Not installed[/yellow]")

        # Check for any external Gemini executable in the system's PATH.
        try:
            external_path: str = find_executable("gemini")
            _print_success(f"External executable found: [green]{external_path}[/green]")
        except Exception:
            _print_error("No external 'gemini' executable found in system PATH.")

        # Verify if the installation directory is included in the system's PATH.
        path_env: str = os.environ.get("PATH", "")
        if str(install_dir) in path_env:
            _print_success("Installation directory is in system PATH.")
        else:
            _print_warning(f"Installation directory [yellow]{install_dir}[/yellow] is NOT in system PATH.")
            path_cmd: str = f'export PATH="{install_dir}:$PATH"'
            _print(f"  To add it, run: [cyan]{path_cmd}[/cyan]")
            _print("  (Remember to source your shell's profile file afterwards, e.g., ~/.bashrc or ~/.zshrc)")

    def _process_images(self, images: str) -> List[str]:
        """
        Processes a comma-separated string of image paths or URLs.

        If an item is a URL, it downloads the image to a temporary file.
        If an item is a local path, it resolves the absolute path.

        Args:
            images: A comma-separated string where each part is either a local
                    file path or a URL to an image.

        Returns:
            A list of absolute file paths to the processed images (including
            paths to downloaded temporary files).

        Raises:
            SystemExit: If an image cannot be processed (e.g., download fails, file not found).
        """
        import tempfile
        import urllib.request
        from pathlib import Path

        image_list: List[str] = [img.strip() for img in images.split(",") if img.strip()]
        processed_paths: List[str] = []

        for img in image_list:
            try:
                if img.startswith(("http://", "https://")):
                    # Handle image URLs: download to a temporary file.
                    # Determine file suffix from URL for appropriate temporary file extension.
                    suffix: str = Path(img).suffix or ".jpg"
                    # Create a named temporary file that is automatically deleted when closed.
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                        logger.debug(f"Downloading image from URL: {img}")
                        with urllib.request.urlopen(img) as response:
                            tmp_file.write(response.read())
                        processed_paths.append(tmp_file.name)
                        logger.debug(f"Image downloaded to temporary file: {tmp_file.name}")
                else:
                    # Handle local image file paths.
                    path: Path = Path(img).expanduser().resolve()
                    if path.exists() and path.is_file():
                        processed_paths.append(str(path))
                    else:
                        _print_error(f"Image file not found or is not a file: {img}")
                        sys.exit(1)  # Exit if a local file is not found.
            except Exception as e:
                _print_error(f"Failed to process image {img}: {e}")
                sys.exit(1)  # Exit on any processing error.

        return processed_paths


def main():
    """Main entry point for Fire CLI."""
    fire.Fire(GeminiCLI)
