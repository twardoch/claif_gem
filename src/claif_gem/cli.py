# this_file: claif_gem/src/claif_gem/cli.py
"""CLI interface for Gemini with OpenAI-compatible API."""

import sys

import fire
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.spinner import Spinner

from claif_gem.client import GeminiClient

console = Console()


class CLI:
    """Command-line interface for Gemini."""

    def __init__(self, api_key: str | None = None, cli_path: str | None = None):
        """Initialize CLI with optional API key.

        Args:
            api_key: Google API key (defaults to GEMINI_API_KEY or GOOGLE_API_KEY env var)
            cli_path: Path to gemini CLI executable (defaults to searching PATH)
        """
        self._client = GeminiClient(api_key=api_key, cli_path=cli_path)

    def query(
        self,
        prompt: str,
        model: str = "gemini-1.5-flash",
        temperature: float = 0.7,
        max_tokens: int | None = None,
        stream: bool = False,
        system: str | None = None,
        json_output: bool = False,
    ):
        """Query Gemini with a prompt.

        Args:
            prompt: The user prompt to send
            model: Gemini model name to use
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            system: Optional system message
            json_output: Output raw JSON instead of formatted text
        """
        # Build messages
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        # Prepare parameters
        params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens:
            params["max_tokens"] = max_tokens

        try:
            if stream:
                self._stream_response(params, json_output)
            else:
                self._sync_response(params, json_output)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)

    def _sync_response(self, params: dict, json_output: bool):
        """Handle synchronous response."""
        with console.status("[bold green]Querying Gemini...", spinner="dots"):
            response = self._client.chat.completions.create(**params)

        if json_output:
            console.print_json(response.model_dump_json(indent=2))
        else:
            content = response.choices[0].message.content
            console.print(
                Panel(
                    Markdown(content),
                    title=f"[bold blue]Gemini Response[/bold blue] (Model: {response.model})",
                    border_style="blue",
                )
            )

    def _stream_response(self, params: dict, json_output: bool):
        """Handle streaming response."""
        params["stream"] = True

        if json_output:
            # Stream JSON chunks
            for chunk in self._client.chat.completions.create(**params):
                console.print_json(chunk.model_dump_json())
        else:
            # Stream formatted text
            content = ""
            with Live(
                Panel(
                    Spinner("dots", text="Waiting for response..."),
                    title="[bold blue]Gemini Response[/bold blue]",
                    border_style="blue",
                ),
                refresh_per_second=10,
                console=console,
            ) as live:
                for chunk in self._client.chat.completions.create(**params):
                    if chunk.choices and chunk.choices[0].delta.content:
                        content += chunk.choices[0].delta.content
                        live.update(
                            Panel(
                                Markdown(content),
                                title=f"[bold blue]Gemini Response[/bold blue] (Model: {params['model']})",
                                border_style="blue",
                            )
                        )

    def models(self, json_output: bool = False):
        """List available Gemini models.

        Args:
            json_output: Output as JSON instead of formatted table
        """
        models = [
            {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro", "context": "2M"},
            {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash", "context": "1M"},
            {"id": "gemini-1.5-flash-8b", "name": "Gemini 1.5 Flash 8B", "context": "1M"},
            {"id": "gemini-2.0-flash-exp", "name": "Gemini 2.0 Flash (Experimental)", "context": "1M"},
            {"id": "gemini-pro", "name": "Gemini Pro", "context": "32K"},
            {"id": "gemini-pro-vision", "name": "Gemini Pro Vision", "context": "32K"},
        ]

        if json_output:
            console.print_json(data=models)
        else:
            from rich.table import Table

            table = Table(title="Available Gemini Models")
            table.add_column("Model ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Context Window", style="yellow")

            for model in models:
                table.add_row(model["id"], model["name"], model["context"])

            console.print(table)

    def chat(
        self,
        model: str = "gemini-1.5-flash",
        temperature: float = 0.7,
        system: str | None = None,
    ):
        """Start an interactive chat session with Gemini.

        Args:
            model: Gemini model name to use
            temperature: Sampling temperature (0-2)
            system: Optional system message
        """
        console.print(
            Panel(
                "[bold green]Gemini Interactive Chat[/bold green]\n"
                f"Model: {model} | Temperature: {temperature}\n"
                "Type 'exit' or 'quit' to end the session.",
                border_style="green",
            )
        )

        messages = []
        if system:
            messages.append({"role": "system", "content": system})

        while True:
            # Get user input
            try:
                user_input = console.input("\n[bold cyan]You:[/bold cyan] ")
            except (EOFError, KeyboardInterrupt):
                break

            if user_input.lower() in ["exit", "quit"]:
                break

            # Add user message
            messages.append({"role": "user", "content": user_input})

            # Get assistant response
            console.print("\n[bold magenta]Gemini:[/bold magenta] ", end="")

            try:
                content = ""
                for chunk in self._client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    stream=True,
                ):
                    if chunk.choices and chunk.choices[0].delta.content:
                        chunk_content = chunk.choices[0].delta.content
                        content += chunk_content
                        console.print(chunk_content, end="")

                # Add assistant message to history
                messages.append({"role": "assistant", "content": content})
                console.print()  # New line after response

            except Exception as e:
                console.print(f"\n[red]Error: {e}[/red]")
                # Remove the user message if we failed to get a response
                messages.pop()

        console.print("\n[green]Chat session ended.[/green]")

    def version(self):
        """Show version information."""
        from claif_gem.__version__ import __version__

        console.print(f"claif-gem version {__version__}")


def main():
    """Main entry point for the CLI."""
    fire.Fire(CLI)
