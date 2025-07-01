# this_file: src/claif_gem/cli.py
"""Fire-based CLI for CLAIF Gemini wrapper."""

import asyncio
import sys
import time

import fire
from loguru import logger
from rich.console import Console
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn

try:
    from claif.common import (
        Provider,
        ResponseMetrics,
        format_metrics,
        format_response,
        load_config,
    )
except ImportError:
    from claif_gem._compat import (
        Provider,
        ResponseMetrics,
        format_metrics,
        format_response,
        load_config,
    )
from claif_gem.client import query
from claif_gem.types import GeminiOptions

console = Console()


class GeminiCLI:
    """CLAIF Gemini CLI with Fire interface."""

    def __init__(self, config_file: str | None = None, verbose: bool = False):
        """Initialize CLI with optional config file."""
        self.config = load_config(config_file)
        if verbose:
            self.config.verbose = True
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
        """
        options = GeminiOptions(
            model=model,
            temperature=temperature,
            system_prompt=system,
            auto_approve=auto_approve,
            yes_mode=yes_mode,
            max_context_length=max_context,
            timeout=timeout,
            verbose=self.config.verbose,
        )

        start_time = time.time()

        try:
            # Run async query
            messages = asyncio.run(self._query_async(prompt, options))

            # Format and display response
            for message in messages:
                formatted = format_response(message, output_format)
                console.print(formatted)

            # Show metrics if requested
            if show_metrics:
                duration = time.time() - start_time
                metrics = ResponseMetrics(
                    duration=duration,
                    provider=Provider.GEMINI,
                    model=model or "default",
                )
                console.print("\n" + format_metrics(metrics))

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            if self.config.verbose:
                console.print_exception()
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
            verbose=self.config.verbose,
        )

        try:
            asyncio.run(self._stream_async(prompt, options))
        except KeyboardInterrupt:
            console.print("\n[yellow]Stream interrupted[/yellow]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            if self.config.verbose:
                console.print_exception()
            sys.exit(1)

    async def _stream_async(self, prompt: str, options: GeminiOptions) -> None:
        """Stream responses with live display."""
        content_buffer = []

        with Live(console=console, refresh_per_second=10) as live:
            async for message in query(prompt, options):
                # Update live display
                if isinstance(message.content, str):
                    content_buffer.append(message.content)
                elif isinstance(message.content, list):
                    for block in message.content:
                        if hasattr(block, "text"):
                            content_buffer.append(block.text)

                live.update("".join(content_buffer))

    def health(self) -> None:
        """Check Gemini service health."""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                task = progress.add_task("Checking Gemini health...", total=None)

                # Simple health check
                result = asyncio.run(self._health_check())
                progress.update(task, completed=True)

            if result:
                console.print("[green]✓ Gemini service is healthy[/green]")
            else:
                console.print("[red]✗ Gemini service is not responding[/red]")
                sys.exit(1)

        except Exception as e:
            console.print(f"[red]Health check failed: {e}[/red]")
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
        console.print("[bold]Available Gemini Models:[/bold]")
        console.print("  • gemini-pro (default)")
        console.print("  • gemini-pro-vision")
        console.print("  • gemini-ultra")
        console.print("\nNote: Model availability depends on your API access level.")

    def config(self, action: str = "show", **kwargs) -> None:
        """Manage Gemini configuration.

        Args:
            action: Action to perform (show, set)
            **kwargs: Configuration values for 'set' action
        """
        if action == "show":
            console.print("[bold]Gemini Configuration:[/bold]")
            gemini_config = self.config.providers.get(Provider.GEMINI, {})

            if isinstance(gemini_config, dict):
                for key, value in gemini_config.items():
                    console.print(f"  {key}: {value}")
            else:
                console.print(f"  enabled: {gemini_config.enabled}")
                console.print(f"  model: {gemini_config.model}")
                console.print(f"  timeout: {gemini_config.timeout}")

        elif action == "set":
            if not kwargs:
                console.print("[red]No configuration values provided[/red]")
                return

            # Update configuration
            for key, value in kwargs.items():
                console.print(f"[green]Set {key} = {value}[/green]")

            console.print(
                "\n[yellow]Note: Configuration changes are temporary. Update config file for persistence.[/yellow]"
            )

        else:
            console.print(f"[red]Unknown action: {action}[/red]")
            console.print("Available actions: show, set")


def main():
    """Main entry point for Fire CLI."""
    fire.Fire(GeminiCLI)
